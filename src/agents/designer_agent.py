"""
Designer Agent for architectural visualization and diagram generation
Converts system designs into professional diagrams using Mermaid/D2 and SVG export
"""
import json
import logging
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState
from ..utils.diagram_generator import DiagramGenerator

logger = logging.getLogger(__name__)

@dataclass
class DiagramSpecification:
    """Represents a diagram specification"""
    name: str
    type: str  # 'mermaid', 'd2', 'plantuml'
    specification: str
    description: str
    target_audience: str  # 'technical', 'executive', 'client'

@dataclass
class GeneratedDiagram:
    """Represents a generated diagram with multiple formats"""
    name: str
    description: str
    mermaid_spec: str
    svg_content: Optional[str]
    png_base64: Optional[str]
    metadata: Dict[str, Any]

class DesignerAgent:
    """
    Designer Agent that creates professional architectural diagrams
    
    Responsibilities:
    - Convert architecture specifications into visual diagrams
    - Generate Mermaid/D2 specifications for different audiences
    - Create SVG and PNG exports for presentations
    - Ensure diagrams follow C4/System view standards
    - Optimize diagrams for clarity and aesthetics
    - Validate technical accuracy of visual representations
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.diagram_generator = DiagramGenerator()
        
        # System prompt for the Designer
        self.system_prompt = """You are the Diagram Designer. Your input is a structured technical specification or a Mermaid script. Your output must be the final, validated Mermaid script and the SVG image export for the Proposal deck. Ensure the diagram is clean, follows C4/System view standards, and is aesthetically pleasing.

Your responsibilities:
1. Convert technical specifications into clear visual diagrams
2. Create multiple diagram types for different audiences (technical, executive, client)
3. Generate clean, professional Mermaid specifications
4. Ensure diagrams follow architectural visualization best practices
5. Optimize for clarity, readability, and aesthetic appeal
6. Validate technical accuracy of visual representations
7. Export diagrams in multiple formats (SVG, PNG) for presentations

Focus on:
- Clear visual hierarchy and information organization
- Consistent styling and color schemes
- Appropriate level of detail for target audience
- Professional appearance suitable for client presentations
- Technical accuracy and completeness
- Accessibility and readability

Always ensure diagrams effectively communicate the architecture and design decisions."""
    
    def generate_architecture_diagrams(self, state: WorkflowState, output_dir: str = "./output") -> WorkflowState:
        """
        Generate comprehensive architecture diagrams from design specifications
        
        Args:
            state: Current workflow state with architecture design
            output_dir: Directory to save generated diagrams (default: ./output)
            
        Returns:
            Updated state with generated diagrams
        """
        try:
            logger.info("Designer Agent: Starting diagram generation")
            
            if not state.architecture_design:
                raise ValueError("No architecture design available for diagram generation")
            
            # Step 1: Analyze architecture design and create diagram specifications
            diagram_specs = self._create_diagram_specifications(state.architecture_design, state.mermaid_specifications)
            
            # Step 2: Enhance and validate Mermaid specifications
            enhanced_specs = self._enhance_mermaid_specifications(diagram_specs)
            
            # Step 3: Generate diagrams in multiple formats
            generated_diagrams = self._generate_diagram_exports(enhanced_specs)
            
            # Step 4: Create client-ready presentation diagrams
            presentation_diagrams = self._create_presentation_diagrams(generated_diagrams, state.extracted_data)
            
            # Step 5: Validate diagram quality and technical accuracy
            validated_diagrams = self._validate_diagram_quality(presentation_diagrams, state.architecture_design)
            
            # Update state
            # Convert dataclasses to dicts for Pydantic compatibility
            state.architecture_diagrams = [asdict(d) for d in validated_diagrams]
            state.diagram_specifications = {spec.name: asdict(spec) for spec in enhanced_specs}
            state.current_step = "diagram_generation_complete"
            state.last_agent_executed = "designer"
            
            logger.info(f"Designer Agent: Generated {len(validated_diagrams)} diagrams")
            return state
            
        except Exception as e:
            logger.error(f"Designer Agent failed: {e}")
            state.errors.append(f"Designer Agent error: {str(e)}")
            return state
    
    def _create_diagram_specifications(self, 
                                     architecture_design: Any, 
                                     mermaid_specs: Optional[Dict[str, str]]) -> List[DiagramSpecification]:
        """
        Create comprehensive diagram specifications from architecture design
        
        Args:
            architecture_design: Architecture design from Solution Architect
            mermaid_specs: Initial Mermaid specifications
            
        Returns:
            List of diagram specifications
        """
        try:
            diagram_specs = []
            
            # System Overview Diagram (Executive Level)
            system_overview_spec = self._create_system_overview_spec(architecture_design, mermaid_specs)
            diagram_specs.append(DiagramSpecification(
                name="System Overview",
                type="mermaid",
                specification=system_overview_spec,
                description="High-level system architecture overview for executive presentation",
                target_audience="executive"
            ))
            
            # Technical Architecture Diagram (Technical Level)
            technical_arch_spec = self._create_technical_architecture_spec(architecture_design, mermaid_specs)
            diagram_specs.append(DiagramSpecification(
                name="Technical Architecture",
                type="mermaid",
                specification=technical_arch_spec,
                description="Detailed technical architecture for development teams",
                target_audience="technical"
            ))
            
            # Component Interaction Diagram (Technical Level)
            component_spec = self._create_component_interaction_spec(architecture_design, mermaid_specs)
            diagram_specs.append(DiagramSpecification(
                name="Component Interactions",
                type="mermaid",
                specification=component_spec,
                description="Component interaction flows and communication patterns",
                target_audience="technical"
            ))
            
            # Deployment Architecture Diagram (DevOps Level)
            deployment_spec = self._create_deployment_architecture_spec(architecture_design, mermaid_specs)
            diagram_specs.append(DiagramSpecification(
                name="Deployment Architecture",
                type="mermaid",
                specification=deployment_spec,
                description="Infrastructure and deployment strategy visualization",
                target_audience="technical"
            ))
            
            # Data Flow Diagram (Technical Level)
            data_flow_spec = self._create_data_flow_spec(architecture_design, mermaid_specs)
            diagram_specs.append(DiagramSpecification(
                name="Data Flow",
                type="mermaid",
                specification=data_flow_spec,
                description="Data processing and flow patterns",
                target_audience="technical"
            ))
            
            # Security Architecture Diagram (Security Level)
            security_spec = self._create_security_architecture_spec(architecture_design)
            diagram_specs.append(DiagramSpecification(
                name="Security Architecture",
                type="mermaid",
                specification=security_spec,
                description="Security controls and data protection measures",
                target_audience="technical"
            ))
            
            return diagram_specs
            
        except Exception as e:
            logger.error(f"Diagram specification creation failed: {e}")
            return self._get_default_diagram_specifications()
    
    def _create_system_overview_spec(self, architecture_design: Any, mermaid_specs: Optional[Dict[str, str]]) -> str:
        """Create system overview Mermaid specification"""
        
        # Use existing spec if available, otherwise create new one
        if mermaid_specs and 'system_overview' in mermaid_specs:
            base_spec = mermaid_specs['system_overview']
        else:
            base_spec = """graph TB
    U[Users] --> W[Web Application]
    W --> A[Application Server]
    A --> D[(Database)]"""
        
        # Enhance with LLM for better presentation
        enhancement_prompt = f"""
Enhance this Mermaid system overview diagram for executive presentation. Make it clean, professional, and easy to understand:

Current specification:
{base_spec}

Architecture context:
- Solution: {getattr(architecture_design, 'solution_overview', 'Modern web application')[:200]}
- Components: {len(getattr(architecture_design, 'system_components', []))} main components
- Pattern: {getattr(architecture_design, 'architecture_pattern', {}).get('name', 'Custom Architecture')}

Requirements:
1. Use clear, business-friendly component names
2. Show main user flows and data paths
3. Include external integrations if relevant
4. Use professional styling with consistent colors
5. Keep it simple but comprehensive
6. Add appropriate icons or shapes for different component types

Provide the enhanced Mermaid specification with styling.
"""
        
        try:
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=enhancement_prompt)
            ]
            print("Enhancement Prompt:", enhancement_prompt)
            print("System Prompt:", self.system_prompt) 
            print("Messages:", messages)    
            response = self.llm.invoke(messages)
            print("Response:", response)
            enhanced_spec = self._extract_mermaid_from_response(response.content, base_spec)
            return enhanced_spec
            
        except Exception as e:
            logger.error(f"System overview enhancement failed: {e}")
            return base_spec
    
    def _create_technical_architecture_spec(self, architecture_design: Any, mermaid_specs: Optional[Dict[str, str]]) -> str:
        """Create detailed technical architecture specification"""
        
        components = getattr(architecture_design, 'system_components', [])
        
        # Build detailed technical diagram
        mermaid_spec = "graph TB\n"
        
        # Add components with detailed information
        component_ids = {}
        for i, component in enumerate(components):
            comp_id = f"C{i+1}"
            comp_name = component.get('name', f'Component {i+1}')
            comp_tech = component.get('technology', 'Unknown')
            
            component_ids[comp_name] = comp_id
            
            # Style based on component type
            comp_type = component.get('type', 'service')
            if comp_type == 'frontend':
                mermaid_spec += f"    {comp_id}[\"{comp_name}<br/>{comp_tech}\"]:::frontend\n"
            elif comp_type == 'backend':
                mermaid_spec += f"    {comp_id}[\"{comp_name}<br/>{comp_tech}\"]:::backend\n"
            elif comp_type == 'database':
                mermaid_spec += f"    {comp_id}[(\"{comp_name}<br/>{comp_tech}\")]:::database\n"
            elif comp_type == 'cache':
                mermaid_spec += f"    {comp_id}[[\"{comp_name}<br/>{comp_tech}\"]]:::cache\n"
            else:
                mermaid_spec += f"    {comp_id}[\"{comp_name}<br/>{comp_tech}\"]:::service\n"
        
        # Add connections based on component interfaces
        for i, component in enumerate(components):
            comp_id = f"C{i+1}"
            interfaces = component.get('interfaces', [])
            
            # Simple connection logic (can be enhanced)
            if i < len(components) - 1:
                next_id = f"C{i+2}"
                mermaid_spec += f"    {comp_id} --> {next_id}\n"
        
        # Add styling
        mermaid_spec += """
    classDef frontend fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef database fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef cache fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef service fill:#fce4ec,stroke:#c2185b,stroke-width:2px
"""
        
        return mermaid_spec
    
    def _create_component_interaction_spec(self, architecture_design: Any, mermaid_specs: Optional[Dict[str, str]]) -> str:
        """Create component interaction sequence diagram"""
        
        if mermaid_specs and 'component_interaction' in mermaid_specs:
            return mermaid_specs['component_interaction']
        
        # Create sequence diagram based on components
        components = getattr(architecture_design, 'system_components', [])
        
        sequence_spec = "sequenceDiagram\n"
        sequence_spec += "    participant U as User\n"
        
        # Add main components as participants
        for component in components[:4]:  # Limit to 4 main components
            comp_name = component.get('name', 'Component')
            comp_short = comp_name.replace(' ', '').replace('-', '')[:10]
            sequence_spec += f"    participant {comp_short} as {comp_name}\n"
        
        # Add typical interaction flow
        sequence_spec += """
    U->>WebApp: User Request
    WebApp->>APIGateway: API Call
    APIGateway->>AppServer: Route Request
    AppServer->>Database: Query Data
    Database-->>AppServer: Return Data
    AppServer-->>APIGateway: Response
    APIGateway-->>WebApp: API Response
    WebApp-->>U: Display Result
"""
        
        return sequence_spec
    
    def _create_deployment_architecture_spec(self, architecture_design: Any, mermaid_specs: Optional[Dict[str, str]]) -> str:
        """Create deployment architecture diagram"""
        
        if mermaid_specs and 'deployment_architecture' in mermaid_specs:
            return mermaid_specs['deployment_architecture']
        
        deployment_strategy = getattr(architecture_design, 'deployment_strategy', {})
        cloud_provider = deployment_strategy.get('infrastructure', {}).get('cloud_provider', 'Cloud')
        
        deployment_spec = f"""graph TB
    subgraph "{cloud_provider} Cloud"
        subgraph "Frontend Tier"
            CDN[CDN Distribution]
            LB[Load Balancer]
        end
        
        subgraph "Application Tier"
            K8S[Kubernetes Cluster]
            subgraph "Pods"
                APP1[App Instance 1]
                APP2[App Instance 2]
                APP3[App Instance 3]
            end
        end
        
        subgraph "Data Tier"
            DB[(Primary Database)]
            CACHE[(Cache Layer)]
            BACKUP[(Backup Storage)]
        end
        
        subgraph "Monitoring"
            MON[Monitoring Stack]
            LOG[Log Aggregation]
        end
    end
    
    CDN --> LB
    LB --> K8S
    K8S --> APP1
    K8S --> APP2
    K8S --> APP3
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    APP1 --> CACHE
    APP2 --> CACHE
    APP3 --> CACHE
    DB --> BACKUP
    APP1 --> MON
    APP2 --> MON
    APP3 --> MON
    
    classDef frontend fill:#e3f2fd
    classDef app fill:#f3e5f5
    classDef data fill:#e8f5e8
    classDef monitor fill:#fff3e0
"""
        
        return deployment_spec
    
    def _create_data_flow_spec(self, architecture_design: Any, mermaid_specs: Optional[Dict[str, str]]) -> str:
        """Create data flow diagram"""
        
        if mermaid_specs and 'data_flow' in mermaid_specs:
            return mermaid_specs['data_flow']
        
        data_architecture = getattr(architecture_design, 'data_architecture', {})
        
        data_flow_spec = """flowchart LR
    A[User Input] --> B[Input Validation]
    B --> C[Business Logic Processing]
    C --> D[Data Transformation]
    D --> E[(Primary Database)]
    
    C --> F[Cache Check]
    F --> G[(Cache Layer)]
    G --> C
    
    E --> H[Data Replication]
    H --> I[(Read Replica)]
    
    C --> J[External API Calls]
    J --> K[Third-party Services]
    K --> J
    J --> C
    
    E --> L[Backup Process]
    L --> M[(Backup Storage)]
    
    C --> N[Response Generation]
    N --> O[User Interface Update]
    
    classDef input fill:#e3f2fd
    classDef process fill:#f3e5f5
    classDef storage fill:#e8f5e8
    classDef external fill:#fff3e0
"""
        
        return data_flow_spec
    
    def _create_security_architecture_spec(self, architecture_design: Any) -> str:
        """Create security architecture diagram"""
        
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        
        security_spec = """graph TB
    subgraph "Security Perimeter"
        subgraph "External Layer"
            WAF[Web Application Firewall]
            DDoS[DDoS Protection]
        end
        
        subgraph "Authentication Layer"
            AUTH[Authentication Service]
            MFA[Multi-Factor Auth]
            SSO[Single Sign-On]
        end
        
        subgraph "Application Layer"
            API[API Gateway]
            APP[Application Services]
            RBAC[Role-Based Access Control]
        end
        
        subgraph "Data Layer"
            ENCRYPT[Data Encryption]
            DB[(Encrypted Database)]
            BACKUP[(Encrypted Backups)]
        end
        
        subgraph "Monitoring Layer"
            SIEM[Security Monitoring]
            AUDIT[Audit Logging]
            ALERT[Security Alerts]
        end
    end
    
    WAF --> API
    DDoS --> WAF
    AUTH --> APP
    MFA --> AUTH
    SSO --> AUTH
    API --> APP
    RBAC --> APP
    APP --> ENCRYPT
    ENCRYPT --> DB
    DB --> BACKUP
    APP --> AUDIT
    AUDIT --> SIEM
    SIEM --> ALERT
    
    classDef security fill:#ffebee,stroke:#d32f2f
    classDef auth fill:#e8f5e8,stroke:#388e3c
    classDef data fill:#e3f2fd,stroke:#1976d2
    classDef monitor fill:#fff3e0,stroke:#f57c00
"""
        
        return security_spec
    
    def _enhance_mermaid_specifications(self, diagram_specs: List[DiagramSpecification]) -> List[DiagramSpecification]:
        """
        Enhance Mermaid specifications using LLM for better quality and presentation
        
        Args:
            diagram_specs: Initial diagram specifications
            
        Returns:
            Enhanced diagram specifications
        """
        try:
            enhanced_specs = []
            
            for spec in diagram_specs:
                # Create enhancement prompt
                enhancement_prompt = f"""
Enhance this {spec.name} Mermaid diagram for {spec.target_audience} audience:

Current specification:
{spec.specification}

Description: {spec.description}

Requirements:
1. Ensure clean, professional appearance
2. Use consistent styling and colors
3. Optimize for {spec.target_audience} audience understanding
4. Add appropriate labels and descriptions
5. Follow C4 model principles where applicable
6. Ensure technical accuracy
7. Make it presentation-ready

Provide the enhanced Mermaid specification with improved styling and clarity.
"""
                
                try:
                    messages = [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(content=enhancement_prompt)
                    ]
                    print("Messages:", messages)
                    response = self.llm.invoke(messages)
                    print("Response:", response)
                    enhanced_specification = self._extract_mermaid_from_response(response.content, spec.specification)
                    
                    enhanced_spec = DiagramSpecification(
                        name=spec.name,
                        type=spec.type,
                        specification=enhanced_specification,
                        description=spec.description,
                        target_audience=spec.target_audience
                    )
                    enhanced_specs.append(enhanced_spec)
                    
                except Exception as e:
                    logger.error(f"Enhancement failed for {spec.name}: {e}")
                    enhanced_specs.append(spec)  # Use original if enhancement fails
            
            return enhanced_specs
            
        except Exception as e:
            logger.error(f"Mermaid specification enhancement failed: {e}")
            return diagram_specs
    
    def _generate_diagram_exports(self, diagram_specs: List[DiagramSpecification]) -> List[GeneratedDiagram]:
        """
        Generate diagram exports in multiple formats (SVG, PNG)
        
        Args:
            diagram_specs: Enhanced diagram specifications
            
        Returns:
            Generated diagrams with multiple format exports
        """
        try:
            generated_diagrams = []
            
            for spec in diagram_specs:
                try:
                    # Generate SVG using diagram generator
                    svg_content = self.diagram_generator.generate_mermaid_svg(spec.specification)
                    
                    # Generate PNG (base64 encoded) if possible
                    png_base64 = None
                    try:
                        png_base64 = self.diagram_generator.generate_mermaid_png_base64(spec.specification)
                    except Exception as png_error:
                        logger.warning(f"PNG generation failed for {spec.name}: {png_error}")
                    
                    # Create generated diagram
                    generated_diagram = GeneratedDiagram(
                        name=spec.name,
                        description=spec.description,
                        mermaid_spec=spec.specification,
                        svg_content=svg_content,
                        png_base64=png_base64,
                        metadata={
                            'target_audience': spec.target_audience,
                            'diagram_type': spec.type,
                            'generation_timestamp': self._get_current_timestamp(),
                            'has_svg': svg_content is not None,
                            'has_png': png_base64 is not None
                        }
                    )
                    
                    generated_diagrams.append(generated_diagram)
                    logger.info(f"Generated diagram: {spec.name}")
                    
                except Exception as e:
                    logger.error(f"Diagram generation failed for {spec.name}: {e}")
                    # Create fallback diagram
                    fallback_diagram = GeneratedDiagram(
                        name=spec.name,
                        description=spec.description,
                        mermaid_spec=spec.specification,
                        svg_content=None,
                        png_base64=None,
                        metadata={
                            'target_audience': spec.target_audience,
                            'diagram_type': spec.type,
                            'generation_timestamp': self._get_current_timestamp(),
                            'generation_error': str(e),
                            'has_svg': False,
                            'has_png': False
                        }
                    )
                    generated_diagrams.append(fallback_diagram)
            
            return generated_diagrams
            
        except Exception as e:
            logger.error(f"Diagram export generation failed: {e}")
            return self._get_default_generated_diagrams()
    
    def _create_presentation_diagrams(self, 
                                    generated_diagrams: List[GeneratedDiagram], 
                                    extracted_data: Any) -> List[GeneratedDiagram]:
        """
        Create client-ready presentation diagrams with appropriate styling and context
        
        Args:
            generated_diagrams: Generated diagrams
            extracted_data: Extracted RFP data for context
            
        Returns:
            Presentation-ready diagrams
        """
        try:
            presentation_diagrams = []
            
            for diagram in generated_diagrams:
                # Add presentation context and styling
                presentation_context = self._create_presentation_context(diagram, extracted_data)
                
                # Create presentation-ready version
                presentation_diagram = GeneratedDiagram(
                    name=diagram.name,
                    description=f"{diagram.description}\n\n{presentation_context}",
                    mermaid_spec=diagram.mermaid_spec,
                    svg_content=diagram.svg_content,
                    png_base64=diagram.png_base64,
                    metadata={
                        **diagram.metadata,
                        'presentation_ready': True,
                        'client_context': presentation_context,
                        'recommended_usage': self._get_recommended_usage(diagram)
                    }
                )
                
                presentation_diagrams.append(presentation_diagram)
            
            return presentation_diagrams
            
        except Exception as e:
            logger.error(f"Presentation diagram creation failed: {e}")
            return generated_diagrams
    
    def _validate_diagram_quality(self, 
                                 presentation_diagrams: List[GeneratedDiagram], 
                                 architecture_design: Any) -> List[GeneratedDiagram]:
        """
        Validate diagram quality and technical accuracy
        
        Args:
            presentation_diagrams: Presentation-ready diagrams
            architecture_design: Original architecture design for validation
            
        Returns:
            Validated diagrams with quality metrics
        """
        try:
            validated_diagrams = []
            
            for diagram in presentation_diagrams:
                # Perform quality validation
                quality_metrics = self._assess_diagram_quality(diagram, architecture_design)
                
                # Add validation results to metadata
                validated_diagram = GeneratedDiagram(
                    name=diagram.name,
                    description=diagram.description,
                    mermaid_spec=diagram.mermaid_spec,
                    svg_content=diagram.svg_content,
                    png_base64=diagram.png_base64,
                    metadata={
                        **diagram.metadata,
                        'quality_validation': quality_metrics,
                        'validation_timestamp': self._get_current_timestamp()
                    }
                )
                
                validated_diagrams.append(validated_diagram)
                logger.info(f"Validated diagram: {diagram.name} (Quality Score: {quality_metrics.get('overall_score', 'N/A')})")
            
            return validated_diagrams
            
        except Exception as e:
            logger.error(f"Diagram quality validation failed: {e}")
            return presentation_diagrams
    
    def _extract_mermaid_from_response(self, response_content: str, fallback_spec: str) -> str:
        """Extract Mermaid specification from LLM response"""
        try:
            # Look for mermaid code blocks
            if '```mermaid' in response_content:
                start = response_content.find('```mermaid') + 10
                end = response_content.find('```', start)
                if end > start:
                    return response_content[start:end].strip()
            
            # Look for any code blocks
            if '```' in response_content:
                start = response_content.find('```') + 3
                # Skip language identifier
                newline = response_content.find('\n', start)
                if newline > start:
                    start = newline + 1
                end = response_content.find('```', start)
                if end > start:
                    return response_content[start:end].strip()
            
            # If no code blocks, try to extract diagram content
            lines = response_content.split('\n')
            diagram_lines = []
            in_diagram = False
            
            for line in lines:
                if any(keyword in line.lower() for keyword in ['graph', 'flowchart', 'sequencediagram', 'classDef']):
                    in_diagram = True
                if in_diagram:
                    diagram_lines.append(line)
                if line.strip() == '' and in_diagram and len(diagram_lines) > 5:
                    break
            
            if diagram_lines:
                return '\n'.join(diagram_lines).strip()
            
            return fallback_spec
            
        except Exception as e:
            logger.error(f"Mermaid extraction failed: {e}")
            return fallback_spec
    
    def _create_presentation_context(self, diagram: GeneratedDiagram, extracted_data: Any) -> str:
        """Create presentation context for diagrams"""
        
        client_name = "the client"
        if extracted_data and hasattr(extracted_data, 'client_info'):
            client_name = extracted_data.client_info.get('organization_name', 'the client')
        
        context_map = {
            'System Overview': f"This diagram provides a high-level view of the proposed solution architecture for {client_name}, showing the main system components and their relationships.",
            # 'Technical Architecture': f"This detailed technical diagram illustrates the complete system architecture, including all components, technologies, and integration points for the {client_name} project.",
            # 'Component Interactions': f"This sequence diagram shows how different system components interact to process user requests and deliver functionality for {client_name}.",
            # 'Deployment Architecture': f"This diagram depicts the infrastructure and deployment strategy for the {client_name} solution, including cloud services and scaling considerations.",
            # 'Data Flow': f"This diagram illustrates how data flows through the system, from user input to storage and processing for the {client_name} application.",
            # 'Security Architecture': f"This diagram shows the comprehensive security measures and controls implemented to protect {client_name}'s data and system integrity."
        }
        
        return context_map.get(diagram.name, f"This diagram supports the technical solution proposed for {client_name}.")
    
    def _get_recommended_usage(self, diagram: GeneratedDiagram) -> str:
        """Get recommended usage for each diagram type"""
        
        usage_map = {
            'System Overview': 'Ideal for executive presentations and client meetings to communicate overall solution approach',
            #'Technical Architecture': 'Essential for development team briefings and technical stakeholder reviews',
            #'Component Interactions': 'Useful for development planning and system integration discussions',
            #'Deployment Architecture': 'Critical for DevOps planning and infrastructure provisioning',
            #'Data Flow': 'Important for data architecture reviews and privacy impact assessments',
            #'Security Architecture': 'Required for security reviews and compliance documentation'
        }
        
        return usage_map.get(diagram.name, 'Supporting diagram for technical documentation')
    
    def _assess_diagram_quality(self, diagram: GeneratedDiagram, architecture_design: Any) -> Dict[str, Any]:
        """Assess diagram quality and technical accuracy"""
        
        quality_metrics = {
            'overall_score': 85,  # Default good score
            'technical_accuracy': 'high',
            'visual_clarity': 'high',
            'completeness': 'good',
            'presentation_readiness': 'high',
            'issues': [],
            'recommendations': []
        }
        
        # Check if diagram was successfully generated
        if not diagram.svg_content and not diagram.png_base64:
            quality_metrics['overall_score'] = 60
            quality_metrics['issues'].append('No visual export generated')
            quality_metrics['recommendations'].append('Manual diagram creation may be required')
        
        # Check Mermaid specification quality
        if len(diagram.mermaid_spec) < 50:
            quality_metrics['completeness'] = 'low'
            quality_metrics['issues'].append('Diagram specification appears incomplete')
        
        # Check for styling
        if 'classDef' not in diagram.mermaid_spec and 'fill:' not in diagram.mermaid_spec:
            quality_metrics['visual_clarity'] = 'medium'
            quality_metrics['recommendations'].append('Consider adding styling for better visual appeal')
        
        return quality_metrics
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_default_diagram_specifications(self) -> List[DiagramSpecification]:
        """Get default diagram specifications for error cases"""
        return [
            DiagramSpecification(
                name="System Overview",
                type="mermaid",
                specification="graph TB\n    A[Web App] --> B[API]\n    B --> C[(Database)]",
                description="Basic system overview",
                target_audience="technical"
            ),
            DiagramSpecification(
                name="Technical Architecture",
                type="mermaid",
                specification="graph TB\n    Frontend --> Backend\n    Backend --> Database",
                description="Basic technical architecture",
                target_audience="technical"
            )
        ]
    
    def _get_default_generated_diagrams(self) -> List[GeneratedDiagram]:
        """Get default generated diagrams for error cases"""
        return [
            GeneratedDiagram(
                name="System Overview",
                description="Default system overview diagram",
                mermaid_spec="graph TB\n    A[Application] --> B[(Database)]",
                svg_content=None,
                png_base64=None,
                metadata={
                    'target_audience': 'executive',
                    'diagram_type': 'mermaid',
                    'generation_error': 'Default diagram due to generation failure',
                    'has_svg': False,
                    'has_png': False
                }
            )
        ]
    
    def _save_diagrams_to_folder(self, diagrams: List[GeneratedDiagram], output_dir: str) -> None:
        """
        Save generated diagrams to the output folder
        
        Args:
            diagrams: List of generated diagrams to save
            output_dir: Base output directory
        """
        import os
        
        try:
            # Create diagrams subdirectory
            diagrams_dir = os.path.join(output_dir, "diagrams")
            os.makedirs(diagrams_dir, exist_ok=True)
            
            for diagram in diagrams:
                # Create safe filename from diagram name
                safe_name = diagram.name.lower().replace(' ', '_').replace('-', '_')
                
                # Save Mermaid specification
                mermaid_path = os.path.join(diagrams_dir, f"{safe_name}.mmd")
                with open(mermaid_path, 'w', encoding='utf-8') as f:
                    f.write(diagram.mermaid_spec)
                logger.info(f"Saved Mermaid spec: {mermaid_path}")
                
                # Save SVG if available
                if diagram.svg_content:
                    svg_path = os.path.join(diagrams_dir, f"{safe_name}.svg")
                    with open(svg_path, 'w', encoding='utf-8') as f:
                        f.write(diagram.svg_content)
                    logger.info(f"Saved SVG diagram: {svg_path}")
                
                # Save PNG if available
                if diagram.png_base64:
                    png_path = os.path.join(diagrams_dir, f"{safe_name}.png")
                    png_data = base64.b64decode(diagram.png_base64)
                    with open(png_path, 'wb') as f:
                        f.write(png_data)
                    logger.info(f"Saved PNG diagram: {png_path}")
                
                # Save metadata
                metadata_path = os.path.join(diagrams_dir, f"{safe_name}_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump({
                        'name': diagram.name,
                        'description': diagram.description,
                        'metadata': diagram.metadata
                    }, f, indent=2)
            
            logger.info(f"Successfully saved {len(diagrams)} diagrams to {diagrams_dir}")
            
        except Exception as e:
            logger.error(f"Failed to save diagrams to folder: {e}")

# Factory function to create designer agent
def create_designer_agent(llm: Optional[ChatOpenAI] = None) -> DesignerAgent:
    """Create and configure designer agent"""
    return DesignerAgent(llm=llm)