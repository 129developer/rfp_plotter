"""
Supervisor Node (Orchestrator) for the RFP LangGraph Agent System
Central control system that manages state and routes execution between specialized agents
"""
import json
import logging
from typing import Dict, List, Optional, Any, Literal
from dataclasses import dataclass
from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState, RFPProposal

logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Available agent types in the system"""
    DEEP_RESEARCHER = "deep_researcher"
    SOLUTION_ARCHITECT = "solution_architect"
    DESIGNER = "designer"
    PROJECT_MANAGER = "project_manager"
    CTO = "cto"
    QA_CEO = "qa_ceo"
    COMPLETE = "complete"

class ValidationResult(Enum):
    """Validation results for agent outputs"""
    VALID = "valid"
    INVALID = "invalid"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"

@dataclass
class RoutingDecision:
    """Represents a routing decision made by the supervisor"""
    next_agent: AgentType
    reason: str
    validation_result: ValidationResult
    required_corrections: List[str]
    confidence: float

class SupervisorAgent:
    """
    Supervisor Node that orchestrates the RFP processing workflow
    
    Responsibilities:
    - Analyze shared state and determine next agent
    - Validate outputs from previous agents
    - Route execution to appropriate specialized agents
    - Handle rejection scenarios and correction loops
    - Manage overall workflow state
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Define the standard workflow sequence
        self.standard_sequence = [
            AgentType.DEEP_RESEARCHER,
            AgentType.SOLUTION_ARCHITECT,
            AgentType.DESIGNER,
            AgentType.PROJECT_MANAGER,
            AgentType.CTO,
            AgentType.QA_CEO,
            AgentType.COMPLETE
        ]
        
        # Define validation criteria for each agent's output
        self.validation_criteria = {
            AgentType.DEEP_RESEARCHER: {
                'required_fields': ['extracted_requirements', 'client_context', 'research_findings'],
                'quality_checks': ['requirements_completeness', 'research_depth']
            },
            AgentType.SOLUTION_ARCHITECT: {
                'required_fields': ['architecture_design', 'technology_stack', 'system_components'],
                'quality_checks': ['technical_feasibility', 'scalability_considerations']
            },
            AgentType.DESIGNER: {
                'required_fields': ['architecture_diagrams', 'visual_representations'],
                'quality_checks': ['diagram_clarity', 'technical_accuracy']
            },
            AgentType.PROJECT_MANAGER: {
                'required_fields': ['project_plan', 'effort_estimates', 'timeline'],
                'quality_checks': ['estimate_reasonableness', 'risk_assessment']
            },
            AgentType.CTO: {
                'required_fields': ['technical_validation', 'security_assessment', 'architecture_approval'],
                'quality_checks': ['security_compliance', 'technical_debt_analysis']
            },
            AgentType.QA_CEO: {
                'required_fields': ['quality_assessment', 'executive_review', 'final_approval'],
                'quality_checks': ['completeness_validation', 'tone_analysis']
            }
        }
    
    def route_next_agent(self, state: WorkflowState) -> RoutingDecision:
        """
        Analyze the current state and determine the next agent to execute
        
        Args:
            state: Current workflow state
            
        Returns:
            Routing decision with next agent and reasoning
        """
        try:
            # Get current workflow status
            current_step = state.current_step
            last_agent = state.last_agent_executed
            
            # Validate the output of the previous agent (if any)
            if last_agent:
                validation_result = self._validate_agent_output(state, last_agent)
                
                # Handle rejection scenarios
                if validation_result == ValidationResult.REJECTED:
                    return self._handle_rejection(state, last_agent)
                elif validation_result == ValidationResult.NEEDS_REVISION:
                    return self._handle_revision_request(state, last_agent)
            else:
                validation_result = ValidationResult.VALID
            
            # Determine next agent based on workflow state
            next_agent = self._determine_next_agent(state)
            
            # Generate routing decision
            decision = RoutingDecision(
                next_agent=next_agent,
                reason=self._generate_routing_reason(state, next_agent, validation_result),
                validation_result=validation_result,
                required_corrections=self._get_required_corrections(state, last_agent),
                confidence=self._calculate_routing_confidence(state, next_agent)
            )
            
            logger.info(f"Supervisor routing decision: {next_agent.value} (reason: {decision.reason})")
            return decision
            
        except Exception as e:
            logger.error(f"Supervisor routing failed: {e}")
            return self._get_fallback_routing_decision(state)
    
    def _validate_agent_output(self, state: WorkflowState, agent_type: str) -> ValidationResult:
        """
        Validate the output of the specified agent
        
        Args:
            state: Current workflow state
            agent_type: Type of agent to validate
            
        Returns:
            Validation result
        """
        try:
            agent_enum = AgentType(agent_type)
            criteria = self.validation_criteria.get(agent_enum, {})
            
            # Check required fields
            required_fields = criteria.get('required_fields', [])
            missing_fields = []
            
            for field in required_fields:
                if not self._check_field_exists(state, field):
                    missing_fields.append(field)
            
            if missing_fields:
                logger.warning(f"Agent {agent_type} missing required fields: {missing_fields}")
                return ValidationResult.INVALID
            
            # Perform quality checks using LLM
            quality_result = self._perform_quality_checks(state, agent_enum)
            
            if quality_result == "rejected":
                return ValidationResult.REJECTED
            elif quality_result == "needs_revision":
                return ValidationResult.NEEDS_REVISION
            else:
                return ValidationResult.VALID
                
        except Exception as e:
            logger.error(f"Agent output validation failed: {e}")
            return ValidationResult.NEEDS_REVISION
    
    def _perform_quality_checks(self, state: WorkflowState, agent_type: AgentType) -> str:
        """
        Perform LLM-based quality checks on agent output
        
        Args:
            state: Current workflow state
            agent_type: Agent type to validate
            
        Returns:
            Quality check result: "valid", "needs_revision", or "rejected"
        """
        try:
            # Create validation prompt based on agent type
            validation_prompt = self._create_validation_prompt(state, agent_type)
            
            messages = [
                SystemMessage(content="""You are the RFP Automation Supervisor. Your job is to analyze the shared state and validate the output of the previous agent. 

Respond with one of these validation results:
- "valid": Output meets quality standards and requirements
- "needs_revision": Output has minor issues that need correction
- "rejected": Output has major flaws and needs complete rework

Provide your assessment based on completeness, quality, and alignment with RFP requirements."""),
                HumanMessage(content=validation_prompt)
            ]
            print(messages)
            response = self.llm.invoke(messages)
            print(response)
            result = response.content.lower().strip()
            
            # Extract validation result
            if "rejected" in result:
                return "rejected"
            elif "needs_revision" in result:
                return "needs_revision"
            else:
                return "valid"
                
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            return "needs_revision"
    
    def _create_validation_prompt(self, state: WorkflowState, agent_type: AgentType) -> str:
        """Create validation prompt for specific agent type"""
        
        base_context = f"""
Current workflow state:
- Step: {state.current_step}
- Last agent: {state.last_agent_executed}
- Validating: {agent_type.value}

State data available:
- Raw documents: {'Yes' if state.raw_documents else 'No'}
- Extracted data: {'Yes' if state.extracted_data else 'No'}
- Architecture: {'Yes' if state.architecture_design else 'No'}
- Proposal: {'Yes' if state.proposal else 'No'}
"""
        
        if agent_type == AgentType.DEEP_RESEARCHER:
            return f"""{base_context}

Validate the Deep Researcher output:
- Are requirements properly extracted and structured?
- Is client context adequately researched?
- Are external research findings relevant and comprehensive?
- Is the extracted data sufficient for solution design?

Extracted data summary: {str(state.extracted_data)[:500] if state.extracted_data else 'None'}
"""
        
        elif agent_type == AgentType.SOLUTION_ARCHITECT:
            return f"""{base_context}

Validate the Solution Architect output:
- Is the architecture design technically sound?
- Is the technology stack appropriate for requirements?
- Are system components well-defined?
- Does the solution address all identified requirements?

Architecture summary: {str(state.architecture_design)[:500] if state.architecture_design else 'None'}
"""
        
        elif agent_type == AgentType.DESIGNER:
            return f"""{base_context}

Validate the Designer output:
- Are architecture diagrams clear and professional?
- Do visual representations accurately reflect the technical design?
- Are diagrams suitable for client presentation?

Diagrams available: {len(state.architecture_diagrams) if state.architecture_diagrams else 0}
"""
        
        elif agent_type == AgentType.PROJECT_MANAGER:
            return f"""{base_context}

Validate the Project Manager output:
- Is the project plan comprehensive and realistic?
- Are effort estimates reasonable and well-justified?
- Is the timeline achievable with proper risk buffers?
- Are resource allocations appropriate?

Project plan summary: {str(state.project_plan)[:500] if state.project_plan else 'None'}
"""
        
        elif agent_type == AgentType.CTO:
            return f"""{base_context}

Validate the CTO output:
- Has technical validation been thorough?
- Are security assessments comprehensive?
- Is the architecture approval justified?
- Have technical debt concerns been addressed?

CTO validation: {str(state.cto_validation)[:500] if state.cto_validation else 'None'}
"""
        
        elif agent_type == AgentType.QA_CEO:
            return f"""{base_context}

Validate the QA + CEO output:
- Is quality assessment thorough and accurate?
- Does executive review address strategic concerns?
- Is the proposal ready for client presentation?
- Are all completeness checks satisfied?

Final proposal: {'Complete' if state.proposal else 'Incomplete'}
"""
        
        else:
            return f"{base_context}\n\nValidate the output for agent: {agent_type.value}"
    
    def _determine_next_agent(self, state: WorkflowState) -> AgentType:
        """
        Determine the next agent to execute based on workflow state
        
        Args:
            state: Current workflow state
            
        Returns:
            Next agent to execute
        """
        try:
            # If no agents have been executed, start with Deep Researcher
            if not state.last_agent_executed:
                return AgentType.DEEP_RESEARCHER
            
            # Get current position in standard sequence
            last_agent_enum = AgentType(state.last_agent_executed)
            
            try:
                current_index = self.standard_sequence.index(last_agent_enum)
                
                # Move to next agent in sequence
                if current_index < len(self.standard_sequence) - 1:
                    return self.standard_sequence[current_index + 1]
                else:
                    return AgentType.COMPLETE
                    
            except ValueError:
                # Last agent not in standard sequence, determine based on state
                return self._determine_agent_from_state(state)
                
        except Exception as e:
            logger.error(f"Next agent determination failed: {e}")
            return AgentType.DEEP_RESEARCHER
    
    def _determine_agent_from_state(self, state: WorkflowState) -> AgentType:
        """Determine next agent based on current state when not following standard sequence"""
        
        if not state.extracted_data:
            return AgentType.DEEP_RESEARCHER
        elif not state.architecture_design:
            return AgentType.SOLUTION_ARCHITECT
        elif not state.architecture_diagrams:
            return AgentType.DESIGNER
        elif not state.project_plan:
            return AgentType.PROJECT_MANAGER
        elif not state.cto_validation:
            return AgentType.CTO
        elif not state.final_approval:
            return AgentType.QA_CEO
        else:
            return AgentType.COMPLETE
    
    def _handle_rejection(self, state: WorkflowState, rejected_agent: str) -> RoutingDecision:
        """
        Handle rejection scenario - route back to appropriate agent for rework
        
        Args:
            state: Current workflow state
            rejected_agent: Agent whose output was rejected
            
        Returns:
            Routing decision for correction
        """
        # Special handling for CTO rejections
        if rejected_agent == AgentType.CTO.value:
            # CTO rejection typically means architecture needs rework
            return RoutingDecision(
                next_agent=AgentType.SOLUTION_ARCHITECT,
                reason="CTO rejected architecture - routing back to Solution Architect for redesign",
                validation_result=ValidationResult.REJECTED,
                required_corrections=["Address CTO technical concerns", "Redesign architecture"],
                confidence=0.9
            )
        else:
            # For other rejections, route back to the same agent
            rejected_agent_enum = AgentType(rejected_agent)
            return RoutingDecision(
                next_agent=rejected_agent_enum,
                reason=f"Output rejected - routing back to {rejected_agent} for rework",
                validation_result=ValidationResult.REJECTED,
                required_corrections=["Address validation failures", "Improve output quality"],
                confidence=0.8
            )
    
    def _handle_revision_request(self, state: WorkflowState, agent_type: str) -> RoutingDecision:
        """
        Handle revision request - minor corrections needed
        
        Args:
            state: Current workflow state
            agent_type: Agent that needs to make revisions
            
        Returns:
            Routing decision for revision
        """
        # Track revision attempts to prevent infinite loops
        revision_key = f"{agent_type}_revision_count"
        revision_count = state.metadata.get(revision_key, 0)
        
        # If we've tried revisions too many times, accept and move forward
        MAX_REVISION_ATTEMPTS = 2
        if revision_count >= MAX_REVISION_ATTEMPTS:
            logger.warning(f"Max revision attempts ({MAX_REVISION_ATTEMPTS}) reached for {agent_type}, accepting output and moving forward")
            # Move to next agent instead of looping
            next_agent = self._determine_next_agent(state)
            return RoutingDecision(
                next_agent=next_agent,
                reason=f"Max revisions reached for {agent_type}, accepting output and proceeding",
                validation_result=ValidationResult.VALID,
                required_corrections=[],
                confidence=0.6
            )
        
        # Increment revision counter
        state.metadata[revision_key] = revision_count + 1
        
        agent_enum = AgentType(agent_type)
        return RoutingDecision(
            next_agent=agent_enum,
            reason=f"Minor revisions needed for {agent_type} output (attempt {revision_count + 1}/{MAX_REVISION_ATTEMPTS})",
            validation_result=ValidationResult.NEEDS_REVISION,
            required_corrections=["Address minor quality issues", "Refine output"],
            confidence=0.7
        )
    
    def _check_field_exists(self, state: WorkflowState, field_name: str) -> bool:
        """Check if a required field exists in the state"""
        
        def check_attr_or_item(obj, field):
            if obj is None:
                return False
            if isinstance(obj, dict):
                return field in obj and obj[field] is not None
            return hasattr(obj, field) and getattr(obj, field) is not None

        field_mapping = {
            # Deep Researcher (RFPExtractedData model)
            'extracted_requirements': lambda s: check_attr_or_item(s.extracted_data, 'functional_modules'),
            'client_context': lambda s: check_attr_or_item(s.extracted_data, 'client_organization'),
            'research_findings': lambda s: s.extracted_data is not None, # Research is integrated into extracted_data
            
            # Solution Architect (Dict)
            'architecture_design': lambda s: s.architecture_design is not None,
            'technology_stack': lambda s: check_attr_or_item(s.architecture_design, 'technology_stack'),
            'system_components': lambda s: check_attr_or_item(s.architecture_design, 'system_components'),
            
            # Designer (List[Dict])
            'architecture_diagrams': lambda s: s.architecture_diagrams and len(s.architecture_diagrams) > 0,
            'visual_representations': lambda s: s.architecture_diagrams is not None,
            
            # Project Manager (Dict)
            'project_plan': lambda s: s.project_plan is not None,
            'effort_estimates': lambda s: check_attr_or_item(s.project_plan, 'estimates') or check_attr_or_item(s.project_estimate, 'total_estimate'),
            'timeline': lambda s: check_attr_or_item(s.project_plan, 'timeline'),
            
            # CTO (Dict)
            'technical_validation': lambda s: s.cto_validation is not None,
            'security_assessment': lambda s: check_attr_or_item(s.cto_validation, 'security_audit'),
            'architecture_approval': lambda s: check_attr_or_item(s.cto_validation, 'approved'),
            
            # QA CEO (Dict)
            'quality_assessment': lambda s: s.qa_results is not None,
            'executive_review': lambda s: check_attr_or_item(s.qa_results, 'executive_review'),
            'final_approval': lambda s: s.final_approval is not None
        }
        
        check_function = field_mapping.get(field_name)
        if check_function:
            return check_function(state)
        else:
            # Generic check - look for field in state
            return hasattr(state, field_name) and getattr(state, field_name) is not None
    
    def _generate_routing_reason(self, 
                                state: WorkflowState, 
                                next_agent: AgentType, 
                                validation_result: ValidationResult) -> str:
        """Generate human-readable reason for routing decision"""
        
        if validation_result == ValidationResult.REJECTED:
            return f"Previous agent output rejected - routing to {next_agent.value} for rework"
        elif validation_result == ValidationResult.NEEDS_REVISION:
            return f"Minor revisions needed - routing to {next_agent.value} for corrections"
        else:
            if next_agent == AgentType.COMPLETE:
                return "All agents completed successfully - workflow complete"
            else:
                return f"Previous validation passed - proceeding to {next_agent.value}"
    
    def _get_required_corrections(self, state: WorkflowState, agent_type: Optional[str]) -> List[str]:
        """Get list of required corrections based on validation results"""
        if not agent_type:
            return []
        
        # This would typically be populated by the validation process
        # For now, return generic corrections
        return [
            "Address validation feedback",
            "Ensure all required fields are complete",
            "Improve output quality and completeness"
        ]
    
    def _calculate_routing_confidence(self, state: WorkflowState, next_agent: AgentType) -> float:
        """Calculate confidence level for routing decision"""
        
        # Base confidence
        confidence = 0.8
        
        # Increase confidence if following standard sequence
        if state.last_agent_executed:
            try:
                last_agent_enum = AgentType(state.last_agent_executed)
                last_index = self.standard_sequence.index(last_agent_enum)
                expected_next = self.standard_sequence[last_index + 1] if last_index < len(self.standard_sequence) - 1 else AgentType.COMPLETE
                
                if next_agent == expected_next:
                    confidence = 0.95
                    
            except (ValueError, IndexError):
                confidence = 0.7
        
        # Adjust based on state completeness
        state_completeness = self._calculate_state_completeness(state)
        confidence = confidence * (0.5 + 0.5 * state_completeness)
        
        return min(confidence, 1.0)
    
    def _calculate_state_completeness(self, state: WorkflowState) -> float:
        """Calculate how complete the current state is"""
        
        completeness_checks = [
            state.raw_documents is not None,
            state.extracted_data is not None,
            state.architecture_design is not None,
            state.architecture_diagrams is not None,
            state.project_plan is not None,
            state.cto_validation is not None,
            state.qa_results is not None,
            state.proposal is not None
        ]
        
        return sum(completeness_checks) / len(completeness_checks)
    
    def _get_fallback_routing_decision(self, state: WorkflowState) -> RoutingDecision:
        """Get fallback routing decision when normal routing fails"""
        
        return RoutingDecision(
            next_agent=AgentType.DEEP_RESEARCHER,
            reason="Fallback routing due to supervisor error",
            validation_result=ValidationResult.NEEDS_REVISION,
            required_corrections=["Manual review required"],
            confidence=0.3
        )

# Factory function to create supervisor agent
def create_supervisor_agent(llm: Optional[ChatOpenAI] = None) -> SupervisorAgent:
    """Create and configure supervisor agent"""
    return SupervisorAgent(llm=llm)