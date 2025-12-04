"""
Deep Researcher Agent for comprehensive RFP analysis and external research
Focuses on extracting and structuring client needs from raw documents with external research
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from ..models.rfp_models import WorkflowState, RFPExtractedData
from ..tools.search_tools import create_search_tools
from ..utils.document_parser import DocumentParser

logger = logging.getLogger(__name__)

@dataclass
class ResearchContext:
    """Context information for research activities"""
    client_name: str
    industry: str
    project_type: str
    key_technologies: List[str]
    research_priorities: List[str]

class DeepResearcherAgent:
    """
    Deep Researcher Agent that performs comprehensive analysis and external research
    
    Responsibilities:
    - Extract structured requirements from raw RFP documents
    - Conduct external research on client, industry, and technologies
    - Analyze market context and competitive landscape
    - Structure findings for downstream agents
    """
    
    def __init__(self, llm: Optional[ChatOpenAI] = None, google_api_key: Optional[str] = None, search_engine_id: Optional[str] = None):
        self.llm = llm or ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
        self.document_parser = DocumentParser()
        
        # Initialize search tools
        self.search_tools = create_search_tools(google_api_key, search_engine_id)
        self.google_search = self.search_tools['google_search']
        self.technology_research = self.search_tools['technology_research']
        self.client_research = self.search_tools['client_research']
        
        # System prompt for the Deep Researcher
        self.system_prompt = """You are the Deep Researcher Agent. Your sole focus is comprehensive, grounded research and extraction of requirements from the raw RFP text and external sources. You must find the 'why' and 'what' of the client's needs.

Your responsibilities:
1. Extract and structure all requirements from RFP documents
2. Research client background and industry context
3. Investigate mentioned technologies and standards
4. Analyze market rates and competitive landscape
5. Identify implicit requirements and constraints
6. Structure findings for technical solution design

Focus on:
- Comprehensive requirement extraction
- Deep client and industry research
- Technology and market analysis
- Identifying gaps and assumptions
- Providing rich context for solution design

Always ground your analysis in evidence from the documents and research findings."""
    
    def process_rfp_documents(self, state: WorkflowState) -> WorkflowState:
        """
        Process RFP documents and conduct comprehensive research
        
        Args:
            state: Current workflow state with raw documents
            
        Returns:
            Updated state with extracted data and research findings
        """
        try:
            logger.info("Deep Researcher Agent: Starting comprehensive RFP analysis")
            
            # Step 1: Extract structured information from documents
            extracted_data = self._extract_structured_requirements(state.raw_documents)
            
            # Step 2: Identify research context
            research_context = self._identify_research_context(extracted_data)
            
            # Step 3: Conduct external research
            research_findings = self._conduct_external_research(research_context)
            
            # Step 4: Enhance extracted data with research findings
            enhanced_data = self._enhance_with_research(extracted_data, research_findings)
            
            # Step 5: Validate and structure final output
            final_data = self._validate_and_structure_output(enhanced_data)
            
            # Update state
            state.extracted_data = final_data
            state.current_step = "deep_research_complete"
            state.last_agent_executed = "deep_researcher"
            
            logger.info("Deep Researcher Agent: Analysis complete")
            return state
            
        except Exception as e:
            logger.error(f"Deep Researcher Agent failed: {e}")
            # Return state with error information
            state.errors.append(f"Deep Researcher Agent error: {str(e)}")
            return state
    
    def _extract_structured_requirements(self, raw_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract structured requirements from raw RFP documents
        
        Args:
            raw_documents: List of raw document data
            
        Returns:
            Structured requirements data
        """
        try:
            # Combine all document content
            combined_content = ""
            document_metadata = []
            
            for doc in raw_documents:
                combined_content += f"\n\n--- Document: {doc.get('filename', 'Unknown')} ---\n"
                content = doc.get('content')
                combined_content += content if content else ''
                document_metadata.append({
                    'filename': doc.get('filename', 'Unknown'),
                    'type': doc.get('type', 'Unknown'),
                    'size': len(content) if content else 0
                })
            
            # Create extraction prompt
            extraction_prompt = f"""
Analyze the following RFP documents and extract structured requirements:

{combined_content}

Extract and structure the following information:

1. CLIENT INFORMATION:
   - Organization name and background
   - Industry and business context
   - Key stakeholders and decision makers
   - Current technology landscape

2. PROJECT OVERVIEW:
   - Project title and description
   - Business objectives and goals
   - Success criteria and KPIs
   - Project scope and boundaries

3. FUNCTIONAL REQUIREMENTS:
   - Core functionality needed
   - User roles and permissions
   - Business processes to support
   - Integration requirements

4. TECHNICAL REQUIREMENTS:
   - Technology preferences or constraints
   - Performance requirements
   - Security and compliance needs
   - Scalability and availability requirements

5. CONSTRAINTS AND ASSUMPTIONS:
   - Budget constraints
   - Timeline requirements
   - Resource limitations
   - Regulatory or compliance requirements

6. EVALUATION CRITERIA:
   - How proposals will be evaluated
   - Weighting of different factors
   - Mandatory vs. preferred requirements

Provide detailed, structured output in JSON format with clear categorization.
"""
            
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=extraction_prompt)
            ]
            print(messages)
            response = self.llm.invoke(messages)
            print(response)
            # Parse the response and structure the data
            extracted_info = self._parse_extraction_response(response.content)
            
            # Add metadata
            extracted_info['document_metadata'] = document_metadata
            extracted_info['extraction_timestamp'] = self._get_current_timestamp()
            
            return extracted_info
            
        except Exception as e:
            logger.error(f"Requirement extraction failed: {e}")
            return self._get_default_extraction()
    
    def _identify_research_context(self, extracted_data: Dict[str, Any]) -> ResearchContext:
        """
        Identify key research priorities based on extracted data
        
        Args:
            extracted_data: Structured requirements data
            
        Returns:
            Research context for external research
        """
        try:
            client_info = extracted_data.get('client_information', {})
            project_info = extracted_data.get('project_overview', {})
            technical_reqs = extracted_data.get('technical_requirements', {})
            
            # Extract key information
            client_name = client_info.get('organization_name', 'Unknown Client')
            industry = client_info.get('industry', 'General')
            project_type = project_info.get('project_type', 'Software Development')
            
            # Identify key technologies mentioned
            key_technologies = []
            tech_prefs = technical_reqs.get('technology_preferences', [])
            if isinstance(tech_prefs, list):
                key_technologies.extend(tech_prefs)
            elif isinstance(tech_prefs, str):
                # Extract technology names from text
                key_technologies = self._extract_technology_names(tech_prefs)
            
            # Determine research priorities
            research_priorities = [
                'client_background',
                'industry_standards',
                'technology_analysis',
                'market_rates',
                'competitive_landscape'
            ]
            
            # Add specific priorities based on requirements
            if 'security' in str(technical_reqs).lower():
                research_priorities.append('security_standards')
            if 'compliance' in str(technical_reqs).lower():
                research_priorities.append('compliance_requirements')
            if 'integration' in str(extracted_data).lower():
                research_priorities.append('integration_patterns')
            
            return ResearchContext(
                client_name=client_name,
                industry=industry,
                project_type=project_type,
                key_technologies=key_technologies,
                research_priorities=research_priorities
            )
            
        except Exception as e:
            logger.error(f"Research context identification failed: {e}")
            return ResearchContext(
                client_name="Unknown Client",
                industry="General",
                project_type="Software Development",
                key_technologies=[],
                research_priorities=['client_background', 'technology_analysis']
            )
    
    def _conduct_external_research(self, context: ResearchContext) -> Dict[str, Any]:
        """
        Conduct comprehensive external research
        
        Args:
            context: Research context with priorities
            
        Returns:
            Research findings organized by category
        """
        try:
            research_findings = {
                'client_research': {},
                'industry_analysis': {},
                'technology_research': {},
                'market_analysis': {},
                'competitive_landscape': {}
            }
            
            # Client background research
            if 'client_background' in context.research_priorities:
                logger.info(f"Researching client: {context.client_name}")
                client_data = self.client_research.research_client(context.client_name, context.industry)
                research_findings['client_research'] = client_data
            
            # Technology research
            if 'technology_analysis' in context.research_priorities and context.key_technologies:
                logger.info(f"Researching technologies: {context.key_technologies}")
                tech_research = {}
                for tech in context.key_technologies[:3]:  # Limit to top 3 technologies
                    tech_data = self.technology_research.research_technology(tech)
                    tech_research[tech] = tech_data
                research_findings['technology_research'] = tech_research
            
            # Industry standards research
            if 'industry_standards' in context.research_priorities:
                logger.info(f"Researching industry standards for: {context.industry}")
                industry_results = self.google_search.search(
                    f"{context.industry} industry standards best practices", 
                    num_results=3
                )
                research_findings['industry_analysis'] = {
                    'standards': [r.snippet for r in industry_results],
                    'sources': [r.url for r in industry_results]
                }
            
            # Market rates research
            if 'market_rates' in context.research_priorities:
                logger.info(f"Researching market rates for: {context.project_type}")
                market_results = self.google_search.search(
                    f"{context.project_type} development costs market rates", 
                    num_results=3
                )
                research_findings['market_analysis'] = {
                    'cost_insights': [r.snippet for r in market_results],
                    'sources': [r.url for r in market_results]
                }
            
            # Competitive landscape
            if 'competitive_landscape' in context.research_priorities:
                logger.info(f"Researching competitive landscape")
                competitive_results = self.google_search.search(
                    f"{context.industry} {context.project_type} vendors solutions", 
                    num_results=3
                )
                research_findings['competitive_landscape'] = {
                    'competitors': [r.snippet for r in competitive_results],
                    'sources': [r.url for r in competitive_results]
                }
            
            research_findings['research_timestamp'] = self._get_current_timestamp()
            research_findings['research_context'] = {
                'client_name': context.client_name,
                'industry': context.industry,
                'project_type': context.project_type,
                'technologies_researched': context.key_technologies
            }
            
            return research_findings
            
        except Exception as e:
            logger.error(f"External research failed: {e}")
            return self._get_default_research_findings()
    
    def _enhance_with_research(self, 
                             extracted_data: Dict[str, Any], 
                             research_findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance extracted requirements with research findings
        
        Args:
            extracted_data: Original extracted requirements
            research_findings: External research results
            
        Returns:
            Enhanced requirements with research context
        """
        try:
            enhanced_data = extracted_data.copy()
            
            # Add research findings to client information
            if 'client_research' in research_findings:
                client_info = enhanced_data.get('client_information', {})
                client_research = research_findings['client_research']
                
                client_info['research_background'] = client_research.get('background', [])
                client_info['technology_preferences_research'] = client_research.get('tech_preferences', [])
                client_info['industry_context'] = client_research.get('industry_context', [])
                
                enhanced_data['client_information'] = client_info
            
            # Enhance technical requirements with technology research
            if 'technology_research' in research_findings:
                tech_reqs = enhanced_data.get('technical_requirements', {})
                tech_research = research_findings['technology_research']
                
                tech_reqs['technology_analysis'] = {}
                for tech, research in tech_research.items():
                    tech_reqs['technology_analysis'][tech] = {
                        'best_practices': research.get('best_practices', []),
                        'security_considerations': research.get('security_considerations', []),
                        'performance_notes': research.get('performance_notes', [])
                    }
                
                enhanced_data['technical_requirements'] = tech_reqs
            
            # Add market context
            if 'market_analysis' in research_findings:
                market_data = research_findings['market_analysis']
                enhanced_data['market_context'] = {
                    'cost_insights': market_data.get('cost_insights', []),
                    'market_trends': market_data.get('market_trends', [])
                }
            
            # Add competitive context
            if 'competitive_landscape' in research_findings:
                competitive_data = research_findings['competitive_landscape']
                enhanced_data['competitive_context'] = {
                    'competitors': competitive_data.get('competitors', []),
                    'differentiation_opportunities': self._identify_differentiation_opportunities(competitive_data)
                }
            
            # Add industry standards context
            if 'industry_analysis' in research_findings:
                industry_data = research_findings['industry_analysis']
                enhanced_data['industry_standards'] = {
                    'standards': industry_data.get('standards', []),
                    'compliance_considerations': self._extract_compliance_considerations(industry_data)
                }
            
            # Add research metadata
            enhanced_data['research_metadata'] = {
                'research_conducted': True,
                'research_timestamp': research_findings.get('research_timestamp'),
                'research_scope': list(research_findings.keys()),
                'enhancement_timestamp': self._get_current_timestamp()
            }
            
            return enhanced_data
            
        except Exception as e:
            logger.error(f"Research enhancement failed: {e}")
            return extracted_data
    
    def _validate_and_structure_output(self, enhanced_data: Dict[str, Any]) -> RFPExtractedData:
        """
        Validate and structure the final output
        
        Args:
            enhanced_data: Enhanced requirements data
            
        Returns:
            Structured RFPExtractedData object
        """
        try:
            # Extract client information
            client_info = enhanced_data.get('client_information', {})
            project_info = enhanced_data.get('project_overview', {})
            requirements = enhanced_data.get('requirements', {})
            tech_reqs = enhanced_data.get('technical_requirements', {})
            constraints = enhanced_data.get('constraints', {})
            eval_criteria = enhanced_data.get('evaluation_criteria', {})
            
            # Extract evaluation criteria as list
            if isinstance(eval_criteria, dict):
                criteria_list = eval_criteria.get('criteria', [])
            elif isinstance(eval_criteria, list):
                criteria_list = eval_criteria
            else:
                criteria_list = []
            
            # Map to RFPExtractedData fields
            return RFPExtractedData(
                project_title=project_info.get('project_title'),
                client_organization=client_info.get('organization_name'),
                division_department=client_info.get('division'),
                business_goals=project_info.get('objectives', []),
                success_criteria=project_info.get('success_criteria', []),
                
                functional_modules=self._ensure_list(requirements.get('functional', [])),
                integrations=self._ensure_list(requirements.get('integrations', [])),
                technology_preferences=self._ensure_list(tech_reqs.get('technology_preferences', [])),
                technology_constraints=self._ensure_list(tech_reqs.get('constraints', [])),
                scalability_requirements=self._ensure_list(tech_reqs.get('scalability', [])),
                performance_expectations=self._ensure_list(tech_reqs.get('performance', [])),
                hosting_constraints=self._ensure_list(tech_reqs.get('hosting', [])),
                
                defined_phases=self._ensure_list(project_info.get('phases', [])),
                mandatory_deliverables=self._ensure_list(requirements.get('deliverables', [])),
                out_of_scope_items=self._ensure_list(requirements.get('out_of_scope', [])),
                timelines=self._ensure_list(constraints.get('timeline_list', [constraints.get('timeline', '')])),
                dependencies=self._ensure_list(requirements.get('dependencies', [])),
                acceptance_criteria=self._ensure_list(requirements.get('acceptance_criteria', [])),
                
                budget_ranges=self._ensure_list([constraints.get('budget', 'Not specified')]),
                vendor_restrictions=self._ensure_list(constraints.get('vendor_restrictions', [])),
                security_requirements=self._ensure_list(tech_reqs.get('security', [])),
                interoperability_constraints=self._ensure_list(tech_reqs.get('interoperability', [])),
                
                rfp_release_date=enhanced_data.get('rfp_release_date'),
                submission_deadline=enhanced_data.get('submission_deadline'),
                evaluation_criteria=self._ensure_list(criteria_list),
                contact_persons=self._ensure_list(enhanced_data.get('contact_persons', [])),
                
                raw_content=str(enhanced_data)
            )
            
        except Exception as e:
            logger.error(f"Output validation failed: {e}")
            return self._get_default_extracted_data()
    
    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure value is a list of strings"""
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [value]
        if value is None:
            return []
        return [str(value)]

    def _parse_extraction_response(self, response_content: str) -> Dict[str, Any]:
        """Parse LLM response for requirement extraction"""
        try:
            # Try to extract JSON from response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_content[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback: structure the response manually
                return self._structure_text_response(response_content)
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from extraction response, using text parsing")
            return self._structure_text_response(response_content)
    
    def _parse_validation_response(self, response_content: str, fallback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response for validation"""
        try:
            # Try to extract JSON from response
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_content[json_start:json_end]
                return json.loads(json_str)
            else:
                return fallback_data
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from validation response, using fallback")
            return fallback_data
    
    def _structure_text_response(self, text_response: str) -> Dict[str, Any]:
        """Structure text response when JSON parsing fails"""
        return {
            'client_information': {
                'organization_name': 'Client Organization',
                'industry': 'Technology',
                'background': text_response[:200] + '...' if len(text_response) > 200 else text_response
            },
            'project_overview': {
                'project_title': 'RFP Project',
                'description': 'Project extracted from RFP documents',
                'objectives': ['Extracted from RFP analysis']
            },
            'requirements': {
                'functional': ['Requirements extracted from documents'],
                'non_functional': ['Performance and quality requirements']
            },
            'technical_requirements': {
                'technology_preferences': [],
                'constraints': []
            },
            'constraints': {
                'budget': 'To be determined',
                'timeline': 'As specified in RFP'
            },
            'evaluation_criteria': ['Technical capability', 'Cost', 'Timeline']
        }
    
    def _extract_technology_names(self, text: str) -> List[str]:
        """Extract technology names from text"""
        # Common technology keywords
        tech_keywords = [
            'java', 'python', 'javascript', 'react', 'angular', 'vue',
            'nodejs', 'express', 'django', 'flask', 'spring',
            'mysql', 'postgresql', 'mongodb', 'redis',
            'aws', 'azure', 'gcp', 'docker', 'kubernetes',
            'microservices', 'api', 'rest', 'graphql'
        ]
        
        text_lower = text.lower()
        found_technologies = []
        
        for tech in tech_keywords:
            if tech in text_lower:
                found_technologies.append(tech.title())
        
        return found_technologies[:5]  # Limit to top 5
    
    def _identify_differentiation_opportunities(self, competitive_data: Dict[str, Any]) -> List[str]:
        """Identify differentiation opportunities from competitive research"""
        return [
            "Focus on unique technical capabilities",
            "Emphasize superior customer service",
            "Highlight cost-effective solutions",
            "Demonstrate industry expertise",
            "Showcase innovative approaches"
        ]
    
    def _extract_compliance_considerations(self, industry_data: Dict[str, Any]) -> List[str]:
        """Extract compliance considerations from industry research"""
        return [
            "Industry-specific regulatory requirements",
            "Data privacy and security standards",
            "Quality assurance protocols",
            "Audit and reporting requirements"
        ]
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp string"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _get_default_extraction(self) -> Dict[str, Any]:
        """Get default extraction data for error cases"""
        return {
            'client_information': {
                'organization_name': 'Unknown Client',
                'industry': 'General',
                'background': 'Client information not available'
            },
            'project_overview': {
                'project_title': 'RFP Project',
                'description': 'Project details extraction failed',
                'objectives': ['Manual analysis required']
            },
            'requirements': {
                'functional': ['Requirements analysis failed'],
                'non_functional': ['Manual review needed']
            },
            'technical_requirements': {
                'technology_preferences': [],
                'constraints': ['Analysis incomplete']
            },
            'constraints': {
                'budget': 'Not specified',
                'timeline': 'Not specified'
            },
            'evaluation_criteria': ['Manual review required'],
            'extraction_error': True
        }
    
    def _get_default_research_findings(self) -> Dict[str, Any]:
        """Get default research findings for error cases"""
        return {
            'client_research': {
                'background': ['Research unavailable'],
                'tech_preferences': [],
                'industry_context': []
            },
            'technology_research': {},
            'market_analysis': {
                'cost_insights': ['Market research unavailable'],
                'market_trends': []
            },
            'competitive_landscape': {
                'competitors': ['Competitive analysis unavailable']
            },
            'industry_analysis': {
                'standards': ['Industry research unavailable']
            },
            'research_error': True
        }
    
    def _get_default_extracted_data(self) -> RFPExtractedData:
        """Get default extracted data for error cases"""
        return RFPExtractedData(
            project_title='RFP Project',
            client_organization='Unknown Client',
            business_goals=['Analysis failed'],
            functional_modules=['Manual review required'],
            evaluation_criteria=['Manual review required'],
            raw_content='Extraction failed'
        )

def create_deep_researcher_agent(llm: Optional[ChatOpenAI] = None, 
                                google_api_key: Optional[str] = None,
                                search_engine_id: Optional[str] = None) -> DeepResearcherAgent:
    """Create and configure deep researcher agent"""
    return DeepResearcherAgent(llm=llm, google_api_key=google_api_key, search_engine_id=search_engine_id)


def create_deep_researcher_node():
    """Create a LangGraph node for the Deep Researcher agent"""
    agent = create_deep_researcher_agent()

    def deep_researcher_node(state: WorkflowState) -> WorkflowState:
        result = agent.process_rfp_documents(state)
        # Optional type safety: convert dict to WorkflowState if needed
        if isinstance(result, dict):
            result = WorkflowState.parse_obj(result)
        return result

    return deep_researcher_node
