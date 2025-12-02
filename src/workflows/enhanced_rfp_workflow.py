"""
Enhanced RFP LangGraph Workflow with Specialized Multi-Agent Architecture
Orchestrates 7 specialized agents with supervisor-based routing and state management
"""
import logging
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState
from ..agents.supervisor_agent import create_supervisor_agent, AgentType
from ..agents.deep_researcher_agent import create_deep_researcher_agent
from ..agents.solution_architect_agent import create_solution_architect_agent
from ..agents.designer_agent import create_designer_agent
from ..agents.project_manager_agent import create_project_manager_agent
from ..agents.cto_agent import create_cto_agent
from ..agents.qa_ceo_agent import create_qa_ceo_agent

logger = logging.getLogger(__name__)

@dataclass
class WorkflowConfig:
    """Configuration for the enhanced RFP workflow"""
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.1
    google_api_key: Optional[str] = None
    search_engine_id: Optional[str] = None
    max_iterations: int = 50
    enable_supervisor_validation: bool = True
    enable_cto_rejection: bool = True
    enable_quality_gates: bool = False
    recursion_limit: int = 50

class EnhancedRFPWorkflow:
    """
    Enhanced RFP Workflow with specialized multi-agent architecture
    
    Features:
    - 7 specialized agents with distinct responsibilities
    - Supervisor-based routing and validation
    - CTO rejection and loop-back capability
    - Comprehensive quality gates
    - State management and error handling
    - Flexible configuration and extensibility
    """
    
    def __init__(self, config: WorkflowConfig, output_dir: str = "./output"):
        self.config = config
        self.output_dir = output_dir
        self.llm = ChatOpenAI(model=config.llm_model, temperature=config.llm_temperature)
        
        # Initialize all agents
        self.supervisor_agent = create_supervisor_agent(self.llm)
        self.deep_researcher_agent = create_deep_researcher_agent(
            self.llm, config.google_api_key, config.search_engine_id
        )
        self.solution_architect_agent = create_solution_architect_agent(self.llm)
        self.designer_agent = create_designer_agent(self.llm)
        self.project_manager_agent = create_project_manager_agent(self.llm)
        self.cto_agent = create_cto_agent(self.llm)
        self.qa_ceo_agent = create_qa_ceo_agent(self.llm)
        
        # Build the workflow graph
        self.workflow = self._build_workflow_graph()
    
    def _build_workflow_graph(self) -> StateGraph:
        """Build the LangGraph workflow with all agents and routing logic"""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add all agent nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("deep_researcher", self._deep_researcher_node)
        workflow.add_node("solution_architect", self._solution_architect_node)
        workflow.add_node("designer", self._designer_node)
        workflow.add_node("project_manager", self._project_manager_node)
        workflow.add_node("cto", self._cto_node)
        workflow.add_node("qa_ceo", self._qa_ceo_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional routing from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_from_supervisor,
            {
                "deep_researcher": "deep_researcher",
                "solution_architect": "solution_architect",
                "designer": "designer",
                "project_manager": "project_manager",
                "cto": "cto",
                "qa_ceo": "qa_ceo",
                "complete": END
            }
        )
        
        # Add edges back to supervisor from each agent
        workflow.add_edge("deep_researcher", "supervisor")
        workflow.add_edge("solution_architect", "supervisor")
        workflow.add_edge("designer", "supervisor")
        workflow.add_edge("project_manager", "supervisor")
        workflow.add_edge("cto", "supervisor")
        workflow.add_edge("qa_ceo", "supervisor")
        
        return workflow
    
    def _supervisor_node(self, state: WorkflowState) -> WorkflowState:
        """Supervisor node that manages routing and validation"""
        try:
            logger.info(f"Supervisor: Current step = {state.current_step}, Last agent = {state.last_agent_executed}")
            
            # Route to next agent
            routing_decision = self.supervisor_agent.route_next_agent(state)
            
            # Update state with routing decision (convert dataclass to dict)
            state.routing_decision = {
                'next_agent': routing_decision.next_agent.value,
                'reason': routing_decision.reason,
                'validation_result': routing_decision.validation_result.value,
                'required_corrections': routing_decision.required_corrections,
                'confidence': routing_decision.confidence
            }
            state.supervisor_feedback = {
                'next_agent': routing_decision.next_agent.value,
                'reason': routing_decision.reason,
                'validation_result': routing_decision.validation_result.value,
                'confidence': routing_decision.confidence
            }
            
            # Handle rejection scenarios
            if routing_decision.validation_result.value == 'rejected':
                logger.warning(f"Supervisor: Rejecting output from {state.last_agent_executed}")
                state.errors.append(f"Output rejected by supervisor: {routing_decision.reason}")
            
            return state
            
        except Exception as e:
            logger.error(f"Supervisor node failed: {e}")
            state.errors.append(f"Supervisor error: {str(e)}")
            return state
    
    def _deep_researcher_node(self, state: WorkflowState) -> WorkflowState:
        """Deep Researcher agent node"""
        try:
            logger.info("Executing Deep Researcher Agent")
            return self.deep_researcher_agent.process_rfp_documents(state)
        except Exception as e:
            logger.error(f"Deep Researcher node failed: {e}")
            state.errors.append(f"Deep Researcher error: {str(e)}")
            return state
    
    def _solution_architect_node(self, state: WorkflowState) -> WorkflowState:
        """Solution Architect agent node"""
        try:
            logger.info("Executing Solution Architect Agent")
            return self.solution_architect_agent.design_solution_architecture(state, output_dir=self.output_dir)
        except Exception as e:
            logger.error(f"Solution Architect node failed: {e}")
            state.errors.append(f"Solution Architect error: {str(e)}")
            return state
    
    def _designer_node(self, state: WorkflowState) -> WorkflowState:
        """Designer agent node"""
        try:
            logger.info("Executing Designer Agent")
            return self.designer_agent.generate_architecture_diagrams(state, output_dir=self.output_dir)
        except Exception as e:
            logger.error(f"Designer node failed: {e}")
            state.errors.append(f"Designer error: {str(e)}")
            return state
    
    def _project_manager_node(self, state: WorkflowState) -> WorkflowState:
        """Project Manager agent node"""
        try:
            logger.info("Executing Project Manager Agent")
            return self.project_manager_agent.create_project_plan(state)
        except Exception as e:
            logger.error(f"Project Manager node failed: {e}")
            state.errors.append(f"Project Manager error: {str(e)}")
            return state
    
    def _cto_node(self, state: WorkflowState) -> WorkflowState:
        """CTO agent node"""
        try:
            logger.info("Executing CTO Agent")
            return self.cto_agent.validate_technical_solution(state)
        except Exception as e:
            logger.error(f"CTO node failed: {e}")
            state.errors.append(f"CTO error: {str(e)}")
            return state
    
    def _qa_ceo_node(self, state: WorkflowState) -> WorkflowState:
        """QA + CEO agent node"""
        try:
            logger.info("Executing QA + CEO Agent")
            return self.qa_ceo_agent.conduct_final_review(state)
        except Exception as e:
            logger.error(f"QA + CEO node failed: {e}")
            state.errors.append(f"QA + CEO error: {str(e)}")
            return state
    
    def _route_from_supervisor(self, state: WorkflowState) -> str:
        """Route from supervisor based on routing decision"""
        try:
            if hasattr(state, 'routing_decision') and state.routing_decision:
                next_agent_value = state.routing_decision.get('next_agent')
                
                # Map agent type values to node names
                agent_mapping = {
                    AgentType.DEEP_RESEARCHER.value: "deep_researcher",
                    AgentType.SOLUTION_ARCHITECT.value: "solution_architect",
                    AgentType.DESIGNER.value: "designer",
                    AgentType.PROJECT_MANAGER.value: "project_manager",
                    AgentType.CTO.value: "cto",
                    AgentType.QA_CEO.value: "qa_ceo",
                    AgentType.COMPLETE.value: "complete"
                }
                
                return agent_mapping.get(next_agent_value, "complete")
            else:
                # Fallback routing
                logger.warning("No routing decision available, using fallback routing")
                return self._fallback_routing(state)
                
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return "complete"
    
    def _fallback_routing(self, state: WorkflowState) -> str:
        """Fallback routing when supervisor routing fails"""
        
        # Simple sequential routing based on state
        if not state.extracted_data:
            return "deep_researcher"
        elif not state.architecture_design:
            return "solution_architect"
        elif not state.architecture_diagrams:
            return "designer"
        elif not state.project_plan:
            return "project_manager"
        elif not state.cto_validation:
            return "cto"
        elif not state.final_approval:
            return "qa_ceo"
        else:
            return "complete"
    
    def process_rfp(self, raw_documents: List[Dict[str, Any]]) -> WorkflowState:
        """
        Process RFP documents through the enhanced multi-agent workflow
        
        Args:
            raw_documents: List of raw document data
            
        Returns:
            Final workflow state with complete proposal
        """
        try:
            logger.info("Starting enhanced RFP processing workflow")
            
            # Initialize workflow state
            initial_state = WorkflowState(
                raw_documents=raw_documents,
                current_step="workflow_start",
                errors=[],
                metadata={
                    'workflow_type': 'enhanced_multi_agent',
                    'agent_count': 7,
                    'config': {
                        'llm_model': self.config.llm_model,
                        'max_iterations': self.config.max_iterations,
                        'supervisor_validation': self.config.enable_supervisor_validation,
                        'recursion_limit': self.config.recursion_limit
                    }
                }
            )
            
            # Compile and run the workflow
            compiled_workflow = self.workflow.compile()
            
            # Execute workflow with iteration limit and recursion limit
            iteration_count = 0
            current_state = initial_state
            
            # Configure recursion limit for LangGraph
            config = {"recursion_limit": self.config.recursion_limit}
            
            for state_update in compiled_workflow.stream(initial_state, config):
                iteration_count += 1
                
                # Update current state
                if state_update:
                    # Get the latest state from the update
                    for node_name, node_state in state_update.items():
                        if isinstance(node_state, dict):
                            try:
                                current_state = WorkflowState(**node_state)
                            except Exception as e:
                                logger.warning(f"Failed to convert state dict to WorkflowState: {e}")
                                # Keep it as dict but we might have issues later
                                current_state = node_state
                        else:
                            current_state = node_state
                        logger.info(f"Iteration {iteration_count}: Executed {node_name}")
                
                # Check iteration limit
                if iteration_count >= self.config.max_iterations:
                    logger.warning(f"Workflow reached maximum iterations ({self.config.max_iterations})")
                    current_state.errors.append("Workflow terminated due to iteration limit")
                    break
                
                # Check for completion
                if hasattr(current_state, 'routing_decision') and current_state.routing_decision:
                    if current_state.routing_decision.get('next_agent') == AgentType.COMPLETE.value:
                        logger.info("Workflow completed successfully")
                        break
            
            # Finalize state
            current_state.current_step = "workflow_complete"
            current_state.metadata['iteration_count'] = iteration_count
            current_state.metadata['completion_status'] = 'completed' if iteration_count < self.config.max_iterations else 'terminated'
            
            # Log final status
            self._log_workflow_summary(current_state)
            
            return current_state
            
        except Exception as e:
            logger.error(f"Enhanced RFP workflow failed: {e}")
            
            # Return error state
            error_state = WorkflowState(
                raw_documents=raw_documents,
                current_step="workflow_error",
                errors=[f"Workflow execution failed: {str(e)}"],
                metadata={
                    'workflow_type': 'enhanced_multi_agent',
                    'completion_status': 'failed'
                }
            )
            return error_state
    
    def _log_workflow_summary(self, final_state: WorkflowState) -> None:
        """Log workflow execution summary"""
        
        try:
            summary = {
                'completion_status': final_state.metadata.get('completion_status', 'unknown'),
                'iteration_count': final_state.metadata.get('iteration_count', 0),
                'errors_count': len(final_state.errors),
                'components_completed': {
                    'extracted_data': final_state.extracted_data is not None,
                    'architecture_design': final_state.architecture_design is not None,
                    'architecture_diagrams': final_state.architecture_diagrams is not None,
                    'project_plan': final_state.project_plan is not None,
                    'cto_validation': final_state.cto_validation is not None,
                    'final_approval': final_state.final_approval is not None,
                    'proposal': final_state.proposal is not None
                }
            }
            
            completed_components = sum(summary['components_completed'].values())
            total_components = len(summary['components_completed'])
            completion_percentage = (completed_components / total_components) * 100
            
            logger.info(f"Workflow Summary:")
            logger.info(f"  Status: {summary['completion_status']}")
            logger.info(f"  Iterations: {summary['iteration_count']}")
            logger.info(f"  Completion: {completion_percentage:.1f}% ({completed_components}/{total_components})")
            logger.info(f"  Errors: {summary['errors_count']}")
            
            if final_state.errors:
                logger.warning("Workflow errors:")
                for error in final_state.errors:
                    logger.warning(f"  - {error}")
            
            # Log agent execution status
            if hasattr(final_state, 'last_agent_executed') and final_state.last_agent_executed:
                logger.info(f"  Last agent executed: {final_state.last_agent_executed}")
            
            # Log approval status if available
            if final_state.final_approval:
                approval_status = getattr(final_state.final_approval, 'approval_status', 'unknown')
                quality_score = getattr(final_state.final_approval, 'overall_quality_score', 'unknown')
                logger.info(f"  Final approval: {approval_status} (Quality: {quality_score})")
            
        except Exception as e:
            logger.error(f"Failed to log workflow summary: {e}")
    
    def get_workflow_status(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Get current workflow status and progress
        
        Args:
            state: Current workflow state
            
        Returns:
            Status information dictionary
        """
        try:
            # Calculate progress
            progress_steps = [
                ('extracted_data', state.extracted_data is not None),
                ('architecture_design', state.architecture_design is not None),
                ('architecture_diagrams', state.architecture_diagrams is not None),
                ('project_plan', state.project_plan is not None),
                ('cto_validation', state.cto_validation is not None),
                ('final_approval', state.final_approval is not None),
                ('proposal', state.proposal is not None)
            ]
            
            completed_steps = sum(1 for _, completed in progress_steps if completed)
            total_steps = len(progress_steps)
            progress_percentage = (completed_steps / total_steps) * 100
            
            # Determine current phase
            current_phase = "Initialization"
            for step_name, completed in progress_steps:
                if not completed:
                    current_phase = step_name.replace('_', ' ').title()
                    break
            else:
                current_phase = "Complete"
            
            # Get agent status
            agent_status = {}
            if hasattr(state, 'last_agent_executed') and state.last_agent_executed:
                agent_status['last_executed'] = state.last_agent_executed
            
            if hasattr(state, 'routing_decision') and state.routing_decision:
                agent_status['next_agent'] = state.routing_decision.get('next_agent')
                agent_status['routing_confidence'] = state.routing_decision.get('confidence')
            
            return {
                'current_step': state.current_step,
                'current_phase': current_phase,
                'progress_percentage': progress_percentage,
                'completed_steps': completed_steps,
                'total_steps': total_steps,
                'agent_status': agent_status,
                'error_count': len(state.errors),
                'has_errors': len(state.errors) > 0,
                'metadata': state.metadata
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return {
                'current_step': 'unknown',
                'current_phase': 'Error',
                'progress_percentage': 0,
                'error_count': 1,
                'has_errors': True,
                'status_error': str(e)
            }
    
    def validate_workflow_config(self) -> List[str]:
        """
        Validate workflow configuration and dependencies
        
        Returns:
            List of validation issues (empty if valid)
        """
        issues = []
        
        try:
            # Check LLM configuration
            if not self.llm:
                issues.append("LLM not properly configured")
            
            # Check agent initialization
            agents = [
                ('supervisor_agent', self.supervisor_agent),
                ('deep_researcher_agent', self.deep_researcher_agent),
                ('solution_architect_agent', self.solution_architect_agent),
                ('designer_agent', self.designer_agent),
                ('project_manager_agent', self.project_manager_agent),
                ('cto_agent', self.cto_agent),
                ('qa_ceo_agent', self.qa_ceo_agent)
            ]
            
            for agent_name, agent in agents:
                if not agent:
                    issues.append(f"{agent_name} not properly initialized")
            
            # Check workflow graph
            if not self.workflow:
                issues.append("Workflow graph not properly built")
            
            # Check configuration values
            if self.config.max_iterations <= 0:
                issues.append("max_iterations must be positive")
            
            if self.config.llm_temperature < 0 or self.config.llm_temperature > 2:
                issues.append("llm_temperature should be between 0 and 2")
            
            # Check optional dependencies
            if not self.config.google_api_key:
                issues.append("Google API key not configured - external research will be limited")
            
            if not self.config.search_engine_id:
                issues.append("Search engine ID not configured - external research will be limited")
            
        except Exception as e:
            issues.append(f"Configuration validation failed: {str(e)}")
        
        return issues

# Factory function to create enhanced workflow
def create_enhanced_rfp_workflow(config: Optional[WorkflowConfig] = None, output_dir: str = "./output") -> EnhancedRFPWorkflow:
    """
    Create and configure enhanced RFP workflow
    
    Args:
        config: Workflow configuration (uses defaults if not provided)
        output_dir: Directory to save outputs (default: ./output)
        
    Returns:
        Configured enhanced RFP workflow
    """
    if config is None:
        config = WorkflowConfig()
    
    return EnhancedRFPWorkflow(config, output_dir=output_dir)

# Convenience function for quick workflow execution
def process_rfp_with_enhanced_workflow(
    raw_documents: List[Dict[str, Any]],
    config: Optional[WorkflowConfig] = None,
    output_dir: str = "./output"
) -> WorkflowState:
    """
    Process RFP documents using the enhanced multi-agent workflow
    
    Args:
        raw_documents: List of raw document data
        config: Workflow configuration
        output_dir: Directory to save outputs (default: ./output)
        
    Returns:
        Final workflow state with complete proposal
    """
    workflow = create_enhanced_rfp_workflow(config, output_dir=output_dir)
    return workflow.process_rfp(raw_documents)