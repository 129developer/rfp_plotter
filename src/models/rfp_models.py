"""
Pydantic models for RFP proposal data structures.
Based on the JSON schema defined in the RFP template definition.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class CoverInfo(BaseModel):
    """Cover page information"""
    project_title: str = Field(..., description="RFP project title")
    client_name: str = Field(..., description="Client organization name")
    vendor_name: str = Field(default="Your Company", description="Vendor company name")
    version: str = Field(default="1.0", description="Document version")
    date: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"), description="Document date")
    logo_paths: List[str] = Field(default_factory=list, description="Paths to logo images")


class MetaInfo(BaseModel):
    """Document metadata"""
    doc_version: str = Field(default="1.0", description="Document version")
    prepared_by: str = Field(default="RFP Agent", description="Document preparer")
    contact_email: str = Field(default="contact@yourcompany.com", description="Contact email")
    confidentiality_note: str = Field(
        default="This document contains confidential and proprietary information.",
        description="Confidentiality statement"
    )


class BackgroundAndObjectives(BaseModel):
    """Background context and key objectives"""
    context: str = Field(..., description="Business context and problem statement")
    key_objectives: List[str] = Field(..., description="Key business objectives")
    current_state: str = Field(..., description="Current state description")


class Dependency(BaseModel):
    """Project dependency"""
    dependency: str = Field(..., description="Dependency description")
    owner: str = Field(..., description="Dependency owner")
    lead_time: str = Field(..., description="Expected lead time")


class Services(BaseModel):
    """Services information"""
    service_list: List[str] = Field(default_factory=list, description="List of services")
    service_descriptions: Dict[str, str] = Field(default_factory=dict, description="Service descriptions")


class Phase(BaseModel):
    """Project phase definition"""
    phase_number: int = Field(..., description="Phase number")
    title: str = Field(..., description="Phase title")
    scope_summary: str = Field(..., description="Phase scope summary")
    deliverables: List[str] = Field(default_factory=list, description="Phase deliverables")
    excluded_items: List[str] = Field(default_factory=list, description="Out of scope items")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")
    services: Services = Field(default_factory=Services, description="Phase services")
    assumptions: List[str] = Field(default_factory=list, description="Phase assumptions")
    dependencies: List[Dependency] = Field(default_factory=list, description="Phase dependencies")


class DiagramSpec(BaseModel):
    """Diagram specification for architecture/deployment diagrams"""
    nodes: List[str] = Field(default_factory=list, description="Diagram nodes")
    edges: List[List[str]] = Field(default_factory=list, description="Diagram edges as [from, to] pairs")


class SolutionArchitecture(BaseModel):
    """Solution architecture information"""
    architecture_summary: str = Field(..., description="Architecture overview")
    diagram_spec: DiagramSpec = Field(default_factory=DiagramSpec, description="Architecture diagram specification")
    key_technology_choices: List[str] = Field(default_factory=list, description="Key technology decisions")


class DeploymentView(BaseModel):
    """Deployment view information"""
    environments: List[str] = Field(default_factory=list, description="Deployment environments")
    networking_notes: str = Field(default="", description="Networking considerations")
    diagram_spec: DiagramSpec = Field(default_factory=DiagramSpec, description="Deployment diagram specification")


class Milestone(BaseModel):
    """Project milestone"""
    name: str = Field(..., description="Milestone name")
    date: str = Field(..., description="Target date")
    description: str = Field(default="", description="Milestone description")


class UAT(BaseModel):
    """User Acceptance Testing information"""
    phase: str = Field(..., description="UAT phase")
    duration: str = Field(..., description="UAT duration")
    participants: List[str] = Field(default_factory=list, description="UAT participants")


class Plan(BaseModel):
    """Project plan information"""
    methodology: str = Field(default="Agile", description="Project methodology")
    sprint_length_days: int = Field(default=14, description="Sprint length in days")
    milestones: List[Milestone] = Field(default_factory=list, description="Project milestones")
    uats: List[UAT] = Field(default_factory=list, description="UAT phases")


class CostItem(BaseModel):
    """Cost table item"""
    item: str = Field(..., description="Cost item name")
    description: str = Field(default="", description="Item description")
    cost: float = Field(..., description="Item cost")
    unit: str = Field(default="", description="Cost unit")


class Commercials(BaseModel):
    """Commercial information"""
    cost_table: List[CostItem] = Field(default_factory=list, description="Cost breakdown")
    payment_terms: str = Field(default="Net 30", description="Payment terms")
    licensing_costs: List[CostItem] = Field(default_factory=list, description="Licensing costs")
    assumptions_affecting_cost: List[str] = Field(default_factory=list, description="Cost assumptions")


class UserStory(BaseModel):
    """User story definition"""
    role: str = Field(..., description="User role")
    goal: str = Field(..., description="User goal")
    benefit: str = Field(..., description="Expected benefit")
    acceptance_criteria: List[str] = Field(default_factory=list, description="Acceptance criteria")


class AppendixStories(BaseModel):
    """Appendix user stories"""
    user_stories: List[UserStory] = Field(default_factory=list, description="User stories")


class Component(BaseModel):
    """Technology component recommendation"""
    name: str = Field(..., description="Component name")
    description: str = Field(..., description="Component description")
    rationale: str = Field(..., description="Selection rationale")
    alternatives: List[str] = Field(default_factory=list, description="Alternative options")


class InfraCost(BaseModel):
    """Infrastructure cost item"""
    service: str = Field(..., description="Infrastructure service")
    monthly_cost: float = Field(..., description="Monthly cost")
    annual_cost: float = Field(..., description="Annual cost")
    notes: str = Field(default="", description="Additional notes")


class Contact(BaseModel):
    """Contact information"""
    name: str = Field(default="", description="Contact name")
    role: str = Field(default="", description="Contact role")
    email: str = Field(default="", description="Contact email")
    phone: str = Field(default="", description="Contact phone")


class RFPProposal(BaseModel):
    """Complete RFP proposal data structure"""
    cover: CoverInfo = Field(..., description="Cover page information")
    meta: MetaInfo = Field(default_factory=MetaInfo, description="Document metadata")
    background_and_objectives: BackgroundAndObjectives = Field(..., description="Background and objectives")
    phases: List[Phase] = Field(default_factory=list, description="Project phases")
    solution_architecture: SolutionArchitecture = Field(..., description="Solution architecture")
    deployment_view: DeploymentView = Field(default_factory=DeploymentView, description="Deployment view")
    plan: Plan = Field(default_factory=Plan, description="Project plan")
    commercials: Commercials = Field(default_factory=Commercials, description="Commercial information")
    appendix_stories: AppendixStories = Field(default_factory=AppendixStories, description="User stories")
    components: List[Component] = Field(default_factory=list, description="Technology components")
    infra_costs: List[InfraCost] = Field(default_factory=list, description="Infrastructure costs")
    contact: Contact = Field(default_factory=Contact, description="Contact information")


class RFPExtractedData(BaseModel):
    """Raw extracted data from RFP document before mapping to proposal structure"""
    
    # Business Information
    project_title: Optional[str] = None
    client_organization: Optional[str] = None
    division_department: Optional[str] = None
    business_goals: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    
    # Technical Information
    functional_modules: List[str] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list)
    technology_preferences: List[str] = Field(default_factory=list)
    technology_constraints: List[str] = Field(default_factory=list)
    scalability_requirements: List[str] = Field(default_factory=list)
    performance_expectations: List[str] = Field(default_factory=list)
    hosting_constraints: List[str] = Field(default_factory=list)
    
    # Scope & Delivery
    defined_phases: List[str] = Field(default_factory=list)
    mandatory_deliverables: List[str] = Field(default_factory=list)
    out_of_scope_items: List[str] = Field(default_factory=list)
    timelines: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Constraints
    budget_ranges: List[str] = Field(default_factory=list)
    vendor_restrictions: List[str] = Field(default_factory=list)
    security_requirements: List[str] = Field(default_factory=list)
    interoperability_constraints: List[str] = Field(default_factory=list)
    
    # Additional Metadata
    rfp_release_date: Optional[str] = None
    submission_deadline: Optional[str] = None
    evaluation_criteria: List[str] = Field(default_factory=list)
    contact_persons: List[str] = Field(default_factory=list)
    
    # Raw content for reference
    raw_content: str = Field(default="", description="Original document content")


class WorkflowState(BaseModel):
    """State object for LangGraph workflow"""
    
    # Input
    document_path: Optional[str] = None
    document_content: Optional[str] = None
    raw_documents: Optional[List[Dict[str, Any]]] = None
    
    # Processing stages
    extracted_data: Optional[RFPExtractedData] = None
    normalized_data: Optional[RFPExtractedData] = None
    proposal: Optional[RFPProposal] = None
    
    # Enhanced workflow stages
    architecture_design: Optional[Dict[str, Any]] = None
    architecture_diagrams: Optional[List[Dict[str, Any]]] = None
    project_plan: Optional[Dict[str, Any]] = None
    project_estimate: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    cto_validation: Optional[Dict[str, Any]] = None
    final_approval: Optional[Dict[str, Any]] = None
    qa_results: Optional[Dict[str, Any]] = None
    routing_decision: Optional[Dict[str, Any]] = None
    supervisor_feedback: Optional[Dict[str, Any]] = None
    mermaid_specifications: Optional[Dict[str, Any]] = None
    diagram_specifications: Optional[Dict[str, Any]] = None
    ppt_path: Optional[str] = None
    
    # Output
    json_output: Optional[Dict[str, Any]] = None
    
    # Metadata
    processing_errors: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)  # Alias for enhanced workflow
    processing_status: str = Field(default="initialized")
    current_step: str = Field(default="start")
    last_agent_executed: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)