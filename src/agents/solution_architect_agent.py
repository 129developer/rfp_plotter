"""
Software Solution Architect Agent for technical system design
Designs scalable, reliable, and cost-effective technical solutions based on extracted requirements
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState, RFPExtractedData
from ..tools.tech_stack_tools import create_tech_stack_tools

logger = logging.getLogger(__name__)

@dataclass
class ArchitectureDesign:
    """Represents a complete architecture design"""
    solution_overview: str
    architecture_pattern: Dict[str, Any]
    technology_stack: Dict[str, Any]
    system_components: List[Dict[str, Any]]
    integration_points: List[Dict[str, Any]]
    scalability_strategy: Dict[str, Any]
    security_considerations: Dict[str, Any]
    deployment_strategy: Dict[str, Any]
    design_rationale: Dict[str, Any]

class SolutionArchitectAgent:
    """
    Software Solution Architect Agent that designs technical systems
    
    Responsibilities:
    - Analyze extracted requirements and design technical solutions
    - Select appropriate technology stacks and architecture patterns
    - Define system components and integration points
    - Consider scalability, security, and maintainability
    - Generate Mermaid diagrams for visualization
    - Provide detailed technical specifications
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Initialize tech stack tools
        self.tech_tools = create_tech_stack_tools()
        self.tech_stack_db = self.tech_tools['tech_stack_db']
        
        # System prompt for the Solution Architect
        self.system_prompt = """You are the Software Solution Architect. Based on the structured requirements, you must design a scalable, reliable, and cost-effective technical solution. Define the core components, technology stack (using common standards like AWS/GCP/Azure/Kubernetes), and key integration points.

Your responsibilities:
1. Analyze requirements and design appropriate architecture
2. Select optimal technology stack based on requirements and constraints
3. Define system components and their interactions
4. Plan integration points and data flows
5. Consider scalability, performance, and security requirements
6. Design deployment and infrastructure strategy
7. Generate Mermaid diagram specifications for visualization
8. Provide detailed technical rationale for all decisions

Focus on:
- Scalable and maintainable architecture
- Appropriate technology selection
- Clear component definitions
- Integration and data flow design
- Security and performance considerations
- Cost-effective solutions
- Industry best practices

Always justify your technical decisions with clear rationale based on requirements and constraints."""
    
    def design_solution_architecture(self, state: WorkflowState, output_dir: str = "./output") -> WorkflowState:
        """
        Design comprehensive technical solution architecture
        
        Args:
            state: Current workflow state with extracted requirements
            output_dir: Directory to save solution documentation (default: ./output)
            
        Returns:
            Updated state with architecture design
        """
        try:
            logger.info("Solution Architect Agent: Starting architecture design")
            
            if not state.extracted_data:
                raise ValueError("No extracted requirements data available for architecture design")
            
            # Step 1: Analyze requirements for architecture design
            architecture_requirements = self._analyze_architecture_requirements(state.extracted_data)
            
            # Step 2: Recommend technology stack
            tech_stack_recommendation = self._recommend_technology_stack(architecture_requirements)
            
            # Step 3: Design system architecture
            system_architecture = self._design_system_architecture(architecture_requirements, tech_stack_recommendation)
            
            # Step 4: Define integration strategy
            integration_strategy = self._design_integration_strategy(system_architecture, architecture_requirements)
            
            # Step 5: Plan scalability and performance
            scalability_design = self._design_scalability_strategy(system_architecture, architecture_requirements)
            
            # Step 6: Address security considerations
            security_design = self._design_security_architecture(system_architecture, architecture_requirements)
            
            # Step 7: Plan deployment strategy
            deployment_strategy = self._design_deployment_strategy(system_architecture, tech_stack_recommendation)
            
            # Step 8: Generate Mermaid diagram specifications
            mermaid_specs = self._generate_mermaid_specifications(system_architecture)
            
            # Step 9: Create comprehensive architecture design
            architecture_design = ArchitectureDesign(
                solution_overview=self._create_solution_overview(system_architecture, architecture_requirements),
                architecture_pattern=system_architecture['pattern'],
                technology_stack=tech_stack_recommendation,
                system_components=system_architecture['components'],
                integration_points=integration_strategy,
                scalability_strategy=scalability_design,
                security_considerations=security_design,
                deployment_strategy=deployment_strategy,
                design_rationale=self._create_design_rationale(system_architecture, tech_stack_recommendation)
            )
            
            # Step 10: Save solution to Markdown file
            self._save_solution_to_markdown(architecture_design, output_dir)
            
            # Update state (convert dataclass to dict for Pydantic compatibility)
            state.architecture_design = {
                'solution_overview': architecture_design.solution_overview,
                'architecture_pattern': architecture_design.architecture_pattern,
                'technology_stack': architecture_design.technology_stack,
                'system_components': architecture_design.system_components,
                'integration_points': architecture_design.integration_points,
                'scalability_strategy': architecture_design.scalability_strategy,
                'security_considerations': architecture_design.security_considerations,
                'deployment_strategy': architecture_design.deployment_strategy,
                'design_rationale': architecture_design.design_rationale
            }
            state.mermaid_specifications = mermaid_specs
            state.current_step = "architecture_design_complete"
            state.last_agent_executed = "solution_architect"
            
            logger.info("Solution Architect Agent: Architecture design complete")
            return state
            
        except Exception as e:
            logger.error(f"Solution Architect Agent failed: {e}")
            state.errors.append(f"Solution Architect Agent error: {str(e)}")
            return state
    
    def _analyze_architecture_requirements(self, extracted_data: RFPExtractedData) -> Dict[str, Any]:
        """
        Analyze extracted requirements for architecture design
        
        Args:
            extracted_data: Extracted requirements data
            
        Returns:
            Architecture requirements analysis
        """
        try:
            # Create wrapper to access fields with backward compatibility
            # Map new field structure to old accessors
            functional_reqs = extracted_data.functional_modules or []
            
            # Build pseudo properties for compatibility
            client_info = {
                'organization_name': extracted_data.client_organization,
                'division': extracted_data.division_department
            }
            
            technical_specs = {
                'technology_preferences': extracted_data.technology_preferences,
                'constraints': extracted_data.technology_constraints,
                'scalability': extracted_data.scalability_requirements,
                'performance_requirements': extracted_data.performance_expectations,
                'hosting': extracted_data.hosting_constraints,
                'security': extracted_data.security_requirements,
                'interoperability': extracted_data.interoperability_constraints,
                'expected_users': 'Not specified',
                'response_time': 'Not specified',
                'throughput': 'Not specified',
                'availability': '99.9%',
                'compliance_requirements': [],
                'external_systems': extracted_data.integrations,
                'api_requirements': {}
            }
            
            constraints = {
                'budget': extracted_data.budget_ranges[0] if extracted_data.budget_ranges else 'Not specified',
                'timeline': extracted_data.timelines[0] if extracted_data.timelines else 'Not specified',
                'timeline_list': extracted_data.timelines,
                'vendor_restrictions': extracted_data.vendor_restrictions
            }
            
            # Analyze project characteristics
            project_analysis = self._analyze_project_characteristics(extracted_data)
            
            # Determine architecture requirements
            arch_requirements = {
                'project_characteristics': project_analysis,
                'functional_requirements': functional_reqs,
                'technical_requirements': {
                    'technology_preferences': extracted_data.technology_preferences,
                    'constraints': extracted_data.technology_constraints,
                    'scalability': extracted_data.scalability_requirements,
                    'performance_requirements': extracted_data.performance_expectations,
                    'hosting': extracted_data.hosting_constraints,
                    'security': extracted_data.security_requirements,
                    'interoperability': extracted_data.interoperability_constraints,
                    'expected_users': 'Not specified',
                    'response_time': 'Not specified',
                    'throughput': 'Not specified',
                    'availability': '99.9%',
                    'compliance_requirements': [],
                    'external_systems': extracted_data.integrations,
                    'api_requirements': {}
                },
                'constraints': constraints,
                'client_context': client_info,
                'scalability_needs': self._assess_scalability_needs(extracted_data),
                'security_requirements': self._assess_security_requirements(extracted_data),
                'integration_needs': self._assess_integration_needs(extracted_data),
                'performance_requirements': self._assess_performance_requirements(extracted_data)
            }
            
            return arch_requirements
            
        except Exception as e:
            logger.error(f"Architecture requirements analysis failed: {e}")
            return self._get_default_architecture_requirements()
    
    def _analyze_project_characteristics(self, extracted_data: RFPExtractedData) -> Dict[str, Any]:
        """Analyze project characteristics for architecture decisions"""
        
        # Estimate project size and complexity
        functional_count = len(extracted_data.functional_modules or [])
        
        if functional_count <= 5:
            project_size = 'small'
            complexity = 'simple'
        elif functional_count <= 15:
            project_size = 'medium'
            complexity = 'moderate'
        else:
            project_size = 'large'
            complexity = 'complex'
        
        # Estimate team size based on project characteristics
        if project_size == 'small':
            team_size = 'small'
        elif project_size == 'medium':
            team_size = 'medium'
        else:
            team_size = 'large'
        
        # Assess timeline pressure
        timeline_constraints = extracted_data.timelines[0] if extracted_data.timelines else ''
        if 'urgent' in str(timeline_constraints).lower() or 'asap' in str(timeline_constraints).lower():
            timeline_pressure = 'tight'
        elif 'flexible' in str(timeline_constraints).lower():
            timeline_pressure = 'relaxed'
        else:
            timeline_pressure = 'normal'
        
        # Assess budget constraints
        budget_constraints = extracted_data.budget_ranges[0] if extracted_data.budget_ranges else ''
        if 'limited' in str(budget_constraints).lower() or 'tight' in str(budget_constraints).lower():
            budget = 'low'
        elif 'generous' in str(budget_constraints).lower() or 'flexible' in str(budget_constraints).lower():
            budget = 'high'
        else:
            budget = 'medium'
        
        return {
            'project_size': project_size,
            'complexity': complexity,
            'team_size': team_size,
            'timeline_pressure': timeline_pressure,
            'budget': budget,
            'risk_level': 'high' if complexity == 'complex' or timeline_pressure == 'tight' else 'medium'
        }
    
    def _assess_scalability_needs(self, extracted_data: RFPExtractedData) -> Dict[str, Any]:
        """Assess scalability requirements"""
        
        # Construct technical_specs locally since it's not an attribute
        technical_specs = {
            'technology_preferences': extracted_data.technology_preferences,
            'constraints': extracted_data.technology_constraints,
            'scalability': extracted_data.scalability_requirements,
            'performance_requirements': extracted_data.performance_expectations,
            'hosting': extracted_data.hosting_constraints,
            'security': extracted_data.security_requirements,
            'interoperability': extracted_data.interoperability_constraints,
            'expected_users': 'Not specified',
            'response_time': 'Not specified',
            'throughput': 'Not specified',
            'availability': '99.9%',
            'compliance_requirements': [],
            'external_systems': extracted_data.integrations,
            'api_requirements': {}
        }
        # Build requirements text for analysis
        requirements_text = str(extracted_data.functional_modules) + str(extracted_data.integrations)
        
        # Look for scalability indicators
        scalability_indicators = ['scale', 'growth', 'users', 'load', 'performance', 'concurrent']
        scalability_mentions = sum(1 for indicator in scalability_indicators 
                                 if indicator in requirements_text.lower())
        
        if scalability_mentions >= 3:
            scalability_level = 'high'
        elif scalability_mentions >= 1:
            scalability_level = 'medium'
        else:
            scalability_level = 'low'
        
        return {
            'scalability_level': scalability_level,
            'scalability_level': scalability_level,
            'expected_users': 'Not specified',
            'performance_requirements': extracted_data.scalability_requirements,
            'growth_expectations': 'Moderate growth expected'
        }
    
    def _assess_security_requirements(self, extracted_data: RFPExtractedData) -> Dict[str, Any]:
        """Assess security requirements"""
        
        # Construct technical_specs locally
        technical_specs = {
            'compliance_requirements': []
        }
        # Build requirements text for analysis
        requirements_text = str(extracted_data.security_requirements) + str(extracted_data.functional_modules)
        
        # Look for security indicators
        security_indicators = ['security', 'authentication', 'authorization', 'encryption', 'compliance', 'privacy']
        security_mentions = sum(1 for indicator in security_indicators 
                              if indicator in requirements_text.lower())
        
        if security_mentions >= 4:
            security_level = 'high'
        elif security_mentions >= 2:
            security_level = 'medium'
        else:
            security_level = 'standard'
        
        return {
            'security_level': security_level,
            'authentication_required': 'authentication' in requirements_text.lower(),
            'data_encryption_required': 'encryption' in requirements_text.lower(),
            'compliance_requirements': []
        }
    
    def _assess_integration_needs(self, extracted_data: RFPExtractedData) -> Dict[str, Any]:
        """Assess integration requirements"""
        
        # Build requirements text for analysis
        requirements_text = str(extracted_data.integrations) + str(extracted_data.functional_modules)
        
        # Construct technical_specs locally
        technical_specs = {
            'external_systems': extracted_data.integrations,
            'api_requirements': {}
        }
        
        # Look for integration indicators
        integration_indicators = ['integration', 'api', 'third-party', 'external', 'connect', 'sync']
        integration_mentions = sum(1 for indicator in integration_indicators 
                                 if indicator in requirements_text.lower())
        
        if integration_mentions >= 3:
            integration_complexity = 'high'
        elif integration_mentions >= 1:
            integration_complexity = 'medium'
        else:
            integration_complexity = 'low'
        
        return {
            'integration_complexity': integration_complexity,
            'integration_complexity': integration_complexity,
            'external_systems': extracted_data.integrations,
            'api_requirements': {},
            'data_synchronization': 'sync' in requirements_text.lower()
        }
    
    def _assess_performance_requirements(self, extracted_data: RFPExtractedData) -> Dict[str, Any]:
        """Assess performance requirements"""
        
        # Construct technical_specs locally
        technical_specs = {
            'response_time': 'Not specified',
            'throughput': 'Not specified',
            'availability': '99.9%'
        }
        # Build requirements text for analysis  
        requirements_text = str(extracted_data.performance_expectations) + str(extracted_data.functional_modules)
        
        # Look for performance indicators
        performance_indicators = ['performance', 'speed', 'fast', 'response time', 'latency', 'throughput']
        performance_mentions = sum(1 for indicator in performance_indicators 
                                 if indicator in requirements_text.lower())
        
        if performance_mentions >= 3:
            performance_level = 'high'
        elif performance_mentions >= 1:
            performance_level = 'medium'
        else:
            performance_level = 'standard'
        
        return {
            'performance_level': performance_level,
            'performance_level': performance_level,
            'response_time_requirements': extracted_data.performance_expectations[0] if extracted_data.performance_expectations else 'Not specified',
            'throughput_requirements': 'Not specified',
            'availability_requirements': '99.9%'
        }
    
    def _recommend_technology_stack(self, arch_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend optimal technology stack based on requirements
        
        Args:
            arch_requirements: Architecture requirements analysis
            
        Returns:
            Technology stack recommendation
        """
        try:
            # Extract project characteristics for recommendation
            project_chars = arch_requirements['project_characteristics']
            
            # Use tech stack database to get recommendation
            recommendation_input = {
                'project_size': project_chars['project_size'],
                'team_size': project_chars['team_size'],
                'complexity': project_chars['complexity'],
                'budget': project_chars['budget'],
                'timeline': project_chars['timeline_pressure'],
                'scalability': arch_requirements['scalability_needs']['scalability_level']
            }
            
            tech_recommendation = self.tech_stack_db.recommend_tech_stack(recommendation_input)
            
            # Enhance recommendation with requirement-specific considerations
            enhanced_recommendation = self._enhance_tech_recommendation(
                tech_recommendation, 
                arch_requirements
            )
            
            return enhanced_recommendation
            
        except Exception as e:
            logger.error(f"Technology stack recommendation failed: {e}")
            return self._get_default_tech_stack()
    
    def _enhance_tech_recommendation(self, 
                                   base_recommendation: Dict[str, Any], 
                                   arch_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance technology recommendation with specific requirements"""
        
        enhanced = base_recommendation.copy()
        
        # Add security-specific technologies if high security requirements
        security_reqs = arch_requirements['security_requirements']
        if security_reqs['security_level'] == 'high':
            enhanced['security_stack'] = {
                'authentication': 'OAuth 2.0 / JWT',
                'encryption': 'AES-256',
                'api_security': 'API Gateway with rate limiting',
                'monitoring': 'Security Information and Event Management (SIEM)'
            }
        
        # Add integration-specific technologies
        integration_reqs = arch_requirements['integration_needs']
        if integration_reqs['integration_complexity'] == 'high':
            enhanced['integration_stack'] = {
                'api_gateway': 'Kong / AWS API Gateway',
                'message_queue': 'RabbitMQ / Apache Kafka',
                'data_sync': 'Apache NiFi / Talend',
                'monitoring': 'Prometheus / Grafana'
            }
        
        # Add performance-specific technologies
        performance_reqs = arch_requirements['performance_requirements']
        if performance_reqs['performance_level'] == 'high':
            enhanced['performance_stack'] = {
                'caching': 'Redis / Memcached',
                'cdn': 'CloudFlare / AWS CloudFront',
                'load_balancer': 'NGINX / HAProxy',
                'monitoring': 'New Relic / DataDog'
            }
        
        return enhanced
    
    def _design_system_architecture(self, 
                                  arch_requirements: Dict[str, Any], 
                                  tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design the overall system architecture
        
        Args:
            arch_requirements: Architecture requirements
            tech_stack: Recommended technology stack
            
        Returns:
            System architecture design
        """
        try:
            # Select architecture pattern based on requirements
            pattern = tech_stack.get('architecture_pattern', {})
            
            # Design system components
            components = self._design_system_components(arch_requirements, tech_stack, pattern)
            
            # Define data architecture
            data_architecture = self._design_data_architecture(arch_requirements, tech_stack)
            
            # Create system architecture
            system_architecture = {
                'pattern': pattern,
                'components': components,
                'data_architecture': data_architecture,
                'communication_patterns': self._define_communication_patterns(pattern, components),
                'deployment_units': self._define_deployment_units(components, pattern)
            }
            
            return system_architecture
            
        except Exception as e:
            logger.error(f"System architecture design failed: {e}")
            return self._get_default_system_architecture()
    
    def _design_system_components(self, 
                                arch_requirements: Dict[str, Any], 
                                tech_stack: Dict[str, Any], 
                                pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design individual system components"""
        
        components = []
        functional_reqs = arch_requirements['functional_requirements']
        
        # Core application components
        components.append({
            'name': 'Web Application',
            'type': 'frontend',
            'technology': tech_stack['technologies'].get('frontend', {}).name if tech_stack['technologies'].get('frontend') else 'React',
            'responsibilities': ['User interface', 'User experience', 'Client-side logic'],
            'interfaces': ['REST API', 'WebSocket (if needed)']
        })
        
        components.append({
            'name': 'API Gateway',
            'type': 'gateway',
            'technology': 'NGINX / AWS API Gateway',
            'responsibilities': ['Request routing', 'Authentication', 'Rate limiting', 'Load balancing'],
            'interfaces': ['HTTP/HTTPS', 'WebSocket']
        })
        
        components.append({
            'name': 'Application Server',
            'type': 'backend',
            'technology': tech_stack['technologies'].get('backend', {}).name if tech_stack['technologies'].get('backend') else 'Node.js',
            'responsibilities': ['Business logic', 'API endpoints', 'Data processing'],
            'interfaces': ['REST API', 'Database connections']
        })
        
        components.append({
            'name': 'Database',
            'type': 'database',
            'technology': tech_stack['technologies'].get('database', {}).name if tech_stack['technologies'].get('database') else 'PostgreSQL',
            'responsibilities': ['Data storage', 'Data integrity', 'Query processing'],
            'interfaces': ['SQL/NoSQL queries', 'Connection pooling']
        })
        
        # Add additional components based on requirements
        if arch_requirements['integration_needs']['integration_complexity'] == 'high':
            components.append({
                'name': 'Integration Service',
                'type': 'integration',
                'technology': 'Apache Camel / MuleSoft',
                'responsibilities': ['External system integration', 'Data transformation', 'Message routing'],
                'interfaces': ['REST API', 'Message queues', 'File transfers']
            })
        
        if arch_requirements['security_requirements']['security_level'] == 'high':
            components.append({
                'name': 'Authentication Service',
                'type': 'security',
                'technology': 'OAuth 2.0 / Keycloak',
                'responsibilities': ['User authentication', 'Authorization', 'Token management'],
                'interfaces': ['OAuth endpoints', 'LDAP/AD integration']
            })
        
        if arch_requirements['performance_requirements']['performance_level'] == 'high':
            components.append({
                'name': 'Caching Layer',
                'type': 'cache',
                'technology': 'Redis / Memcached',
                'responsibilities': ['Data caching', 'Session storage', 'Performance optimization'],
                'interfaces': ['Cache API', 'Memory management']
            })
        
        return components
    
    def _design_data_architecture(self, 
                                arch_requirements: Dict[str, Any], 
                                tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """Design data architecture and storage strategy"""
        
        return {
            'primary_database': {
                'type': tech_stack['technologies'].get('database', {}).name if tech_stack['technologies'].get('database') else 'PostgreSQL',
                'purpose': 'Primary application data storage',
                'backup_strategy': 'Daily automated backups with point-in-time recovery',
                'scaling_strategy': 'Read replicas for high-read workloads'
            },
            'data_flow': {
                'ingestion': 'API endpoints and file uploads',
                'processing': 'Application server business logic',
                'storage': 'Normalized relational database schema',
                'retrieval': 'Optimized queries with indexing'
            },
            'data_security': {
                'encryption_at_rest': 'AES-256 encryption for sensitive data',
                'encryption_in_transit': 'TLS 1.3 for all data transmission',
                'access_control': 'Role-based access with principle of least privilege',
                'audit_logging': 'Comprehensive audit trail for all data operations'
            }
        }
    
    def _define_communication_patterns(self, 
                                     pattern: Dict[str, Any], 
                                     components: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Define communication patterns between components"""
        
        return {
            'synchronous': {
                'pattern': 'REST API calls',
                'use_cases': ['User requests', 'Real-time data retrieval', 'CRUD operations'],
                'protocols': ['HTTP/HTTPS', 'JSON over REST']
            },
            'asynchronous': {
                'pattern': 'Message queues',
                'use_cases': ['Background processing', 'Event notifications', 'Batch operations'],
                'protocols': ['AMQP', 'WebSocket for real-time updates']
            },
            'data_access': {
                'pattern': 'Connection pooling',
                'use_cases': ['Database operations', 'Cache access', 'File storage'],
                'protocols': ['SQL', 'NoSQL', 'File system APIs']
            }
        }
    
    def _define_deployment_units(self, 
                               components: List[Dict[str, Any]], 
                               pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Define deployment units and containerization strategy"""
        
        deployment_units = []
        
        # Group components into deployment units
        frontend_components = [c for c in components if c['type'] == 'frontend']
        backend_components = [c for c in components if c['type'] in ['backend', 'gateway', 'security']]
        data_components = [c for c in components if c['type'] in ['database', 'cache']]
        
        if frontend_components:
            deployment_units.append({
                'name': 'Frontend Application',
                'components': [c['name'] for c in frontend_components],
                'deployment_strategy': 'Static hosting with CDN',
                'scaling': 'CDN edge locations',
                'technology': 'Docker container or static files'
            })
        
        if backend_components:
            deployment_units.append({
                'name': 'Backend Services',
                'components': [c['name'] for c in backend_components],
                'deployment_strategy': 'Container orchestration',
                'scaling': 'Horizontal pod autoscaling',
                'technology': 'Docker containers with Kubernetes'
            })
        
        if data_components:
            deployment_units.append({
                'name': 'Data Layer',
                'components': [c['name'] for c in data_components],
                'deployment_strategy': 'Managed cloud services or dedicated instances',
                'scaling': 'Vertical scaling with read replicas',
                'technology': 'Cloud-managed databases and caching services'
            })
        
        return deployment_units
    
    def _design_integration_strategy(self, 
                                   system_architecture: Dict[str, Any], 
                                   arch_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design integration points and strategies"""
        
        integration_points = []
        integration_needs = arch_requirements['integration_needs']
        
        # API integrations
        if integration_needs['integration_complexity'] in ['medium', 'high']:
            integration_points.append({
                'name': 'External API Integration',
                'type': 'REST API',
                'purpose': 'Third-party service integration',
                'pattern': 'API Gateway with circuit breaker',
                'security': 'API key authentication with rate limiting',
                'error_handling': 'Retry logic with exponential backoff'
            })
        
        # Data synchronization
        if integration_needs.get('data_synchronization'):
            integration_points.append({
                'name': 'Data Synchronization',
                'type': 'ETL Pipeline',
                'purpose': 'External system data synchronization',
                'pattern': 'Scheduled batch processing',
                'security': 'Encrypted data transfer with validation',
                'error_handling': 'Failed job retry with alerting'
            })
        
        # Real-time integrations
        if 'real-time' in str(arch_requirements['functional_requirements']).lower():
            integration_points.append({
                'name': 'Real-time Data Integration',
                'type': 'WebSocket/SSE',
                'purpose': 'Real-time data updates',
                'pattern': 'Event-driven architecture',
                'security': 'Token-based authentication',
                'error_handling': 'Connection recovery with buffering'
            })
        
        return integration_points
    
    def _design_scalability_strategy(self, 
                                   system_architecture: Dict[str, Any], 
                                   arch_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design scalability and performance strategy"""
        
        scalability_needs = arch_requirements['scalability_needs']
        
        return {
            'horizontal_scaling': {
                'strategy': 'Container orchestration with auto-scaling',
                'triggers': 'CPU utilization > 70%, Memory > 80%',
                'limits': 'Max 10 instances per service',
                'implementation': 'Kubernetes Horizontal Pod Autoscaler'
            },
            'vertical_scaling': {
                'strategy': 'Resource allocation optimization',
                'triggers': 'Performance monitoring alerts',
                'limits': 'Based on cost-benefit analysis',
                'implementation': 'Cloud provider instance resizing'
            },
            'database_scaling': {
                'strategy': 'Read replicas and connection pooling',
                'triggers': 'Database connection saturation',
                'limits': 'Up to 5 read replicas',
                'implementation': 'Master-slave replication with load balancing'
            },
            'caching_strategy': {
                'levels': ['Browser cache', 'CDN', 'Application cache', 'Database query cache'],
                'implementation': 'Multi-tier caching with TTL management',
                'invalidation': 'Event-driven cache invalidation'
            }
        }
    
    def _design_security_architecture(self, 
                                    system_architecture: Dict[str, Any], 
                                    arch_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """Design security architecture and controls"""
        
        security_reqs = arch_requirements['security_requirements']
        
        return {
            'authentication': {
                'method': 'OAuth 2.0 with JWT tokens',
                'providers': 'Internal identity provider with external SSO support',
                'session_management': 'Stateless JWT with refresh token rotation',
                'multi_factor': 'TOTP-based MFA for admin users'
            },
            'authorization': {
                'model': 'Role-Based Access Control (RBAC)',
                'implementation': 'Fine-grained permissions with resource-level access',
                'enforcement': 'API gateway and application-level checks'
            },
            'data_protection': {
                'encryption_at_rest': 'AES-256 for sensitive data fields',
                'encryption_in_transit': 'TLS 1.3 for all communications',
                'key_management': 'Cloud-based key management service',
                'data_classification': 'Automated sensitive data discovery and tagging'
            },
            'network_security': {
                'segmentation': 'VPC with private subnets for backend services',
                'firewall': 'Web Application Firewall (WAF) with DDoS protection',
                'monitoring': 'Network traffic analysis and intrusion detection'
            },
            'compliance': {
                'frameworks': security_reqs.get('compliance_requirements', ['SOC 2', 'GDPR']),
                'audit_logging': 'Comprehensive audit trail with tamper protection',
                'vulnerability_management': 'Regular security scans and penetration testing'
            }
        }
    
    def _design_deployment_strategy(self, 
                                  system_architecture: Dict[str, Any], 
                                  tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """Design deployment and infrastructure strategy"""
        
        return {
            'deployment_model': {
                'approach': 'Cloud-native containerized deployment',
                'orchestration': 'Kubernetes with Helm charts',
                'environments': ['Development', 'Staging', 'Production'],
                'promotion_strategy': 'GitOps with automated testing gates'
            },
            'infrastructure': {
                'cloud_provider': tech_stack['technologies'].get('cloud', {}).name if tech_stack['technologies'].get('cloud') else 'AWS',
                'compute': 'Managed Kubernetes service (EKS/GKE/AKS)',
                'storage': 'Managed database services with automated backups',
                'networking': 'Load balancers with SSL termination and CDN'
            },
            'ci_cd_pipeline': {
                'source_control': 'Git with feature branch workflow',
                'build_automation': 'Docker image builds with security scanning',
                'testing': 'Automated unit, integration, and security tests',
                'deployment': 'Blue-green deployment with rollback capability'
            },
            'monitoring': {
                'application_monitoring': 'APM with distributed tracing',
                'infrastructure_monitoring': 'Metrics, logs, and alerting',
                'security_monitoring': 'SIEM with threat detection',
                'business_monitoring': 'KPI dashboards and reporting'
            }
        }
    
    def _generate_mermaid_specifications(self, system_architecture: Dict[str, Any]) -> Dict[str, str]:
        """Generate Mermaid diagram specifications for the architecture"""
        
        try:
            # System overview diagram
            system_overview = self._generate_system_overview_mermaid(system_architecture)
            
            # Component interaction diagram
            component_diagram = self._generate_component_interaction_mermaid(system_architecture)
            
            # Deployment diagram
            deployment_diagram = self._generate_deployment_mermaid(system_architecture)
            
            # Data flow diagram
            data_flow_diagram = self._generate_data_flow_mermaid(system_architecture)
            
            return {
                'system_overview': system_overview,
                'component_interaction': component_diagram,
                'deployment_architecture': deployment_diagram,
                'data_flow': data_flow_diagram
            }
            
        except Exception as e:
            logger.error(f"Mermaid specification generation failed: {e}")
            return self._get_default_mermaid_specs()
    
    def _generate_system_overview_mermaid(self, system_architecture: Dict[str, Any]) -> str:
        """Generate system overview Mermaid diagram"""
        
        components = system_architecture.get('components', [])
        
        mermaid_spec = "graph TB\n"
        
        # Add components
        for i, component in enumerate(components):
            comp_id = f"C{i+1}"
            comp_name = component['name']
            comp_type = component['type']
            
            # Style based on component type
            if comp_type == 'frontend':
                mermaid_spec += f"    {comp_id}[{comp_name}]:::frontend\n"
            elif comp_type == 'backend':
                mermaid_spec += f"    {comp_id}[{comp_name}]:::backend\n"
            elif comp_type == 'database':
                mermaid_spec += f"    {comp_id}[({comp_name})]:::database\n"
            else:
                mermaid_spec += f"    {comp_id}[{comp_name}]:::service\n"
        
        # Add connections (simplified)
        if len(components) >= 3:
            mermaid_spec += "    C1 --> C2\n"
            mermaid_spec += "    C2 --> C3\n"
            if len(components) >= 4:
                mermaid_spec += "    C2 --> C4\n"
        
        # Add styling
        mermaid_spec += """
    classDef frontend fill:#e1f5fe
    classDef backend fill:#f3e5f5
    classDef database fill:#e8f5e8
    classDef service fill:#fff3e0
"""
        
        return mermaid_spec
    
    def _generate_component_interaction_mermaid(self, system_architecture: Dict[str, Any]) -> str:
        """Generate component interaction Mermaid diagram"""
        
        return """sequenceDiagram
    participant U as User
    participant W as Web App
    participant G as API Gateway
    participant A as App Server
    participant D as Database
    
    U->>W: User Request
    W->>G: API Call
    G->>A: Route Request
    A->>D: Query Data
    D-->>A: Return Data
    A-->>G: Response
    G-->>W: API Response
    W-->>U: Display Result
"""
    
    def _generate_deployment_mermaid(self, system_architecture: Dict[str, Any]) -> str:
        """Generate deployment architecture Mermaid diagram"""
        
        return """graph TB
    subgraph "Cloud Infrastructure"
        subgraph "Frontend Tier"
            CDN[CDN]
            LB[Load Balancer]
        end
        
        subgraph "Application Tier"
            APP1[App Instance 1]
            APP2[App Instance 2]
            APP3[App Instance 3]
        end
        
        subgraph "Data Tier"
            DB[(Primary DB)]
            CACHE[(Cache)]
            REPLICA[(Read Replica)]
        end
    end
    
    CDN --> LB
    LB --> APP1
    LB --> APP2
    LB --> APP3
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    APP1 --> CACHE
    APP2 --> CACHE
    APP3 --> CACHE
    DB --> REPLICA
"""
    
    def _generate_data_flow_mermaid(self, system_architecture: Dict[str, Any]) -> str:
        """Generate data flow Mermaid diagram"""
        
        return """flowchart LR
    A[User Input] --> B[Validation]
    B --> C[Business Logic]
    C --> D[Data Processing]
    D --> E[(Database)]
    E --> F[Response Generation]
    F --> G[User Interface]
    
    C --> H[External APIs]
    H --> C
    
    D --> I[(Cache)]
    I --> D
"""
    
    def _create_solution_overview(self, 
                                system_architecture: Dict[str, Any], 
                                arch_requirements: Dict[str, Any]) -> str:
        """Create comprehensive solution overview"""
        
        pattern_name = system_architecture['pattern'].get('name', 'Custom Architecture')
        component_count = len(system_architecture['components'])
        
        overview = f"""
## Solution Architecture Overview

The proposed solution follows a {pattern_name} approach with {component_count} core components designed to meet the client's requirements for scalability, security, and maintainability.

### Key Architectural Decisions:

1. **Architecture Pattern**: {pattern_name}
   - Chosen for its balance of simplicity and scalability
   - Supports the project's complexity level and team size
   - Enables efficient development and maintenance

2. **Technology Stack**: Modern, proven technologies
   - Frontend: React-based user interface for responsive design
   - Backend: Node.js/Python for rapid development and scalability
   - Database: PostgreSQL for data integrity and complex queries
   - Cloud: AWS/Azure for reliability and managed services

3. **Scalability Strategy**: Horizontal and vertical scaling
   - Container-based deployment with Kubernetes orchestration
   - Auto-scaling based on demand metrics
   - Caching layers for performance optimization

4. **Security Architecture**: Defense in depth
   - Multi-factor authentication and role-based access control
   - End-to-end encryption for data protection
   - Regular security audits and vulnerability assessments

5. **Integration Approach**: API-first design
   - RESTful APIs for external system integration
   - Event-driven architecture for real-time updates
   - Robust error handling and retry mechanisms

This architecture provides a solid foundation for the client's current needs while enabling future growth and evolution.
"""
        
        return overview.strip()
    
    def _create_design_rationale(self, 
                               system_architecture: Dict[str, Any], 
                               tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed design rationale"""
        
        return {
            'architecture_pattern': {
                'choice': system_architecture['pattern'].get('name', 'Custom'),
                'rationale': 'Selected based on project size, team capabilities, and scalability requirements',
                'alternatives_considered': ['Microservices', 'Monolithic', 'Serverless'],
                'trade_offs': 'Balanced complexity vs. maintainability'
            },
            'technology_selections': {
                'frontend': {
                    'choice': tech_stack['technologies'].get('frontend', {}).name if tech_stack['technologies'].get('frontend') else 'React',
                    'rationale': 'Popular framework with strong ecosystem and community support',
                    'alternatives': ['Angular', 'Vue.js'],
                    'benefits': ['Component reusability', 'Large talent pool', 'Extensive libraries']
                },
                'backend': {
                    'choice': tech_stack['technologies'].get('backend', {}).name if tech_stack['technologies'].get('backend') else 'Node.js',
                    'rationale': 'JavaScript ecosystem consistency and rapid development',
                    'alternatives': ['Python', 'Java', '.NET'],
                    'benefits': ['Fast development', 'JSON native', 'Microservices ready']
                },
                'database': {
                    'choice': tech_stack['technologies'].get('database', {}).name if tech_stack['technologies'].get('database') else 'PostgreSQL',
                    'rationale': 'ACID compliance with JSON support for flexibility',
                    'alternatives': ['MySQL', 'MongoDB'],
                    'benefits': ['Data integrity', 'Complex queries', 'Extensibility']
                }
            },
            'design_principles': [
                'Separation of concerns for maintainability',
                'API-first design for integration flexibility',
                'Security by design with defense in depth',
                'Scalability through horizontal scaling',
                'Observability with comprehensive monitoring'
            ]
        }
    
    def _get_default_architecture_requirements(self) -> Dict[str, Any]:
        """Get default architecture requirements for error cases"""
        return {
            'project_characteristics': {
                'project_size': 'medium',
                'complexity': 'moderate',
                'team_size': 'small',
                'timeline_pressure': 'normal',
                'budget': 'medium',
                'risk_level': 'medium'
            },
            'functional_requirements': ['Web application development'],
            'technical_requirements': {'performance': 'standard'},
            'constraints': {'budget': 'medium', 'timeline': 'normal'},
            'client_context': {'industry': 'general'},
            'scalability_needs': {'scalability_level': 'medium'},
            'security_requirements': {'security_level': 'standard'},
            'integration_needs': {'integration_complexity': 'low'},
            'performance_requirements': {'performance_level': 'standard'}
        }
    
    def _get_default_tech_stack(self) -> Dict[str, Any]:
        """Get default technology stack for error cases"""
        return {
            'architecture_pattern': {
                'name': 'Monolithic Architecture',
                'description': 'Single deployable unit'
            },
            'technologies': {
                'frontend': type('Tech', (), {'name': 'React'})(),
                'backend': type('Tech', (), {'name': 'Node.js'})(),
                'database': type('Tech', (), {'name': 'PostgreSQL'})(),
                'cloud': type('Tech', (), {'name': 'AWS'})()
            },
            'rationale': {
                'react': 'Popular frontend framework',
                'nodejs': 'JavaScript ecosystem',
                'postgresql': 'Reliable database',
                'aws': 'Comprehensive cloud platform'
            },
            'estimated_complexity': 'medium',
            'estimated_cost_factor': 1.0
        }
    
    def _get_default_system_architecture(self) -> Dict[str, Any]:
        """Get default system architecture for error cases"""
        return {
            'pattern': {'name': 'Monolithic Architecture'},
            'components': [
                {
                    'name': 'Web Application',
                    'type': 'frontend',
                    'technology': 'React',
                    'responsibilities': ['User interface']
                },
                {
                    'name': 'Application Server',
                    'type': 'backend',
                    'technology': 'Node.js',
                    'responsibilities': ['Business logic']
                },
                {
                    'name': 'Database',
                    'type': 'database',
                    'technology': 'PostgreSQL',
                    'responsibilities': ['Data storage']
                }
            ],
            'data_architecture': {'primary_database': {'type': 'PostgreSQL'}},
            'communication_patterns': {'synchronous': {'pattern': 'REST API'}},
            'deployment_units': [{'name': 'Full Application', 'components': ['All']}]
        }
    
    def _get_default_mermaid_specs(self) -> Dict[str, str]:
        """Get default Mermaid specifications for error cases"""
        return {
            'system_overview': """graph TB
    A[Web App] --> B[API Server]
    B --> C[(Database)]""",
            'component_interaction': """sequenceDiagram
    User->>App: Request
    App->>DB: Query
    DB-->>App: Data
    App-->>User: Response""",
            'deployment_architecture': """graph TB
    LB[Load Balancer] --> APP[Application]
    APP --> DB[(Database)]""",
            'data_flow': """flowchart LR
    Input --> Process --> Output"""
        }
    
    def _save_solution_to_markdown(self, architecture_design: ArchitectureDesign, output_dir: str) -> None:
        """Save the architecture solution as a Markdown file"""
        import os
        from datetime import datetime
        
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            markdown_content = f"""# Technical Solution Architecture

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

{architecture_design.solution_overview}

---

## Architecture Pattern

**Pattern:** {architecture_design.architecture_pattern.get('name', 'Custom Architecture')}

**Description:** {architecture_design.architecture_pattern.get('description', 'Custom architectural approach')}

---

## Technology Stack

{self._format_tech_stack(architecture_design.technology_stack)}

---

## System Components

{self._format_components(architecture_design.system_components)}

---

## Integration Points

{self._format_integration_points(architecture_design.integration_points)}

---

## Scalability Strategy

{self._format_scalability_strategy(architecture_design.scalability_strategy)}

---

## Security Considerations

{self._format_security_considerations(architecture_design.security_considerations)}

---

## Deployment Strategy

{self._format_deployment_strategy(architecture_design.deployment_strategy)}

---

*This document was automatically generated by the Solution Architect Agent*
"""
            
            output_path = os.path.join(output_dir, "solution_architecture.md")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Saved solution architecture to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save solution to Markdown: {e}")
    
    def _format_tech_stack(self, tech_stack: Dict[str, Any]) -> str:
        """Format technology stack as markdown"""
        output = []
        technologies = tech_stack.get('technologies', {})
        
        for category, tech in technologies.items():
            tech_name = tech.name if hasattr(tech, 'name') else str(tech)
            output.append(f"**{category.title()}:** {tech_name}")
        
        return '\n'.join(output) if output else "**Technologies:** Modern web stack"
    
    def _format_components(self, components: List[Dict[str, Any]]) -> str:
        """Format system components as markdown"""
        if not components:
            return "No components defined"
        
        output = []
        for i, component in enumerate(components, 1):
            output.append(f"### {i}. {component.get('name', 'Component')}")
            output.append(f"**Type:** {component.get('type', 'Unknown')}")
            output.append(f"**Technology:** {component.get('technology', 'TBD')}")
            output.append("")
        
        return '\n'.join(output)
    
    def _format_integration_points(self, integration_points: List[Dict[str, Any]]) -> str:
        """Format integration points as markdown"""
        if not integration_points:
            return "No external integrations required"
        
        output = []
        for i, integration in enumerate(integration_points, 1):
            output.append(f"### {i}. {integration.get('name', 'Integration')}")
            output.append(f"**Type:** {integration.get('type', 'Unknown')}")
            output.append(f"**Purpose:** {integration.get('purpose', 'N/A')}")
            output.append("")
        
        return '\n'.join(output)
    
    def _format_scalability_strategy(self, scalability: Dict[str, Any]) -> str:
        """Format scalability strategy as markdown"""
        output = []
        
        for strategy_name, strategy_details in scalability.items():
            output.append(f"### {strategy_name.replace('_', ' ').title()}")
            if isinstance(strategy_details, dict):
                for key, value in strategy_details.items():
                    output.append(f"**{key.replace('_', ' ').title()}:** {value}")
            output.append("")
        
        return '\n'.join(output)
    
    def _format_security_considerations(self, security: Dict[str, Any]) -> str:
        """Format security considerations as markdown"""
        output = []
        
        for category, details in security.items():
            output.append(f"### {category.replace('_', ' ').title()}")
            if isinstance(details, dict):
                for key, value in details.items():
                    output.append(f"**{key.replace('_', ' ').title()}:** {value}")
            output.append("")
        
        return '\n'.join(output)
    
    def _format_deployment_strategy(self, deployment: Dict[str, Any]) -> str:
        """Format deployment strategy as markdown"""
        output = []
        
        for section, details in deployment.items():
            output.append(f"### {section.replace('_', ' ').title()}")
            if isinstance(details, dict):
                for key, value in details.items():
                    if isinstance(value, list):
                        output.append(f"**{key.replace('_', ' ').title()}:** {', '.join(str(v) for v in value)}")
                    else:
                        output.append(f"**{key.replace('_', ' ').title()}:** {value}")
            output.append("")
        
        return '\n'.join(output)

# Factory function to create solution architect agent
def create_solution_architect_agent(llm: Optional[ChatOpenAI] = None) -> SolutionArchitectAgent:
    """Create and configure solution architect agent"""
    return SolutionArchitectAgent(llm=llm)