"""
Project estimation and planning tools for the Project Manager Agent
"""
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import math

logger = logging.getLogger(__name__)

class ComplexityLevel(Enum):
    """Project complexity levels"""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class RiskLevel(Enum):
    """Risk levels for estimation"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"

@dataclass
class ComponentEstimate:
    """Estimate for a single component"""
    name: str
    description: str
    base_hours: float
    complexity_multiplier: float
    risk_multiplier: float
    final_hours: float
    confidence_level: str  # "low", "medium", "high"
    dependencies: List[str]

@dataclass
class ProjectPhase:
    """Project phase with timeline and resources"""
    name: str
    description: str
    duration_weeks: float
    effort_hours: float
    team_size: int
    key_deliverables: List[str]
    dependencies: List[str]
    risk_factors: List[str]

class HistoricalDataLookup:
    """Tool for looking up historical effort data for similar components"""
    
    def __init__(self):
        self.historical_data = self._initialize_historical_data()
    
    def _initialize_historical_data(self) -> Dict[str, Dict[str, Any]]:
        """Initialize historical effort data"""
        return {
            "authentication": {
                "base_hours": 80,
                "range": (60, 120),
                "complexity_factors": {
                    "simple": 0.8,  # Basic login/logout
                    "moderate": 1.0,  # OAuth, role-based
                    "complex": 1.5,  # Multi-factor, SSO
                    "very_complex": 2.0  # Advanced security, biometrics
                },
                "typical_tasks": [
                    "User registration and login",
                    "Password reset functionality",
                    "Session management",
                    "Role-based access control"
                ]
            },
            "user_management": {
                "base_hours": 100,
                "range": (80, 150),
                "complexity_factors": {
                    "simple": 0.8,
                    "moderate": 1.0,
                    "complex": 1.4,
                    "very_complex": 1.8
                },
                "typical_tasks": [
                    "User profile management",
                    "User roles and permissions",
                    "User search and filtering",
                    "Bulk user operations"
                ]
            },
            "dashboard": {
                "base_hours": 120,
                "range": (90, 180),
                "complexity_factors": {
                    "simple": 0.7,
                    "moderate": 1.0,
                    "complex": 1.6,
                    "very_complex": 2.2
                },
                "typical_tasks": [
                    "Data visualization components",
                    "Interactive charts and graphs",
                    "Real-time data updates",
                    "Customizable widgets"
                ]
            },
            "reporting": {
                "base_hours": 90,
                "range": (70, 140),
                "complexity_factors": {
                    "simple": 0.8,
                    "moderate": 1.0,
                    "complex": 1.5,
                    "very_complex": 2.0
                },
                "typical_tasks": [
                    "Report generation",
                    "Export functionality",
                    "Scheduled reports",
                    "Custom report builder"
                ]
            },
            "api_development": {
                "base_hours": 60,
                "range": (40, 100),
                "complexity_factors": {
                    "simple": 0.7,
                    "moderate": 1.0,
                    "complex": 1.4,
                    "very_complex": 1.8
                },
                "typical_tasks": [
                    "REST API endpoints",
                    "Request/response validation",
                    "API documentation",
                    "Rate limiting and security"
                ]
            },
            "database_design": {
                "base_hours": 80,
                "range": (60, 120),
                "complexity_factors": {
                    "simple": 0.8,
                    "moderate": 1.0,
                    "complex": 1.5,
                    "very_complex": 2.0
                },
                "typical_tasks": [
                    "Database schema design",
                    "Data migration scripts",
                    "Indexing and optimization",
                    "Backup and recovery procedures"
                ]
            },
            "integration": {
                "base_hours": 100,
                "range": (70, 150),
                "complexity_factors": {
                    "simple": 0.8,
                    "moderate": 1.0,
                    "complex": 1.6,
                    "very_complex": 2.2
                },
                "typical_tasks": [
                    "Third-party API integration",
                    "Data synchronization",
                    "Error handling and retry logic",
                    "Integration testing"
                ]
            },
            "testing": {
                "base_hours": 40,
                "range": (30, 80),
                "complexity_factors": {
                    "simple": 0.7,
                    "moderate": 1.0,
                    "complex": 1.4,
                    "very_complex": 1.8
                },
                "typical_tasks": [
                    "Unit test development",
                    "Integration testing",
                    "End-to-end testing",
                    "Performance testing"
                ]
            },
            "deployment": {
                "base_hours": 60,
                "range": (40, 100),
                "complexity_factors": {
                    "simple": 0.8,
                    "moderate": 1.0,
                    "complex": 1.5,
                    "very_complex": 2.0
                },
                "typical_tasks": [
                    "CI/CD pipeline setup",
                    "Environment configuration",
                    "Monitoring and logging",
                    "Security hardening"
                ]
            },
            "documentation": {
                "base_hours": 30,
                "range": (20, 50),
                "complexity_factors": {
                    "simple": 0.8,
                    "moderate": 1.0,
                    "complex": 1.3,
                    "very_complex": 1.6
                },
                "typical_tasks": [
                    "Technical documentation",
                    "User manuals",
                    "API documentation",
                    "Deployment guides"
                ]
            }
        }
    
    def get_component_estimate(self, component_name: str, complexity: str = "moderate") -> Dict[str, Any]:
        """
        Get historical estimate for a component
        
        Args:
            component_name: Name of the component
            complexity: Complexity level
            
        Returns:
            Historical estimate data
        """
        component_key = component_name.lower().replace(" ", "_")
        
        if component_key in self.historical_data:
            data = self.historical_data[component_key]
            base_hours = data["base_hours"]
            complexity_multiplier = data["complexity_factors"].get(complexity, 1.0)
            
            return {
                "component": component_name,
                "base_hours": base_hours,
                "complexity_multiplier": complexity_multiplier,
                "estimated_hours": base_hours * complexity_multiplier,
                "range": data["range"],
                "typical_tasks": data["typical_tasks"]
            }
        else:
            # Return generic estimate for unknown components
            return {
                "component": component_name,
                "base_hours": 80,
                "complexity_multiplier": 1.0,
                "estimated_hours": 80,
                "range": (60, 120),
                "typical_tasks": [f"Development of {component_name}"]
            }

class EstimationModel:
    """Estimation model using various techniques (COCOMO, Function Points, etc.)"""
    
    def __init__(self):
        self.risk_multipliers = {
            RiskLevel.LOW: 1.1,
            RiskLevel.MEDIUM: 1.3,
            RiskLevel.HIGH: 1.6,
            RiskLevel.VERY_HIGH: 2.0
        }
        
        self.team_productivity_factors = {
            1: 1.0,  # Single developer
            2: 1.8,  # Small team
            3: 2.4,  # Small team
            4: 3.0,  # Medium team
            5: 3.5,  # Medium team
            6: 4.0,  # Large team
            7: 4.2,  # Large team (diminishing returns)
            8: 4.4   # Large team (communication overhead)
        }
    
    def calculate_project_estimate(self, 
                                 components: List[Dict[str, Any]], 
                                 project_factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate comprehensive project estimate
        
        Args:
            components: List of project components with estimates
            project_factors: Project-level factors affecting estimation
            
        Returns:
            Comprehensive project estimate
        """
        try:
            # Extract project factors
            team_size = project_factors.get('team_size', 3)
            overall_complexity = project_factors.get('complexity', 'moderate')
            risk_level = RiskLevel(project_factors.get('risk_level', 'medium'))
            timeline_pressure = project_factors.get('timeline_pressure', 'normal')  # relaxed, normal, tight
            team_experience = project_factors.get('team_experience', 'medium')  # low, medium, high
            
            # Calculate base effort from components
            total_base_hours = 0
            component_estimates = []
            
            for component in components:
                comp_estimate = self._estimate_component(component, overall_complexity)
                component_estimates.append(comp_estimate)
                total_base_hours += comp_estimate.final_hours
            
            # Apply project-level multipliers
            risk_multiplier = self.risk_multipliers[risk_level]
            
            # Team experience multiplier
            experience_multipliers = {
                'low': 1.4,
                'medium': 1.0,
                'high': 0.8
            }
            experience_multiplier = experience_multipliers.get(team_experience, 1.0)
            
            # Timeline pressure multiplier
            timeline_multipliers = {
                'relaxed': 0.9,
                'normal': 1.0,
                'tight': 1.3
            }
            timeline_multiplier = timeline_multipliers.get(timeline_pressure, 1.0)
            
            # Calculate adjusted effort
            adjusted_hours = total_base_hours * risk_multiplier * experience_multiplier * timeline_multiplier
            
            # Calculate duration based on team size
            productivity_factor = self.team_productivity_factors.get(team_size, 4.0)
            duration_weeks = adjusted_hours / (productivity_factor * 40)  # 40 hours per week per effective developer
            
            # Add buffer for project management, meetings, etc.
            management_overhead = 0.15  # 15% overhead
            total_effort_hours = adjusted_hours * (1 + management_overhead)
            
            # Calculate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(total_effort_hours, duration_weeks)
            
            return {
                'total_effort_hours': total_effort_hours,
                'duration_weeks': duration_weeks,
                'team_size': team_size,
                'component_estimates': component_estimates,
                'multipliers': {
                    'risk': risk_multiplier,
                    'experience': experience_multiplier,
                    'timeline': timeline_multiplier,
                    'management_overhead': management_overhead
                },
                'confidence_intervals': confidence_intervals,
                'cost_estimate': self._calculate_cost_estimate(total_effort_hours, team_size),
                'key_assumptions': self._generate_assumptions(project_factors)
            }
            
        except Exception as e:
            logger.error(f"Project estimation failed: {e}")
            return self._get_default_estimate()
    
    def _estimate_component(self, component: Dict[str, Any], overall_complexity: str) -> ComponentEstimate:
        """Estimate effort for a single component"""
        name = component.get('name', 'Unknown Component')
        description = component.get('description', '')
        base_hours = component.get('base_hours', 80)
        
        # Complexity multiplier
        complexity_multipliers = {
            'simple': 0.8,
            'moderate': 1.0,
            'complex': 1.4,
            'very_complex': 1.8
        }
        complexity_multiplier = complexity_multipliers.get(overall_complexity, 1.0)
        
        # Risk multiplier (component-specific)
        component_risk = component.get('risk_level', 'medium')
        risk_multipliers = {
            'low': 1.0,
            'medium': 1.2,
            'high': 1.5,
            'very_high': 1.8
        }
        risk_multiplier = risk_multipliers.get(component_risk, 1.2)
        
        final_hours = base_hours * complexity_multiplier * risk_multiplier
        
        # Determine confidence level
        if component_risk in ['low'] and overall_complexity in ['simple', 'moderate']:
            confidence = 'high'
        elif component_risk in ['medium'] and overall_complexity in ['moderate', 'complex']:
            confidence = 'medium'
        else:
            confidence = 'low'
        
        return ComponentEstimate(
            name=name,
            description=description,
            base_hours=base_hours,
            complexity_multiplier=complexity_multiplier,
            risk_multiplier=risk_multiplier,
            final_hours=final_hours,
            confidence_level=confidence,
            dependencies=component.get('dependencies', [])
        )
    
    def _calculate_confidence_intervals(self, effort_hours: float, duration_weeks: float) -> Dict[str, Any]:
        """Calculate confidence intervals for estimates"""
        # Standard estimation uncertainty ranges
        effort_ranges = {
            'optimistic': effort_hours * 0.8,  # 20% under
            'most_likely': effort_hours,
            'pessimistic': effort_hours * 1.4   # 40% over
        }
        
        duration_ranges = {
            'optimistic': duration_weeks * 0.85,  # 15% under
            'most_likely': duration_weeks,
            'pessimistic': duration_weeks * 1.3   # 30% over
        }
        
        return {
            'effort_hours': effort_ranges,
            'duration_weeks': duration_ranges
        }
    
    def _calculate_cost_estimate(self, effort_hours: float, team_size: int) -> Dict[str, Any]:
        """Calculate cost estimates based on effort and team composition"""
        # Standard hourly rates (these would typically come from configuration)
        hourly_rates = {
            'senior_developer': 120,
            'mid_developer': 90,
            'junior_developer': 65,
            'project_manager': 130,
            'architect': 140,
            'qa_engineer': 80
        }
        
        # Typical team composition based on team size
        if team_size <= 2:
            team_composition = {
                'senior_developer': 0.6,
                'mid_developer': 0.4
            }
        elif team_size <= 4:
            team_composition = {
                'senior_developer': 0.3,
                'mid_developer': 0.5,
                'junior_developer': 0.2
            }
        else:
            team_composition = {
                'senior_developer': 0.2,
                'mid_developer': 0.4,
                'junior_developer': 0.3,
                'project_manager': 0.1
            }
        
        # Calculate weighted average rate
        weighted_rate = sum(hourly_rates[role] * percentage 
                          for role, percentage in team_composition.items())
        
        total_cost = effort_hours * weighted_rate
        
        return {
            'total_cost': total_cost,
            'hourly_rate_average': weighted_rate,
            'team_composition': team_composition,
            'cost_ranges': {
                'optimistic': total_cost * 0.8,
                'most_likely': total_cost,
                'pessimistic': total_cost * 1.4
            }
        }
    
    def _generate_assumptions(self, project_factors: Dict[str, Any]) -> List[str]:
        """Generate key assumptions for the estimate"""
        assumptions = [
            "Estimates based on historical data from similar projects",
            "Team has access to necessary tools and environments",
            "Requirements are stable with minimal scope changes",
            "Standard working hours (40 hours/week per team member)",
            "No major technical blockers or external dependencies"
        ]
        
        # Add specific assumptions based on project factors
        if project_factors.get('timeline_pressure') == 'tight':
            assumptions.append("Tight timeline may require overtime or additional resources")
        
        if project_factors.get('team_experience') == 'low':
            assumptions.append("Additional time allocated for team learning and ramp-up")
        
        if project_factors.get('risk_level') == 'high':
            assumptions.append("High-risk factors may require additional contingency planning")
        
        return assumptions
    
    def _get_default_estimate(self) -> Dict[str, Any]:
        """Get default estimate for error cases"""
        return {
            'total_effort_hours': 800,
            'duration_weeks': 12,
            'team_size': 3,
            'component_estimates': [],
            'multipliers': {
                'risk': 1.3,
                'experience': 1.0,
                'timeline': 1.0,
                'management_overhead': 0.15
            },
            'confidence_intervals': {
                'effort_hours': {'optimistic': 640, 'most_likely': 800, 'pessimistic': 1120},
                'duration_weeks': {'optimistic': 10, 'most_likely': 12, 'pessimistic': 16}
            },
            'cost_estimate': {
                'total_cost': 80000,
                'hourly_rate_average': 100,
                'cost_ranges': {'optimistic': 64000, 'most_likely': 80000, 'pessimistic': 112000}
            },
            'key_assumptions': ['Default estimate due to calculation error']
        }

class ProjectPlanGenerator:
    """Generate detailed project plans with phases and milestones"""
    
    def generate_project_plan(self, 
                            estimate: Dict[str, Any], 
                            requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a detailed project plan based on estimates and requirements
        
        Args:
            estimate: Project estimate from EstimationModel
            requirements: Project requirements and constraints
            
        Returns:
            Detailed project plan with phases and milestones
        """
        try:
            total_duration = estimate['duration_weeks']
            total_effort = estimate['total_effort_hours']
            team_size = estimate['team_size']
            
            # Define standard project phases
            phases = self._generate_project_phases(total_duration, total_effort, requirements)
            
            # Generate milestones
            milestones = self._generate_milestones(phases)
            
            # Calculate resource allocation
            resource_allocation = self._calculate_resource_allocation(phases, team_size)
            
            # Identify critical path and dependencies
            critical_path = self._identify_critical_path(phases)
            
            # Generate risk mitigation strategies
            risk_mitigation = self._generate_risk_mitigation(estimate, requirements)
            
            return {
                'project_phases': phases,
                'milestones': milestones,
                'resource_allocation': resource_allocation,
                'critical_path': critical_path,
                'risk_mitigation': risk_mitigation,
                'total_duration_weeks': total_duration,
                'total_effort_hours': total_effort,
                'success_criteria': self._define_success_criteria(requirements)
            }
            
        except Exception as e:
            logger.error(f"Project plan generation failed: {e}")
            return self._get_default_project_plan()
    
    def _generate_project_phases(self, 
                               total_duration: float, 
                               total_effort: float, 
                               requirements: Dict[str, Any]) -> List[ProjectPhase]:
        """Generate project phases based on duration and requirements"""
        phases = []
        
        # Phase 1: Discovery & Planning (10% of duration, 8% of effort)
        discovery_duration = total_duration * 0.10
        discovery_effort = total_effort * 0.08
        phases.append(ProjectPhase(
            name="Discovery & Planning",
            description="Requirements analysis, technical planning, and project setup",
            duration_weeks=discovery_duration,
            effort_hours=discovery_effort,
            team_size=2,
            key_deliverables=[
                "Detailed requirements specification",
                "Technical architecture document",
                "Project plan and timeline",
                "Development environment setup"
            ],
            dependencies=[],
            risk_factors=["Incomplete requirements", "Technical unknowns"]
        ))
        
        # Phase 2: Core Development (60% of duration, 65% of effort)
        core_duration = total_duration * 0.60
        core_effort = total_effort * 0.65
        phases.append(ProjectPhase(
            name="Core Development",
            description="Implementation of core functionality and features",
            duration_weeks=core_duration,
            effort_hours=core_effort,
            team_size=max(2, int(total_effort / (core_duration * 40))) if core_duration > 0 else 2,
            key_deliverables=[
                "Core application functionality",
                "Database implementation",
                "API development",
                "User interface components"
            ],
            dependencies=["Discovery & Planning"],
            risk_factors=["Technical complexity", "Integration challenges", "Scope creep"]
        ))
        
        # Phase 3: Integration & Testing (20% of duration, 20% of effort)
        integration_duration = total_duration * 0.20
        integration_effort = total_effort * 0.20
        phases.append(ProjectPhase(
            name="Integration & Testing",
            description="System integration, testing, and bug fixes",
            duration_weeks=integration_duration,
            effort_hours=integration_effort,
            team_size=max(2, team_size - 1),
            key_deliverables=[
                "Integrated system testing",
                "Performance optimization",
                "Security testing",
                "Bug fixes and refinements"
            ],
            dependencies=["Core Development"],
            risk_factors=["Integration issues", "Performance bottlenecks", "Security vulnerabilities"]
        ))
        
        # Phase 4: Deployment & Launch (10% of duration, 7% of effort)
        deployment_duration = total_duration * 0.10
        deployment_effort = total_effort * 0.07
        phases.append(ProjectPhase(
            name="Deployment & Launch",
            description="Production deployment, monitoring setup, and go-live support",
            duration_weeks=deployment_duration,
            effort_hours=deployment_effort,
            team_size=2,
            key_deliverables=[
                "Production deployment",
                "Monitoring and alerting setup",
                "User training and documentation",
                "Go-live support"
            ],
            dependencies=["Integration & Testing"],
            risk_factors=["Deployment issues", "Production environment problems", "User adoption"]
        ))
        
        return phases
    
    def _generate_milestones(self, phases: List[ProjectPhase]) -> List[Dict[str, Any]]:
        """Generate project milestones based on phases"""
        milestones = []
        cumulative_weeks = 0
        
        for phase in phases:
            cumulative_weeks += phase.duration_weeks
            
            milestone = {
                'name': f"{phase.name} Complete",
                'week': int(cumulative_weeks),
                'deliverables': phase.key_deliverables,
                'success_criteria': [
                    f"All {phase.name.lower()} deliverables completed",
                    "Quality gates passed",
                    "Stakeholder approval received"
                ]
            }
            milestones.append(milestone)
        
        return milestones
    
    def _calculate_resource_allocation(self, 
                                    phases: List[ProjectPhase], 
                                    total_team_size: int) -> Dict[str, Any]:
        """Calculate resource allocation across phases"""
        allocation = {
            'by_phase': {},
            'by_role': {},
            'peak_team_size': max(phase.team_size for phase in phases),
            'average_team_size': sum(phase.team_size for phase in phases) / len(phases)
        }
        
        for phase in phases:
            allocation['by_phase'][phase.name] = {
                'team_size': phase.team_size,
                'effort_hours': phase.effort_hours,
                'duration_weeks': phase.duration_weeks
            }
        
        # Estimate role distribution
        allocation['by_role'] = {
            'Senior Developer': 0.3,
            'Mid-level Developer': 0.4,
            'Junior Developer': 0.2,
            'Project Manager': 0.1
        }
        
        return allocation
    
    def _identify_critical_path(self, phases: List[ProjectPhase]) -> List[str]:
        """Identify critical path through project phases"""
        # For this implementation, assume sequential phases form the critical path
        return [phase.name for phase in phases]
    
    def _generate_risk_mitigation(self, 
                                estimate: Dict[str, Any], 
                                requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate risk mitigation strategies"""
        risks = [
            {
                'risk': 'Schedule Delays',
                'probability': 'medium',
                'impact': 'high',
                'mitigation': [
                    'Regular progress monitoring and reporting',
                    'Maintain 15% schedule buffer',
                    'Identify and address blockers early',
                    'Consider parallel development where possible'
                ]
            },
            {
                'risk': 'Scope Creep',
                'probability': 'high',
                'impact': 'medium',
                'mitigation': [
                    'Formal change control process',
                    'Regular stakeholder communication',
                    'Clear requirements documentation',
                    'Impact assessment for all changes'
                ]
            },
            {
                'risk': 'Technical Challenges',
                'probability': 'medium',
                'impact': 'high',
                'mitigation': [
                    'Technical proof of concepts early',
                    'Regular architecture reviews',
                    'Access to senior technical expertise',
                    'Fallback solutions for high-risk components'
                ]
            },
            {
                'risk': 'Resource Availability',
                'probability': 'medium',
                'impact': 'medium',
                'mitigation': [
                    'Cross-training team members',
                    'Maintain bench of available resources',
                    'Clear resource allocation planning',
                    'Early identification of resource conflicts'
                ]
            }
        ]
        
        return risks
    
    def _define_success_criteria(self, requirements: Dict[str, Any]) -> List[str]:
        """Define project success criteria"""
        return [
            "All functional requirements implemented and tested",
            "System performance meets specified requirements",
            "Security requirements satisfied",
            "User acceptance testing completed successfully",
            "Production deployment completed without major issues",
            "Project delivered within approved budget and timeline",
            "Stakeholder satisfaction achieved"
        ]
    
    def _get_default_project_plan(self) -> Dict[str, Any]:
        """Get default project plan for error cases"""
        return {
            'project_phases': [],
            'milestones': [],
            'resource_allocation': {},
            'critical_path': [],
            'risk_mitigation': [],
            'total_duration_weeks': 12,
            'total_effort_hours': 800,
            'success_criteria': ['Default plan due to generation error']
        }

class EstimationEngine:
    """Main estimation engine that combines all estimation tools"""
    
    def __init__(self):
        self.historical_lookup = HistoricalDataLookup()
        self.estimation_model = EstimationModel()
        self.plan_generator = ProjectPlanGenerator()
    
    def estimate_features(self, features: List[str]) -> List[Dict[str, Any]]:
        """
        Estimate effort for a list of features
        
        Args:
            features: List of feature names
            
        Returns:
            List of feature estimates with effort hours
        """
        try:
            estimates = []
            
            for feature in features:
                # Map feature names to component types
                component_type = self._map_feature_to_component(feature)
                
                # Get estimate from historical data
                estimate = self.historical_lookup.get_component_estimate(
                    component_type, 
                    ComplexityLevel.MODERATE
                )
                
                estimates.append({
                    'feature': feature,
                    'component_type': component_type,
                    'effort_hours': estimate.final_hours,
                    'complexity': estimate.complexity_multiplier,
                    'confidence': estimate.confidence_level,
                    'description': estimate.description
                })
            
            return estimates
            
        except Exception as e:
            logger.error(f"Feature estimation failed: {e}")
            # Return default estimates
            return [
                {
                    'feature': feature,
                    'component_type': 'general',
                    'effort_hours': 80,
                    'complexity': 1.0,
                    'confidence': 'medium',
                    'description': f'Default estimate for {feature}'
                }
                for feature in features
            ]
    
    def _map_feature_to_component(self, feature: str) -> str:
        """Map feature name to component type for historical lookup"""
        feature_lower = feature.lower()
        
        if any(keyword in feature_lower for keyword in ['auth', 'login', 'signup', 'register']):
            return 'authentication'
        elif any(keyword in feature_lower for keyword in ['user', 'profile', 'account']):
            return 'user_management'
        elif any(keyword in feature_lower for keyword in ['dashboard', 'overview', 'summary']):
            return 'dashboard'
        elif any(keyword in feature_lower for keyword in ['report', 'analytics', 'chart']):
            return 'reporting'
        elif any(keyword in feature_lower for keyword in ['api', 'endpoint', 'service']):
            return 'api_development'
        elif any(keyword in feature_lower for keyword in ['database', 'data', 'storage']):
            return 'database_design'
        elif any(keyword in feature_lower for keyword in ['payment', 'checkout', 'billing']):
            return 'payment_integration'
        elif any(keyword in feature_lower for keyword in ['inventory', 'product', 'catalog']):
            return 'inventory_management'
        else:
            return 'general_feature'
    
    def estimate_project(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Estimate entire project based on requirements
        
        Args:
            requirements: Project requirements dictionary
            
        Returns:
            Complete project estimate
        """
        try:
            # Extract components from requirements
            components = requirements.get('components', [])
            
            # Calculate project estimate
            estimate = self.estimation_model.calculate_project_estimate(
                components, requirements
            )
            
            # Generate project plan
            plan = self.plan_generator.generate_project_plan(estimate, requirements)
            
            # Combine results
            return {
                'estimate': estimate,
                'plan': plan,
                'summary': {
                    'total_effort_hours': estimate['total_effort_hours'],
                    'duration_weeks': estimate['duration_weeks'],
                    'team_size': estimate['team_size'],
                    'estimated_cost': estimate.get('cost_estimate', {}).get('total_cost', 0),
                    'confidence_level': 'medium'
                }
            }
            
        except Exception as e:
            logger.error(f"Project estimation failed: {e}")
            return {
                'estimate': self.estimation_model._get_default_estimate(),
                'plan': self.plan_generator._get_default_project_plan(),
                'summary': {
                    'total_effort_hours': 800,
                    'duration_weeks': 12,
                    'team_size': 3,
                    'estimated_cost': 80000,
                    'confidence_level': 'low'
                }
            }

# Factory function to create estimation tools
def create_estimation_tools() -> Dict[str, Any]:
    """Create and configure estimation tools"""
    historical_lookup = HistoricalDataLookup()
    estimation_model = EstimationModel()
    plan_generator = ProjectPlanGenerator()
    
    return {
        'historical_data_lookup': historical_lookup,
        'estimation_model': estimation_model,
        'project_plan_generator': plan_generator,
        'get_component_estimate': historical_lookup.get_component_estimate,
        'calculate_project_estimate': estimation_model.calculate_project_estimate,
        'generate_project_plan': plan_generator.generate_project_plan
    }