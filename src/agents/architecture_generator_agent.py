"""
Architecture generator agent for creating and enhancing solution architecture diagrams.
Generates architecture and deployment diagrams based on proposal specifications.
"""

from typing import Dict, Any, List, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import logging

from ..models.rfp_models import WorkflowState, DiagramSpec, SolutionArchitecture, DeploymentView
from ..utils.diagram_generator import DiagramGenerator, validate_diagram_spec

logger = logging.getLogger(__name__)


class ArchitectureGeneratorAgent:
    """Agent for generating and enhancing architecture diagrams"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.3):
        """
        Initialize the architecture generator agent.
        
        Args:
            model_name: OpenAI model to use
            temperature: Model temperature for creativity in architecture design
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.diagram_generator = DiagramGenerator()
        
        # Create architecture enhancement prompt
        self.enhancement_prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", """Please enhance the architecture diagram specification based on the following proposal:

**Current Architecture:**
Summary: {architecture_summary}
Nodes: {current_nodes}
Edges: {current_edges}

**Technology Choices:**
{technology_choices}

**Functional Requirements:**
{functional_modules}

**Integration Requirements:**
{integrations}

**Constraints:**
{constraints}

Please provide an enhanced architecture with:
1. Improved node structure
2. Better edge relationships
3. Additional components if needed
4. Deployment considerations

Format your response as JSON with 'nodes' and 'edges' arrays.""")
        ])
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for architecture enhancement"""
        return """You are a senior solution architect with expertise in designing scalable, modern software architectures. Your task is to enhance and improve architecture diagrams based on project requirements and constraints.

**Architecture Design Principles:**

1. **Layered Architecture:**
   - Presentation Layer (Web UI, Mobile Apps)
   - API/Service Layer (REST APIs, GraphQL)
   - Business Logic Layer (Application Services)
   - Data Access Layer (Repositories, ORM)
   - Data Storage Layer (Databases, Caches)

2. **Modern Patterns:**
   - Microservices where appropriate
   - API Gateway for service orchestration
   - Event-driven architecture for loose coupling
   - CQRS for complex read/write scenarios
   - Circuit breakers for resilience

3. **Integration Patterns:**
   - Message queues for async communication
   - API gateways for external integrations
   - Event buses for internal communication
   - Data synchronization services

4. **Infrastructure Components:**
   - Load balancers for scalability
   - Caching layers for performance
   - Monitoring and logging services
   - Security components (Auth, Authorization)

5. **Cloud-Native Considerations:**
   - Container orchestration (Kubernetes)
   - Service mesh for microservices
   - Auto-scaling capabilities
   - Multi-region deployment

**Enhancement Guidelines:**
- Add missing architectural layers
- Include necessary infrastructure components
- Consider security and monitoring aspects
- Ensure scalability and maintainability
- Address integration requirements
- Follow cloud-native best practices

**Output Format:**
Provide enhanced architecture as JSON with:
- 'nodes': Array of component names
- 'edges': Array of [from, to] connection pairs
- Keep node names clear and descriptive
- Ensure all edges reference valid nodes"""
    
    def enhance_architecture(self, state: WorkflowState) -> WorkflowState:
        """
        Enhance the architecture diagram in the proposal.
        
        Args:
            state: Current workflow state containing the proposal
            
        Returns:
            Updated workflow state with enhanced architecture diagrams
        """
        try:
            if not state.proposal:
                raise ValueError("No proposal available for architecture enhancement")
            
            logger.info("Starting architecture enhancement...")
            
            # Extract current architecture information
            arch = state.proposal.solution_architecture
            current_nodes = arch.diagram_spec.nodes if arch.diagram_spec else []
            current_edges = arch.diagram_spec.edges if arch.diagram_spec else []
            
            # Gather requirements for enhancement
            functional_modules = []
            integrations = []
            constraints = []
            
            if state.normalized_data:
                functional_modules = state.normalized_data.functional_modules
                integrations = state.normalized_data.integrations
                constraints = (state.normalized_data.technology_constraints + 
                             state.normalized_data.hosting_constraints)
            
            # Enhance architecture using LLM
            enhanced_spec = self._enhance_with_llm(
                arch.architecture_summary,
                current_nodes,
                current_edges,
                arch.key_technology_choices,
                functional_modules,
                integrations,
                constraints
            )
            
            # Validate enhanced specification
            validation_issues = validate_diagram_spec(enhanced_spec['nodes'], enhanced_spec['edges'])
            if validation_issues:
                logger.warning(f"Architecture validation issues: {validation_issues}")
                # Use original if enhancement is invalid
                enhanced_spec = {'nodes': current_nodes, 'edges': current_edges}
            
            # Update architecture diagram spec
            state.proposal.solution_architecture.diagram_spec = DiagramSpec(
                nodes=enhanced_spec['nodes'],
                edges=enhanced_spec['edges']
            )
            
            # Generate deployment architecture if not present
            if not state.proposal.deployment_view.diagram_spec.nodes:
                deployment_spec = self._generate_deployment_architecture(
                    state.proposal.deployment_view.environments,
                    enhanced_spec['nodes']
                )
                state.proposal.deployment_view.diagram_spec = DiagramSpec(
                    nodes=deployment_spec['nodes'],
                    edges=deployment_spec['edges']
                )
            
            # Generate actual diagram files
            self._generate_diagram_files(state)
            
            state.current_step = "architecture_enhanced"
            logger.info("Architecture enhancement completed successfully")
            return state
            
        except Exception as e:
            error_msg = f"Error enhancing architecture: {str(e)}"
            logger.error(error_msg)
            state.processing_errors.append(error_msg)
            return state
    
    def _enhance_with_llm(self, summary: str, nodes: List[str], edges: List[List[str]],
                         tech_choices: List[str], functional_modules: List[str],
                         integrations: List[str], constraints: List[str]) -> Dict[str, Any]:
        """Use LLM to enhance architecture specification"""
        
        try:
            response = self.enhancement_prompt | self.llm
            
            result = response.invoke({
                "architecture_summary": summary or "Modern web application architecture",
                "current_nodes": nodes,
                "current_edges": edges,
                "technology_choices": tech_choices,
                "functional_modules": functional_modules,
                "integrations": integrations,
                "constraints": constraints
            })
            
            # Parse JSON response
            import json
            enhanced_spec = json.loads(result.content)
            
            # Validate structure
            if 'nodes' not in enhanced_spec or 'edges' not in enhanced_spec:
                raise ValueError("Invalid response format")
            
            return enhanced_spec
            
        except Exception as e:
            logger.error(f"Error in LLM architecture enhancement: {e}")
            # Return improved default architecture
            return self._create_default_enhanced_architecture(nodes, edges, functional_modules, integrations)
    
    def _create_default_enhanced_architecture(self, current_nodes: List[str], current_edges: List[List[str]],
                                            functional_modules: List[str], integrations: List[str]) -> Dict[str, Any]:
        """Create a default enhanced architecture when LLM enhancement fails"""
        
        # Start with current nodes or create basic structure
        nodes = current_nodes.copy() if current_nodes else [
            "Web Frontend",
            "API Gateway", 
            "Application Server",
            "Database"
        ]
        
        # Add missing essential components
        essential_components = [
            "Load Balancer",
            "Authentication Service",
            "Logging Service",
            "Monitoring Service"
        ]
        
        for component in essential_components:
            if component not in nodes:
                nodes.append(component)
        
        # Add integration components
        if integrations:
            if "Integration Layer" not in nodes:
                nodes.append("Integration Layer")
            
            for integration in integrations[:3]:  # Limit to 3
                integration_node = f"External {integration}"
                if integration_node not in nodes:
                    nodes.append(integration_node)
        
        # Add functional modules as services
        for module in functional_modules[:3]:  # Limit to 3
            service_node = f"{module} Service"
            if service_node not in nodes:
                nodes.append(service_node)
        
        # Create logical edges
        edges = []
        
        # Basic flow
        if "Load Balancer" in nodes and "Web Frontend" in nodes:
            edges.append(["Load Balancer", "Web Frontend"])
        if "Web Frontend" in nodes and "API Gateway" in nodes:
            edges.append(["Web Frontend", "API Gateway"])
        if "API Gateway" in nodes and "Application Server" in nodes:
            edges.append(["API Gateway", "Application Server"])
        if "Application Server" in nodes and "Database" in nodes:
            edges.append(["Application Server", "Database"])
        
        # Authentication flow
        if "Authentication Service" in nodes and "API Gateway" in nodes:
            edges.append(["API Gateway", "Authentication Service"])
        
        # Integration flow
        if "Integration Layer" in nodes and "Application Server" in nodes:
            edges.append(["Application Server", "Integration Layer"])
        
        for integration in integrations[:3]:
            integration_node = f"External {integration}"
            if integration_node in nodes and "Integration Layer" in nodes:
                edges.append(["Integration Layer", integration_node])
        
        # Service connections
        for module in functional_modules[:3]:
            service_node = f"{module} Service"
            if service_node in nodes and "Application Server" in nodes:
                edges.append(["Application Server", service_node])
        
        # Monitoring connections
        if "Monitoring Service" in nodes:
            for node in ["Application Server", "Database", "API Gateway"]:
                if node in nodes:
                    edges.append([node, "Monitoring Service"])
        
        return {"nodes": nodes, "edges": edges}
    
    def _generate_deployment_architecture(self, environments: List[str], 
                                        app_components: List[str]) -> Dict[str, Any]:
        """Generate deployment architecture specification"""
        
        if not environments:
            environments = ["Development", "Testing", "Production"]
        
        # Create deployment nodes
        nodes = []
        edges = []
        
        # Add environment-specific infrastructure
        for env in environments:
            # Add environment-specific components
            env_components = [
                f"{env} Load Balancer",
                f"{env} App Cluster",
                f"{env} Database",
                f"{env} Cache"
            ]
            nodes.extend(env_components)
            
            # Connect components within environment
            edges.append([f"{env} Load Balancer", f"{env} App Cluster"])
            edges.append([f"{env} App Cluster", f"{env} Database"])
            edges.append([f"{env} App Cluster", f"{env} Cache"])
        
        # Add shared components
        shared_components = [
            "CI/CD Pipeline",
            "Container Registry",
            "Monitoring Dashboard",
            "Log Aggregation"
        ]
        nodes.extend(shared_components)
        
        # Connect CI/CD to environments
        for env in environments:
            edges.append(["CI/CD Pipeline", f"{env} App Cluster"])
        
        # Connect monitoring to all environments
        for env in environments:
            edges.append([f"{env} App Cluster", "Monitoring Dashboard"])
            edges.append([f"{env} App Cluster", "Log Aggregation"])
        
        return {"nodes": nodes, "edges": edges}
    
    def _generate_diagram_files(self, state: WorkflowState) -> None:
        """Generate actual diagram files from specifications"""
        
        try:
            # Generate solution architecture diagram
            arch_spec = state.proposal.solution_architecture.diagram_spec
            if arch_spec.nodes:
                arch_diagram_path = self.diagram_generator.generate_architecture_diagram(
                    arch_spec.nodes,
                    arch_spec.edges,
                    "Solution Architecture"
                )
                
                if arch_diagram_path:
                    logger.info(f"Generated architecture diagram: {arch_diagram_path}")
                    # Store path in state for later use
                    if not hasattr(state, 'generated_files'):
                        state.generated_files = {}
                    state.generated_files['architecture_diagram'] = arch_diagram_path
            
            # Generate deployment diagram
            deploy_spec = state.proposal.deployment_view.diagram_spec
            if deploy_spec.nodes:
                deploy_diagram_path = self.diagram_generator.generate_deployment_diagram(
                    state.proposal.deployment_view.environments,
                    [node for node in deploy_spec.nodes if 'App Cluster' in node],
                    "Deployment Architecture"
                )
                
                if deploy_diagram_path:
                    logger.info(f"Generated deployment diagram: {deploy_diagram_path}")
                    if not hasattr(state, 'generated_files'):
                        state.generated_files = {}
                    state.generated_files['deployment_diagram'] = deploy_diagram_path
                    
        except Exception as e:
            logger.error(f"Error generating diagram files: {e}")
    
    def validate_architecture(self, architecture: SolutionArchitecture) -> List[str]:
        """
        Validate the architecture specification.
        
        Args:
            architecture: Solution architecture to validate
            
        Returns:
            List of validation issues
        """
        issues = []
        
        if not architecture.architecture_summary:
            issues.append("Missing architecture summary")
        
        if not architecture.diagram_spec.nodes:
            issues.append("No architecture components defined")
        
        # Validate diagram specification
        diagram_issues = validate_diagram_spec(
            architecture.diagram_spec.nodes,
            architecture.diagram_spec.edges
        )
        issues.extend(diagram_issues)
        
        # Check for essential components
        essential_components = ["Database", "API", "Frontend"]
        has_essential = any(
            any(essential.lower() in node.lower() for essential in essential_components)
            for node in architecture.diagram_spec.nodes
        )
        
        if not has_essential:
            issues.append("Missing essential architecture components (Database, API, Frontend)")
        
        return issues


def create_architecture_generator_node():
    """Create a LangGraph node for architecture generation"""
    agent = ArchitectureGeneratorAgent()
    
    def architecture_node(state: WorkflowState) -> WorkflowState:
        """LangGraph node function for architecture generation"""
        return agent.enhance_architecture(state)
    
    return architecture_node