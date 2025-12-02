"""
Proposal generation agent for mapping extracted RFP data to the proposal template structure.
Creates a complete RFP proposal following the template definition.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import logging

from ..models.rfp_models import (
    RFPExtractedData, RFPProposal, WorkflowState, CoverInfo, MetaInfo,
    BackgroundAndObjectives, Phase, SolutionArchitecture, DeploymentView,
    Plan, Commercials, AppendixStories, UserStory, Component, Milestone,
    CostItem, Dependency, Services, DiagramSpec
)

logger = logging.getLogger(__name__)


class ProposalGeneratorAgent:
    """Agent for generating structured RFP proposals from extracted data"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.2):
        """
        Initialize the proposal generator agent.
        
        Args:
            model_name: OpenAI model to use
            temperature: Model temperature for creativity in proposal generation
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=RFPProposal)
        
        # Create proposal generation prompt
        self.generation_prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", """Generate a comprehensive RFP proposal based on the following extracted and normalized data:

**Extracted RFP Data:**
{extracted_data}

**Additional Context:**
- Vendor Name: {vendor_name}
- Contact Email: {contact_email}
- Default Methodology: Agile with 2-week sprints

Please create a complete proposal that addresses all requirements and follows best practices for RFP responses.""")
        ])
        
        # Create generation chain
        self.generation_chain = self.generation_prompt | self.llm | self.parser
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for proposal generation"""
        return """You are an expert RFP proposal writer with extensive experience in creating winning proposals for technology projects. Your task is to transform extracted RFP data into a comprehensive, professional proposal that follows the specified template structure.

**Proposal Generation Guidelines:**

1. **Cover & Meta Information:**
   - Use extracted project title and client name
   - Generate professional version numbering
   - Include appropriate confidentiality statements

2. **Background & Objectives:**
   - Synthesize business context from extracted goals
   - Create clear, measurable objectives
   - Describe current state challenges

3. **Phase Structure:**
   - Organize deliverables into logical phases (typically 2-4 phases)
   - Ensure each phase has clear scope and acceptance criteria
   - Include appropriate services for each phase
   - Map dependencies and assumptions

4. **Solution Architecture:**
   - Propose appropriate architecture based on requirements
   - Create diagram specifications with nodes and edges
   - Justify technology choices based on constraints

5. **Deployment View:**
   - Recommend deployment environments (Dev, Test, Prod)
   - Consider hosting constraints from RFP
   - Include networking and security considerations

6. **Project Plan:**
   - Use Agile methodology with appropriate sprint lengths
   - Create realistic milestones based on phases
   - Include UAT phases for each major deliverable

7. **Commercials:**
   - Provide realistic cost estimates
   - Break down costs by phase and resource type
   - Include licensing and infrastructure costs
   - State payment terms and cost assumptions

8. **User Stories & Components:**
   - Generate user stories from functional requirements
   - Recommend appropriate technology components
   - Provide rationale for technology choices

**Quality Standards:**
- Ensure all mandatory deliverables are addressed
- Maintain consistency across all sections
- Use professional language and formatting
- Include realistic timelines and costs
- Address all stated constraints and requirements

**Default Values:**
- Methodology: Agile with 2-week sprints
- Payment Terms: Net 30 days
- Vendor: Professional technology consulting firm
- Architecture: Modern, scalable, cloud-native when appropriate

{format_instructions}"""
    
    def generate_proposal(self, state: WorkflowState, vendor_name: str = "TechSolutions Inc.", 
                         contact_email: str = "proposals@techsolutions.com") -> WorkflowState:
        """
        Generate a complete RFP proposal from normalized data.
        
        Args:
            state: Current workflow state containing normalized data
            vendor_name: Name of the proposing vendor
            contact_email: Contact email for the proposal
            
        Returns:
            Updated workflow state with generated proposal
        """
        try:
            if not state.normalized_data:
                raise ValueError("No normalized data available for proposal generation")
            
            logger.info("Starting proposal generation...")
            
            # Convert normalized data to JSON for processing
            extracted_json = state.normalized_data.model_dump_json(indent=2)
            
            # Generate proposal using LLM
            proposal = self.generation_chain.invoke({
                "extracted_data": extracted_json,
                "vendor_name": vendor_name,
                "contact_email": contact_email,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Apply post-processing improvements
            proposal = self._post_process_proposal(proposal, state.normalized_data)
            
            # Update state
            state.proposal = proposal
            state.json_output = proposal.model_dump()
            state.current_step = "proposal_generated"
            state.processing_status = "proposal_generated"
            
            logger.info("Proposal generation completed successfully")
            return state
            
        except Exception as e:
            error_msg = f"Error generating proposal: {str(e)}"
            logger.error(error_msg)
            state.processing_errors.append(error_msg)
            state.processing_status = "error"
            return state
    
    def _post_process_proposal(self, proposal: RFPProposal, extracted_data: RFPExtractedData) -> RFPProposal:
        """Apply post-processing improvements to the generated proposal"""
        
        # Ensure cover information is complete
        if not proposal.cover.project_title and extracted_data.project_title:
            proposal.cover.project_title = extracted_data.project_title
        
        if not proposal.cover.client_name and extracted_data.client_organization:
            proposal.cover.client_name = extracted_data.client_organization
        
        # Ensure at least one phase exists
        if not proposal.phases:
            proposal.phases = self._create_default_phases(extracted_data)
        
        # Ensure solution architecture has basic structure
        if not proposal.solution_architecture.architecture_summary:
            proposal.solution_architecture = self._create_default_architecture(extracted_data)
        
        # Ensure deployment view is populated
        if not proposal.deployment_view.environments:
            proposal.deployment_view.environments = ["Development", "Testing", "Production"]
        
        # Ensure plan has milestones
        if not proposal.plan.milestones:
            proposal.plan.milestones = self._create_default_milestones(proposal.phases)
        
        # Ensure commercials have basic cost structure
        if not proposal.commercials.cost_table:
            proposal.commercials.cost_table = self._create_default_costs(proposal.phases)
        
        return proposal
    
    def _create_default_phases(self, extracted_data: RFPExtractedData) -> List[Phase]:
        """Create default phases if none were generated"""
        phases = []
        
        # Phase 1: Analysis and Design
        phase1 = Phase(
            phase_number=1,
            title="Analysis and Design",
            scope_summary="Requirements analysis, system design, and project planning",
            deliverables=[
                "Requirements specification document",
                "System architecture design",
                "Technical specification",
                "Project plan and timeline"
            ],
            acceptance_criteria=[
                "All requirements documented and approved",
                "Architecture design reviewed and signed off",
                "Technical specifications complete"
            ],
            services=Services(
                service_list=["Business Analysis", "System Architecture", "Technical Design"],
                service_descriptions={
                    "Business Analysis": "Detailed requirements gathering and analysis",
                    "System Architecture": "High-level system design and architecture",
                    "Technical Design": "Detailed technical specifications"
                }
            )
        )
        phases.append(phase1)
        
        # Phase 2: Development and Testing
        if extracted_data.mandatory_deliverables:
            phase2 = Phase(
                phase_number=2,
                title="Development and Testing",
                scope_summary="System development, unit testing, and integration testing",
                deliverables=extracted_data.mandatory_deliverables[:5],  # Limit to first 5
                acceptance_criteria=[
                    "All features developed according to specifications",
                    "Unit tests pass with 90%+ coverage",
                    "Integration testing completed successfully"
                ],
                services=Services(
                    service_list=["Software Development", "Quality Assurance", "Testing"],
                    service_descriptions={
                        "Software Development": "Full-stack application development",
                        "Quality Assurance": "Code review and quality assurance",
                        "Testing": "Comprehensive testing including unit and integration tests"
                    }
                )
            )
            phases.append(phase2)
        
        # Phase 3: Deployment and Go-Live
        phase3 = Phase(
            phase_number=len(phases) + 1,
            title="Deployment and Go-Live",
            scope_summary="System deployment, user training, and go-live support",
            deliverables=[
                "Production deployment",
                "User training materials",
                "Go-live support",
                "Documentation handover"
            ],
            acceptance_criteria=[
                "System successfully deployed to production",
                "Users trained and comfortable with system",
                "All documentation delivered"
            ],
            services=Services(
                service_list=["Deployment", "Training", "Support"],
                service_descriptions={
                    "Deployment": "Production deployment and configuration",
                    "Training": "End-user and administrator training",
                    "Support": "Go-live support and issue resolution"
                }
            )
        )
        phases.append(phase3)
        
        return phases
    
    def _create_default_architecture(self, extracted_data: RFPExtractedData) -> SolutionArchitecture:
        """Create default solution architecture"""
        
        # Determine architecture based on requirements
        nodes = ["Web Frontend", "API Gateway", "Application Server", "Database"]
        edges = [
            ["Web Frontend", "API Gateway"],
            ["API Gateway", "Application Server"],
            ["Application Server", "Database"]
        ]
        
        # Add integration nodes if integrations are mentioned
        if extracted_data.integrations:
            nodes.append("Integration Layer")
            edges.append(["Application Server", "Integration Layer"])
            for integration in extracted_data.integrations[:3]:  # Limit to 3
                integration_node = f"External {integration}"
                nodes.append(integration_node)
                edges.append(["Integration Layer", integration_node])
        
        technology_choices = []
        if extracted_data.technology_preferences:
            technology_choices = extracted_data.technology_preferences[:5]  # Limit to 5
        else:
            technology_choices = [
                "React.js for frontend development",
                "Node.js for backend services",
                "PostgreSQL for data storage",
                "Docker for containerization",
                "AWS for cloud hosting"
            ]
        
        return SolutionArchitecture(
            architecture_summary="Modern, scalable web application architecture with clear separation of concerns and robust integration capabilities.",
            diagram_spec=DiagramSpec(nodes=nodes, edges=edges),
            key_technology_choices=technology_choices
        )
    
    def _create_default_milestones(self, phases: List[Phase]) -> List[Milestone]:
        """Create default milestones based on phases"""
        milestones = []
        current_date = datetime.now()
        
        for i, phase in enumerate(phases):
            # Estimate phase duration (4-8 weeks per phase)
            weeks_offset = (i + 1) * 6
            milestone_date = current_date + timedelta(weeks=weeks_offset)
            
            milestone = Milestone(
                name=f"{phase.title} Complete",
                date=milestone_date.strftime("%Y-%m-%d"),
                description=f"Completion of {phase.title} with all deliverables and acceptance criteria met"
            )
            milestones.append(milestone)
        
        return milestones
    
    def _create_default_costs(self, phases: List[Phase]) -> List[CostItem]:
        """Create default cost structure based on phases"""
        cost_items = []
        
        # Base costs per phase (these are examples - real costs would be calculated differently)
        base_costs = {
            "Analysis and Design": 25000,
            "Development and Testing": 75000,
            "Deployment and Go-Live": 15000
        }
        
        for phase in phases:
            phase_cost = base_costs.get(phase.title, 30000)  # Default cost
            
            cost_item = CostItem(
                item=f"{phase.title} Phase",
                description=f"All services and deliverables for {phase.title}",
                cost=phase_cost,
                unit="Fixed Price"
            )
            cost_items.append(cost_item)
        
        # Add project management cost
        total_dev_cost = sum(item.cost for item in cost_items)
        pm_cost = CostItem(
            item="Project Management",
            description="Overall project management and coordination",
            cost=total_dev_cost * 0.15,  # 15% of development cost
            unit="Fixed Price"
        )
        cost_items.append(pm_cost)
        
        return cost_items
    
    def validate_proposal(self, proposal: RFPProposal, extracted_data: RFPExtractedData) -> List[str]:
        """
        Validate the generated proposal against the original requirements.
        
        Args:
            proposal: Generated proposal
            extracted_data: Original extracted data
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check essential information
        if not proposal.cover.project_title:
            issues.append("Missing project title")
        
        if not proposal.cover.client_name:
            issues.append("Missing client name")
        
        if not proposal.phases:
            issues.append("No project phases defined")
        
        # Check that mandatory deliverables are addressed
        if extracted_data.mandatory_deliverables:
            all_deliverables = []
            for phase in proposal.phases:
                all_deliverables.extend(phase.deliverables)
            
            missing_deliverables = []
            for deliverable in extracted_data.mandatory_deliverables:
                if not any(deliverable.lower() in existing.lower() for existing in all_deliverables):
                    missing_deliverables.append(deliverable)
            
            if missing_deliverables:
                issues.append(f"Missing mandatory deliverables: {', '.join(missing_deliverables[:3])}")
        
        # Check architecture
        if not proposal.solution_architecture.architecture_summary:
            issues.append("Missing solution architecture summary")
        
        # Check costs
        if not proposal.commercials.cost_table:
            issues.append("Missing cost breakdown")
        
        return issues


def create_proposal_generator_node():
    """Create a LangGraph node for proposal generation"""
    agent = ProposalGeneratorAgent()
    
    def generate_node(state: WorkflowState) -> WorkflowState:
        """LangGraph node function for proposal generation"""
        return agent.generate_proposal(state)
    
    return generate_node