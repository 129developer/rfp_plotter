# RFP LangGraph Agent - Enhanced Multi-Agent System

A sophisticated LangGraph-based multi-agent system for processing RFP (Request for Proposal) documents and generating professional proposal responses using specialized AI agents.

## 🎯 Enhanced Multi-Agent Architecture

The system features **7 specialized agents** working together in a supervisor-orchestrated workflow:

### Agent Roles

1. **🎭 Supervisor Agent (Orchestrator)**
   - Routes workflow between specialized agents
   - Validates outputs and manages state transitions
   - Handles error recovery and quality gates

2. **🔍 Deep Researcher Agent**
   - Conducts external research using Google Search API
   - Extracts and validates RFP requirements
   - Gathers competitive intelligence and market data

3. **🏗️ Solution Architect Agent**
   - Designs comprehensive technical architecture
   - Recommends optimal technology stacks from database
   - Generates Mermaid diagram specifications

4. **🎨 Designer Agent**
   - Creates professional architectural diagrams
   - Converts Mermaid specs to SVG/PNG formats
   - Ensures presentation-ready visualizations

5. **📊 Project Manager Agent**
   - Generates detailed project plans and estimates
   - Calculates effort, timeline, and resource allocation
   - Performs comprehensive risk assessment

6. **👨‍💼 CTO Agent (Technical Validator)**
   - Conducts security audits and architecture reviews
   - Analyzes technical debt and maintainability
   - Has authority to approve/reject technical solutions

7. **✅ QA + CEO Agent (Final Approver)**
   - Performs quality assurance and tone analysis
   - Conducts executive-level strategic review
   - Provides final approval with detailed feedback

## 🚀 Features

### Standard Workflow
- **Document Parsing**: Extracts structured information from PDF, DOCX, TXT, and Markdown RFP documents
- **Data Normalization**: Cleans and standardizes extracted data for consistency
- **Proposal Generation**: Creates comprehensive proposals following professional templates
- **Architecture Diagrams**: Generates solution and deployment architecture diagrams
- **PowerPoint Generation**: Produces professional PowerPoint presentations

### Enhanced Multi-Agent Workflow
- **Specialized Expertise**: Each agent brings domain-specific knowledge and tools
- **Quality Gates**: Multiple validation layers ensure high-quality output
- **CTO Rejection**: Technical solutions can be rejected and reworked automatically
- **Executive Approval**: Final CEO-level review and strategic sign-off
- **External Research**: Google Search integration for competitive intelligence
- **Professional Diagrams**: Automated generation of presentation-ready visuals
- **Risk Management**: Detailed project planning with comprehensive risk mitigation
- **Security Auditing**: Built-in security validation and compliance checking

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. Clone or download the project:
```bash
git clone <repository-url>
cd rfp-langgraph-agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your OpenAI API key:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 🎯 Usage

### Web Interface (Streamlit)

Launch the interactive web interface:

```bash
streamlit run demo_app.py
```

Then open your browser to `http://localhost:8501` and:

1. Enter your OpenAI API key in the sidebar
2. Configure vendor information
3. Upload an RFP document or use the sample
4. Click "Process RFP" to generate the proposal
5. Download the generated JSON and PowerPoint files

### Command Line Interface

#### Standard Workflow
Process RFP documents using the original single-agent workflow:

```bash
# Process a file
python cli_demo.py --file path/to/rfp.pdf --output ./output

# Use the sample RFP
python cli_demo.py --sample --output ./output

# Process text content directly
python cli_demo.py --text "Your RFP content here..." --output ./output
```

#### Enhanced Multi-Agent Workflow
Use the new 7-agent specialized workflow for superior results:

```bash
# Enhanced workflow with all 7 specialized agents
python cli_demo.py --enhanced --sample --output ./output

# Enhanced workflow with external research (requires Google API keys)
python cli_demo.py --enhanced --sample \
  --google-api-key "your-google-api-key" \
  --search-engine-id "your-search-engine-id" \
  --output ./output

# Enhanced workflow with debug and intermediate results
python cli_demo.py --enhanced --sample --debug --save-intermediate --json-only
```

#### Additional Options

```bash
# Generate only JSON (skip PowerPoint)
python cli_demo.py --sample --json-only

# Enable debug mode with intermediate results
python cli_demo.py --sample --debug --save-intermediate

# Custom vendor information
python cli_demo.py --sample --vendor-name "Your Company" --contact-email "you@company.com"
```

### Python API

#### Standard Workflow
Use the original workflow programmatically:

```python
from src.workflows.rfp_workflow import process_rfp_document
from src.utils.ppt_generator import generate_ppt_from_proposal

# Process an RFP document
result = process_rfp_document(
    document_path="path/to/rfp.pdf",
    config={
        "vendor_name": "Your Company",
        "contact_email": "contact@yourcompany.com"
    }
)

# Check results
if result.proposal:
    print(f"Generated proposal for: {result.proposal.cover.client_name}")
    
    # Generate PowerPoint
    ppt_path = generate_ppt_from_proposal(result.proposal)
    print(f"PowerPoint saved to: {ppt_path}")
```

#### Enhanced Multi-Agent Workflow
Use the new specialized multi-agent system:

```python
from src.workflows.enhanced_rfp_workflow import create_enhanced_rfp_workflow, WorkflowConfig

# Configure enhanced workflow
config = WorkflowConfig(
    llm_model="gpt-4o-mini",
    google_api_key="your-google-api-key",  # Optional for external research
    search_engine_id="your-search-engine-id",  # Optional
    max_iterations=50,
    enable_supervisor_validation=True,
    enable_cto_rejection=True,
    enable_quality_gates=True
)

# Create enhanced workflow
enhanced_workflow = create_enhanced_rfp_workflow(config)

# Prepare documents
raw_documents = [{
    'type': 'file',
    'path': 'path/to/rfp.pdf',
    'content': None
}]

# Process with all 7 specialized agents
result = enhanced_workflow.process_rfp(raw_documents)

# Check results
if result.proposal:
    print(f"Enhanced proposal generated!")
    print(f"Final approval: {result.final_approval.approval_status.value}")
    print(f"Quality score: {result.final_approval.overall_quality_score}%")
    
    # Access specialized outputs
    if result.cto_validation:
        print(f"CTO validation: {result.cto_validation.validation_result.value}")
    
    if result.architecture_diagrams:
        print(f"Generated {len(result.architecture_diagrams)} diagrams")
```

## 📁 Project Structure

```
rfp-langgraph-agent/
├── src/
│   ├── agents/                 # Specialized AI agents
│   │   ├── supervisor_agent.py          # Orchestrator & router
│   │   ├── deep_researcher_agent.py     # External research & validation
│   │   ├── solution_architect_agent.py  # Technical architecture design
│   │   ├── designer_agent.py            # Diagram generation & visualization
│   │   ├── project_manager_agent.py     # Planning & estimation
│   │   ├── cto_agent.py                 # Technical validation & approval
│   │   ├── qa_ceo_agent.py              # Quality assurance & final approval
│   │   ├── document_parser_agent.py     # Document processing (standard)
│   │   ├── data_normalizer_agent.py     # Data normalization (standard)
│   │   ├── proposal_generator_agent.py  # Proposal generation (standard)
│   │   └── architecture_generator_agent.py # Architecture generation (standard)
│   ├── tools/                  # Specialized agent tools
│   │   ├── search_tools.py              # Google Search & web research
│   │   ├── tech_stack_tools.py          # Technology recommendation database
│   │   ├── security_tools.py            # Security auditing & validation
│   │   ├── estimation_tools.py          # Project estimation & planning
│   │   └── quality_tools.py             # Quality assurance & tone analysis
│   ├── models/                 # Pydantic data models
│   │   └── rfp_models.py
│   ├── utils/                  # Utility functions
│   │   ├── document_parser.py
│   │   ├── diagram_generator.py         # Enhanced with Mermaid CLI support
│   │   └── ppt_generator.py
│   └── workflows/              # LangGraph workflows
│       ├── rfp_workflow.py              # Standard single-agent workflow
│       └── enhanced_rfp_workflow.py     # Enhanced multi-agent workflow
├── examples/
│   └── sample_rfp.md          # Sample RFP document
├── demo_app.py                # Streamlit web interface
├── cli_demo.py                # Enhanced command-line interface
├── test_enhanced_system.py    # Comprehensive test suite
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## 🧪 Testing

### Comprehensive Test Suite
Run the complete test suite to verify all components:

```bash
python test_enhanced_system.py
```

This will test:
- Individual agent creation and functionality
- Specialized tool initialization
- Enhanced multi-agent workflow integration
- Error handling and validation

### Quick Test Commands

```bash
# Test standard workflow
python cli_demo.py --sample --json-only --debug

# Test enhanced workflow
python cli_demo.py --enhanced --sample --json-only --debug

# Test with external research (requires Google API keys)
python cli_demo.py --enhanced --sample \
  --google-api-key "your-key" \
  --search-engine-id "your-id" \
  --json-only
```

## 🔄 Workflow Overview

### Standard Workflow
The original RFP processing workflow:

1. **Document Parsing**: Extract structured information from the RFP document
2. **Data Normalization**: Clean and standardize the extracted data
3. **Proposal Generation**: Map data to proposal template and generate structured output
4. **Architecture Enhancement**: Create and enhance solution architecture diagrams
5. **Validation**: Validate the generated proposal for completeness
6. **Output Generation**: Generate JSON and PowerPoint outputs

### Enhanced Multi-Agent Workflow
The new specialized multi-agent workflow:

1. **🎭 Supervisor**: Orchestrates workflow and validates agent transitions
2. **🔍 Deep Researcher**: Conducts external research and requirement extraction
3. **🏗️ Solution Architect**: Designs technical architecture and selects tech stack
4. **🎨 Designer**: Creates professional diagrams and visualizations
5. **📊 Project Manager**: Generates detailed plans, estimates, and risk assessments
6. **👨‍💼 CTO**: Validates technical solutions and security compliance
7. **✅ QA + CEO**: Performs final quality assurance and executive approval

Each agent has specialized tools and can iterate until quality gates are met.

## 📊 Generated Outputs

### JSON Structure
The system generates a comprehensive JSON structure containing:
- Cover information (title, client, vendor details)
- Background and objectives
- Project phases with deliverables and acceptance criteria
- Solution architecture with diagram specifications
- Deployment view and environments
- Project plan with milestones
- Commercial proposal with cost breakdown
- User stories and technology components

### PowerPoint Presentation
The generated PowerPoint includes:
- Professional cover slide
- Background and objectives
- Phase-by-phase scope and deliverables
- Solution architecture overview
- Deployment architecture
- Project timeline and milestones
- Commercial proposal with cost tables
- Appendix with user stories and components

## 🎨 Customization

### Modifying Templates
- Edit `src/agents/proposal_generator_agent.py` to customize proposal structure
- Modify `src/utils/ppt_generator.py` to change PowerPoint styling and layout
- Update `src/models/rfp_models.py` to add new data fields

### Adding New Agents
1. Create a new agent in `src/agents/`
2. Add the agent node to the workflow in `src/workflows/rfp_workflow.py`
3. Update the state model if needed

### Custom Diagram Generation
- Extend `src/utils/diagram_generator.py` to support new diagram types
- Modify architecture generation logic in `src/agents/architecture_generator_agent.py`

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the project root directory
2. **API Key Issues**: Verify your OpenAI API key is set correctly
3. **File Format Errors**: Check that your RFP document is in a supported format (PDF, DOCX, TXT, MD)
4. **Memory Issues**: For large documents, consider increasing system memory or processing in chunks

### Debug Mode
Enable debug mode to see detailed processing information:
```bash
python cli_demo.py --sample --debug --save-intermediate
```

### Logging
The system uses Python's logging module. Set the log level to see more details:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 Example RFP

The project includes a sample RFP document (`examples/sample_rfp.md`) that demonstrates:
- Customer Management System requirements
- Technical specifications and constraints
- Project phases and deliverables
- Integration requirements
- Budget and timeline constraints

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- Uses [LangChain](https://github.com/langchain-ai/langchain) for LLM integration
- PowerPoint generation powered by [python-pptx](https://github.com/scanny/python-pptx)
- Web interface built with [Streamlit](https://streamlit.io/)

## 📞 Support

For questions, issues, or contributions, please:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed information about your problem

---

**Note**: This system requires an OpenAI API key and generates costs based on usage. Please monitor your API usage and set appropriate limits.