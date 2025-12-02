"""
Data normalization agent for cleaning and standardizing extracted RFP data.
Ensures consistent formatting and structure across different RFP styles.
"""

import re
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
import logging

from ..models.rfp_models import RFPExtractedData, WorkflowState

logger = logging.getLogger(__name__)


class DataNormalizerAgent:
    """Agent for normalizing and cleaning extracted RFP data"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.1):
        """
        Initialize the data normalizer agent.
        
        Args:
            model_name: OpenAI model to use
            temperature: Model temperature for consistency
        """
        self.llm = ChatOpenAI(model=model_name, temperature=temperature)
        self.parser = PydanticOutputParser(pydantic_object=RFPExtractedData)
        
        # Create normalization prompt
        self.normalization_prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("human", "Please normalize and clean the following extracted RFP data:\n\n{extracted_data}")
        ])
        
        # Create normalization chain
        self.normalization_chain = self.normalization_prompt | self.llm | self.parser
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for data normalization"""
        return """You are a data normalization specialist for RFP (Request for Proposal) documents. Your task is to clean, standardize, and improve the structure of extracted RFP data.

**Normalization Rules:**

1. **Text Cleaning:**
   - Remove excessive whitespace and line breaks
   - Fix capitalization inconsistencies
   - Standardize punctuation
   - Remove redundant information

2. **List Standardization:**
   - Convert long paragraphs into bullet points
   - Remove duplicate items
   - Ensure consistent formatting
   - Group related items together

3. **Requirement Classification:**
   - Convert "must" requirements into acceptance criteria
   - Distinguish between mandatory and optional items
   - Identify functional vs non-functional requirements

4. **Timeline Normalization:**
   - Convert timeline sentences into structured milestone objects
   - Standardize date formats
   - Extract specific deadlines and durations

5. **Technical Information:**
   - Standardize technology names and versions
   - Group related technical requirements
   - Identify integration points clearly

6. **User Role Identification:**
   - Extract and standardize user roles for user story generation
   - Identify stakeholder groups
   - Map roles to functional requirements

7. **Constraint Organization:**
   - Categorize constraints by type (technical, business, legal)
   - Prioritize constraints by impact
   - Identify dependencies between constraints

**Quality Improvements:**
- Expand abbreviations and acronyms
- Add context where information is unclear
- Ensure completeness of related information
- Maintain traceability to original content

**Output Requirements:**
- Return data in the same RFPExtractedData structure
- Preserve all original information while improving clarity
- Add explanatory notes where helpful
- Ensure consistency across all fields

{format_instructions}"""
    
    def normalize_data(self, state: WorkflowState) -> WorkflowState:
        """
        Normalize and clean extracted RFP data.
        
        Args:
            state: Current workflow state containing extracted data
            
        Returns:
            Updated workflow state with normalized data
        """
        try:
            if not state.extracted_data:
                raise ValueError("No extracted data available for normalization")
            
            logger.info("Starting data normalization...")
            
            # Convert extracted data to JSON for processing
            extracted_json = state.extracted_data.model_dump_json(indent=2)
            
            # Apply LLM-based normalization
            normalized_data = self.normalization_chain.invoke({
                "extracted_data": extracted_json,
                "format_instructions": self.parser.get_format_instructions()
            })
            
            # Apply rule-based normalization
            normalized_data = self._apply_rule_based_normalization(normalized_data)
            
            # Update state
            state.normalized_data = normalized_data
            state.current_step = "data_normalized"
            state.processing_status = "data_normalized"
            
            logger.info("Data normalization completed successfully")
            return state
            
        except Exception as e:
            error_msg = f"Error normalizing data: {str(e)}"
            logger.error(error_msg)
            state.processing_errors.append(error_msg)
            state.processing_status = "error"
            return state
    
    def _apply_rule_based_normalization(self, data: RFPExtractedData) -> RFPExtractedData:
        """Apply rule-based normalization to the data"""
        
        # Clean and standardize text fields
        if data.project_title:
            data.project_title = self._clean_text(data.project_title)
        
        if data.client_organization:
            data.client_organization = self._clean_text(data.client_organization)
        
        # Normalize lists
        data.business_goals = self._normalize_list(data.business_goals)
        data.success_criteria = self._normalize_list(data.success_criteria)
        data.functional_modules = self._normalize_list(data.functional_modules)
        data.integrations = self._normalize_list(data.integrations)
        data.technology_preferences = self._normalize_list(data.technology_preferences)
        data.technology_constraints = self._normalize_list(data.technology_constraints)
        data.mandatory_deliverables = self._normalize_list(data.mandatory_deliverables)
        data.out_of_scope_items = self._normalize_list(data.out_of_scope_items)
        data.dependencies = self._normalize_list(data.dependencies)
        data.acceptance_criteria = self._normalize_list(data.acceptance_criteria)
        
        # Standardize technology names
        data.technology_preferences = self._standardize_technology_names(data.technology_preferences)
        data.technology_constraints = self._standardize_technology_names(data.technology_constraints)
        
        # Extract and normalize timelines
        data.timelines = self._normalize_timelines(data.timelines)
        
        # Normalize budget information
        data.budget_ranges = self._normalize_budget_ranges(data.budget_ranges)
        
        return data
    
    def _clean_text(self, text: str) -> str:
        """Clean and standardize text"""
        if not text:
            return text
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Fix common formatting issues
        text = re.sub(r'\s+([,.;:])', r'\1', text)  # Remove space before punctuation
        text = re.sub(r'([.!?])\s*([a-z])', r'\1 \2', text)  # Ensure space after sentence endings
        
        return text
    
    def _normalize_list(self, items: List[str]) -> List[str]:
        """Normalize a list of items"""
        if not items:
            return items
        
        normalized = []
        for item in items:
            if not item or not item.strip():
                continue
            
            # Clean the item
            cleaned_item = self._clean_text(item)
            
            # Skip duplicates (case-insensitive)
            if not any(cleaned_item.lower() == existing.lower() for existing in normalized):
                normalized.append(cleaned_item)
        
        return normalized
    
    def _standardize_technology_names(self, tech_list: List[str]) -> List[str]:
        """Standardize technology names and versions"""
        if not tech_list:
            return tech_list
        
        # Common technology name mappings
        tech_mappings = {
            'javascript': 'JavaScript',
            'js': 'JavaScript',
            'typescript': 'TypeScript',
            'ts': 'TypeScript',
            'python': 'Python',
            'java': 'Java',
            'c#': 'C#',
            'csharp': 'C#',
            'dotnet': '.NET',
            '.net': '.NET',
            'nodejs': 'Node.js',
            'node.js': 'Node.js',
            'reactjs': 'React',
            'react.js': 'React',
            'vuejs': 'Vue.js',
            'vue.js': 'Vue.js',
            'angular': 'Angular',
            'angularjs': 'AngularJS',
            'mysql': 'MySQL',
            'postgresql': 'PostgreSQL',
            'postgres': 'PostgreSQL',
            'mongodb': 'MongoDB',
            'mongo': 'MongoDB',
            'redis': 'Redis',
            'elasticsearch': 'Elasticsearch',
            'aws': 'Amazon Web Services (AWS)',
            'azure': 'Microsoft Azure',
            'gcp': 'Google Cloud Platform (GCP)',
            'docker': 'Docker',
            'kubernetes': 'Kubernetes',
            'k8s': 'Kubernetes'
        }
        
        standardized = []
        for tech in tech_list:
            tech_lower = tech.lower().strip()
            standardized_name = tech_mappings.get(tech_lower, tech)
            if standardized_name not in standardized:
                standardized.append(standardized_name)
        
        return standardized
    
    def _normalize_timelines(self, timelines: List[str]) -> List[str]:
        """Normalize timeline information"""
        if not timelines:
            return timelines
        
        normalized = []
        for timeline in timelines:
            if not timeline:
                continue
            
            # Extract specific dates and durations
            timeline = self._clean_text(timeline)
            
            # Look for common timeline patterns
            timeline = re.sub(r'(\d+)\s*weeks?', r'\1 weeks', timeline, flags=re.IGNORECASE)
            timeline = re.sub(r'(\d+)\s*months?', r'\1 months', timeline, flags=re.IGNORECASE)
            timeline = re.sub(r'(\d+)\s*days?', r'\1 days', timeline, flags=re.IGNORECASE)
            
            normalized.append(timeline)
        
        return normalized
    
    def _normalize_budget_ranges(self, budget_ranges: List[str]) -> List[str]:
        """Normalize budget range information"""
        if not budget_ranges:
            return budget_ranges
        
        normalized = []
        for budget in budget_ranges:
            if not budget:
                continue
            
            # Clean and standardize budget format
            budget = self._clean_text(budget)
            
            # Standardize currency symbols and formats
            budget = re.sub(r'\$\s*(\d)', r'$\1', budget)  # Remove space after $
            budget = re.sub(r'(\d)\s*k\b', r'\1K', budget, flags=re.IGNORECASE)  # Standardize K
            budget = re.sub(r'(\d)\s*m\b', r'\1M', budget, flags=re.IGNORECASE)  # Standardize M
            
            normalized.append(budget)
        
        return normalized
    
    def validate_normalization(self, original: RFPExtractedData, normalized: RFPExtractedData) -> List[str]:
        """
        Validate that normalization preserved important information.
        
        Args:
            original: Original extracted data
            normalized: Normalized data
            
        Returns:
            List of validation issues
        """
        issues = []
        
        # Check that key information wasn't lost
        if original.project_title and not normalized.project_title:
            issues.append("Project title was lost during normalization")
        
        if original.client_organization and not normalized.client_organization:
            issues.append("Client organization was lost during normalization")
        
        # Check list lengths (normalized should not be significantly shorter)
        original_goals = len(original.business_goals)
        normalized_goals = len(normalized.business_goals)
        if original_goals > 0 and normalized_goals < original_goals * 0.7:
            issues.append(f"Significant loss of business goals: {original_goals} -> {normalized_goals}")
        
        original_deliverables = len(original.mandatory_deliverables)
        normalized_deliverables = len(normalized.mandatory_deliverables)
        if original_deliverables > 0 and normalized_deliverables < original_deliverables * 0.7:
            issues.append(f"Significant loss of deliverables: {original_deliverables} -> {normalized_deliverables}")
        
        return issues


def create_data_normalizer_node():
    """Create a LangGraph node for data normalization"""
    agent = DataNormalizerAgent()
    
    def normalize_node(state: WorkflowState) -> WorkflowState:
        """LangGraph node function for data normalization"""
        return agent.normalize_data(state)
    
    return normalize_node