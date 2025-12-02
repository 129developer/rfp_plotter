"""
Quality assurance and analysis tools for the QA + CEO Agent
"""
import json
import logging
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class ToneCategory(Enum):
    """Tone categories for analysis"""
    PROFESSIONAL = "professional"
    TECHNICAL = "technical"
    EXECUTIVE = "executive"
    CASUAL = "casual"
    FORMAL = "formal"

class ReadingLevel(Enum):
    """Reading level categories"""
    ELEMENTARY = "elementary"
    MIDDLE_SCHOOL = "middle_school"
    HIGH_SCHOOL = "high_school"
    COLLEGE = "college"
    GRADUATE = "graduate"

@dataclass
class ToneAnalysisResult:
    """Result of tone analysis"""
    overall_tone: ToneCategory
    confidence_score: float
    reading_level: ReadingLevel
    issues: List[str]
    recommendations: List[str]
    word_count: int
    sentence_count: int
    avg_sentence_length: float

@dataclass
class CompletenessCheck:
    """Result of completeness checking"""
    field_name: str
    is_complete: bool
    is_meaningful: bool
    issues: List[str]
    recommendations: List[str]

class ToneAnalyzer:
    """Tool for analyzing tone, voice, and reading level of proposal text"""
    
    def __init__(self):
        self.professional_indicators = [
            'solution', 'implementation', 'methodology', 'approach', 'framework',
            'architecture', 'strategy', 'deliverable', 'milestone', 'objective',
            'requirement', 'specification', 'analysis', 'assessment', 'evaluation'
        ]
        
        self.technical_indicators = [
            'api', 'database', 'server', 'client', 'framework', 'library',
            'algorithm', 'protocol', 'interface', 'module', 'component',
            'architecture', 'infrastructure', 'deployment', 'configuration'
        ]
        
        self.executive_indicators = [
            'strategic', 'business', 'value', 'roi', 'investment', 'growth',
            'competitive', 'market', 'opportunity', 'revenue', 'cost',
            'efficiency', 'transformation', 'innovation', 'leadership'
        ]
        
        self.casual_indicators = [
            'easy', 'simple', 'quick', 'just', 'basically', 'pretty',
            'really', 'very', 'quite', 'kind of', 'sort of'
        ]
        
        self.problematic_phrases = [
            'we think', 'we believe', 'probably', 'maybe', 'might',
            'could be', 'should work', 'hopefully', 'try to'
        ]
    
    def analyze_tone(self, text: str, target_tone: ToneCategory = ToneCategory.PROFESSIONAL) -> ToneAnalysisResult:
        """
        Analyze the tone and quality of proposal text
        
        Args:
            text: Text to analyze
            target_tone: Expected tone category
            
        Returns:
            Tone analysis results
        """
        try:
            if not text or not text.strip():
                return self._get_empty_analysis()
            
            # Handle string input for target_tone
            if isinstance(target_tone, str):
                try:
                    target_tone = ToneCategory(target_tone)
                except ValueError:
                    logger.warning(f"Invalid tone category '{target_tone}', defaulting to PROFESSIONAL")
                    target_tone = ToneCategory.PROFESSIONAL
            
            # Basic text metrics
            words = text.split()
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            
            word_count = len(words)
            sentence_count = len(sentences)
            avg_sentence_length = word_count / max(sentence_count, 1)
            
            # Analyze tone indicators
            text_lower = text.lower()
            
            professional_score = sum(1 for indicator in self.professional_indicators 
                                   if indicator in text_lower)
            technical_score = sum(1 for indicator in self.technical_indicators 
                                if indicator in text_lower)
            executive_score = sum(1 for indicator in self.executive_indicators 
                                if indicator in text_lower)
            casual_score = sum(1 for indicator in self.casual_indicators 
                             if indicator in text_lower)
            
            # Determine overall tone
            scores = {
                ToneCategory.PROFESSIONAL: professional_score,
                ToneCategory.TECHNICAL: technical_score,
                ToneCategory.EXECUTIVE: executive_score,
                ToneCategory.CASUAL: casual_score
            }
            
            overall_tone = max(scores, key=scores.get)
            max_score = scores[overall_tone]
            confidence_score = min(max_score / max(word_count / 100, 1), 1.0)
            
            # Determine reading level
            reading_level = self._calculate_reading_level(avg_sentence_length, word_count)
            
            # Identify issues
            issues = []
            recommendations = []
            
            # Check for problematic phrases
            problematic_found = [phrase for phrase in self.problematic_phrases 
                               if phrase in text_lower]
            if problematic_found:
                issues.append(f"Uncertain language detected: {', '.join(problematic_found)}")
                recommendations.append("Use confident, definitive language in proposals")
            
            # Check sentence length
            if avg_sentence_length > 25:
                issues.append("Sentences are too long (average > 25 words)")
                recommendations.append("Break down complex sentences for better readability")
            elif avg_sentence_length < 10:
                issues.append("Sentences are too short (average < 10 words)")
                recommendations.append("Combine short sentences for better flow")
            
            # Check tone alignment
            if overall_tone != target_tone:
                issues.append(f"Tone mismatch: detected {overall_tone.value}, expected {target_tone.value}")
                recommendations.append(f"Adjust language to be more {target_tone.value}")
            
            # Check for passive voice (simplified detection)
            passive_indicators = ['was', 'were', 'been', 'being']
            passive_count = sum(1 for word in words if word.lower() in passive_indicators)
            if passive_count / word_count > 0.1:  # More than 10% passive indicators
                issues.append("Excessive passive voice detected")
                recommendations.append("Use active voice for stronger, clearer communication")
            
            return ToneAnalysisResult(
                overall_tone=overall_tone,
                confidence_score=confidence_score,
                reading_level=reading_level,
                issues=issues,
                recommendations=recommendations,
                word_count=word_count,
                sentence_count=sentence_count,
                avg_sentence_length=avg_sentence_length
            )
            
        except Exception as e:
            logger.error(f"Tone analysis failed: {e}")
            return self._get_default_analysis()
    
    def _calculate_reading_level(self, avg_sentence_length: float, word_count: int) -> ReadingLevel:
        """Calculate reading level based on text complexity"""
        # Simplified Flesch-Kincaid-like calculation
        if avg_sentence_length < 12:
            return ReadingLevel.MIDDLE_SCHOOL
        elif avg_sentence_length < 16:
            return ReadingLevel.HIGH_SCHOOL
        elif avg_sentence_length < 20:
            return ReadingLevel.COLLEGE
        else:
            return ReadingLevel.GRADUATE
    
    def _get_empty_analysis(self) -> ToneAnalysisResult:
        """Get analysis result for empty text"""
        return ToneAnalysisResult(
            overall_tone=ToneCategory.PROFESSIONAL,
            confidence_score=0.0,
            reading_level=ReadingLevel.HIGH_SCHOOL,
            issues=["No text provided for analysis"],
            recommendations=["Provide content for tone analysis"],
            word_count=0,
            sentence_count=0,
            avg_sentence_length=0.0
        )
    
    def _get_default_analysis(self) -> ToneAnalysisResult:
        """Get default analysis result for error cases"""
        return ToneAnalysisResult(
            overall_tone=ToneCategory.PROFESSIONAL,
            confidence_score=0.5,
            reading_level=ReadingLevel.COLLEGE,
            issues=["Analysis failed - manual review recommended"],
            recommendations=["Perform manual tone and quality review"],
            word_count=0,
            sentence_count=0,
            avg_sentence_length=15.0
        )

class CompletenessChecker:
    """Tool for validating completeness of proposal data"""
    
    def __init__(self):
        self.required_fields = {
            'cover': {
                'client_name': 'Client organization name',
                'project_title': 'Project title or name',
                'vendor_name': 'Vendor/proposing organization name',
                'date': 'Proposal date',
                'contact_info': 'Contact information'
            },
            'background': {
                'client_overview': 'Client background and context',
                'problem_statement': 'Problem or challenge description',
                'objectives': 'Project objectives and goals'
            },
            'phases': {
                'phase_list': 'Project phases or work breakdown',
                'deliverables': 'Key deliverables for each phase',
                'timeline': 'Project timeline and milestones'
            },
            'architecture': {
                'solution_overview': 'High-level solution description',
                'technical_approach': 'Technical implementation approach',
                'technology_stack': 'Proposed technology stack'
            },
            'commercials': {
                'cost_breakdown': 'Detailed cost breakdown',
                'payment_terms': 'Payment terms and schedule',
                'assumptions': 'Key assumptions and dependencies'
            }
        }
        
        self.placeholder_patterns = [
            r'\[.*?\]',  # [placeholder text]
            r'<.*?>',    # <placeholder text>
            r'TODO',     # TODO items
            r'TBD',      # To be determined
            r'XXX',      # XXX placeholders
            r'PLACEHOLDER',
            r'INSERT.*HERE',
            r'FILL.*IN'
        ]
    
    def check_completeness(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check completeness of proposal data against required fields
        
        Args:
            proposal_data: Proposal data to validate
            
        Returns:
            Completeness check results
        """
        try:
            results = {
                'overall_completeness': 0.0,
                'section_results': {},
                'missing_fields': [],
                'placeholder_fields': [],
                'recommendations': [],
                'critical_issues': []
            }
            
            total_fields = 0
            complete_fields = 0
            
            # Check each section
            for section_name, fields in self.required_fields.items():
                section_data = proposal_data.get(section_name, {})
                section_results = []
                
                for field_name, field_description in fields.items():
                    total_fields += 1
                    check_result = self._check_field_completeness(
                        section_data, field_name, field_description
                    )
                    section_results.append(check_result)
                    
                    if check_result.is_complete and check_result.is_meaningful:
                        complete_fields += 1
                    elif not check_result.is_complete:
                        results['missing_fields'].append(f"{section_name}.{field_name}")
                    elif not check_result.is_meaningful:
                        results['placeholder_fields'].append(f"{section_name}.{field_name}")
                
                results['section_results'][section_name] = {
                    'checks': section_results,
                    'completeness': sum(1 for c in section_results 
                                      if c.is_complete and c.is_meaningful) / len(section_results)
                }
            
            # Calculate overall completeness
            results['overall_completeness'] = complete_fields / total_fields if total_fields > 0 else 0.0
            
            # Generate recommendations
            results['recommendations'] = self._generate_completeness_recommendations(results)
            
            # Identify critical issues
            results['critical_issues'] = self._identify_critical_issues(results)
            
            return results
            
        except Exception as e:
            logger.error(f"Completeness check failed: {e}")
            return self._get_default_completeness_results()
    
    def _check_field_completeness(self, 
                                section_data: Dict[str, Any], 
                                field_name: str, 
                                field_description: str) -> CompletenessCheck:
        """Check completeness of a single field"""
        field_value = section_data.get(field_name)
        
        # Check if field exists and has content
        is_complete = field_value is not None and str(field_value).strip() != ""
        
        # Check if content is meaningful (not placeholder)
        is_meaningful = True
        issues = []
        recommendations = []
        
        if not is_complete:
            issues.append(f"Field '{field_name}' is missing or empty")
            recommendations.append(f"Provide {field_description}")
            is_meaningful = False
        else:
            # Check for placeholder patterns
            field_str = str(field_value).lower()
            for pattern in self.placeholder_patterns:
                if re.search(pattern, field_str, re.IGNORECASE):
                    is_meaningful = False
                    issues.append(f"Field '{field_name}' contains placeholder text")
                    recommendations.append(f"Replace placeholder with actual {field_description}")
                    break
            
            # Check for very short content (likely incomplete)
            if len(field_str.strip()) < 10:
                issues.append(f"Field '{field_name}' content is too brief")
                recommendations.append(f"Provide more detailed {field_description}")
            
            # Check for generic/template content
            generic_phrases = ['lorem ipsum', 'sample text', 'example', 'template']
            if any(phrase in field_str for phrase in generic_phrases):
                is_meaningful = False
                issues.append(f"Field '{field_name}' contains generic template content")
                recommendations.append(f"Replace with specific {field_description}")
        
        return CompletenessCheck(
            field_name=field_name,
            is_complete=is_complete,
            is_meaningful=is_meaningful,
            issues=issues,
            recommendations=recommendations
        )
    
    def _generate_completeness_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on completeness results"""
        recommendations = []
        
        completeness = results['overall_completeness']
        
        if completeness < 0.5:
            recommendations.append("CRITICAL: Proposal is significantly incomplete - major sections missing")
            recommendations.append("Complete all required fields before submission")
        elif completeness < 0.8:
            recommendations.append("WARNING: Proposal has missing or incomplete sections")
            recommendations.append("Review and complete all identified missing fields")
        elif completeness < 0.95:
            recommendations.append("Minor completeness issues identified")
            recommendations.append("Address remaining placeholder content")
        else:
            recommendations.append("Proposal completeness is satisfactory")
        
        # Specific recommendations for missing fields
        if results['missing_fields']:
            recommendations.append(f"Missing fields: {', '.join(results['missing_fields'])}")
        
        if results['placeholder_fields']:
            recommendations.append(f"Placeholder content in: {', '.join(results['placeholder_fields'])}")
        
        return recommendations
    
    def _identify_critical_issues(self, results: Dict[str, Any]) -> List[str]:
        """Identify critical issues that must be resolved"""
        critical_issues = []
        
        # Critical sections that must be complete
        critical_sections = ['cover', 'background', 'commercials']
        
        for section in critical_sections:
            section_result = results['section_results'].get(section, {})
            if section_result.get('completeness', 0) < 0.8:
                critical_issues.append(f"Critical section '{section}' is incomplete")
        
        # Overall completeness threshold
        if results['overall_completeness'] < 0.6:
            critical_issues.append("Overall proposal completeness below acceptable threshold")
        
        return critical_issues
    
    def _get_default_completeness_results(self) -> Dict[str, Any]:
        """Get default completeness results for error cases"""
        return {
            'overall_completeness': 0.0,
            'section_results': {},
            'missing_fields': [],
            'placeholder_fields': [],
            'recommendations': ['Completeness check failed - manual review required'],
            'critical_issues': ['Unable to validate proposal completeness']
        }

class ExecutiveReviewer:
    """Tool for executive-level review of proposals"""
    
    def review_executive_alignment(self, proposal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Review proposal for executive-level concerns and strategic alignment
        
        Args:
            proposal_data: Complete proposal data
            
        Returns:
            Executive review results
        """
        try:
            review_results = {
                'strategic_alignment': 'medium',
                'business_value_clarity': 'medium',
                'risk_assessment': 'medium',
                'executive_summary_quality': 'medium',
                'recommendations': [],
                'concerns': [],
                'approval_readiness': False
            }
            
            # Check executive summary quality
            exec_summary = proposal_data.get('executive_summary', '')
            if exec_summary:
                summary_quality = self._assess_executive_summary(exec_summary)
                review_results['executive_summary_quality'] = summary_quality
            else:
                review_results['concerns'].append("Missing executive summary")
            
            # Check business value articulation
            commercials = proposal_data.get('commercials', {})
            if commercials:
                value_clarity = self._assess_business_value(commercials)
                review_results['business_value_clarity'] = value_clarity
            else:
                review_results['concerns'].append("Missing commercial/business value section")
            
            # Check strategic alignment
            background = proposal_data.get('background', {})
            if background:
                alignment = self._assess_strategic_alignment(background)
                review_results['strategic_alignment'] = alignment
            else:
                review_results['concerns'].append("Missing background/strategic context")
            
            # Overall risk assessment
            architecture = proposal_data.get('architecture', {})
            phases = proposal_data.get('phases', {})
            risk_level = self._assess_overall_risk(architecture, phases, commercials)
            review_results['risk_assessment'] = risk_level
            
            # Generate executive recommendations
            review_results['recommendations'] = self._generate_executive_recommendations(review_results)
            
            # Determine approval readiness
            review_results['approval_readiness'] = self._determine_approval_readiness(review_results)
            
            return review_results
            
        except Exception as e:
            logger.error(f"Executive review failed: {e}")
            return self._get_default_executive_review()
    
    def _assess_executive_summary(self, summary: str) -> str:
        """Assess quality of executive summary"""
        if not summary or len(summary.strip()) < 100:
            return 'poor'
        
        # Check for key executive elements
        executive_elements = [
            'business', 'value', 'roi', 'investment', 'strategic',
            'competitive', 'growth', 'efficiency', 'transformation'
        ]
        
        summary_lower = summary.lower()
        element_count = sum(1 for element in executive_elements if element in summary_lower)
        
        if element_count >= 4:
            return 'high'
        elif element_count >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_business_value(self, commercials: Dict[str, Any]) -> str:
        """Assess clarity of business value proposition"""
        value_indicators = ['roi', 'cost_savings', 'revenue_impact', 'efficiency_gains', 'value_proposition']
        
        present_indicators = sum(1 for indicator in value_indicators 
                               if indicator in commercials and commercials[indicator])
        
        if present_indicators >= 3:
            return 'high'
        elif present_indicators >= 1:
            return 'medium'
        else:
            return 'low'
    
    def _assess_strategic_alignment(self, background: Dict[str, Any]) -> str:
        """Assess strategic alignment with client needs"""
        alignment_indicators = ['objectives', 'strategic_goals', 'business_drivers', 'success_criteria']
        
        present_indicators = sum(1 for indicator in alignment_indicators 
                               if indicator in background and background[indicator])
        
        if present_indicators >= 3:
            return 'high'
        elif present_indicators >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _assess_overall_risk(self, 
                           architecture: Dict[str, Any], 
                           phases: Dict[str, Any], 
                           commercials: Dict[str, Any]) -> str:
        """Assess overall project risk level"""
        risk_factors = 0
        
        # Technical complexity risk
        if architecture.get('complexity', 'medium') in ['high', 'very_high']:
            risk_factors += 1
        
        # Timeline risk
        if phases.get('timeline_pressure', 'normal') == 'tight':
            risk_factors += 1
        
        # Cost risk
        total_cost = commercials.get('total_cost', 0)
        if total_cost > 500000:  # High-value project
            risk_factors += 1
        
        if risk_factors >= 2:
            return 'high'
        elif risk_factors == 1:
            return 'medium'
        else:
            return 'low'
    
    def _generate_executive_recommendations(self, review_results: Dict[str, Any]) -> List[str]:
        """Generate executive-level recommendations"""
        recommendations = []
        
        if review_results['executive_summary_quality'] == 'low':
            recommendations.append("Strengthen executive summary with clear business value proposition")
        
        if review_results['business_value_clarity'] == 'low':
            recommendations.append("Articulate clear ROI and business benefits")
        
        if review_results['strategic_alignment'] == 'low':
            recommendations.append("Better align proposal with client's strategic objectives")
        
        if review_results['risk_assessment'] == 'high':
            recommendations.append("Develop comprehensive risk mitigation strategies")
        
        # General executive recommendations
        recommendations.extend([
            "Ensure proposal addresses executive decision criteria",
            "Include competitive differentiation and unique value proposition",
            "Provide clear success metrics and measurement approach"
        ])
        
        return recommendations
    
    def _determine_approval_readiness(self, review_results: Dict[str, Any]) -> bool:
        """Determine if proposal is ready for executive approval"""
        # Must have at least medium quality in all areas
        quality_scores = [
            review_results['strategic_alignment'],
            review_results['business_value_clarity'],
            review_results['executive_summary_quality']
        ]
        
        # Check if all scores are at least 'medium'
        acceptable_scores = ['medium', 'high']
        all_acceptable = all(score in acceptable_scores for score in quality_scores)
        
        # No critical concerns
        no_critical_concerns = len(review_results['concerns']) == 0
        
        return all_acceptable and no_critical_concerns
    
    def _get_default_executive_review(self) -> Dict[str, Any]:
        """Get default executive review for error cases"""
        return {
            'strategic_alignment': 'medium',
            'business_value_clarity': 'medium',
            'risk_assessment': 'medium',
            'executive_summary_quality': 'medium',
            'recommendations': ['Manual executive review recommended due to analysis failure'],
            'concerns': ['Unable to complete automated executive review'],
            'approval_readiness': False
        }

class QualityAssessment:
    """Main quality assessment engine that combines all quality tools"""
    
    def __init__(self):
        self.tone_analyzer = ToneAnalyzer()
        self.completeness_checker = CompletenessChecker()
        self.executive_reviewer = ExecutiveReviewer()
    
    def assess_document_quality(self, document_content: str, document_type: str = 'rfp') -> Dict[str, Any]:
        """
        Perform comprehensive quality assessment of a document
        
        Args:
            document_content: The document content to assess
            document_type: Type of document ('rfp', 'proposal', 'report')
            
        Returns:
            Comprehensive quality assessment results
        """
        try:
            # Perform tone analysis
            tone_results = self.tone_analyzer.analyze_tone(document_content)
            
            # Check completeness
            completeness_results = self.completeness_checker.check_completeness(
                document_content, document_type
            )
            
            # Executive review
            executive_results = self.executive_reviewer.review_executive_alignment(
                document_content
            )
            
            # Calculate overall quality score
            overall_score = self._calculate_overall_score(
                tone_results, completeness_results, executive_results
            )
            
            # Generate improvement recommendations
            recommendations = self._generate_improvement_recommendations(
                tone_results, completeness_results, executive_results
            )
            
            return {
                'overall_score': overall_score,
                'tone_analysis': tone_results,
                'completeness_check': completeness_results,
                'executive_review': executive_results,
                'recommendations': recommendations,
                'quality_level': self._determine_quality_level(overall_score),
                'approval_ready': self._is_approval_ready(
                    tone_results, completeness_results, executive_results
                )
            }
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            return self._get_default_assessment()
    
    def _calculate_overall_score(self, 
                               tone_results: Dict[str, Any],
                               completeness_results: Dict[str, Any],
                               executive_results: Dict[str, Any]) -> float:
        """Calculate overall quality score from component assessments"""
        try:
            # Convert qualitative scores to numeric
            score_mapping = {'low': 1, 'medium': 2, 'high': 3}
            
            # Tone score (30% weight)
            tone_score = score_mapping.get(tone_results.get('overall_tone', 'medium'), 2)
            
            # Completeness score (40% weight)
            completeness_score = completeness_results.get('completeness_percentage', 70) / 100 * 3
            
            # Executive alignment score (30% weight)
            exec_scores = [
                score_mapping.get(executive_results.get('strategic_alignment', 'medium'), 2),
                score_mapping.get(executive_results.get('business_value_clarity', 'medium'), 2),
                score_mapping.get(executive_results.get('executive_summary_quality', 'medium'), 2)
            ]
            exec_score = sum(exec_scores) / len(exec_scores)
            
            # Calculate weighted average
            overall = (tone_score * 0.3 + completeness_score * 0.4 + exec_score * 0.3)
            
            # Convert back to 0-100 scale
            return (overall / 3) * 100
            
        except Exception as e:
            logger.error(f"Score calculation failed: {e}")
            return 70.0  # Default score
    
    def _determine_quality_level(self, score: float) -> str:
        """Determine quality level based on score"""
        if score >= 85:
            return 'excellent'
        elif score >= 75:
            return 'good'
        elif score >= 60:
            return 'acceptable'
        else:
            return 'needs_improvement'
    
    def _is_approval_ready(self,
                          tone_results: Dict[str, Any],
                          completeness_results: Dict[str, Any],
                          executive_results: Dict[str, Any]) -> bool:
        """Determine if document is ready for approval"""
        try:
            # Check minimum thresholds
            tone_acceptable = tone_results.get('overall_tone') in ['medium', 'high']
            completeness_acceptable = completeness_results.get('completeness_percentage', 0) >= 80
            executive_acceptable = executive_results.get('approval_readiness', False)
            
            return tone_acceptable and completeness_acceptable and executive_acceptable
            
        except Exception:
            return False
    
    def _generate_improvement_recommendations(self,
                                            tone_results: Dict[str, Any],
                                            completeness_results: Dict[str, Any],
                                            executive_results: Dict[str, Any]) -> List[str]:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        # Tone improvements
        if tone_results.get('overall_tone') == 'low':
            recommendations.append("Improve document tone to be more professional and confident")
        
        tone_issues = tone_results.get('tone_issues', [])
        if tone_issues:
            recommendations.append(f"Address tone issues: {', '.join(tone_issues)}")
        
        # Completeness improvements
        missing_sections = completeness_results.get('missing_sections', [])
        if missing_sections:
            recommendations.append(f"Add missing sections: {', '.join(missing_sections)}")
        
        incomplete_sections = completeness_results.get('incomplete_sections', [])
        if incomplete_sections:
            recommendations.append(f"Complete sections: {', '.join(incomplete_sections)}")
        
        # Executive alignment improvements
        exec_concerns = executive_results.get('concerns', [])
        if exec_concerns:
            recommendations.extend([f"Address concern: {concern}" for concern in exec_concerns])
        
        exec_recommendations = executive_results.get('recommendations', [])
        recommendations.extend(exec_recommendations)
        
        # General recommendations if none specific
        if not recommendations:
            recommendations = [
                "Review document for clarity and completeness",
                "Ensure all sections are properly developed",
                "Verify alignment with business objectives"
            ]
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _get_default_assessment(self) -> Dict[str, Any]:
        """Get default assessment for error cases"""
        return {
            'overall_score': 70.0,
            'tone_analysis': {'overall_tone': 'medium', 'tone_issues': []},
            'completeness_check': {'completeness_percentage': 70, 'missing_sections': []},
            'executive_review': {'approval_readiness': False, 'concerns': ['Assessment failed']},
            'recommendations': ['Manual quality review recommended'],
            'quality_level': 'acceptable',
            'approval_ready': False
        }

# Factory function to create quality tools
def create_quality_tools() -> Dict[str, Any]:
    """Create and configure quality assurance tools"""
    tone_analyzer = ToneAnalyzer()
    completeness_checker = CompletenessChecker()
    executive_reviewer = ExecutiveReviewer()
    
    return {
        'tone_analyzer': tone_analyzer,
        'completeness_checker': completeness_checker,
        'executive_reviewer': executive_reviewer,
        'analyze_tone': tone_analyzer.analyze_tone,
        'check_completeness': completeness_checker.check_completeness,
        'review_executive_alignment': executive_reviewer.review_executive_alignment
    }