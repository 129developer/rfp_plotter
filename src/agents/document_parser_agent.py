"""
Document parsing agent for extracting structured information from RFP documents.
Uses LangChain and OpenAI to analyze and extract key information.
"""

from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import logging

from ..models.rfp_models import RFPExtractedData, WorkflowState
from ..utils.document_parser import DocumentParser

logger = logging.getLogger(__name__)


class DocumentParserAgent:
    """Agent for parsing RFP documents and extracting structured information"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.1):
        """
        Initialize the document parser agent.
        
        Args:
            model_name: OpenAI model to use
            temperature: Model temperature for consistency
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=RFPExtractedData)
        
        # Create the extraction prompt
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "Please analyze the following RFP document and extract structured information:\n\n{document_content}")
        ])
        
        # Create the extraction chain
        self.extraction_chain = self.extraction_prompt | self.llm | self.parser
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for document extraction"""
        return """You are an expert RFP (Request for Proposal) document analyzer. Your task is to extract structured information from RFP documents and organize it according to the specified schema.

When analyzing an RFP document, focus on extracting the following types of information:

**Business Information:**
- Project title and RFP name
- Client organization and department
- Business goals and expected outcomes
- Success criteria and KPIs

**Technical Information:**
- Required functional modules and features
- System integrations needed
- Technology preferences and constraints
- Scalability and performance requirements
- Hosting and infrastructure constraints

**Scope & Delivery:**
- Project phases and timeline
- Mandatory deliverables
- Out-of-scope items
- Dependencies on client or third parties
- Acceptance criteria

**Constraints:**
- Budget ranges or cost expectations
- Vendor restrictions or requirements
- Security and compliance requirements
- Legacy system constraints

**Additional Metadata:**
- RFP release and submission dates
- Evaluation criteria
- Contact information

**Instructions:**
1. Extract information exactly as stated in the document
2. If information is not explicitly stated, leave the field empty rather than making assumptions
3. Convert long paragraphs into bullet points when appropriate
4. Identify and extract user roles for potential user story generation
5. Look for implicit requirements that may not be explicitly stated
6. Pay attention to "must have" vs "nice to have" requirements

Format your response as a valid JSON object matching the RFPExtractedData schema.

{format_instructions}"""
    
    def parse_document(self, state: WorkflowState) -> WorkflowState:
        """
        Parse a document and extract structured information.
        
        Args:
            state: Current workflow state containing document information
            
        Returns:
            Updated workflow state with extracted data
        """
        try:
            # Extract document content if not already available
            if not state.document_content and state.document_path:
                state.document_content = DocumentParser.extract_text_from_file(state.document_path)
            
            if not state.document_content:
                raise ValueError("No document content available for parsing")
            
            # Format the prompt with schema instructions
            formatted_prompt = self.extraction_prompt.format_messages(
                document_content=state.document_content,
                format_instructions=self.parser.get_format_instructions()
            )
            
            # Extract structured data using the LLM
            logger.info("Starting document extraction with LLM...")
            extracted_data = self.extraction_chain.invoke({
                "document_content": state.document_content
            })
            
            # Store raw content for reference
            extracted_data.raw_content = state.document_content
            
            # Update state
            state.extracted_data = extracted_data
            state.current_step = "document_parsed"
            state.processing_status = "document_parsed"
            
            logger.info("Document extraction completed successfully")
            return state
            
        except Exception as e:
            error_msg = f"Error parsing document: {str(e)}"
            logger.error(error_msg)
            state.processing_errors.append(error_msg)
            state.processing_status = "error"
            return state
    
    def validate_extraction(self, extracted_data: RFPExtractedData) -> List[str]:
        """
        Validate the extracted data and return any issues found.
        
        Args:
            extracted_data: The extracted RFP data
            
        Returns:
            List of validation issues (empty if no issues)
        """
        issues = []
        
        # Check for essential information
        if not extracted_data.project_title:
            issues.append("Project title not found")
        
        if not extracted_data.client_organization:
            issues.append("Client organization not identified")
        
        if not extracted_data.business_goals:
            issues.append("No business goals extracted")
        
        if not extracted_data.mandatory_deliverables:
            issues.append("No mandatory deliverables identified")
        
        # Check for technical requirements
        if not extracted_data.functional_modules and not extracted_data.technology_preferences:
            issues.append("No technical requirements identified")
        
        return issues
    
    def enhance_extraction(self, state: WorkflowState, focus_areas: List[str] = None) -> WorkflowState:
        """
        Perform a second pass extraction focusing on specific areas that may have been missed.
        
        Args:
            state: Current workflow state
            focus_areas: Specific areas to focus on (e.g., ['technical', 'timeline', 'budget'])
            
        Returns:
            Updated workflow state with enhanced extraction
        """
        if not state.extracted_data or not state.document_content:
            return state
        
        try:
            # Create focused extraction prompt
            focus_prompt = self._create_focus_prompt(focus_areas or [])
            
            enhanced_prompt = ChatPromptTemplate.from_messages([
                ("system", focus_prompt),
                ("human", """Based on the initial extraction, please review the document again and provide additional details for the specified focus areas.

Initial extraction summary:
- Project: {project_title}
- Client: {client_organization}
- Business goals: {business_goals_count} identified
- Deliverables: {deliverables_count} identified
- Technical modules: {modules_count} identified

Document content:
{document_content}""")
            ])
            
            # Invoke focused extraction
            response = enhanced_prompt | self.llm | self.parser
            
            enhanced_data = response.invoke({
                "project_title": state.extracted_data.project_title or "Not specified",
                "client_organization": state.extracted_data.client_organization or "Not specified",
                "business_goals_count": len(state.extracted_data.business_goals),
                "deliverables_count": len(state.extracted_data.mandatory_deliverables),
                "modules_count": len(state.extracted_data.functional_modules),
                "document_content": state.document_content
            })
            
            # Merge enhanced data with original extraction
            state.extracted_data = self._merge_extracted_data(state.extracted_data, enhanced_data)
            
            logger.info("Enhanced extraction completed")
            return state
            
        except Exception as e:
            error_msg = f"Error in enhanced extraction: {str(e)}"
            logger.error(error_msg)
            state.processing_errors.append(error_msg)
            return state
    
    def _create_focus_prompt(self, focus_areas: List[str]) -> str:
        """Create a focused extraction prompt for specific areas"""
        base_prompt = """You are performing a focused re-analysis of an RFP document. Pay special attention to the following areas:"""
        
        focus_instructions = {
            'technical': "- Technical requirements, system architecture, integrations, and technology constraints",
            'timeline': "- Project timelines, milestones, deadlines, and delivery schedules",
            'budget': "- Cost expectations, budget constraints, and commercial terms",
            'scope': "- Project scope, deliverables, and out-of-scope items",
            'constraints': "- Technical constraints, security requirements, and compliance needs"
        }
        
        for area in focus_areas:
            if area in focus_instructions:
                base_prompt += f"\n{focus_instructions[area]}"
        
        base_prompt += f"\n\nExtract information in the RFPExtractedData format:\n{self.parser.get_format_instructions()}"
        
        return base_prompt
    
    def _merge_extracted_data(self, original: RFPExtractedData, enhanced: RFPExtractedData) -> RFPExtractedData:
        """Merge enhanced extraction data with original data"""
        # Create a new instance with merged data
        merged_data = original.model_copy()
        
        # Merge lists by extending with new unique items
        for field_name, field_value in enhanced.model_dump().items():
            if isinstance(field_value, list) and field_value:
                original_list = getattr(merged_data, field_name) or []
                # Add new items that aren't already present
                for item in field_value:
                    if item not in original_list:
                        original_list.append(item)
                setattr(merged_data, field_name, original_list)
            elif isinstance(field_value, str) and field_value and not getattr(merged_data, field_name):
                # Fill in missing string fields
                setattr(merged_data, field_name, field_value)
        
        return merged_data


def create_document_parser_node():
    """Create a LangGraph node for document parsing"""
    agent = DocumentParserAgent()
    
    def parse_node(state: WorkflowState) -> WorkflowState:
        """LangGraph node function for document parsing"""
        return agent.parse_document(state)
    
    return parse_node