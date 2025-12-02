"""
QA + CEO Agent for final quality assurance and executive approval
Final quality assurance and executive sign-off before proposal rendering
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState, RFPProposal
from ..tools.quality_tools import create_quality_tools

logger = logging.getLogger(__name__)

class ApprovalStatus(Enum):
    """Final approval status"""
    APPROVED = "approved"
    CONDITIONALLY_APPROVED = "conditionally_approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"

class QualityLevel(Enum):
    """Quality assessment levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"

@dataclass
class QualityAssessment:
    """Quality assessment results"""
    category: str
    quality_level: QualityLevel
    score: int  # 0-100
    issues: List[str]
    recommendations: List[str]

@dataclass
class ExecutiveReview:
    """Executive review results"""
    strategic_alignment: str
    business_value_clarity: str
    risk_assessment: str
    competitive_positioning: str
    executive_recommendations: List[str]
    approval_readiness: bool

@dataclass
class FinalApproval:
    """Final approval decision"""
    approval_status: ApprovalStatus
    overall_quality_score: int
    quality_assessments: List[QualityAssessment]
    executive_review: ExecutiveReview
    completeness_check: Dict[str, Any]
    tone_analysis: Dict[str, Any]
    final_recommendations: List[str]
    approval_conditions: List[str]
    rejection_reasons: List[str]

class QACEOAgent:
    """
    QA + CEO Agent that provides final quality assurance and executive approval
    
    Responsibilities:
    - Conduct comprehensive quality assurance of the complete proposal
    - Perform tone analysis and ensure professional presentation
    - Validate completeness against RFP requirements
    - Conduct executive-level strategic review
    - Assess competitive positioning and value proposition
    - Ensure proposal meets client expectations and standards
    - Provide final approval or rejection with detailed feedback
    - Generate executive summary and recommendations
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        
        # Initialize quality tools
        self.quality_tools = create_quality_tools()
        self.tone_analyzer = self.quality_tools['tone_analyzer']
        self.completeness_checker = self.quality_tools['completeness_checker']
        self.executive_reviewer = self.quality_tools['executive_reviewer']
        
        # System prompt for the QA + CEO
        self.system_prompt = """You are the QA + CEO Agent. You provide the final quality assurance and executive approval for the RFP proposal. Your role combines detailed quality control with strategic executive oversight to ensure the proposal meets the highest standards.

Your responsibilities:
1. Conduct comprehensive quality assurance of all proposal components
2. Perform tone analysis to ensure professional, confident presentation
3. Validate completeness against original RFP requirements
4. Review strategic alignment with business objectives
5. Assess competitive positioning and value proposition
6. Ensure proposal meets client expectations and industry standards
7. Provide final approval or rejection with detailed rationale
8. Generate executive summary and strategic recommendations

Your authority:
- APPROVED: Proposal meets all quality and strategic requirements
- CONDITIONALLY APPROVED: Proposal acceptable with minor modifications
- NEEDS REVISION: Proposal requires significant improvements
- REJECTED: Proposal has fundamental issues requiring complete rework

Quality Standards:
- Technical accuracy and completeness
- Professional tone and presentation
- Strategic alignment with client needs
- Competitive differentiation
- Clear value proposition
- Risk mitigation and feasibility
- Cost-effectiveness and ROI

Be thorough, strategic, and decisive. Ensure the proposal represents our organization's best work and maximizes win probability."""
    
    def conduct_final_review(self, state: WorkflowState) -> WorkflowState:
        """
        Conduct final quality assurance and executive review
        
        Args:
            state: Current workflow state with complete proposal
            
        Returns:
            Updated state with final approval decision
        """
        try:
            logger.info("QA + CEO Agent: Starting final review and approval")
            
            # Validate that all required components are available
            self._validate_proposal_completeness(state)
            
            # Step 1: Conduct comprehensive quality assurance
            quality_assessments = self._conduct_quality_assurance(state)
            
            # Step 2: Perform tone analysis on proposal content
            tone_analysis = self._perform_tone_analysis(state)
            
            # Step 3: Validate completeness against RFP requirements
            completeness_check = self._validate_completeness(state)
            
            # Step 4: Conduct executive strategic review
            executive_review = self._conduct_executive_review(state)
            
            # Step 5: Assess competitive positioning
            competitive_assessment = self._assess_competitive_positioning(state)
            
            # Step 6: Validate business case and ROI
            business_case_validation = self._validate_business_case(state)
            
            # Step 7: Make final approval decision
            final_approval = self._make_final_approval_decision(
                quality_assessments,
                tone_analysis,
                completeness_check,
                executive_review,
                competitive_assessment,
                business_case_validation
            )
            
            # Step 8: Generate final proposal if approved
            if final_approval.approval_status in [ApprovalStatus.APPROVED, ApprovalStatus.CONDITIONALLY_APPROVED]:
                final_proposal = self._generate_final_proposal(state, final_approval)
                state.proposal = final_proposal
            
            # Update state (convert dataclass to dict for Pydantic compatibility)
            state.final_approval = asdict(final_approval)
            state.qa_results = {
                'quality_assessments': quality_assessments,
                'tone_analysis': tone_analysis,
                'completeness_check': completeness_check,
                'executive_review': executive_review
            }
            state.current_step = "final_approval_complete"
            state.last_agent_executed = "qa_ceo"
            
            logger.info(f"QA + CEO Agent: Review complete - {final_approval.approval_status.value} (Score: {final_approval.overall_quality_score})")
            return state
            
        except Exception as e:
            logger.error(f"QA + CEO Agent failed: {e}")
            state.errors.append(f"QA + CEO Agent error: {str(e)}")
            return state
    
    def _validate_proposal_completeness(self, state: WorkflowState) -> None:
        """Validate that all required proposal components are available"""
        
        missing_components = []
        
        if not state.extracted_data:
            missing_components.append("extracted_data")
        if not state.architecture_design:
            missing_components.append("architecture_design")
        if not state.architecture_diagrams:
            missing_components.append("architecture_diagrams")
        if not state.project_plan:
            missing_components.append("project_plan")
        if not state.cto_validation:
            missing_components.append("cto_validation")
        
        if missing_components:
            raise ValueError(f"Missing required proposal components: {', '.join(missing_components)}")
    
    def _conduct_quality_assurance(self, state: WorkflowState) -> List[QualityAssessment]:
        """
        Conduct comprehensive quality assurance of all proposal components
        
        Args:
            state: Current workflow state
            
        Returns:
            List of quality assessments
        """
        try:
            quality_assessments = []
            
            # Assess requirements analysis quality
            requirements_qa = self._assess_requirements_quality(state.extracted_data)
            quality_assessments.append(requirements_qa)
            
            # Assess architecture design quality
            architecture_qa = self._assess_architecture_quality(state.architecture_design, state.cto_validation)
            quality_assessments.append(architecture_qa)
            
            # Assess diagram quality
            diagrams_qa = self._assess_diagrams_quality(state.architecture_diagrams)
            quality_assessments.append(diagrams_qa)
            
            # Assess project plan quality
            project_plan_qa = self._assess_project_plan_quality(state.project_plan, state.project_estimate)
            quality_assessments.append(project_plan_qa)
            
            # Assess technical validation quality
            technical_validation_qa = self._assess_technical_validation_quality(state.cto_validation)
            quality_assessments.append(technical_validation_qa)
            
            return quality_assessments
            
        except Exception as e:
            logger.error(f"Quality assurance failed: {e}")
            return self._get_default_quality_assessments()
    
    def _assess_requirements_quality(self, extracted_data: Any) -> QualityAssessment:
        """Assess quality of requirements analysis"""
        
        if not extracted_data:
            return QualityAssessment(
                category="Requirements Analysis",
                quality_level=QualityLevel.POOR,
                score=0,
                issues=["No requirements data available"],
                recommendations=["Complete requirements analysis"]
            )
        
        issues = []
        score = 100
        
        # Check client information completeness
        client_info = getattr(extracted_data, 'client_info', {})
        if not client_info.get('organization_name'):
            issues.append("Client organization name missing")
            score -= 15
        
        # Check requirements completeness
        requirements = getattr(extracted_data, 'requirements', {})
        functional_reqs = requirements.get('functional', [])
        if len(functional_reqs) < 3:
            issues.append("Insufficient functional requirements identified")
            score -= 20
        
        # Check technical specifications
        technical_specs = getattr(extracted_data, 'technical_specs', {})
        if not technical_specs:
            issues.append("Technical specifications incomplete")
            score -= 15
        
        # Check research data
        research_data = getattr(extracted_data, 'research_data', {})
        if not research_data:
            issues.append("External research data missing")
            score -= 10
        
        # Determine quality level
        if score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif score >= 75:
            quality_level = QualityLevel.GOOD
        elif score >= 60:
            quality_level = QualityLevel.ACCEPTABLE
        else:
            quality_level = QualityLevel.POOR
        
        recommendations = []
        if issues:
            recommendations.extend([
                "Enhance requirements analysis depth",
                "Validate requirements with stakeholders",
                "Conduct additional research if needed"
            ])
        else:
            recommendations.append("Requirements analysis meets quality standards")
        
        return QualityAssessment(
            category="Requirements Analysis",
            quality_level=quality_level,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_architecture_quality(self, architecture_design: Any, cto_validation: Any) -> QualityAssessment:
        """Assess quality of architecture design"""
        
        if not architecture_design:
            return QualityAssessment(
                category="Architecture Design",
                quality_level=QualityLevel.POOR,
                score=0,
                issues=["No architecture design available"],
                recommendations=["Complete architecture design"]
            )
        
        issues = []
        score = 100
        
        # Check CTO validation results
        if cto_validation:
            cto_score = getattr(cto_validation, 'overall_score', 70)
            if cto_score < 80:
                issues.append(f"CTO validation score ({cto_score}) below excellent threshold")
                score = min(score, cto_score)
            
            validation_result = getattr(cto_validation, 'validation_result', None)
            if validation_result and validation_result.value == 'rejected':
                issues.append("Architecture rejected by CTO")
                score = 30
            elif validation_result and validation_result.value == 'needs_revision':
                issues.append("Architecture requires revision per CTO feedback")
                score = min(score, 60)
        
        # Check architecture completeness
        components = getattr(architecture_design, 'system_components', [])
        if len(components) < 3:
            issues.append("Architecture appears incomplete - insufficient components")
            score -= 15
        
        # Check security considerations
        security_considerations = getattr(architecture_design, 'security_considerations', {})
        if not security_considerations:
            issues.append("Security considerations not adequately addressed")
            score -= 20
        
        # Check scalability strategy
        scalability_strategy = getattr(architecture_design, 'scalability_strategy', {})
        if not scalability_strategy:
            issues.append("Scalability strategy not defined")
            score -= 15
        
        # Determine quality level
        if score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif score >= 75:
            quality_level = QualityLevel.GOOD
        elif score >= 60:
            quality_level = QualityLevel.ACCEPTABLE
        else:
            quality_level = QualityLevel.POOR
        
        recommendations = []
        if issues:
            recommendations.extend([
                "Address CTO feedback and recommendations",
                "Enhance architecture documentation",
                "Validate scalability and security approaches"
            ])
        else:
            recommendations.append("Architecture design meets quality standards")
        
        return QualityAssessment(
            category="Architecture Design",
            quality_level=quality_level,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_diagrams_quality(self, architecture_diagrams: List[Any]) -> QualityAssessment:
        """Assess quality of architecture diagrams"""
        
        if not architecture_diagrams:
            return QualityAssessment(
                category="Architecture Diagrams",
                quality_level=QualityLevel.POOR,
                score=0,
                issues=["No architecture diagrams available"],
                recommendations=["Generate architecture diagrams"]
            )
        
        issues = []
        score = 100
        
        # Check diagram count and variety
        if len(architecture_diagrams) < 3:
            issues.append("Insufficient number of diagrams for comprehensive presentation")
            score -= 20
        
        # Check diagram generation success
        successful_diagrams = 0
        for diagram in architecture_diagrams:
            if hasattr(diagram, 'svg_content') and diagram.svg_content:
                successful_diagrams += 1
            elif hasattr(diagram, 'png_base64') and diagram.png_base64:
                successful_diagrams += 1
        
        if successful_diagrams == 0:
            issues.append("No diagrams successfully generated")
            score = 20
        elif successful_diagrams < len(architecture_diagrams) * 0.7:
            issues.append("Many diagrams failed to generate properly")
            score -= 30
        
        # Check diagram quality metadata
        quality_issues = 0
        for diagram in architecture_diagrams:
            if hasattr(diagram, 'metadata'):
                quality_validation = diagram.metadata.get('quality_validation', {})
                if quality_validation.get('overall_score', 100) < 80:
                    quality_issues += 1
        
        if quality_issues > 0:
            issues.append(f"{quality_issues} diagrams have quality concerns")
            score -= quality_issues * 10
        
        # Determine quality level
        if score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif score >= 75:
            quality_level = QualityLevel.GOOD
        elif score >= 60:
            quality_level = QualityLevel.ACCEPTABLE
        else:
            quality_level = QualityLevel.POOR
        
        recommendations = []
        if issues:
            recommendations.extend([
                "Regenerate failed diagrams",
                "Improve diagram clarity and presentation",
                "Ensure all key architectural views are covered"
            ])
        else:
            recommendations.append("Architecture diagrams meet quality standards")
        
        return QualityAssessment(
            category="Architecture Diagrams",
            quality_level=quality_level,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_project_plan_quality(self, project_plan: Any, project_estimate: Any) -> QualityAssessment:
        """Assess quality of project plan and estimates"""
        
        if not project_plan:
            return QualityAssessment(
                category="Project Plan",
                quality_level=QualityLevel.POOR,
                score=0,
                issues=["No project plan available"],
                recommendations=["Complete project planning"]
            )
        
        issues = []
        score = 100
        
        # Check plan completeness
        phases = getattr(project_plan, 'phases', [])
        if len(phases) < 3:
            issues.append("Project plan lacks sufficient detail - too few phases")
            score -= 20
        
        milestones = getattr(project_plan, 'milestones', [])
        if len(milestones) < 2:
            issues.append("Insufficient milestones defined")
            score -= 15
        
        # Check risk management
        risk_mitigation = getattr(project_plan, 'risk_mitigation', [])
        if len(risk_mitigation) < 3:
            issues.append("Inadequate risk mitigation strategies")
            score -= 15
        
        # Check estimates reasonableness
        if project_estimate:
            duration_weeks = getattr(project_estimate, 'duration_weeks', 0)
            total_cost = getattr(project_estimate, 'cost_estimate', {}).get('total_cost', 0)
            
            if duration_weeks > 52:
                issues.append("Project duration exceeds 1 year - may be unrealistic")
                score -= 10
            elif duration_weeks < 4:
                issues.append("Project duration seems too short for proposed scope")
                score -= 15
            
            if total_cost > 1000000:
                issues.append("Very high cost estimate - ensure strong justification")
                score -= 10
        
        # Check resource allocation
        resource_allocation = getattr(project_plan, 'resource_allocation', {})
        if not resource_allocation:
            issues.append("Resource allocation not defined")
            score -= 15
        
        # Determine quality level
        if score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif score >= 75:
            quality_level = QualityLevel.GOOD
        elif score >= 60:
            quality_level = QualityLevel.ACCEPTABLE
        else:
            quality_level = QualityLevel.POOR
        
        recommendations = []
        if issues:
            recommendations.extend([
                "Enhance project plan detail and risk management",
                "Validate estimates with historical data",
                "Ensure realistic timeline and resource allocation"
            ])
        else:
            recommendations.append("Project plan meets quality standards")
        
        return QualityAssessment(
            category="Project Plan",
            quality_level=quality_level,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations
        )
    
    def _assess_technical_validation_quality(self, cto_validation: Any) -> QualityAssessment:
        """Assess quality of technical validation"""
        
        if not cto_validation:
            return QualityAssessment(
                category="Technical Validation",
                quality_level=QualityLevel.POOR,
                score=0,
                issues=["No CTO validation available"],
                recommendations=["Complete technical validation"]
            )
        
        issues = []
        score = getattr(cto_validation, 'overall_score', 70)
        
        # Check validation result
        validation_result = getattr(cto_validation, 'validation_result', None)
        if validation_result:
            if validation_result.value == 'rejected':
                issues.append("Technical solution rejected by CTO")
                score = 20
            elif validation_result.value == 'needs_revision':
                issues.append("Technical solution requires revision")
                score = min(score, 60)
            elif validation_result.value == 'approved_with_conditions':
                issues.append("Technical solution approved with conditions")
                score = min(score, 80)
        
        # Check technical issues
        technical_issues = getattr(cto_validation, 'technical_issues', [])
        critical_issues = [issue for issue in technical_issues if hasattr(issue, 'criticality') and issue.criticality.value == 'critical']
        if critical_issues:
            issues.append(f"{len(critical_issues)} critical technical issues identified")
            score = min(score, 40)
        
        # Check security assessment
        security_assessment = getattr(cto_validation, 'security_assessment', {})
        security_score = security_assessment.get('security_score', 100)
        if security_score < 70:
            issues.append(f"Security assessment score ({security_score}) below acceptable threshold")
            score = min(score, security_score)
        
        # Determine quality level
        if score >= 90:
            quality_level = QualityLevel.EXCELLENT
        elif score >= 75:
            quality_level = QualityLevel.GOOD
        elif score >= 60:
            quality_level = QualityLevel.ACCEPTABLE
        else:
            quality_level = QualityLevel.POOR
        
        recommendations = []
        if issues:
            recommendations.extend([
                "Address all CTO feedback and technical issues",
                "Improve security posture if needed",
                "Validate technical decisions with stakeholders"
            ])
        else:
            recommendations.append("Technical validation meets quality standards")
        
        return QualityAssessment(
            category="Technical Validation",
            quality_level=quality_level,
            score=max(0, score),
            issues=issues,
            recommendations=recommendations
        )
    
    def _perform_tone_analysis(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Perform tone analysis on proposal content
        
        Args:
            state: Current workflow state
            
        Returns:
            Tone analysis results
        """
        try:
            # Collect text content from various proposal components
            proposal_text = self._collect_proposal_text(state)
            
            # Perform tone analysis using quality tools
            tone_analysis = self.tone_analyzer.analyze_tone(proposal_text, target_tone='professional')
            
            # Add executive-level tone assessment
            executive_tone_assessment = self._assess_executive_tone(proposal_text)
            
            return {
                'tone_analysis': tone_analysis,
                'executive_assessment': executive_tone_assessment,
                'overall_tone_score': self._calculate_tone_score(tone_analysis, executive_tone_assessment),
                'tone_recommendations': self._generate_tone_recommendations(tone_analysis, executive_tone_assessment)
            }
            
        except Exception as e:
            logger.error(f"Tone analysis failed: {e}")
            return self._get_default_tone_analysis()
    
    def _collect_proposal_text(self, state: WorkflowState) -> str:
        """Collect text content from proposal components"""
        
        text_parts = []
        
        # Add solution overview
        if state.architecture_design:
            solution_overview = getattr(state.architecture_design, 'solution_overview', '')
            if solution_overview:
                text_parts.append(solution_overview)
        
        # Add project plan descriptions
        if state.project_plan:
            phases = getattr(state.project_plan, 'phases', [])
            for phase in phases:
                if isinstance(phase, dict) and 'description' in phase:
                    text_parts.append(phase['description'])
        
        # Add CTO recommendations
        if state.cto_validation:
            recommendations = getattr(state.cto_validation, 'recommendations', [])
            text_parts.extend(recommendations)
        
        # Combine all text
        combined_text = '\n\n'.join(text_parts)
        
        # If no text collected, create sample text
        if not combined_text.strip():
            combined_text = "This proposal presents a comprehensive technical solution designed to meet the client's requirements through modern architecture and proven technologies."
        
        return combined_text
    
    def _assess_executive_tone(self, proposal_text: str) -> Dict[str, Any]:
        """Assess tone from executive perspective"""
        
        # Check for executive-level language
        executive_indicators = [
            'strategic', 'business value', 'roi', 'competitive advantage',
            'market opportunity', 'growth', 'efficiency', 'transformation'
        ]
        
        text_lower = proposal_text.lower()
        executive_language_count = sum(1 for indicator in executive_indicators if indicator in text_lower)
        
        # Check for confidence indicators
        confidence_indicators = ['will deliver', 'ensures', 'guarantees', 'proven', 'established']
        confidence_count = sum(1 for indicator in confidence_indicators if indicator in text_lower)
        
        # Check for uncertainty language
        uncertainty_indicators = ['might', 'could', 'possibly', 'perhaps', 'maybe']
        uncertainty_count = sum(1 for indicator in uncertainty_indicators if indicator in text_lower)
        
        # Calculate executive tone score
        executive_score = (executive_language_count * 10) + (confidence_count * 5) - (uncertainty_count * 10)
        executive_score = max(0, min(100, executive_score))
        
        return {
            'executive_language_score': executive_score,
            'confidence_level': 'high' if confidence_count > uncertainty_count else 'medium' if confidence_count == uncertainty_count else 'low',
            'business_focus': 'strong' if executive_language_count >= 3 else 'moderate' if executive_language_count >= 1 else 'weak',
            'executive_readiness': 'excellent' if executive_score >= 80 else 'good' if executive_score >= 60 else 'needs_improvement'
        }
    
    def _calculate_tone_score(self, tone_analysis: Any, executive_assessment: Dict[str, Any]) -> int:
        """Calculate overall tone score"""
        
        # Base score from tone analysis
        base_score = 70  # Default if no score available
        if hasattr(tone_analysis, 'confidence_score'):
            base_score = int(tone_analysis.confidence_score * 100)
        
        # Adjust for executive assessment
        executive_score = executive_assessment.get('executive_language_score', 50)
        
        # Weighted average
        overall_score = int((base_score * 0.6) + (executive_score * 0.4))
        
        return max(0, min(100, overall_score))
    
    def _generate_tone_recommendations(self, tone_analysis: Any, executive_assessment: Dict[str, Any]) -> List[str]:
        """Generate tone improvement recommendations"""
        
        recommendations = []
        
        # Check tone analysis issues
        if hasattr(tone_analysis, 'issues') and tone_analysis.issues:
            recommendations.extend(tone_analysis.recommendations if hasattr(tone_analysis, 'recommendations') else [])
        
        # Check executive readiness
        if executive_assessment.get('executive_readiness') == 'needs_improvement':
            recommendations.append("Enhance business language and strategic positioning")
        
        if executive_assessment.get('confidence_level') == 'low':
            recommendations.append("Use more confident, definitive language")
        
        if executive_assessment.get('business_focus') == 'weak':
            recommendations.append("Strengthen business value proposition and ROI messaging")
        
        # Default recommendations if none identified
        if not recommendations:
            recommendations.append("Tone analysis indicates professional, appropriate language")
        
        return recommendations
    
    def _validate_completeness(self, state: WorkflowState) -> Dict[str, Any]:
        """
        Validate completeness against RFP requirements
        
        Args:
            state: Current workflow state
            
        Returns:
            Completeness validation results
        """
        try:
            # Prepare proposal data for completeness check
            proposal_data = self._prepare_proposal_data_for_validation(state)
            
            # Perform completeness check using quality tools
            completeness_results = self.completeness_checker.check_completeness(proposal_data)
            
            # Add executive-level completeness assessment
            executive_completeness = self._assess_executive_completeness(state)
            
            return {
                'completeness_check': completeness_results,
                'executive_completeness': executive_completeness,
                'overall_completeness_score': self._calculate_completeness_score(completeness_results, executive_completeness),
                'completeness_recommendations': self._generate_completeness_recommendations(completeness_results, executive_completeness)
            }
            
        except Exception as e:
            logger.error(f"Completeness validation failed: {e}")
            return self._get_default_completeness_check()
    
    def _prepare_proposal_data_for_validation(self, state: WorkflowState) -> Dict[str, Any]:
        """Prepare proposal data for completeness validation"""
        
        proposal_data = {}
        
        # Cover information
        if state.extracted_data:
            client_info = getattr(state.extracted_data, 'client_info', {})
            proposal_data['cover'] = {
                'client_name': client_info.get('organization_name', ''),
                'project_title': getattr(state.extracted_data, 'project_overview', {}).get('project_title', ''),
                'vendor_name': 'Our Organization',
                'date': self._get_current_date(),
                'contact_info': 'Contact information provided'
            }
        
        # Background information
        if state.extracted_data:
            proposal_data['background'] = {
                'client_overview': str(getattr(state.extracted_data, 'client_info', {})),
                'problem_statement': str(getattr(state.extracted_data, 'project_overview', {})),
                'objectives': str(getattr(state.extracted_data, 'requirements', {}))
            }
        
        # Project phases
        if state.project_plan:
            phases = getattr(state.project_plan, 'phases', [])
            proposal_data['phases'] = {
                'phase_list': [phase.get('name', '') for phase in phases],
                'deliverables': [phase.get('deliverables', []) for phase in phases],
                'timeline': f"{getattr(state.project_estimate, 'duration_weeks', 0)} weeks" if state.project_estimate else ''
            }
        
        # Architecture information
        if state.architecture_design:
            proposal_data['architecture'] = {
                'solution_overview': getattr(state.architecture_design, 'solution_overview', ''),
                'technical_approach': str(getattr(state.architecture_design, 'architecture_pattern', {})),
                'technology_stack': str(getattr(state.architecture_design, 'technology_stack', {}))
            }
        
        # Commercial information
        if state.project_estimate:
            cost_estimate = getattr(state.project_estimate, 'cost_estimate', {})
            proposal_data['commercials'] = {
                'cost_breakdown': str(cost_estimate),
                'payment_terms': 'Standard payment terms apply',
                'assumptions': str(getattr(state.project_estimate, 'risk_assessment', {}))
            }
        
        return proposal_data
    
    def _assess_executive_completeness(self, state: WorkflowState) -> Dict[str, Any]:
        """Assess completeness from executive perspective"""
        
        completeness_score = 100
        missing_elements = []
        
        # Check for executive summary
        if not self._has_executive_summary(state):
            missing_elements.append("Executive summary")
            completeness_score -= 20
        
        # Check for business case
        if not self._has_business_case(state):
            missing_elements.append("Clear business case and ROI")
            completeness_score -= 15
        
        # Check for risk assessment
        if not self._has_risk_assessment(state):
            missing_elements.append("Comprehensive risk assessment")
            completeness_score -= 15
        
        # Check for competitive differentiation
        if not self._has_competitive_differentiation(state):
            missing_elements.append("Competitive differentiation")
            completeness_score -= 10
        
        # Check for success metrics
        if not self._has_success_metrics(state):
            missing_elements.append("Success metrics and KPIs")
            completeness_score -= 10
        
        return {
            'executive_completeness_score': max(0, completeness_score),
            'missing_executive_elements': missing_elements,
            'executive_readiness': 'excellent' if completeness_score >= 90 else 'good' if completeness_score >= 75 else 'needs_improvement'
        }
    
    def _has_executive_summary(self, state: WorkflowState) -> bool:
        """Check if executive summary is present"""
        # This would check for executive summary in the proposal
        return state.architecture_design and hasattr(state.architecture_design, 'solution_overview')
    
    def _has_business_case(self, state: WorkflowState) -> bool:
        """Check if business case is present"""
        return state.project_estimate and hasattr(state.project_estimate, 'cost_estimate')
    
    def _has_risk_assessment(self, state: WorkflowState) -> bool:
        """Check if risk assessment is present"""
        return state.project_plan and hasattr(state.project_plan, 'risk_mitigation')
    
    def _has_competitive_differentiation(self, state: WorkflowState) -> bool:
        """Check if competitive differentiation is present"""
        # This would check for competitive analysis in the research data
        if state.extracted_data:
            research_data = getattr(state.extracted_data, 'research_data', {})
            return 'competitive' in str(research_data).lower()
        return False
    
    def _has_success_metrics(self, state: WorkflowState) -> bool:
        """Check if success metrics are defined"""
        return state.project_plan and hasattr(state.project_plan, 'success_criteria')
    
    def _calculate_completeness_score(self, completeness_results: Dict[str, Any], executive_completeness: Dict[str, Any]) -> int:
        """Calculate overall completeness score"""
        
        # Base completeness score
        base_score = completeness_results.get('overall_completeness', 0.7) * 100
        
        # Executive completeness score
        exec_score = executive_completeness.get('executive_completeness_score', 70)
        
        # Weighted average
        overall_score = int((base_score * 0.7) + (exec_score * 0.3))
        
        return max(0, min(100, overall_score))
    
    def _generate_completeness_recommendations(self, completeness_results: Dict[str, Any], executive_completeness: Dict[str, Any]) -> List[str]:
        """Generate completeness improvement recommendations"""
        
        recommendations = []
        
        # Add base completeness recommendations
        base_recommendations = completeness_results.get('recommendations', [])
        recommendations.extend(base_recommendations)
        
        # Add executive completeness recommendations
        missing_elements = executive_completeness.get('missing_executive_elements', [])
        for element in missing_elements:
            recommendations.append(f"Add {element.lower()}")
        
        # Default recommendation if none identified
        if not recommendations:
            recommendations.append("Proposal completeness meets requirements")
        
        return recommendations
    
    def _conduct_executive_review(self, state: WorkflowState) -> ExecutiveReview:
        """
        Conduct executive-level strategic review
        
        Args:
            state: Current workflow state
            
        Returns:
            Executive review results
        """
        try:
            # Prepare proposal data for executive review
            proposal_data = self._prepare_proposal_data_for_validation(state)
            
            # Perform executive review using quality tools
            executive_review_results = self.executive_reviewer.review_executive_alignment(proposal_data)
            
            # Enhance with additional executive analysis
            strategic_analysis = self._perform_strategic_analysis(state)
            competitive_analysis = self._perform_competitive_analysis(state)
            
            return ExecutiveReview(
                strategic_alignment=executive_review_results.get('strategic_alignment', 'medium'),
                business_value_clarity=executive_review_results.get('business_value_clarity', 'medium'),
                risk_assessment=executive_review_results.get('risk_assessment', 'medium'),
                competitive_positioning=competitive_analysis.get('positioning', 'neutral'),
                executive_recommendations=self._generate_executive_recommendations(
                    executive_review_results, strategic_analysis, competitive_analysis
                ),
                approval_readiness=executive_review_results.get('approval_readiness', False)
            )
            
        except Exception as e:
            logger.error(f"Executive review failed: {e}")
            return self._get_default_executive_review()
    
    def _perform_strategic_analysis(self, state: WorkflowState) -> Dict[str, Any]:
        """Perform strategic analysis of the proposal"""
        
        strategic_factors = {
            'technology_alignment': 'good',  # Based on CTO validation
            'market_positioning': 'strong',  # Based on research data
            'scalability_potential': 'high',  # Based on architecture design
            'innovation_level': 'moderate'   # Based on technology choices
        }
        
        # Adjust based on actual state data
        if state.cto_validation:
            cto_score = getattr(state.cto_validation, 'overall_score', 70)
            if cto_score >= 90:
                strategic_factors['technology_alignment'] = 'excellent'
            elif cto_score < 70:
                strategic_factors['technology_alignment'] = 'needs_improvement'
        
        if state.architecture_design:
            scalability_strategy = getattr(state.architecture_design, 'scalability_strategy', {})
            if scalability_strategy:
                strategic_factors['scalability_potential'] = 'high'
            else:
                strategic_factors['scalability_potential'] = 'medium'
        
        return strategic_factors
    
    def _perform_competitive_analysis(self, state: WorkflowState) -> Dict[str, Any]:
        """Perform competitive analysis"""
        
        competitive_factors = {
            'positioning': 'strong',
            'differentiation': 'clear',
            'value_proposition': 'compelling',
            'competitive_advantage': 'technology_expertise'
        }
        
        # Check for competitive research data
        if state.extracted_data:
            research_data = getattr(state.extracted_data, 'research_data', {})
            if 'competitive' in str(research_data).lower():
                competitive_factors['positioning'] = 'well_researched'
        
        return competitive_factors
    
    def _generate_executive_recommendations(self, *analyses) -> List[str]:
        """Generate executive-level recommendations"""
        
        recommendations = []
        
        for analysis in analyses:
            if isinstance(analysis, dict):
                # Check for specific issues and generate recommendations
                if analysis.get('strategic_alignment') == 'low':
                    recommendations.append("Strengthen strategic alignment with client objectives")
                
                if analysis.get('business_value_clarity') == 'low':
                    recommendations.append("Clarify business value proposition and ROI")
                
                if analysis.get('approval_readiness') is False:
                    recommendations.append("Address executive concerns before final submission")
        
        # Default recommendations
        if not recommendations:
            recommendations.extend([
                "Proposal demonstrates strong strategic alignment",
                "Business value proposition is clear and compelling",
                "Technical solution meets enterprise standards"
            ])
        
        return recommendations
    
    def _assess_competitive_positioning(self, state: WorkflowState) -> Dict[str, Any]:
        """Assess competitive positioning of the proposal"""
        
        # This would typically involve detailed competitive analysis
        # For now, provide a basic assessment
        
        positioning_score = 75  # Base score
        
        # Check for unique value propositions
        if state.architecture_design:
            solution_overview = getattr(state.architecture_design, 'solution_overview', '')
            if 'innovative' in solution_overview.lower() or 'unique' in solution_overview.lower():
                positioning_score += 10
        
        # Check for cost competitiveness
        if state.project_estimate:
            cost_estimate = getattr(state.project_estimate, 'cost_estimate', {})
            cost_factor = cost_estimate.get('cost_ranges', {}).get('most_likely', 0)
            if cost_factor > 0 and cost_factor < 100000:  # Competitive pricing
                positioning_score += 5
        
        return {
            'positioning_score': min(100, positioning_score),
            'competitive_strengths': [
                'Technical expertise and proven methodologies',
                'Comprehensive solution approach',
                'Strong project management and delivery track record'
            ],
            'differentiation_factors': [
                'Modern architecture and technology stack',
                'Comprehensive security and scalability approach',
                'Detailed project planning and risk management'
            ],
            'positioning_recommendation': 'strong' if positioning_score >= 80 else 'good' if positioning_score >= 70 else 'needs_improvement'
        }
    
    def _validate_business_case(self, state: WorkflowState) -> Dict[str, Any]:
        """Validate the business case and ROI"""
        
        business_case_score = 70  # Base score
        
        # Check for cost-benefit analysis
        if state.project_estimate:
            cost_estimate = getattr(state.project_estimate, 'cost_estimate', {})
            if cost_estimate:
                business_case_score += 15
        
        # Check for risk assessment
        if state.project_plan:
            risk_mitigation = getattr(state.project_plan, 'risk_mitigation', [])
            if len(risk_mitigation) >= 3:
                business_case_score += 10
        
        # Check for success criteria
        if state.project_plan:
            success_criteria = getattr(state.project_plan, 'success_criteria', [])
            if len(success_criteria) >= 3:
                business_case_score += 5
        
        return {
            'business_case_score': min(100, business_case_score),
            'roi_clarity': 'good' if business_case_score >= 80 else 'acceptable' if business_case_score >= 70 else 'needs_improvement',
            'business_justification': 'strong' if business_case_score >= 85 else 'adequate',
            'investment_recommendation': 'proceed' if business_case_score >= 75 else 'review_required'
        }
    
    def _make_final_approval_decision(self, *assessments) -> FinalApproval:
        """
        Make final approval decision based on all assessments
        
        Args:
            assessments: All assessment results
            
        Returns:
            Final approval decision
        """
        try:
            quality_assessments = assessments[0] if len(assessments) > 0 else []
            tone_analysis = assessments[1] if len(assessments) > 1 else {}
            completeness_check = assessments[2] if len(assessments) > 2 else {}
            executive_review = assessments[3] if len(assessments) > 3 else None
            competitive_assessment = assessments[4] if len(assessments) > 4 else {}
            business_case_validation = assessments[5] if len(assessments) > 5 else {}
            
            # Calculate overall quality score
            quality_scores = []
            if isinstance(quality_assessments, list):
                quality_scores = [qa.score for qa in quality_assessments if hasattr(qa, 'score')]
            
            tone_score = tone_analysis.get('overall_tone_score', 70)
            completeness_score = completeness_check.get('overall_completeness_score', 70)
            competitive_score = competitive_assessment.get('positioning_score', 75)
            business_score = business_case_validation.get('business_case_score', 70)
            
            all_scores = quality_scores + [tone_score, completeness_score, competitive_score, business_score]
            overall_quality_score = int(sum(all_scores) / len(all_scores)) if all_scores else 70
            
            # Identify critical issues
            critical_issues = []
            approval_conditions = []
            
            # Check quality assessments
            if isinstance(quality_assessments, list):
                for qa in quality_assessments:
                    if hasattr(qa, 'quality_level') and qa.quality_level == QualityLevel.POOR:
                        critical_issues.append(f"Poor quality in {qa.category}")
                    elif hasattr(qa, 'quality_level') and qa.quality_level == QualityLevel.ACCEPTABLE:
                        approval_conditions.append(f"Improve {qa.category} quality")
            
            # Check executive approval readiness
            if executive_review and not executive_review.approval_readiness:
                critical_issues.append("Executive approval readiness not met")
            
            # Check completeness
            if completeness_score < 70:
                critical_issues.append("Proposal completeness below acceptable threshold")
            
            # Make approval decision
            if critical_issues:
                if overall_quality_score < 50:
                    approval_status = ApprovalStatus.REJECTED
                else:
                    approval_status = ApprovalStatus.NEEDS_REVISION
            elif approval_conditions or overall_quality_score < 80:
                approval_status = ApprovalStatus.CONDITIONALLY_APPROVED
            else:
                approval_status = ApprovalStatus.APPROVED
            
            # Generate final recommendations
            final_recommendations = self._generate_final_recommendations(
                approval_status, quality_assessments, tone_analysis, completeness_check, executive_review
            )
            
            return FinalApproval(
                approval_status=approval_status,
                overall_quality_score=overall_quality_score,
                quality_assessments=quality_assessments if isinstance(quality_assessments, list) else [],
                executive_review=executive_review or self._get_default_executive_review(),
                completeness_check=completeness_check,
                tone_analysis=tone_analysis,
                final_recommendations=final_recommendations,
                approval_conditions=approval_conditions,
                rejection_reasons=critical_issues
            )
            
        except Exception as e:
            logger.error(f"Final approval decision failed: {e}")
            return self._get_default_final_approval()
    
    def _generate_final_recommendations(self, approval_status: ApprovalStatus, *assessments) -> List[str]:
        """Generate final recommendations based on approval status and assessments"""
        
        recommendations = []
        
        if approval_status == ApprovalStatus.APPROVED:
            recommendations.extend([
                "Proposal approved for submission",
                "All quality standards met",
                "Executive approval granted",
                "Proceed with client presentation"
            ])
        elif approval_status == ApprovalStatus.CONDITIONALLY_APPROVED:
            recommendations.extend([
                "Proposal conditionally approved",
                "Address specified conditions before submission",
                "Minor improvements required",
                "Re-review after modifications"
            ])
        elif approval_status == ApprovalStatus.NEEDS_REVISION:
            recommendations.extend([
                "Proposal requires significant revision",
                "Address all identified issues",
                "Improve quality in flagged areas",
                "Resubmit for review after improvements"
            ])
        else:  # REJECTED
            recommendations.extend([
                "Proposal rejected - fundamental issues identified",
                "Complete rework required",
                "Address all critical issues",
                "Consider alternative approach"
            ])
        
        # Add specific recommendations from assessments
        for assessment in assessments:
            if isinstance(assessment, dict):
                assessment_recommendations = assessment.get('recommendations', [])
                if isinstance(assessment_recommendations, list):
                    recommendations.extend(assessment_recommendations[:2])  # Limit to top 2
        
        return recommendations[:10]  # Limit total recommendations
    
    def _generate_final_proposal(self, state: WorkflowState, final_approval: FinalApproval) -> RFPProposal:
        """
        Generate final proposal document
        
        Args:
            state: Current workflow state
            final_approval: Final approval results
            
        Returns:
            Final RFP proposal
        """
        try:
            # Create comprehensive proposal document
            proposal = RFPProposal(
                client_info=getattr(state.extracted_data, 'client_info', {}) if state.extracted_data else {},
                project_overview=getattr(state.extracted_data, 'project_overview', {}) if state.extracted_data else {},
                solution_overview=getattr(state.architecture_design, 'solution_overview', '') if state.architecture_design else '',
                architecture_design=state.architecture_design,
                architecture_diagrams=state.architecture_diagrams or [],
                project_plan=state.project_plan,
                cost_estimate=getattr(state.project_estimate, 'cost_estimate', {}) if state.project_estimate else {},
                timeline=f"{getattr(state.project_estimate, 'duration_weeks', 0)} weeks" if state.project_estimate else '',
                team_composition=getattr(state.project_plan, 'resource_allocation', {}) if state.project_plan else {},
                risk_assessment=getattr(state.project_plan, 'risk_mitigation', []) if state.project_plan else [],
                success_criteria=getattr(state.project_plan, 'success_criteria', []) if state.project_plan else [],
                executive_summary=self._generate_executive_summary(state, final_approval),
                appendices=self._generate_appendices(state),
                metadata={
                    'generation_timestamp': self._get_current_timestamp(),
                    'approval_status': final_approval.approval_status.value,
                    'quality_score': final_approval.overall_quality_score,
                    'agent_workflow': 'multi_agent_specialized'
                }
            )
            
            return proposal
            
        except Exception as e:
            logger.error(f"Final proposal generation failed: {e}")
            return self._get_default_proposal(state)
    
    def _generate_executive_summary(self, state: WorkflowState, final_approval: FinalApproval) -> str:
        """Generate executive summary for the proposal"""
        
        client_name = "the client"
        if state.extracted_data:
            client_info = getattr(state.extracted_data, 'client_info', {})
            client_name = client_info.get('organization_name', 'the client')
        
        duration = f"{getattr(state.project_estimate, 'duration_weeks', 12)} weeks" if state.project_estimate else "12 weeks"
        cost = getattr(state.project_estimate, 'cost_estimate', {}).get('total_cost', 'TBD') if state.project_estimate else 'TBD'
        
        executive_summary = f"""
## Executive Summary

We are pleased to present this comprehensive proposal for {client_name}'s technology initiative. Our solution combines proven methodologies with modern architecture to deliver a scalable, secure, and cost-effective system that meets your strategic objectives.

### Key Highlights:

**Strategic Alignment**: Our proposed solution directly addresses your core business requirements while positioning your organization for future growth and technological advancement.

**Technical Excellence**: The architecture leverages industry-leading technologies and best practices, ensuring reliability, security, and maintainability.

**Delivery Approach**: Our structured {duration} delivery timeline includes comprehensive risk management and quality assurance processes.

**Investment**: The total investment of ${cost:,} if isinstance(cost, (int, float)) else cost represents excellent value for the comprehensive solution and long-term benefits delivered.

**Quality Assurance**: This proposal has undergone rigorous technical validation and quality review, achieving an overall quality score of {final_approval.overall_quality_score}%.

### Value Proposition:

- Modern, scalable architecture designed for your specific needs
- Comprehensive security and compliance framework
- Detailed project planning with realistic timelines and budgets
- Experienced team with proven delivery track record
- Ongoing support and maintenance strategy

We are confident that our solution will exceed your expectations and deliver significant business value. We look forward to partnering with {client_name} on this important initiative.
"""
        
        return executive_summary.strip()
    
    def _generate_appendices(self, state: WorkflowState) -> List[Dict[str, Any]]:
        """Generate appendices for the proposal"""
        
        appendices = []
        
        # Technical specifications appendix
        if state.architecture_design:
            appendices.append({
                'title': 'Technical Specifications',
                'content': str(getattr(state.architecture_design, 'technology_stack', {})),
                'type': 'technical'
            })
        
        # Risk assessment appendix
        if state.project_plan:
            risk_mitigation = getattr(state.project_plan, 'risk_mitigation', [])
            if risk_mitigation:
                appendices.append({
                    'title': 'Risk Assessment and Mitigation',
                    'content': str(risk_mitigation),
                    'type': 'risk'
                })
        
        # CTO validation appendix
        if state.cto_validation:
            appendices.append({
                'title': 'Technical Validation Report',
                'content': f"CTO Validation Score: {getattr(state.cto_validation, 'overall_score', 'N/A')}",
                'type': 'validation'
            })
        
        return appendices
    
    def _get_current_date(self) -> str:
        """Get current date string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_default_quality_assessments(self) -> List[QualityAssessment]:
        """Get default quality assessments for error cases"""
        return [
            QualityAssessment(
                category="Overall Quality",
                quality_level=QualityLevel.ACCEPTABLE,
                score=70,
                issues=["Quality assessment failed"],
                recommendations=["Manual quality review required"]
            )
        ]
    
    def _get_default_tone_analysis(self) -> Dict[str, Any]:
        """Get default tone analysis for error cases"""
        return {
            'overall_tone_score': 70,
            'tone_recommendations': ['Manual tone review required'],
            'executive_assessment': {'executive_readiness': 'needs_review'}
        }
    
    def _get_default_completeness_check(self) -> Dict[str, Any]:
        """Get default completeness check for error cases"""
        return {
            'overall_completeness_score': 70,
            'completeness_recommendations': ['Manual completeness review required']
        }
    
    def _get_default_executive_review(self) -> ExecutiveReview:
        """Get default executive review for error cases"""
        return ExecutiveReview(
            strategic_alignment='medium',
            business_value_clarity='medium',
            risk_assessment='medium',
            competitive_positioning='neutral',
            executive_recommendations=['Manual executive review required'],
            approval_readiness=False
        )
    
    def _get_default_final_approval(self) -> FinalApproval:
        """Get default final approval for error cases"""
        return FinalApproval(
            approval_status=ApprovalStatus.NEEDS_REVISION,
            overall_quality_score=50,
            quality_assessments=[],
            executive_review=self._get_default_executive_review(),
            completeness_check={},
            tone_analysis={},
            final_recommendations=['Manual review required due to system error'],
            approval_conditions=['Complete manual review'],
            rejection_reasons=['Automated review failed']
        )
    
    def _get_default_proposal(self, state: WorkflowState) -> RFPProposal:
        """Get default proposal for error cases"""
        return RFPProposal(
            client_info={'organization_name': 'Client'},
            project_overview={'project_title': 'RFP Project'},
            solution_overview='Technical solution proposal',
            architecture_design=state.architecture_design,
            architecture_diagrams=state.architecture_diagrams or [],
            project_plan=state.project_plan,
            cost_estimate={'total_cost': 'TBD'},
            timeline='TBD',
            team_composition={},
            risk_assessment=[],
            success_criteria=[],
            executive_summary='Executive summary pending manual review',
            appendices=[],
            metadata={
                'generation_timestamp': self._get_current_timestamp(),
                'approval_status': 'needs_review',
                'quality_score': 50,
                'error': 'Proposal generation failed'
            }
        )

# Factory function to create QA + CEO agent
def create_qa_ceo_agent(llm: Optional[ChatOpenAI] = None) -> QACEOAgent:
    """Create and configure QA + CEO agent"""
    return QACEOAgent(llm=llm)