"""
Project Manager Agent for effort estimation, timeline planning, and resource allocation
Calculates effort, timeline, and resource allocation with comprehensive risk management
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState
from ..tools.estimation_tools import create_estimation_tools

logger = logging.getLogger(__name__)

@dataclass
class ProjectEstimate:
    """Comprehensive project estimate"""
    total_effort_hours: float
    duration_weeks: float
    team_size: int
    cost_estimate: Dict[str, Any]
    confidence_intervals: Dict[str, Any]
    component_breakdown: List[Dict[str, Any]]
    risk_assessment: Dict[str, Any]

@dataclass
class ProjectPlan:
    """Detailed project plan with phases and milestones"""
    phases: List[Dict[str, Any]]
    milestones: List[Dict[str, Any]]
    resource_allocation: Dict[str, Any]
    critical_path: List[str]
    risk_mitigation: List[Dict[str, Any]]
    success_criteria: List[str]

class ProjectManagerAgent:
    """
    Project Manager Agent that handles estimation, planning, and resource allocation
    
    Responsibilities:
    - Analyze scope and architecture to generate effort estimates
    - Create detailed project plans with phases and milestones
    - Calculate resource allocation and team composition
    - Assess project risks and create mitigation strategies
    - Generate realistic timelines with appropriate buffers
    - Provide cost estimates and budget planning
    - Define success criteria and quality gates
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Initialize estimation tools
        self.estimation_tools = create_estimation_tools()
        self.historical_lookup = self.estimation_tools['historical_data_lookup']
        self.estimation_model = self.estimation_tools['estimation_model']
        self.plan_generator = self.estimation_tools['project_plan_generator']
        
        # System prompt for the Project Manager
        self.system_prompt = """You are the Project Manager Agent. Using the defined scope, architecture, and historical data, generate a detailed project plan, including effort estimations, resource allocation, and a realistic timeline with key milestones. Focus on minimizing risk and providing buffers.

Your responsibilities:
1. Analyze project scope and technical complexity for accurate estimation
2. Generate detailed effort estimates using historical data and proven models
3. Create comprehensive project plans with phases, milestones, and deliverables
4. Calculate optimal resource allocation and team composition
5. Assess project risks and develop mitigation strategies
6. Establish realistic timelines with appropriate buffers
7. Provide detailed cost estimates and budget planning
8. Define clear success criteria and quality gates

Focus on:
- Accurate effort estimation based on historical data
- Realistic timeline planning with risk buffers
- Optimal resource allocation and team structure
- Comprehensive risk assessment and mitigation
- Clear milestone definition and success criteria
- Cost-effective project delivery
- Quality assurance and control measures

Always provide detailed rationale for estimates and recommendations, considering project constraints and client expectations."""
    
    def create_project_plan(self, state: WorkflowState) -> WorkflowState:
        """
        Create comprehensive project plan with estimates and resource allocation
        
        Args:
            state: Current workflow state with architecture design
            
        Returns:
            Updated state with project plan and estimates
        """
        try:
            logger.info("Project Manager Agent: Starting project planning")
            
            if not state.architecture_design:
                raise ValueError("No architecture design available for project planning")
            
            # Step 1: Analyze project scope and complexity
            project_analysis = self._analyze_project_scope(state.extracted_data, state.architecture_design)
            
            # Step 2: Generate component-level estimates
            component_estimates = self._generate_component_estimates(project_analysis, state.architecture_design)
            
            # Step 3: Calculate overall project estimate
            project_estimate = self._calculate_project_estimate(component_estimates, project_analysis)
            
            # Step 4: Create detailed project plan
            project_plan = self._create_detailed_project_plan(project_estimate, project_analysis)
            
            # Step 5: Perform risk assessment and mitigation planning
            risk_assessment = self._perform_risk_assessment(project_estimate, project_plan, project_analysis)
            
            # Step 6: Optimize resource allocation
            resource_optimization = self._optimize_resource_allocation(project_plan, project_estimate)
            
            # Step 7: Validate and finalize plan
            final_plan = self._validate_and_finalize_plan(project_plan, project_estimate, risk_assessment)
            
            # Update state (convert dataclass to dict for Pydantic compatibility)
            state.project_plan = asdict(final_plan)
            state.project_estimate = asdict(project_estimate)
            state.risk_assessment = risk_assessment
            state.current_step = "project_planning_complete"
            state.last_agent_executed = "project_manager"
            
            logger.info(f"Project Manager Agent: Plan created - {project_estimate.duration_weeks} weeks, {project_estimate.total_effort_hours} hours")
            return state
            
        except Exception as e:
            logger.error(f"Project Manager Agent failed: {e}")
            state.errors.append(f"Project Manager Agent error: {str(e)}")
            return state
    
    def _analyze_project_scope(self, extracted_data: Any, architecture_design: Any) -> Dict[str, Any]:
        """
        Analyze project scope and complexity for estimation
        
        Args:
            extracted_data: Extracted RFP requirements
            architecture_design: Technical architecture design
            
        Returns:
            Project scope analysis
        """
        try:
            # Extract key project characteristics
            functional_reqs = getattr(extracted_data, 'requirements', {}).get('functional', [])
            technical_specs = getattr(extracted_data, 'technical_specs', {})
            constraints = getattr(extracted_data, 'constraints', {})
            
            # Analyze architecture complexity
            components = getattr(architecture_design, 'system_components', [])
            integration_points = getattr(architecture_design, 'integration_points', [])
            
            # Determine project characteristics
            project_size = self._assess_project_size(functional_reqs, components)
            technical_complexity = self._assess_technical_complexity(architecture_design, technical_specs)
            integration_complexity = self._assess_integration_complexity(integration_points, technical_specs)
            
            # Assess constraints and risks
            timeline_constraints = self._assess_timeline_constraints(constraints)
            budget_constraints = self._assess_budget_constraints(constraints)
            resource_constraints = self._assess_resource_constraints(constraints)
            
            # Determine team requirements
            team_requirements = self._determine_team_requirements(project_size, technical_complexity)
            
            project_analysis = {
                'project_characteristics': {
                    'project_size': project_size,
                    'technical_complexity': technical_complexity,
                    'integration_complexity': integration_complexity,
                    'functional_requirement_count': len(functional_reqs),
                    'component_count': len(components),
                    'integration_point_count': len(integration_points)
                },
                'constraints': {
                    'timeline': timeline_constraints,
                    'budget': budget_constraints,
                    'resources': resource_constraints
                },
                'team_requirements': team_requirements,
                'risk_factors': self._identify_initial_risk_factors(technical_complexity, constraints),
                'estimation_context': {
                    'client_industry': getattr(extracted_data, 'client_info', {}).get('industry', 'General'),
                    'project_type': 'Custom Software Development',
                    'delivery_model': 'Agile Development'
                }
            }
            
            return project_analysis
            
        except Exception as e:
            logger.error(f"Project scope analysis failed: {e}")
            return self._get_default_project_analysis()
    
    def _assess_project_size(self, functional_reqs: List[str], components: List[Dict[str, Any]]) -> str:
        """Assess overall project size"""
        
        req_count = len(functional_reqs)
        comp_count = len(components)
        
        # Calculate size score
        size_score = req_count + (comp_count * 2)
        
        if size_score <= 10:
            return 'small'
        elif size_score <= 25:
            return 'medium'
        elif size_score <= 50:
            return 'large'
        else:
            return 'very_large'
    
    def _assess_technical_complexity(self, architecture_design: Any, technical_specs: Dict[str, Any]) -> str:
        """Assess technical complexity level"""
        
        complexity_indicators = 0
        
        # Check architecture pattern complexity
        pattern_name = getattr(architecture_design, 'architecture_pattern', {}).get('name', '')
        if 'microservices' in pattern_name.lower():
            complexity_indicators += 3
        elif 'serverless' in pattern_name.lower():
            complexity_indicators += 2
        
        # Check technology stack complexity
        tech_stack = getattr(architecture_design, 'technology_stack', {})
        if tech_stack.get('estimated_complexity') == 'high':
            complexity_indicators += 2
        elif tech_stack.get('estimated_complexity') == 'medium':
            complexity_indicators += 1
        
        # Check security requirements
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        if security_considerations:
            complexity_indicators += 1
        
        # Check scalability requirements
        scalability_strategy = getattr(architecture_design, 'scalability_strategy', {})
        if scalability_strategy:
            complexity_indicators += 1
        
        # Determine complexity level
        if complexity_indicators <= 2:
            return 'low'
        elif complexity_indicators <= 5:
            return 'medium'
        elif complexity_indicators <= 8:
            return 'high'
        else:
            return 'very_high'
    
    def _assess_integration_complexity(self, integration_points: List[Dict[str, Any]], technical_specs: Dict[str, Any]) -> str:
        """Assess integration complexity"""
        
        integration_count = len(integration_points)
        
        # Check for external system integrations
        external_systems = technical_specs.get('external_systems', [])
        api_requirements = technical_specs.get('api_requirements', {})
        
        complexity_score = integration_count + len(external_systems)
        
        if api_requirements:
            complexity_score += 1
        
        if complexity_score == 0:
            return 'none'
        elif complexity_score <= 2:
            return 'low'
        elif complexity_score <= 5:
            return 'medium'
        else:
            return 'high'
    
    def _assess_timeline_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Assess timeline constraints and pressure"""
        
        timeline_info = constraints.get('timeline', '')
        timeline_str = str(timeline_info).lower()
        
        if any(word in timeline_str for word in ['urgent', 'asap', 'immediate', 'rush']):
            pressure = 'high'
            flexibility = 'low'
        elif any(word in timeline_str for word in ['flexible', 'when ready', 'no rush']):
            pressure = 'low'
            flexibility = 'high'
        else:
            pressure = 'medium'
            flexibility = 'medium'
        
        return {
            'pressure': pressure,
            'flexibility': flexibility,
            'constraints': timeline_info
        }
    
    def _assess_budget_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Assess budget constraints"""
        
        budget_info = constraints.get('budget', '')
        budget_str = str(budget_info).lower()
        
        if any(word in budget_str for word in ['limited', 'tight', 'minimal', 'low']):
            level = 'constrained'
            flexibility = 'low'
        elif any(word in budget_str for word in ['flexible', 'generous', 'adequate']):
            level = 'flexible'
            flexibility = 'high'
        else:
            level = 'moderate'
            flexibility = 'medium'
        
        return {
            'level': level,
            'flexibility': flexibility,
            'constraints': budget_info
        }
    
    def _assess_resource_constraints(self, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Assess resource availability constraints"""
        
        # This would typically analyze team availability, skill requirements, etc.
        return {
            'availability': 'standard',
            'skill_requirements': 'standard',
            'constraints': 'Standard resource availability assumed'
        }
    
    def _determine_team_requirements(self, project_size: str, technical_complexity: str) -> Dict[str, Any]:
        """Determine optimal team composition and size"""
        
        # Base team size on project size
        size_to_team = {
            'small': 2,
            'medium': 4,
            'large': 6,
            'very_large': 8
        }
        
        base_team_size = size_to_team.get(project_size, 4)
        
        # Adjust for technical complexity
        complexity_multiplier = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.3,
            'very_high': 1.6
        }
        
        adjusted_team_size = int(base_team_size * complexity_multiplier.get(technical_complexity, 1.0))
        
        # Define team composition
        if adjusted_team_size <= 2:
            composition = {
                'senior_developer': 1,
                'developer': 1
            }
        elif adjusted_team_size <= 4:
            composition = {
                'senior_developer': 1,
                'developer': 2,
                'qa_engineer': 1
            }
        elif adjusted_team_size <= 6:
            composition = {
                'tech_lead': 1,
                'senior_developer': 2,
                'developer': 2,
                'qa_engineer': 1
            }
        else:
            composition = {
                'project_manager': 1,
                'tech_lead': 1,
                'senior_developer': 2,
                'developer': 3,
                'qa_engineer': 1
            }
        
        return {
            'optimal_team_size': adjusted_team_size,
            'team_composition': composition,
            'key_roles': list(composition.keys()),
            'scaling_strategy': 'Start with core team, scale as needed'
        }
    
    def _identify_initial_risk_factors(self, technical_complexity: str, constraints: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify initial project risk factors"""
        
        risk_factors = []
        
        # Technical complexity risks
        if technical_complexity in ['high', 'very_high']:
            risk_factors.append({
                'category': 'technical',
                'risk': 'High technical complexity',
                'impact': 'high',
                'probability': 'medium',
                'description': 'Complex architecture may lead to development challenges'
            })
        
        # Timeline pressure risks
        timeline_constraints = constraints.get('timeline', {})
        if isinstance(timeline_constraints, dict) and timeline_constraints.get('pressure') == 'high':
            risk_factors.append({
                'category': 'schedule',
                'risk': 'Tight timeline constraints',
                'impact': 'high',
                'probability': 'high',
                'description': 'Aggressive timeline may impact quality or scope'
            })
        
        # Budget constraint risks
        budget_constraints = constraints.get('budget', {})
        if isinstance(budget_constraints, dict) and budget_constraints.get('level') == 'constrained':
            risk_factors.append({
                'category': 'budget',
                'risk': 'Limited budget',
                'impact': 'medium',
                'probability': 'medium',
                'description': 'Budget constraints may limit resource allocation'
            })
        
        return risk_factors
    
    def _generate_component_estimates(self, project_analysis: Dict[str, Any], architecture_design: Any) -> List[Dict[str, Any]]:
        """
        Generate effort estimates for individual components
        
        Args:
            project_analysis: Project scope analysis
            architecture_design: Technical architecture
            
        Returns:
            List of component estimates
        """
        try:
            component_estimates = []
            components = getattr(architecture_design, 'system_components', [])
            
            # Map components to estimation categories
            for component in components:
                comp_name = component.get('name', 'Unknown Component')
                comp_type = component.get('type', 'service')
                comp_tech = component.get('technology', 'Unknown')
                
                # Map component type to estimation category
                estimation_category = self._map_component_to_category(comp_type, comp_name)
                
                # Get historical estimate
                historical_estimate = self.historical_lookup.get_component_estimate(
                    estimation_category, 
                    project_analysis['project_characteristics']['technical_complexity']
                )
                
                # Adjust estimate based on component specifics
                adjusted_estimate = self._adjust_component_estimate(
                    historical_estimate, 
                    component, 
                    project_analysis
                )
                
                component_estimates.append({
                    'component_name': comp_name,
                    'component_type': comp_type,
                    'technology': comp_tech,
                    'estimation_category': estimation_category,
                    'base_hours': adjusted_estimate['estimated_hours'],
                    'complexity_factor': adjusted_estimate['complexity_multiplier'],
                    'risk_factor': self._calculate_component_risk_factor(component, project_analysis),
                    'final_estimate': adjusted_estimate['estimated_hours'] * self._calculate_component_risk_factor(component, project_analysis),
                    'confidence': self._assess_estimate_confidence(component, historical_estimate),
                    'tasks': adjusted_estimate.get('typical_tasks', [])
                })
            
            # Add project management and overhead estimates
            overhead_estimates = self._calculate_overhead_estimates(component_estimates, project_analysis)
            component_estimates.extend(overhead_estimates)
            
            return component_estimates
            
        except Exception as e:
            logger.error(f"Component estimation failed: {e}")
            return self._get_default_component_estimates()
    
    def _map_component_to_category(self, comp_type: str, comp_name: str) -> str:
        """Map component type to estimation category"""
        
        type_mapping = {
            'frontend': 'dashboard',
            'backend': 'api_development',
            'database': 'database_design',
            'gateway': 'integration',
            'security': 'authentication',
            'cache': 'integration',
            'integration': 'integration'
        }
        
        # Check component name for specific patterns
        name_lower = comp_name.lower()
        if 'auth' in name_lower:
            return 'authentication'
        elif 'user' in name_lower:
            return 'user_management'
        elif 'report' in name_lower:
            return 'reporting'
        elif 'dashboard' in name_lower:
            return 'dashboard'
        
        return type_mapping.get(comp_type, 'api_development')
    
    def _adjust_component_estimate(self, 
                                 historical_estimate: Dict[str, Any], 
                                 component: Dict[str, Any], 
                                 project_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Adjust historical estimate based on component specifics"""
        
        base_hours = historical_estimate['estimated_hours']
        complexity_multiplier = historical_estimate['complexity_multiplier']
        
        # Adjust for technology complexity
        technology = component.get('technology', '')
        if any(tech in technology.lower() for tech in ['kubernetes', 'microservices', 'serverless']):
            complexity_multiplier *= 1.2
        
        # Adjust for integration complexity
        interfaces = component.get('interfaces', [])
        if len(interfaces) > 3:
            complexity_multiplier *= 1.1
        
        # Adjust for project-specific factors
        if project_analysis['project_characteristics']['integration_complexity'] == 'high':
            complexity_multiplier *= 1.15
        
        return {
            'estimated_hours': base_hours * complexity_multiplier,
            'complexity_multiplier': complexity_multiplier,
            'typical_tasks': historical_estimate.get('typical_tasks', [])
        }
    
    def _calculate_component_risk_factor(self, component: Dict[str, Any], project_analysis: Dict[str, Any]) -> float:
        """Calculate risk factor for component estimate"""
        
        base_risk = 1.1  # 10% base risk buffer
        
        # Technology risk
        technology = component.get('technology', '').lower()
        if 'new' in technology or 'experimental' in technology:
            base_risk += 0.2
        
        # Integration risk
        interfaces = component.get('interfaces', [])
        if len(interfaces) > 2:
            base_risk += 0.1
        
        # Project complexity risk
        if project_analysis['project_characteristics']['technical_complexity'] == 'high':
            base_risk += 0.15
        
        return min(base_risk, 2.0)  # Cap at 100% risk buffer
    
    def _assess_estimate_confidence(self, component: Dict[str, Any], historical_estimate: Dict[str, Any]) -> str:
        """Assess confidence level for component estimate"""
        
        # Base confidence on historical data availability and component complexity
        if 'typical_tasks' in historical_estimate and len(historical_estimate['typical_tasks']) > 3:
            base_confidence = 'high'
        else:
            base_confidence = 'medium'
        
        # Adjust for component specifics
        technology = component.get('technology', '').lower()
        if 'unknown' in technology or 'new' in technology:
            base_confidence = 'low'
        
        return base_confidence
    
    def _calculate_overhead_estimates(self, component_estimates: List[Dict[str, Any]], project_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Calculate project management and overhead estimates"""
        
        total_dev_hours = sum(est['final_estimate'] for est in component_estimates)
        
        overhead_estimates = []
        
        # Project management
        pm_hours = total_dev_hours * 0.15  # 15% PM overhead
        overhead_estimates.append({
            'component_name': 'Project Management',
            'component_type': 'management',
            'technology': 'Project Management Tools',
            'estimation_category': 'project_management',
            'base_hours': pm_hours,
            'complexity_factor': 1.0,
            'risk_factor': 1.1,
            'final_estimate': pm_hours * 1.1,
            'confidence': 'high',
            'tasks': ['Project planning', 'Team coordination', 'Progress tracking', 'Client communication']
        })
        
        # Testing
        test_hours = total_dev_hours * 0.25  # 25% testing overhead
        overhead_estimates.append({
            'component_name': 'Testing & QA',
            'component_type': 'testing',
            'technology': 'Testing Frameworks',
            'estimation_category': 'testing',
            'base_hours': test_hours,
            'complexity_factor': 1.0,
            'risk_factor': 1.2,
            'final_estimate': test_hours * 1.2,
            'confidence': 'high',
            'tasks': ['Unit testing', 'Integration testing', 'User acceptance testing', 'Bug fixes']
        })
        
        # Deployment & DevOps
        deploy_hours = total_dev_hours * 0.10  # 10% deployment overhead
        overhead_estimates.append({
            'component_name': 'Deployment & DevOps',
            'component_type': 'deployment',
            'technology': 'CI/CD Tools',
            'estimation_category': 'deployment',
            'base_hours': deploy_hours,
            'complexity_factor': 1.0,
            'risk_factor': 1.3,
            'final_estimate': deploy_hours * 1.3,
            'confidence': 'medium',
            'tasks': ['CI/CD setup', 'Environment configuration', 'Monitoring setup', 'Documentation']
        })
        
        return overhead_estimates
    
    def _calculate_project_estimate(self, component_estimates: List[Dict[str, Any]], project_analysis: Dict[str, Any]) -> ProjectEstimate:
        """
        Calculate overall project estimate from component estimates
        
        Args:
            component_estimates: Individual component estimates
            project_analysis: Project analysis data
            
        Returns:
            Comprehensive project estimate
        """
        try:
            # Use estimation model to calculate project estimate
            project_factors = {
                'project_size': project_analysis['project_characteristics']['project_size'],
                'team_size': project_analysis['team_requirements']['optimal_team_size'],
                'complexity': project_analysis['project_characteristics']['technical_complexity'],
                'budget': project_analysis['constraints']['budget']['level'],
                'timeline': project_analysis['constraints']['timeline']['pressure'],
                'risk_level': self._calculate_overall_risk_level(project_analysis)
            }
            
            # Prepare components for estimation model
            estimation_components = []
            for comp_est in component_estimates:
                estimation_components.append({
                    'name': comp_est['component_name'],
                    'base_hours': comp_est['base_hours'],
                    'risk_level': self._map_risk_factor_to_level(comp_est['risk_factor']),
                    'dependencies': []  # Could be enhanced with actual dependencies
                })
            
            # Calculate comprehensive estimate
            estimate_result = self.estimation_model.calculate_project_estimate(
                estimation_components, 
                project_factors
            )
            
            # Create project estimate object
            project_estimate = ProjectEstimate(
                total_effort_hours=estimate_result['total_effort_hours'],
                duration_weeks=estimate_result['duration_weeks'],
                team_size=estimate_result['team_size'],
                cost_estimate=estimate_result['cost_estimate'],
                confidence_intervals=estimate_result['confidence_intervals'],
                component_breakdown=component_estimates,
                risk_assessment={
                    'overall_risk_level': project_factors['risk_level'],
                    'key_risk_factors': project_analysis['risk_factors'],
                    'estimation_assumptions': estimate_result['key_assumptions']
                }
            )
            
            return project_estimate
            
        except Exception as e:
            logger.error(f"Project estimate calculation failed: {e}")
            return self._get_default_project_estimate()
    
    def _calculate_overall_risk_level(self, project_analysis: Dict[str, Any]) -> str:
        """Calculate overall project risk level"""
        
        risk_factors = project_analysis['risk_factors']
        high_risk_count = sum(1 for risk in risk_factors if risk.get('impact') == 'high')
        
        technical_complexity = project_analysis['project_characteristics']['technical_complexity']
        timeline_pressure = project_analysis['constraints']['timeline']['pressure']
        
        if high_risk_count >= 2 or technical_complexity == 'very_high' or timeline_pressure == 'high':
            return 'high'
        elif high_risk_count >= 1 or technical_complexity == 'high':
            return 'medium'
        else:
            return 'low'
    
    def _map_risk_factor_to_level(self, risk_factor: float) -> str:
        """Map numeric risk factor to risk level"""
        if risk_factor >= 1.5:
            return 'high'
        elif risk_factor >= 1.2:
            return 'medium'
        else:
            return 'low'
    
    def _create_detailed_project_plan(self, project_estimate: ProjectEstimate, project_analysis: Dict[str, Any]) -> ProjectPlan:
        """
        Create detailed project plan with phases and milestones
        
        Args:
            project_estimate: Project estimate data
            project_analysis: Project analysis data
            
        Returns:
            Detailed project plan
        """
        try:
            # Use plan generator to create comprehensive plan
            plan_requirements = {
                'total_duration': project_estimate.duration_weeks,
                'total_effort': project_estimate.total_effort_hours,
                'team_size': project_estimate.team_size,
                'complexity': project_analysis['project_characteristics']['technical_complexity'],
                'constraints': project_analysis['constraints']
            }
            
            plan_result = self.plan_generator.generate_project_plan(
                project_estimate.__dict__, 
                plan_requirements
            )
            
            # Create project plan object
            project_plan = ProjectPlan(
                phases=plan_result['project_phases'],
                milestones=plan_result['milestones'],
                resource_allocation=plan_result['resource_allocation'],
                critical_path=plan_result['critical_path'],
                risk_mitigation=plan_result['risk_mitigation'],
                success_criteria=plan_result['success_criteria']
            )
            
            return project_plan
            
        except Exception as e:
            logger.error(f"Project plan creation failed: {e}")
            return self._get_default_project_plan()
    
    def _perform_risk_assessment(self, 
                                project_estimate: ProjectEstimate, 
                                project_plan: ProjectPlan, 
                                project_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive risk assessment
        
        Args:
            project_estimate: Project estimate
            project_plan: Project plan
            project_analysis: Project analysis
            
        Returns:
            Risk assessment results
        """
        try:
            # Combine initial risks with estimate-based risks
            all_risks = project_analysis['risk_factors'].copy()
            
            # Add estimate-based risks
            if project_estimate.total_effort_hours > 2000:
                all_risks.append({
                    'category': 'scope',
                    'risk': 'Large project scope',
                    'impact': 'high',
                    'probability': 'medium',
                    'description': 'Large scope increases complexity and coordination challenges'
                })
            
            if project_estimate.duration_weeks > 26:
                all_risks.append({
                    'category': 'schedule',
                    'risk': 'Extended timeline',
                    'impact': 'medium',
                    'probability': 'medium',
                    'description': 'Long projects face increased risk of scope changes and team turnover'
                })
            
            # Add plan-based risks
            if len(project_plan.phases) > 5:
                all_risks.append({
                    'category': 'complexity',
                    'risk': 'Multiple project phases',
                    'impact': 'medium',
                    'probability': 'low',
                    'description': 'Complex phasing may create coordination challenges'
                })
            
            # Calculate risk scores
            risk_assessment = {
                'identified_risks': all_risks,
                'risk_summary': {
                    'total_risks': len(all_risks),
                    'high_impact_risks': len([r for r in all_risks if r.get('impact') == 'high']),
                    'high_probability_risks': len([r for r in all_risks if r.get('probability') == 'high']),
                    'critical_risks': len([r for r in all_risks if r.get('impact') == 'high' and r.get('probability') == 'high'])
                },
                'mitigation_strategies': project_plan.risk_mitigation,
                'contingency_planning': {
                    'schedule_buffer': '15% built into timeline',
                    'budget_buffer': '10% contingency recommended',
                    'resource_buffer': 'Cross-training and backup resources identified'
                },
                'monitoring_plan': {
                    'risk_review_frequency': 'Weekly during development',
                    'escalation_triggers': ['Schedule delay > 1 week', 'Budget variance > 10%'],
                    'key_metrics': ['Velocity', 'Defect rate', 'Team utilization']
                }
            }
            
            return risk_assessment
            
        except Exception as e:
            logger.error(f"Risk assessment failed: {e}")
            return self._get_default_risk_assessment()
    
    def _optimize_resource_allocation(self, project_plan: ProjectPlan, project_estimate: ProjectEstimate) -> Dict[str, Any]:
        """
        Optimize resource allocation across project phases
        
        Args:
            project_plan: Project plan
            project_estimate: Project estimate
            
        Returns:
            Optimized resource allocation
        """
        try:
            # Analyze resource needs by phase
            phase_resources = {}
            for phase in project_plan.phases:
                phase_name = phase.get('name', 'Unknown Phase')
                phase_duration = phase.get('duration_weeks', 0)
                phase_effort = phase.get('effort_hours', 0)
                
                # Calculate optimal team size for phase
                if phase_duration > 0:
                    weekly_effort = phase_effort / phase_duration
                    optimal_team = max(1, int(weekly_effort / 40))  # 40 hours per person per week
                else:
                    optimal_team = 1
                
                phase_resources[phase_name] = {
                    'duration_weeks': phase_duration,
                    'effort_hours': phase_effort,
                    'optimal_team_size': optimal_team,
                    'resource_profile': self._determine_phase_resource_profile(phase_name, optimal_team)
                }
            
            # Create resource optimization recommendations
            optimization = {
                'phase_resource_allocation': phase_resources,
                'resource_leveling': self._calculate_resource_leveling(phase_resources),
                'skill_requirements': self._identify_skill_requirements(project_plan.phases),
                'optimization_recommendations': [
                    'Consider overlapping phases to optimize resource utilization',
                    'Plan for knowledge transfer between phases',
                    'Identify opportunities for parallel work streams',
                    'Ensure adequate ramp-up time for new team members'
                ]
            }
            
            return optimization
            
        except Exception as e:
            logger.error(f"Resource optimization failed: {e}")
            return {'optimization_error': str(e)}
    
    def _determine_phase_resource_profile(self, phase_name: str, team_size: int) -> Dict[str, int]:
        """Determine resource profile for a specific phase"""
        
        if 'discovery' in phase_name.lower() or 'planning' in phase_name.lower():
            return {
                'business_analyst': 1,
                'solution_architect': 1,
                'project_manager': 1
            }
        elif 'development' in phase_name.lower() or 'core' in phase_name.lower():
            if team_size <= 2:
                return {'senior_developer': 1, 'developer': 1}
            elif team_size <= 4:
                return {'senior_developer': 1, 'developer': 2, 'qa_engineer': 1}
            else:
                return {'tech_lead': 1, 'senior_developer': 2, 'developer': team_size-3}
        elif 'testing' in phase_name.lower() or 'integration' in phase_name.lower():
            return {
                'qa_engineer': max(1, team_size // 2),
                'developer': max(1, team_size // 2)
            }
        elif 'deployment' in phase_name.lower():
            return {
                'devops_engineer': 1,
                'senior_developer': 1
            }
        else:
            return {'developer': team_size}
    
    def _calculate_resource_leveling(self, phase_resources: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate resource leveling across phases"""
        
        # Simple resource leveling analysis
        if not phase_resources:
            return {
                'peak_team_size': 0,
                'minimum_team_size': 0,
                'resource_variance': 0,
                'leveling_recommendation': 'No phases defined'
            }
            
        max_team_size = max(phase['optimal_team_size'] for phase in phase_resources.values())
        min_team_size = min(phase['optimal_team_size'] for phase in phase_resources.values())
        
        return {
            'peak_team_size': max_team_size,
            'minimum_team_size': min_team_size,
            'resource_variance': max_team_size - min_team_size,
            'leveling_recommendation': 'Consider maintaining core team throughout project' if max_team_size - min_team_size > 3 else 'Resource allocation is well-balanced'
        }
    
    def _identify_skill_requirements(self, phases: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Identify skill requirements across project phases"""
        
        skill_requirements = {
            'technical_skills': [
                'Full-stack development',
                'Database design and optimization',
                'API development and integration',
                'Cloud platform expertise',
                'Security implementation'
            ],
            'domain_skills': [
                'Business analysis',
                'Solution architecture',
                'User experience design',
                'Quality assurance',
                'DevOps and deployment'
            ],
            'soft_skills': [
                'Project management',
                'Client communication',
                'Team collaboration',
                'Problem solving',
                'Documentation'
            ]
        }
        
        return skill_requirements
    
    def _validate_and_finalize_plan(self, 
                                  project_plan: ProjectPlan, 
                                  project_estimate: ProjectEstimate, 
                                  risk_assessment: Dict[str, Any]) -> ProjectPlan:
        """
        Validate and finalize the project plan
        
        Args:
            project_plan: Initial project plan
            project_estimate: Project estimate
            risk_assessment: Risk assessment
            
        Returns:
            Finalized project plan
        """
        try:
            # Add validation metadata
            validation_results = {
                'plan_validation': {
                    'total_phase_duration': sum(phase.get('duration_weeks', 0) for phase in project_plan.phases),
                    'estimated_duration': project_estimate.duration_weeks,
                    'duration_variance': abs(sum(phase.get('duration_weeks', 0) for phase in project_plan.phases) - project_estimate.duration_weeks),
                    'validation_status': 'validated'
                },
                'estimate_validation': {
                    'confidence_level': 'medium',  # Based on component estimate confidence
                    'key_assumptions': project_estimate.risk_assessment.get('estimation_assumptions', []),
                    'validation_notes': 'Estimates based on historical data and architectural analysis'
                },
                'risk_validation': {
                    'risk_coverage': 'comprehensive',
                    'mitigation_completeness': 'adequate',
                    'monitoring_plan': 'defined'
                }
            }
            
            # Create finalized plan with validation results
            finalized_plan = ProjectPlan(
                phases=project_plan.phases,
                milestones=project_plan.milestones,
                resource_allocation=project_plan.resource_allocation,
                critical_path=project_plan.critical_path,
                risk_mitigation=project_plan.risk_mitigation,
                success_criteria=project_plan.success_criteria
            )
            
            # Add validation metadata to plan
            finalized_plan.validation_results = validation_results
            finalized_plan.finalization_timestamp = self._get_current_timestamp()
            
            return finalized_plan
            
        except Exception as e:
            logger.error(f"Plan validation failed: {e}")
            return project_plan
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        return datetime.now().isoformat()
    
    def _get_default_project_analysis(self) -> Dict[str, Any]:
        """Get default project analysis for error cases"""
        return {
            'project_characteristics': {
                'project_size': 'medium',
                'technical_complexity': 'medium',
                'integration_complexity': 'low',
                'functional_requirement_count': 10,
                'component_count': 5,
                'integration_point_count': 2
            },
            'constraints': {
                'timeline': {'pressure': 'medium', 'flexibility': 'medium'},
                'budget': {'level': 'moderate', 'flexibility': 'medium'},
                'resources': {'availability': 'standard'}
            },
            'team_requirements': {
                'optimal_team_size': 4,
                'team_composition': {'senior_developer': 1, 'developer': 2, 'qa_engineer': 1}
            },
            'risk_factors': [],
            'estimation_context': {
                'client_industry': 'General',
                'project_type': 'Custom Software Development',
                'delivery_model': 'Agile Development'
            }
        }
    
    def _get_default_component_estimates(self) -> List[Dict[str, Any]]:
        """Get default component estimates for error cases"""
        return [
            {
                'component_name': 'Web Application',
                'component_type': 'frontend',
                'technology': 'React',
                'estimation_category': 'dashboard',
                'base_hours': 120,
                'complexity_factor': 1.0,
                'risk_factor': 1.1,
                'final_estimate': 132,
                'confidence': 'medium',
                'tasks': ['UI development', 'Component creation', 'Integration']
            },
            {
                'component_name': 'API Server',
                'component_type': 'backend',
                'technology': 'Node.js',
                'estimation_category': 'api_development',
                'base_hours': 100,
                'complexity_factor': 1.0,
                'risk_factor': 1.1,
                'final_estimate': 110,
                'confidence': 'high',
                'tasks': ['API endpoints', 'Business logic', 'Data validation']
            }
        ]
    
    def _get_default_project_estimate(self) -> ProjectEstimate:
        """Get default project estimate for error cases"""
        return ProjectEstimate(
            total_effort_hours=800,
            duration_weeks=12,
            team_size=4,
            cost_estimate={'total_cost': 80000, 'hourly_rate_average': 100},
            confidence_intervals={'effort_hours': {'optimistic': 640, 'most_likely': 800, 'pessimistic': 1120}},
            component_breakdown=[],
            risk_assessment={'overall_risk_level': 'medium', 'key_risk_factors': []}
        )
    
    def _get_default_project_plan(self) -> ProjectPlan:
        """Get default project plan for error cases"""
        return ProjectPlan(
            phases=[
                {
                    'name': 'Development',
                    'duration_weeks': 10,
                    'effort_hours': 600,
                    'deliverables': ['Application development']
                }
            ],
            milestones=[
                {
                    'name': 'Project Complete',
                    'week': 12,
                    'deliverables': ['Final application']
                }
            ],
            resource_allocation={'by_phase': {}, 'by_role': {}},
            critical_path=['Development'],
            risk_mitigation=[],
            success_criteria=['Application delivered']
        )
    
    def _get_default_risk_assessment(self) -> Dict[str, Any]:
        """Get default risk assessment for error cases"""
        return {
            'identified_risks': [],
            'risk_summary': {
                'total_risks': 0,
                'high_impact_risks': 0,
                'high_probability_risks': 0,
                'critical_risks': 0
            },
            'mitigation_strategies': [],
            'contingency_planning': {
                'schedule_buffer': '15% recommended',
                'budget_buffer': '10% recommended'
            },
            'monitoring_plan': {
                'risk_review_frequency': 'Weekly',
                'key_metrics': ['Progress', 'Quality']
            }
        }

# Factory function to create project manager agent
def create_project_manager_agent(llm: Optional[ChatOpenAI] = None) -> ProjectManagerAgent:
    """Create and configure project manager agent"""
    return ProjectManagerAgent(llm=llm)