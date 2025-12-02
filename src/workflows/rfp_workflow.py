"""
Main LangGraph workflow for RFP proposal generation.
Orchestrates the complete pipeline from document parsing to proposal generation.
"""

from typing import Dict, Any, List, Optional, Literal
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import logging

from ..models.rfp_models import WorkflowState
from ..agents.document_parser_agent import create_document_parser_node
from ..agents.data_normalizer_agent import create_data_normalizer_node
from ..agents.proposal_generator_agent import create_proposal_generator_node
from ..agents.architecture_generator_agent import create_architecture_generator_node

logger = logging.getLogger(__name__)


class RFPWorkflow:
    """Main workflow class for RFP proposal generation"""
    
    def __init__(self):
        """Initialize the RFP workflow"""
        self.graph = None
        self.checkpointer = MemorySaver()
        self._build_workflow()
    
    def _build_workflow(self):
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("parse_document", create_document_parser_node())
        workflow.add_node("normalize_data", create_data_normalizer_node())
        workflow.add_node("generate_proposal", create_proposal_generator_node())
        workflow.add_node("enhance_architecture", create_architecture_generator_node())
        workflow.add_node("validate_output", self._create_validation_node())
        workflow.add_node("handle_error", self._create_error_handler_node())
        
        # Define the workflow edges
        workflow.set_entry_point("parse_document")
        
        # Main flow
        workflow.add_edge("parse_document", "normalize_data")
        workflow.add_edge("normalize_data", "generate_proposal")
        workflow.add_edge("generate_proposal", "enhance_architecture")
        workflow.add_edge("enhance_architecture", "validate_output")
        
        # Conditional edges for error handling
        workflow.add_conditional_edges(
            "parse_document",
            self._check_parsing_success,
            {
                "success": "normalize_data",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "normalize_data",
            self._check_normalization_success,
            {
                "success": "generate_proposal",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "generate_proposal",
            self._check_generation_success,
            {
                "success": "enhance_architecture",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "enhance_architecture",
            self._check_architecture_success,
            {
                "success": "validate_output",
                "error": "validate_output"  # Continue even if architecture enhancement fails
            }
        )
        
        workflow.add_conditional_edges(
            "validate_output",
            self._check_validation_success,
            {
                "success": END,
                "retry": "generate_proposal",  # Retry generation if validation fails
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("handle_error", END)
        
        # Compile the workflow
        self.graph = workflow.compile(checkpointer=self.checkpointer)
    
    def _check_parsing_success(self, state: WorkflowState) -> Literal["success", "error"]:
        """Check if document parsing was successful"""
        if state.processing_status == "error" or not state.extracted_data:
            return "error"
        return "success"
    
    def _check_normalization_success(self, state: WorkflowState) -> Literal["success", "error"]:
        """Check if data normalization was successful"""
        if state.processing_status == "error" or not state.normalized_data:
            return "error"
        return "success"
    
    def _check_generation_success(self, state: WorkflowState) -> Literal["success", "error"]:
        """Check if proposal generation was successful"""
        if state.processing_status == "error" or not state.proposal:
            return "error"
        return "success"
    
    def _check_architecture_success(self, state: WorkflowState) -> Literal["success", "error"]:
        """Check if architecture enhancement was successful"""
        if state.processing_status == "error":
            return "error"
        return "success"
    
    def _check_validation_success(self, state: WorkflowState) -> Literal["success", "retry", "error"]:
        """Check if output validation was successful"""
        if state.processing_status == "error":
            return "error"
        elif state.processing_status == "validation_failed" and not hasattr(state, '_retry_count'):
            # Allow one retry
            state._retry_count = 1
            return "retry"
        elif state.processing_status == "validation_failed":
            return "error"
        return "success"
    
    def _create_validation_node(self):
        """Create validation node function"""
        def validate_node(state: WorkflowState) -> WorkflowState:
            """Validate the generated proposal"""
            try:
                logger.info("Starting proposal validation...")
                
                validation_issues = []
                
                # Check if proposal exists
                if not state.proposal:
                    validation_issues.append("No proposal generated")
                else:
                    # Validate essential components
                    if not state.proposal.cover.project_title:
                        validation_issues.append("Missing project title")
                    
                    if not state.proposal.cover.client_name:
                        validation_issues.append("Missing client name")
                    
                    if not state.proposal.phases:
                        validation_issues.append("No project phases defined")
                    
                    if not state.proposal.solution_architecture.architecture_summary:
                        validation_issues.append("Missing architecture summary")
                    
                    # Check that each phase has deliverables
                    for i, phase in enumerate(state.proposal.phases):
                        if not phase.deliverables:
                            validation_issues.append(f"Phase {i+1} has no deliverables")
                    
                    # Check commercials
                    if not state.proposal.commercials.cost_table:
                        validation_issues.append("Missing cost breakdown")
                
                # Update state based on validation
                if validation_issues:
                    logger.warning(f"Validation issues found: {validation_issues}")
                    state.processing_errors.extend(validation_issues)
                    
                    # If issues are minor, continue; if major, mark as failed
                    major_issues = [issue for issue in validation_issues 
                                  if any(keyword in issue.lower() 
                                        for keyword in ['missing', 'no proposal', 'no project phases'])]
                    
                    if major_issues:
                        state.processing_status = "validation_failed"
                    else:
                        state.processing_status = "completed_with_warnings"
                        logger.info("Validation completed with minor warnings")
                else:
                    state.processing_status = "completed"
                    logger.info("Validation completed successfully")
                
                state.current_step = "validated"
                return state
                
            except Exception as e:
                error_msg = f"Error during validation: {str(e)}"
                logger.error(error_msg)
                state.processing_errors.append(error_msg)
                state.processing_status = "error"
                return state
        
        return validate_node
    
    def _create_error_handler_node(self):
        """Create error handler node function"""
        def error_handler_node(state: WorkflowState) -> WorkflowState:
            """Handle errors in the workflow"""
            logger.error(f"Workflow error in step '{state.current_step}': {state.processing_errors}")
            
            # Set final error status
            state.processing_status = "failed"
            state.current_step = "error_handled"
            
            # Try to provide partial results if available
            if state.extracted_data and not state.proposal:
                logger.info("Providing partial results - extracted data available")
                state.processing_status = "partial_success"
            
            return state
        
        return error_handler_node
    
    def process_rfp(self, document_path: Optional[str] = None, 
                   document_content: Optional[str] = None,
                   config: Optional[Dict[str, Any]] = None) -> WorkflowState:
        """
        Process an RFP document through the complete workflow.
        
        Args:
            document_path: Path to the RFP document file
            document_content: Direct document content (alternative to file path)
            config: Optional configuration for the workflow
            
        Returns:
            Final workflow state with results
        """
        if not document_path and not document_content:
            raise ValueError("Either document_path or document_content must be provided")
        
        # Initialize state
        initial_state = WorkflowState(
            document_path=document_path,
            document_content=document_content,
            processing_status="initialized",
            current_step="start"
        )
        
        # Set up configuration
        workflow_config = config or {}
        if "thread_id" not in workflow_config:
            import uuid
            workflow_config["thread_id"] = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting RFP processing workflow with thread_id: {workflow_config['thread_id']}")
            
            # Run the workflow
            final_state = None
            for state in self.graph.stream(initial_state, config=workflow_config):
                final_state = list(state.values())[0]  # Get the state from the dict
                logger.info(f"Workflow step completed: {final_state.current_step}")
            
            if final_state is None:
                raise RuntimeError("Workflow did not produce any output")
            
            logger.info(f"Workflow completed with status: {final_state.processing_status}")
            return final_state
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            # Return error state
            error_state = initial_state
            error_state.processing_errors.append(str(e))
            error_state.processing_status = "failed"
            error_state.current_step = "workflow_error"
            return error_state
    
    def get_workflow_status(self, thread_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow execution.
        
        Args:
            thread_id: Thread ID of the workflow execution
            
        Returns:
            Dictionary containing workflow status information
        """
        try:
            # Get the latest state from checkpointer
            config = {"thread_id": thread_id}
            state = self.graph.get_state(config)
            
            if state and state.values:
                current_state = state.values
                return {
                    "status": current_state.get("processing_status", "unknown"),
                    "current_step": current_state.get("current_step", "unknown"),
                    "errors": current_state.get("processing_errors", []),
                    "has_proposal": bool(current_state.get("proposal")),
                    "has_extracted_data": bool(current_state.get("extracted_data"))
                }
            else:
                return {
                    "status": "not_found",
                    "current_step": "unknown",
                    "errors": ["Workflow not found"],
                    "has_proposal": False,
                    "has_extracted_data": False
                }
                
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {
                "status": "error",
                "current_step": "unknown",
                "errors": [str(e)],
                "has_proposal": False,
                "has_extracted_data": False
            }
    
    def resume_workflow(self, thread_id: str, from_step: Optional[str] = None) -> WorkflowState:
        """
        Resume a workflow from a specific step.
        
        Args:
            thread_id: Thread ID of the workflow to resume
            from_step: Optional step to resume from
            
        Returns:
            Final workflow state
        """
        try:
            config = {"thread_id": thread_id}
            
            # Get current state
            current_state_snapshot = self.graph.get_state(config)
            if not current_state_snapshot or not current_state_snapshot.values:
                raise ValueError(f"No workflow found with thread_id: {thread_id}")
            
            # Resume from current state
            final_state = None
            for state in self.graph.stream(None, config=config):
                final_state = list(state.values())[0]
                logger.info(f"Resumed workflow step: {final_state.current_step}")
            
            return final_state
            
        except Exception as e:
            logger.error(f"Error resuming workflow: {e}")
            raise


# Convenience function to create and run workflow
def process_rfp_document(document_path: Optional[str] = None,
                        document_content: Optional[str] = None,
                        config: Optional[Dict[str, Any]] = None) -> WorkflowState:
    """
    Convenience function to process an RFP document.
    
    Args:
        document_path: Path to the RFP document file
        document_content: Direct document content
        config: Optional workflow configuration
        
    Returns:
        Final workflow state with results
    """
    workflow = RFPWorkflow()
    return workflow.process_rfp(document_path, document_content, config)