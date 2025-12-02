"""
CTO Agent for technical validation, security auditing, and architecture governance
Provides technical governance with ability to reject and loop back for optimization
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState
from ..tools.security_tools import create_security_tools

logger = logging.getLogger(__name__)

class ValidationResult(Enum):
    """CTO validation results"""
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class CriticalityLevel(Enum):
    """Issue criticality levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class TechnicalIssue:
    """Represents a technical issue identified by the CTO"""
    category: str
    title: str
    description: str
    criticality: CriticalityLevel
    impact: str
    recommendation: str
    must_fix: bool

@dataclass
class CTOValidation:
    """CTO validation results"""
    validation_result: ValidationResult
    overall_score: int  # 0-100
    technical_issues: List[TechnicalIssue]
    security_assessment: Dict[str, Any]
    architecture_review: Dict[str, Any]
    tech_debt_analysis: Dict[str, Any]
    recommendations: List[str]
    approval_conditions: List[str]
    rejection_reasons: List[str]

class CTOAgent:
    """
    CTO Agent that provides technical governance and validation
    
    Responsibilities:
    - Validate technical architecture against best practices
    - Conduct comprehensive security audits
    - Analyze technical debt and maintainability risks
    - Review technology stack choices and compatibility
    - Assess scalability and performance implications
    - Validate cost-effectiveness of technical decisions
    - Provide approval/rejection with detailed feedback
    - Ensure compliance with enterprise standards
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Initialize security tools
        self.security_tools = create_security_tools()
        self.security_auditor = self.security_tools['security_auditor']
        self.tech_debt_analyzer = self.security_tools['tech_debt_analyzer']
        
        # System prompt for the CTO
        self.system_prompt = """You are the Chief Technology Officer (CTO). Your role is to provide final technical validation of the proposed solution. You have the authority to approve, conditionally approve, or reject the technical architecture based on security, scalability, maintainability, and business alignment.

Your responsibilities:
1. Validate technical architecture against enterprise standards and best practices
2. Conduct comprehensive security audits and risk assessments
3. Analyze technical debt implications and long-term maintainability
4. Review technology stack choices for compatibility and strategic alignment
5. Assess scalability, performance, and operational considerations
6. Evaluate cost-effectiveness and ROI of technical decisions
7. Ensure compliance with regulatory and industry standards
8. Provide clear approval/rejection decisions with detailed rationale

Your authority:
- APPROVE: Architecture meets all technical and business requirements
- APPROVE WITH CONDITIONS: Architecture is acceptable with specific modifications
- NEEDS REVISION: Architecture has issues that require rework but is salvageable
- REJECT: Architecture has fundamental flaws requiring complete redesign

Focus on:
- Security and compliance requirements
- Long-term maintainability and technical debt
- Scalability and performance implications
- Technology stack strategic alignment
- Cost-effectiveness and resource optimization
- Risk mitigation and operational excellence

Be thorough, decisive, and provide clear technical rationale for all decisions."""
    
    def validate_technical_solution(self, state: WorkflowState) -> WorkflowState:
        """
        Perform comprehensive technical validation of the proposed solution
        
        Args:
            state: Current workflow state with complete technical solution
            
        Returns:
            Updated state with CTO validation results
        """
        try:
            logger.info("CTO Agent: Starting technical validation")
            
            if not state.architecture_design:
                raise ValueError("No architecture design available for CTO validation")
            
            if not state.project_plan:
                raise ValueError("No project plan available for CTO validation")
            
            # Step 1: Conduct security audit
            security_assessment = self._conduct_security_audit(state.architecture_design)
            
            # Step 2: Perform architecture review
            architecture_review = self._perform_architecture_review(state.architecture_design, state.extracted_data)
            
            # Step 3: Analyze technical debt and maintainability
            tech_debt_analysis = self._analyze_technical_debt(state.architecture_design)
            
            # Step 4: Validate technology stack choices
            tech_stack_validation = self._validate_technology_stack(state.architecture_design)
            
            # Step 5: Review project plan and estimates
            project_validation = self._validate_project_plan(state.project_plan, state.project_estimate)
            
            # Step 6: Assess business alignment and ROI
            business_alignment = self._assess_business_alignment(state.architecture_design, state.extracted_data, state.project_estimate)
            
            # Step 7: Identify technical issues and risks
            technical_issues = self._identify_technical_issues(
                security_assessment, 
                architecture_review, 
                tech_debt_analysis,
                tech_stack_validation,
                project_validation
            )
            
            # Step 8: Make validation decision
            validation_decision = self._make_validation_decision(
                technical_issues, 
                security_assessment, 
                architecture_review,
                business_alignment
            )
            
            # Step 9: Generate comprehensive validation report
            cto_validation = CTOValidation(
                validation_result=validation_decision['result'],
                overall_score=validation_decision['score'],
                technical_issues=technical_issues,
                security_assessment=security_assessment,
                architecture_review=architecture_review,
                tech_debt_analysis=tech_debt_analysis,
                recommendations=validation_decision['recommendations'],
                approval_conditions=validation_decision.get('conditions', []),
                rejection_reasons=validation_decision.get('rejection_reasons', [])
            )
            
            # Update state (convert dataclass to dict for Pydantic compatibility)
            state.cto_validation = asdict(cto_validation)
            state.current_step = "cto_validation_complete"
            state.last_agent_executed = "cto"
            
            logger.info(f"CTO Agent: Validation complete - {validation_decision['result'].value} (Score: {validation_decision['score']})")
            return state
            
        except Exception as e:
            logger.error(f"CTO Agent failed: {e}")
            state.errors.append(f"CTO Agent error: {str(e)}")
            return state
    
    def _conduct_security_audit(self, architecture_design: Any) -> Dict[str, Any]:
        """
        Conduct comprehensive security audit of the architecture
        
        Args:
            architecture_design: Architecture design to audit
            
        Returns:
            Security audit results
        """
        try:
            # Prepare architecture specification for security audit
            arch_spec = {
                'components': getattr(architecture_design, 'system_components', []),
                'technologies': self._extract_technology_info(architecture_design),
                'data_handling': self._extract_data_handling_info(architecture_design),
                'authentication': self._extract_auth_info(architecture_design),
                'data_protection': self._extract_data_protection_info(architecture_design),
                'input_validation': self._extract_input_validation_info(architecture_design),
                'infrastructure_security': self._extract_infrastructure_security_info(architecture_design),
                'security_monitoring': self._extract_security_monitoring_info(architecture_design)
            }
            
            # Perform security audit using security tools
            audit_results = self.security_auditor.audit_architecture(arch_spec)
            
            # Enhance audit results with CTO-level analysis
            enhanced_results = self._enhance_security_audit(audit_results, architecture_design)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            return self._get_default_security_assessment()
    
    def _extract_technology_info(self, architecture_design: Any) -> Dict[str, Any]:
        """Extract technology information for security audit"""
        
        tech_stack = getattr(architecture_design, 'technology_stack', {})
        technologies = tech_stack.get('technologies', {})
        
        tech_info = {}
        for category, tech in technologies.items():
            if hasattr(tech, 'name'):
                tech_info[category] = tech.name
            else:
                tech_info[category] = str(tech)
        
        return tech_info
    
    def _extract_data_handling_info(self, architecture_design: Any) -> Dict[str, Any]:
        """Extract data handling information"""
        
        data_architecture = getattr(architecture_design, 'data_architecture', {})
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        
        return {
            'primary_database': data_architecture.get('primary_database', {}),
            'data_flow': data_architecture.get('data_flow', {}),
            'data_security': data_architecture.get('data_security', {}),
            'encryption_at_rest': security_considerations.get('data_protection', {}).get('encryption_at_rest'),
            'encryption_in_transit': security_considerations.get('data_protection', {}).get('encryption_in_transit')
        }
    
    def _extract_auth_info(self, architecture_design: Any) -> Dict[str, Any]:
        """Extract authentication information"""
        
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        auth_info = security_considerations.get('authentication', {})
        
        return {
            'mfa_enabled': 'mfa' in str(auth_info).lower() or 'multi-factor' in str(auth_info).lower(),
            'rbac_enabled': 'rbac' in str(auth_info).lower() or 'role-based' in str(auth_info).lower(),
            'authentication_method': auth_info.get('method', 'Unknown'),
            'session_management': auth_info.get('session_management', 'Unknown')
        }
    
    def _extract_data_protection_info(self, architecture_design: Any) -> Dict[str, Any]:
        """Extract data protection information"""
        
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        data_protection = security_considerations.get('data_protection', {})
        
        return {
            'encryption_at_rest': 'encryption' in str(data_protection).lower(),
            'encryption_in_transit': 'tls' in str(data_protection).lower() or 'ssl' in str(data_protection).lower(),
            'key_management': 'key management' in str(data_protection).lower(),
            'data_classification': 'classification' in str(data_protection).lower()
        }
    
    def _extract_input_validation_info(self, architecture_design: Any) -> Dict[str, Any]:
        """Extract input validation information"""
        
        # Look for input validation in components and security considerations
        components = getattr(architecture_design, 'system_components', [])
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        
        has_validation = any('validation' in str(comp).lower() for comp in components)
        has_sql_protection = 'sql' in str(security_considerations).lower() or 'injection' in str(security_considerations).lower()
        
        return {
            'sql_injection_prevention': has_sql_protection,
            'input_validation': has_validation,
            'output_encoding': 'encoding' in str(security_considerations).lower()
        }
    
    def _extract_infrastructure_security_info(self, architecture_design: Any) -> Dict[str, Any]:
        """Extract infrastructure security information"""
        
        deployment_strategy = getattr(architecture_design, 'deployment_strategy', {})
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        
        return {
            'network_segmentation': 'vpc' in str(deployment_strategy).lower() or 'network' in str(security_considerations).lower(),
            'firewall': 'firewall' in str(security_considerations).lower() or 'waf' in str(security_considerations).lower(),
            'container_security': 'container' in str(deployment_strategy).lower()
        }
    
    def _extract_security_monitoring_info(self, architecture_design: Any) -> Dict[str, Any]:
        """Extract security monitoring information"""
        
        deployment_strategy = getattr(architecture_design, 'deployment_strategy', {})
        monitoring = deployment_strategy.get('monitoring', {})
        
        return {
            'security_logging': 'security' in str(monitoring).lower() or 'audit' in str(monitoring).lower(),
            'intrusion_detection': 'intrusion' in str(monitoring).lower() or 'ids' in str(monitoring).lower(),
            'vulnerability_scanning': 'vulnerability' in str(monitoring).lower() or 'scan' in str(monitoring).lower()
        }
    
    def _enhance_security_audit(self, audit_results: Dict[str, Any], architecture_design: Any) -> Dict[str, Any]:
        """Enhance security audit results with CTO-level analysis"""
        
        enhanced_results = audit_results.copy()
        
        # Add CTO-specific security concerns
        cto_concerns = []
        
        # Check for enterprise security requirements
        if audit_results['overall_risk_level'].value in ['high', 'critical']:
            cto_concerns.append("High security risk level requires immediate attention")
        
        # Check compliance gaps
        compliance_gaps = audit_results.get('compliance_gaps', {})
        if compliance_gaps:
            cto_concerns.append(f"Compliance gaps identified: {', '.join(compliance_gaps.keys())}")
        
        # Check security score
        security_score = audit_results.get('security_score', 0)
        if security_score < 70:
            cto_concerns.append(f"Security score ({security_score}) below acceptable threshold")
        
        enhanced_results['cto_security_concerns'] = cto_concerns
        enhanced_results['enterprise_readiness'] = self._assess_enterprise_security_readiness(audit_results)
        enhanced_results['security_investment_required'] = self._estimate_security_investment(audit_results)
        
        return enhanced_results
    
    def _assess_enterprise_security_readiness(self, audit_results: Dict[str, Any]) -> str:
        """Assess enterprise security readiness"""
        
        security_score = audit_results.get('security_score', 0)
        critical_findings = audit_results.get('audit_summary', {}).get('critical_findings', 0)
        
        if security_score >= 90 and critical_findings == 0:
            return 'enterprise_ready'
        elif security_score >= 70 and critical_findings <= 1:
            return 'needs_minor_improvements'
        elif security_score >= 50:
            return 'needs_significant_improvements'
        else:
            return 'not_enterprise_ready'
    
    def _estimate_security_investment(self, audit_results: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate additional security investment required"""
        
        findings = audit_results.get('findings', [])
        critical_count = len([f for f in findings if f.risk_level.value == 'critical'])
        high_count = len([f for f in findings if f.risk_level.value == 'high'])
        
        # Estimate effort in hours
        security_effort = (critical_count * 40) + (high_count * 20)
        
        return {
            'additional_effort_hours': security_effort,
            'estimated_cost': security_effort * 150,  # $150/hour for security work
            'timeline_impact_weeks': max(1, security_effort // 40),
            'priority': 'high' if critical_count > 0 else 'medium'
        }
    
    def _perform_architecture_review(self, architecture_design: Any, extracted_data: Any) -> Dict[str, Any]:
        """
        Perform comprehensive architecture review
        
        Args:
            architecture_design: Architecture design to review
            extracted_data: Original requirements for alignment check
            
        Returns:
            Architecture review results
        """
        try:
            # Review architecture against best practices
            architecture_quality = self._assess_architecture_quality(architecture_design)
            
            # Check requirements alignment
            requirements_alignment = self._check_requirements_alignment(architecture_design, extracted_data)
            
            # Evaluate scalability and performance
            scalability_assessment = self._assess_scalability_design(architecture_design)
            
            # Review technology choices
            technology_assessment = self._assess_technology_choices(architecture_design)
            
            # Check operational considerations
            operational_assessment = self._assess_operational_readiness(architecture_design)
            
            architecture_review = {
                'architecture_quality': architecture_quality,
                'requirements_alignment': requirements_alignment,
                'scalability_assessment': scalability_assessment,
                'technology_assessment': technology_assessment,
                'operational_assessment': operational_assessment,
                'overall_architecture_score': self._calculate_architecture_score(
                    architecture_quality, requirements_alignment, scalability_assessment, 
                    technology_assessment, operational_assessment
                ),
                'architecture_recommendations': self._generate_architecture_recommendations(
                    architecture_quality, scalability_assessment, technology_assessment
                )
            }
            
            return architecture_review
            
        except Exception as e:
            logger.error(f"Architecture review failed: {e}")
            return self._get_default_architecture_review()
    
    def _assess_architecture_quality(self, architecture_design: Any) -> Dict[str, Any]:
        """Assess overall architecture quality"""
        
        components = getattr(architecture_design, 'system_components', [])
        pattern = getattr(architecture_design, 'architecture_pattern', {})
        
        quality_metrics = {
            'component_cohesion': 'high' if len(components) <= 8 else 'medium',
            'separation_of_concerns': 'high' if len(set(c.get('type') for c in components)) >= 3 else 'medium',
            'pattern_appropriateness': 'high' if pattern.get('name') else 'medium',
            'design_consistency': 'high',  # Assume good based on structured approach
            'documentation_quality': 'high' if hasattr(architecture_design, 'design_rationale') else 'medium'
        }
        
        # Calculate overall quality score
        quality_scores = {'high': 3, 'medium': 2, 'low': 1}
        total_score = sum(quality_scores.get(score, 2) for score in quality_metrics.values())
        max_score = len(quality_metrics) * 3
        
        return {
            'quality_metrics': quality_metrics,
            'overall_quality': 'high' if total_score >= max_score * 0.8 else 'medium' if total_score >= max_score * 0.6 else 'low',
            'quality_score': int((total_score / max_score) * 100)
        }
    
    def _check_requirements_alignment(self, architecture_design: Any, extracted_data: Any) -> Dict[str, Any]:
        """Check alignment between architecture and requirements"""
        
        if not extracted_data:
            return {'alignment_score': 50, 'issues': ['No requirements data available for alignment check']}
        
        functional_reqs = getattr(extracted_data, 'requirements', {}).get('functional', [])
        technical_specs = getattr(extracted_data, 'technical_specs', {})
        components = getattr(architecture_design, 'system_components', [])
        
        # Check functional requirement coverage
        req_coverage = len(components) / max(len(functional_reqs), 1)
        coverage_score = min(req_coverage * 100, 100)
        
        # Check technical specification alignment
        tech_alignment_issues = []
        if technical_specs.get('performance_requirements') and not getattr(architecture_design, 'scalability_strategy', None):
            tech_alignment_issues.append('Performance requirements not addressed in scalability strategy')
        
        if technical_specs.get('security_requirements') and not getattr(architecture_design, 'security_considerations', None):
            tech_alignment_issues.append('Security requirements not adequately addressed')
        
        alignment_score = coverage_score
        if tech_alignment_issues:
            alignment_score -= len(tech_alignment_issues) * 10
        
        return {
            'alignment_score': max(alignment_score, 0),
            'requirement_coverage': coverage_score,
            'technical_alignment_issues': tech_alignment_issues,
            'alignment_status': 'good' if alignment_score >= 80 else 'needs_improvement' if alignment_score >= 60 else 'poor'
        }
    
    def _assess_scalability_design(self, architecture_design: Any) -> Dict[str, Any]:
        """Assess scalability design and strategy"""
        
        scalability_strategy = getattr(architecture_design, 'scalability_strategy', {})
        deployment_strategy = getattr(architecture_design, 'deployment_strategy', {})
        
        scalability_features = {
            'horizontal_scaling': bool(scalability_strategy.get('horizontal_scaling')),
            'load_balancing': 'load' in str(deployment_strategy).lower(),
            'caching_strategy': bool(scalability_strategy.get('caching_strategy')),
            'database_scaling': bool(scalability_strategy.get('database_scaling')),
            'auto_scaling': 'auto' in str(scalability_strategy).lower()
        }
        
        scalability_score = sum(scalability_features.values()) / len(scalability_features) * 100
        
        return {
            'scalability_features': scalability_features,
            'scalability_score': scalability_score,
            'scalability_readiness': 'excellent' if scalability_score >= 80 else 'good' if scalability_score >= 60 else 'needs_improvement'
        }
    
    def _assess_technology_choices(self, architecture_design: Any) -> Dict[str, Any]:
        """Assess technology stack choices"""
        
        tech_stack = getattr(architecture_design, 'technology_stack', {})
        technologies = tech_stack.get('technologies', {})
        
        # Use tech debt analyzer for technology assessment
        tech_analysis = self.tech_debt_analyzer.analyze_tech_debt({
            'technologies': technologies,
            'architecture_pattern': getattr(architecture_design, 'architecture_pattern', {})
        })
        
        # Add CTO-specific technology concerns
        strategic_alignment = self._assess_strategic_technology_alignment(technologies)
        
        return {
            'tech_debt_analysis': tech_analysis,
            'strategic_alignment': strategic_alignment,
            'technology_maturity': self._assess_technology_maturity(technologies),
            'vendor_risk': tech_analysis.get('vendor_lock_in_risk', 'medium'),
            'technology_recommendation': 'approved' if tech_analysis.get('overall_debt_risk') == 'low' else 'needs_review'
        }
    
    def _assess_strategic_technology_alignment(self, technologies: Dict[str, Any]) -> Dict[str, Any]:
        """Assess strategic alignment of technology choices"""
        
        # This would typically check against enterprise technology standards
        strategic_techs = ['aws', 'azure', 'kubernetes', 'postgresql', 'react', 'nodejs']
        
        aligned_count = 0
        total_count = len(technologies)
        
        for tech in technologies.values():
            tech_name = getattr(tech, 'name', str(tech)).lower()
            if any(strategic_tech in tech_name for strategic_tech in strategic_techs):
                aligned_count += 1
        
        alignment_score = (aligned_count / max(total_count, 1)) * 100
        
        return {
            'alignment_score': alignment_score,
            'aligned_technologies': aligned_count,
            'total_technologies': total_count,
            'strategic_fit': 'excellent' if alignment_score >= 80 else 'good' if alignment_score >= 60 else 'needs_review'
        }
    
    def _assess_technology_maturity(self, technologies: Dict[str, Any]) -> Dict[str, Any]:
        """Assess maturity of selected technologies"""
        
        maturity_assessment = {
            'mature_technologies': 0,
            'stable_technologies': 0,
            'emerging_technologies': 0,
            'total_technologies': len(technologies)
        }
        
        for tech in technologies.values():
            maturity = getattr(tech, 'maturity', 'stable')
            if maturity == 'mature':
                maturity_assessment['mature_technologies'] += 1
            elif maturity == 'stable':
                maturity_assessment['stable_technologies'] += 1
            else:
                maturity_assessment['emerging_technologies'] += 1
        
        # Calculate maturity score
        total = maturity_assessment['total_technologies']
        if total > 0:
            maturity_score = (
                (maturity_assessment['mature_technologies'] * 3) +
                (maturity_assessment['stable_technologies'] * 2) +
                (maturity_assessment['emerging_technologies'] * 1)
            ) / (total * 3) * 100
        else:
            maturity_score = 0
        
        maturity_assessment['maturity_score'] = maturity_score
        maturity_assessment['maturity_level'] = 'high' if maturity_score >= 80 else 'medium' if maturity_score >= 60 else 'low'
        
        return maturity_assessment
    
    def _assess_operational_readiness(self, architecture_design: Any) -> Dict[str, Any]:
        """Assess operational readiness of the architecture"""
        
        deployment_strategy = getattr(architecture_design, 'deployment_strategy', {})
        monitoring = deployment_strategy.get('monitoring', {})
        
        operational_features = {
            'monitoring_strategy': bool(monitoring),
            'logging_strategy': 'log' in str(monitoring).lower(),
            'alerting_strategy': 'alert' in str(monitoring).lower(),
            'backup_strategy': 'backup' in str(deployment_strategy).lower(),
            'disaster_recovery': 'disaster' in str(deployment_strategy).lower() or 'recovery' in str(deployment_strategy).lower(),
            'ci_cd_pipeline': 'ci' in str(deployment_strategy).lower() or 'pipeline' in str(deployment_strategy).lower()
        }
        
        operational_score = sum(operational_features.values()) / len(operational_features) * 100
        
        return {
            'operational_features': operational_features,
            'operational_score': operational_score,
            'operational_readiness': 'excellent' if operational_score >= 80 else 'good' if operational_score >= 60 else 'needs_improvement'
        }
    
    def _calculate_architecture_score(self, *assessments) -> int:
        """Calculate overall architecture score"""
        
        scores = []
        for assessment in assessments:
            if isinstance(assessment, dict):
                # Extract score from various possible keys
                score = assessment.get('quality_score') or assessment.get('alignment_score') or assessment.get('scalability_score') or assessment.get('operational_score')
                if score is not None:
                    scores.append(score)
        
        return int(sum(scores) / len(scores)) if scores else 70
    
    def _generate_architecture_recommendations(self, *assessments) -> List[str]:
        """Generate architecture improvement recommendations"""
        
        recommendations = []
        
        # Add recommendations based on assessment results
        for assessment in assessments:
            if isinstance(assessment, dict):
                if assessment.get('overall_quality') == 'low':
                    recommendations.append("Improve component design and separation of concerns")
                if assessment.get('scalability_readiness') == 'needs_improvement':
                    recommendations.append("Enhance scalability strategy with auto-scaling and load balancing")
                if assessment.get('operational_readiness') == 'needs_improvement':
                    recommendations.append("Implement comprehensive monitoring, logging, and alerting")
        
        # Add general recommendations
        if not recommendations:
            recommendations.extend([
                "Consider implementing comprehensive monitoring and observability",
                "Ensure proper documentation of architectural decisions",
                "Plan for regular architecture reviews and updates"
            ])
        
        return recommendations
    
    def _analyze_technical_debt(self, architecture_design: Any) -> Dict[str, Any]:
        """
        Analyze technical debt implications of the architecture
        
        Args:
            architecture_design: Architecture design to analyze
            
        Returns:
            Technical debt analysis results
        """
        try:
            # Prepare architecture specification for tech debt analysis
            arch_spec = {
                'technologies': self._extract_technology_info(architecture_design),
                'architecture_pattern': getattr(architecture_design, 'architecture_pattern', {})
            }
            
            # Perform technical debt analysis
            debt_analysis = self.tech_debt_analyzer.analyze_tech_debt(arch_spec)
            
            # Add CTO-specific debt concerns
            cto_debt_concerns = self._identify_cto_debt_concerns(debt_analysis, architecture_design)
            
            enhanced_analysis = {
                **debt_analysis,
                'cto_debt_concerns': cto_debt_concerns,
                'long_term_viability': self._assess_long_term_viability(debt_analysis),
                'maintenance_cost_projection': self._project_maintenance_costs(debt_analysis)
            }
            
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Technical debt analysis failed: {e}")
            return self._get_default_tech_debt_analysis()
    
    def _identify_cto_debt_concerns(self, debt_analysis: Dict[str, Any], architecture_design: Any) -> List[str]:
        """Identify CTO-level technical debt concerns"""
        
        concerns = []
        
        # High-level debt concerns
        if debt_analysis.get('overall_debt_risk') == 'high':
            concerns.append("High technical debt risk may impact long-term maintainability")
        
        if debt_analysis.get('vendor_lock_in_risk') == 'high':
            concerns.append("High vendor lock-in risk limits future technology flexibility")
        
        if debt_analysis.get('operational_complexity') == 'high':
            concerns.append("High operational complexity increases support costs")
        
        # Architecture-specific concerns
        pattern = getattr(architecture_design, 'architecture_pattern', {})
        if 'microservices' in pattern.get('name', '').lower():
            concerns.append("Microservices architecture requires significant operational maturity")
        
        return concerns
    
    def _assess_long_term_viability(self, debt_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess long-term viability of the architecture"""
        
        viability_score = debt_analysis.get('maintainability_score', 70)
        debt_risk = debt_analysis.get('overall_debt_risk', 'medium')
        
        # Adjust viability based on debt risk
        if debt_risk == 'high':
            viability_score -= 20
        elif debt_risk == 'low':
            viability_score += 10
        
        viability_score = max(0, min(100, viability_score))
        
        return {
            'viability_score': viability_score,
            'viability_level': 'excellent' if viability_score >= 80 else 'good' if viability_score >= 60 else 'concerning',
            'projected_lifespan': '5+ years' if viability_score >= 80 else '3-5 years' if viability_score >= 60 else '1-3 years'
        }
    
    def _project_maintenance_costs(self, debt_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Project long-term maintenance costs"""
        
        base_maintenance_factor = 0.2  # 20% of development cost annually
        debt_multiplier = {
            'low': 1.0,
            'medium': 1.3,
            'high': 1.8
        }
        
        debt_risk = debt_analysis.get('overall_debt_risk', 'medium')
        maintenance_factor = base_maintenance_factor * debt_multiplier.get(debt_risk, 1.3)
        
        return {
            'annual_maintenance_factor': maintenance_factor,
            'maintenance_risk': debt_risk,
            'cost_projection': f"{int(maintenance_factor * 100)}% of initial development cost annually"
        }
    
    def _validate_technology_stack(self, architecture_design: Any) -> Dict[str, Any]:
        """Validate technology stack choices and compatibility"""
        
        tech_stack = getattr(architecture_design, 'technology_stack', {})
        technologies = tech_stack.get('technologies', {})
        
        # Check technology compatibility
        compatibility_analysis = self._analyze_technology_compatibility(technologies)
        
        # Check licensing and cost implications
        licensing_analysis = self._analyze_licensing_implications(technologies)
        
        # Check support and community
        support_analysis = self._analyze_technology_support(technologies)
        
        return {
            'compatibility_analysis': compatibility_analysis,
            'licensing_analysis': licensing_analysis,
            'support_analysis': support_analysis,
            'overall_stack_validation': self._calculate_stack_validation_score(
                compatibility_analysis, licensing_analysis, support_analysis
            )
        }
    
    def _analyze_technology_compatibility(self, technologies: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze compatibility between selected technologies"""
        
        # This is a simplified analysis - in practice would check actual compatibility matrices
        compatibility_issues = []
        
        # Check for known incompatibilities (simplified)
        tech_names = [getattr(tech, 'name', str(tech)).lower() for tech in technologies.values()]
        
        # Example compatibility checks
        if 'mongodb' in tech_names and 'postgresql' in tech_names:
            compatibility_issues.append("Multiple database technologies may increase complexity")
        
        return {
            'compatibility_score': 90 if not compatibility_issues else 70,
            'compatibility_issues': compatibility_issues,
            'compatibility_status': 'good' if not compatibility_issues else 'needs_review'
        }
    
    def _analyze_licensing_implications(self, technologies: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze licensing and cost implications"""
        
        # Simplified licensing analysis
        licensing_concerns = []
        estimated_licensing_cost = 0
        
        for tech in technologies.values():
            tech_name = getattr(tech, 'name', str(tech)).lower()
            
            # Check for commercial technologies
            if any(commercial in tech_name for commercial in ['oracle', 'microsoft', 'vmware']):
                licensing_concerns.append(f"Commercial licensing required for {tech_name}")
                estimated_licensing_cost += 10000  # Simplified cost estimate
        
        return {
            'licensing_concerns': licensing_concerns,
            'estimated_annual_licensing_cost': estimated_licensing_cost,
            'licensing_risk': 'high' if estimated_licensing_cost > 50000 else 'medium' if estimated_licensing_cost > 10000 else 'low'
        }
    
    def _analyze_technology_support(self, technologies: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze technology support and community"""
        
        support_assessment = {
            'enterprise_support_available': 0,
            'strong_community': 0,
            'total_technologies': len(technologies)
        }
        
        for tech in technologies.values():
            tech_name = getattr(tech, 'name', str(tech)).lower()
            community_support = getattr(tech, 'community_support', 'good')
            
            # Simplified support assessment
            if community_support == 'excellent':
                support_assessment['strong_community'] += 1
            
            if any(enterprise_tech in tech_name for enterprise_tech in ['aws', 'azure', 'postgresql', 'kubernetes']):
                support_assessment['enterprise_support_available'] += 1
        
        total = support_assessment['total_technologies']
        support_score = ((support_assessment['enterprise_support_available'] + support_assessment['strong_community']) / (total * 2)) * 100 if total > 0 else 0
        
        return {
            **support_assessment,
            'support_score': support_score,
            'support_level': 'excellent' if support_score >= 80 else 'good' if support_score >= 60 else 'concerning'
        }
    
    def _calculate_stack_validation_score(self, *analyses) -> Dict[str, Any]:
        """Calculate overall technology stack validation score"""
        
        scores = []
        for analysis in analyses:
            if isinstance(analysis, dict):
                score = analysis.get('compatibility_score') or analysis.get('support_score') or 70
                scores.append(score)
        
        overall_score = sum(scores) / len(scores) if scores else 70
        
        return {
            'validation_score': int(overall_score),
            'validation_status': 'approved' if overall_score >= 80 else 'conditional' if overall_score >= 60 else 'needs_review'
        }
    
    def _validate_project_plan(self, project_plan: Any, project_estimate: Any) -> Dict[str, Any]:
        """Validate project plan and estimates from CTO perspective"""
        
        try:
            # Extract plan details
            total_duration = getattr(project_estimate, 'duration_weeks', 0)
            total_effort = getattr(project_estimate, 'total_effort_hours', 0)
            total_cost = getattr(project_estimate, 'cost_estimate', {}).get('total_cost', 0)
            
            # Validate estimates against CTO expectations
            estimate_validation = self._validate_estimates(total_duration, total_effort, total_cost)
            
            # Validate project phases and approach
            phase_validation = self._validate_project_phases(project_plan)
            
            # Validate risk management
            risk_validation = self._validate_risk_management(project_plan)
            
            return {
                'estimate_validation': estimate_validation,
                'phase_validation': phase_validation,
                'risk_validation': risk_validation,
                'overall_plan_score': self._calculate_plan_validation_score(
                    estimate_validation, phase_validation, risk_validation
                )
            }
            
        except Exception as e:
            logger.error(f"Project plan validation failed: {e}")
            return {'validation_error': str(e), 'overall_plan_score': 50}
    
    def _validate_estimates(self, duration_weeks: float, effort_hours: float, total_cost: float) -> Dict[str, Any]:
        """Validate project estimates"""
        
        validation_issues = []
        
        # Check duration reasonableness
        if duration_weeks > 52:
            validation_issues.append("Project duration exceeds 1 year - consider phased approach")
        elif duration_weeks < 4:
            validation_issues.append("Project duration seems too short for proposed scope")
        
        # Check effort reasonableness
        if effort_hours > 5000:
            validation_issues.append("High effort estimate - ensure adequate risk management")
        
        # Check cost reasonableness
        if total_cost > 500000:
            validation_issues.append("High cost estimate - ensure strong business case")
        
        return {
            'validation_issues': validation_issues,
            'estimate_confidence': 'high' if not validation_issues else 'medium',
            'estimate_status': 'approved' if len(validation_issues) <= 1 else 'needs_review'
        }
    
    def _validate_project_phases(self, project_plan: Any) -> Dict[str, Any]:
        """Validate project phases and approach"""
        
        phases = getattr(project_plan, 'phases', [])
        
        phase_issues = []
        
        # Check for essential phases
        phase_names = [phase.get('name', '').lower() for phase in phases]
        
        if not any('test' in name for name in phase_names):
            phase_issues.append("No dedicated testing phase identified")
        
        if not any('deploy' in name for name in phase_names):
            phase_issues.append("No deployment phase identified")
        
        # Check phase duration balance
        if len(phases) > 0:
            durations = [phase.get('duration_weeks', 0) for phase in phases]
            max_duration = max(durations) if durations else 0
            total_duration = sum(durations)
            
            if max_duration > total_duration * 0.6:
                phase_issues.append("One phase dominates timeline - consider breaking down")
        
        return {
            'phase_issues': phase_issues,
            'phase_count': len(phases),
            'phase_validation': 'good' if len(phase_issues) <= 1 else 'needs_improvement'
        }
    
    def _validate_risk_management(self, project_plan: Any) -> Dict[str, Any]:
        """Validate risk management approach"""
        
        risk_mitigation = getattr(project_plan, 'risk_mitigation', [])
        
        risk_validation_issues = []
        
        if len(risk_mitigation) < 3:
            risk_validation_issues.append("Insufficient risk mitigation strategies identified")
        
        # Check for key risk categories
        risk_text = str(risk_mitigation).lower()
        if 'technical' not in risk_text:
            risk_validation_issues.append("Technical risks not adequately addressed")
        
        if 'schedule' not in risk_text:
            risk_validation_issues.append("Schedule risks not adequately addressed")
        
        return {
            'risk_validation_issues': risk_validation_issues,
            'risk_mitigation_count': len(risk_mitigation),
            'risk_management_quality': 'good' if len(risk_validation_issues) <= 1 else 'needs_improvement'
        }
    
    def _calculate_plan_validation_score(self, *validations) -> int:
        """Calculate overall plan validation score"""
        
        # Simple scoring based on validation results
        score = 80  # Base score
        
        for validation in validations:
            if isinstance(validation, dict):
                issues = validation.get('validation_issues', []) or validation.get('phase_issues', []) or validation.get('risk_validation_issues', [])
                score -= len(issues) * 5
        
        return max(0, min(100, score))
    
    def _assess_business_alignment(self, architecture_design: Any, extracted_data: Any, project_estimate: Any) -> Dict[str, Any]:
        """Assess business alignment and ROI"""
        
        try:
            # Extract business context
            client_info = getattr(extracted_data, 'client_info', {}) if extracted_data else {}
            project_overview = getattr(extracted_data, 'project_overview', {}) if extracted_data else {}
            
            # Assess strategic alignment
            strategic_alignment = self._assess_strategic_alignment(architecture_design, client_info, project_overview)
            
            # Assess cost-benefit ratio
            cost_benefit = self._assess_cost_benefit_ratio(project_estimate, project_overview)
            
            # Assess technology investment ROI
            technology_roi = self._assess_technology_roi(architecture_design, project_estimate)
            
            return {
                'strategic_alignment': strategic_alignment,
                'cost_benefit_analysis': cost_benefit,
                'technology_roi': technology_roi,
                'business_alignment_score': self._calculate_business_alignment_score(
                    strategic_alignment, cost_benefit, technology_roi
                )
            }
            
        except Exception as e:
            logger.error(f"Business alignment assessment failed: {e}")
            return self._get_default_business_alignment()
    
    def _assess_strategic_alignment(self, architecture_design: Any, client_info: Dict[str, Any], project_overview: Dict[str, Any]) -> Dict[str, Any]:
        """Assess strategic alignment with business objectives"""
        
        # Extract business objectives
        objectives = project_overview.get('objectives', [])
        industry = client_info.get('industry', 'General')
        
        # Assess technology alignment with industry
        tech_stack = getattr(architecture_design, 'technology_stack', {})
        technologies = tech_stack.get('technologies', {})
        
        # Simple industry alignment check
        industry_appropriate = True
        if industry.lower() in ['finance', 'healthcare', 'government']:
            # Check for enterprise-grade technologies
            tech_names = [getattr(tech, 'name', str(tech)).lower() for tech in technologies.values()]
            if not any(enterprise_tech in tech_names for enterprise_tech in ['postgresql', 'aws', 'azure']):
                industry_appropriate = False
        
        return {
            'industry_alignment': 'good' if industry_appropriate else 'needs_review',
            'objective_coverage': len(objectives),
            'strategic_fit': 'excellent' if industry_appropriate and len(objectives) > 0 else 'good'
        }
    
    def _assess_cost_benefit_ratio(self, project_estimate: Any, project_overview: Dict[str, Any]) -> Dict[str, Any]:
        """Assess cost-benefit ratio of the project"""
        
        total_cost = getattr(project_estimate, 'cost_estimate', {}).get('total_cost', 0) if project_estimate else 0
        
        # Simple cost assessment
        if total_cost == 0:
            return {'cost_benefit_ratio': 'unknown', 'cost_assessment': 'no_cost_data'}
        
        # Categorize cost level
        if total_cost < 50000:
            cost_level = 'low'
        elif total_cost < 200000:
            cost_level = 'medium'
        else:
            cost_level = 'high'
        
        # Simple benefit assessment based on project scope
        objectives = project_overview.get('objectives', [])
        benefit_level = 'high' if len(objectives) > 3 else 'medium' if len(objectives) > 1 else 'low'
        
        return {
            'cost_level': cost_level,
            'benefit_level': benefit_level,
            'cost_benefit_ratio': 'favorable' if (cost_level == 'low' and benefit_level in ['medium', 'high']) or (cost_level == 'medium' and benefit_level == 'high') else 'acceptable',
            'investment_recommendation': 'proceed' if cost_level in ['low', 'medium'] else 'review_carefully'
        }
    
    def _assess_technology_roi(self, architecture_design: Any, project_estimate: Any) -> Dict[str, Any]:
        """Assess ROI of technology investments"""
        
        tech_stack = getattr(architecture_design, 'technology_stack', {})
        estimated_cost_factor = tech_stack.get('estimated_cost_factor', 1.0)
        
        # Assess technology investment efficiency
        if estimated_cost_factor <= 0.9:
            roi_assessment = 'excellent'
        elif estimated_cost_factor <= 1.1:
            roi_assessment = 'good'
        elif estimated_cost_factor <= 1.3:
            roi_assessment = 'acceptable'
        else:
            roi_assessment = 'concerning'
        
        return {
            'technology_cost_factor': estimated_cost_factor,
            'roi_assessment': roi_assessment,
            'technology_efficiency': 'high' if estimated_cost_factor <= 1.0 else 'medium' if estimated_cost_factor <= 1.2 else 'low'
        }
    
    def _calculate_business_alignment_score(self, *assessments) -> int:
        """Calculate overall business alignment score"""
        
        score = 75  # Base score
        
        for assessment in assessments:
            if isinstance(assessment, dict):
                if assessment.get('strategic_fit') == 'excellent':
                    score += 10
                elif assessment.get('strategic_fit') == 'good':
                    score += 5
                
                if assessment.get('cost_benefit_ratio') == 'favorable':
                    score += 10
                elif assessment.get('cost_benefit_ratio') == 'acceptable':
                    score += 5
                
                if assessment.get('roi_assessment') == 'excellent':
                    score += 10
                elif assessment.get('roi_assessment') == 'good':
                    score += 5
        
        return max(0, min(100, score))
    
    def _identify_technical_issues(self, *assessments) -> List[TechnicalIssue]:
        """Identify technical issues from all assessments"""
        
        technical_issues = []
        
        # Process security assessment
        security_assessment = assessments[0] if len(assessments) > 0 else {}
        if isinstance(security_assessment, dict):
            security_score = security_assessment.get('security_score', 100)
            if security_score < 70:
                technical_issues.append(TechnicalIssue(
                    category='security',
                    title='Low Security Score',
                    description=f'Security assessment score ({security_score}) below acceptable threshold',
                    criticality=CriticalityLevel.HIGH,
                    impact='High security risk may compromise system integrity',
                    recommendation='Address all critical and high-risk security findings',
                    must_fix=True
                ))
            
            # Check for critical security findings
            findings = security_assessment.get('findings', [])
            critical_findings = [f for f in findings if hasattr(f, 'risk_level') and f.risk_level.value == 'critical']
            if critical_findings:
                technical_issues.append(TechnicalIssue(
                    category='security',
                    title='Critical Security Vulnerabilities',
                    description=f'{len(critical_findings)} critical security vulnerabilities identified',
                    criticality=CriticalityLevel.CRITICAL,
                    impact='Critical vulnerabilities pose immediate security risk',
                    recommendation='Resolve all critical security vulnerabilities before deployment',
                    must_fix=True
                ))
        
        # Process architecture assessment
        architecture_review = assessments[1] if len(assessments) > 1 else {}
        if isinstance(architecture_review, dict):
            arch_score = architecture_review.get('overall_architecture_score', 100)
            if arch_score < 60:
                technical_issues.append(TechnicalIssue(
                    category='architecture',
                    title='Architecture Quality Issues',
                    description=f'Architecture quality score ({arch_score}) below acceptable standards',
                    criticality=CriticalityLevel.MEDIUM,
                    impact='Poor architecture quality may impact maintainability and scalability',
                    recommendation='Improve architecture design and documentation',
                    must_fix=False
                ))
        
        # Process technical debt assessment
        tech_debt_analysis = assessments[2] if len(assessments) > 2 else {}
        if isinstance(tech_debt_analysis, dict):
            debt_risk = tech_debt_analysis.get('overall_debt_risk', 'medium')
            if debt_risk == 'high':
                technical_issues.append(TechnicalIssue(
                    category='technical_debt',
                    title='High Technical Debt Risk',
                    description='Architecture choices may lead to high technical debt',
                    criticality=CriticalityLevel.MEDIUM,
                    impact='High technical debt increases long-term maintenance costs',
                    recommendation='Consider simplifying architecture or improving technology choices',
                    must_fix=False
                ))
        
        return technical_issues
    
    def _make_validation_decision(self, 
                                technical_issues: List[TechnicalIssue], 
                                security_assessment: Dict[str, Any], 
                                architecture_review: Dict[str, Any],
                                business_alignment: Dict[str, Any]) -> Dict[str, Any]:
        """Make final CTO validation decision"""
        
        # Count critical issues
        critical_issues = [issue for issue in technical_issues if issue.criticality == CriticalityLevel.CRITICAL]
        high_issues = [issue for issue in technical_issues if issue.criticality == CriticalityLevel.HIGH]
        must_fix_issues = [issue for issue in technical_issues if issue.must_fix]
        
        # Calculate overall score
        security_score = security_assessment.get('security_score', 100)
        architecture_score = architecture_review.get('overall_architecture_score', 100)
        business_score = business_alignment.get('business_alignment_score', 100)
        
        overall_score = int((security_score + architecture_score + business_score) / 3)
        
        # Make decision based on issues and scores
        if critical_issues:
            result = ValidationResult.REJECTED
            rejection_reasons = [f"Critical issue: {issue.title}" for issue in critical_issues]
            recommendations = [issue.recommendation for issue in critical_issues]
            conditions = []
        elif must_fix_issues or overall_score < 60:
            result = ValidationResult.NEEDS_REVISION
            rejection_reasons = []
            recommendations = [issue.recommendation for issue in must_fix_issues]
            conditions = [f"Must fix: {issue.title}" for issue in must_fix_issues]
        elif high_issues or overall_score < 80:
            result = ValidationResult.APPROVED_WITH_CONDITIONS
            rejection_reasons = []
            recommendations = [issue.recommendation for issue in high_issues]
            conditions = [f"Address before deployment: {issue.title}" for issue in high_issues]
        else:
            result = ValidationResult.APPROVED
            rejection_reasons = []
            recommendations = ["Architecture approved - proceed with implementation"]
            conditions = []
        
        return {
            'result': result,
            'score': overall_score,
            'recommendations': recommendations,
            'conditions': conditions,
            'rejection_reasons': rejection_reasons
        }
    
    def _get_default_security_assessment(self) -> Dict[str, Any]:
        """Get default security assessment for error cases"""
        return {
            'overall_risk_level': 'medium',
            'security_score': 70,
            'findings': [],
            'compliance_gaps': {},
            'recommendations': ['Manual security review required'],
            'cto_security_concerns': ['Security assessment failed'],
            'enterprise_readiness': 'needs_review',
            'security_investment_required': {
                'additional_effort_hours': 40,
                'estimated_cost': 6000,
                'timeline_impact_weeks': 1,
                'priority': 'high'
            }
        }
    
    def _get_default_architecture_review(self) -> Dict[str, Any]:
        """Get default architecture review for error cases"""
        return {
            'architecture_quality': {'overall_quality': 'medium', 'quality_score': 70},
            'requirements_alignment': {'alignment_score': 70, 'alignment_status': 'good'},
            'scalability_assessment': {'scalability_score': 70, 'scalability_readiness': 'good'},
            'technology_assessment': {'technology_recommendation': 'needs_review'},
            'operational_assessment': {'operational_score': 70, 'operational_readiness': 'good'},
            'overall_architecture_score': 70,
            'architecture_recommendations': ['Manual architecture review required']
        }
    
    def _get_default_tech_debt_analysis(self) -> Dict[str, Any]:
        """Get default tech debt analysis for error cases"""
        return {
            'overall_debt_risk': 'medium',
            'debt_factors': [],
            'maintainability_score': 70,
            'operational_complexity': 'medium',
            'vendor_lock_in_risk': 'medium',
            'recommendations': ['Manual technical debt review required'],
            'cto_debt_concerns': ['Technical debt analysis failed'],
            'long_term_viability': {'viability_score': 70, 'viability_level': 'good'},
            'maintenance_cost_projection': {
                'annual_maintenance_factor': 0.25,
                'maintenance_risk': 'medium',
                'cost_projection': '25% of initial development cost annually'
            }
        }
    
    def _get_default_business_alignment(self) -> Dict[str, Any]:
        """Get default business alignment for error cases"""
        return {
            'strategic_alignment': {'strategic_fit': 'good'},
            'cost_benefit_analysis': {'cost_benefit_ratio': 'acceptable'},
            'technology_roi': {'roi_assessment': 'good'},
            'business_alignment_score': 70
        }

# Factory function to create CTO agent
def create_cto_agent(llm: Optional[ChatOpenAI] = None) -> CTOAgent:
    """Create and configure CTO agent"""
    return CTOAgent(llm=llm)