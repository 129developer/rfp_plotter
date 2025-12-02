# Deployment Instructions

## Creating GitHub Repository

To deploy this RFP LangGraph Agent to GitHub, follow these steps:

### 1. Create GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click "New repository" or go to https://github.com/new
3. Repository details:
   - **Repository name**: `rfp-langgraph-agent`
   - **Description**: `LangGraph-based agent for automated RFP proposal generation`
   - **Visibility**: Public (or Private if preferred)
   - **Initialize**: Do NOT initialize with README, .gitignore, or license (we already have these)

### 2. Push Local Repository

After creating the GitHub repository, run these commands in your terminal:

```bash
# Navigate to project directory
cd /workspace/project

# Add GitHub remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/rfp-langgraph-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Alternative: Using GitHub CLI

If you have GitHub CLI installed:

```bash
# Create repository and push
gh repo create rfp-langgraph-agent --public --source=. --remote=origin --push
```

## Repository Structure

The repository contains:

```
rfp-langgraph-agent/
├── .gitignore                 # Git ignore file
├── README.md                  # Main documentation
├── DEPLOYMENT.md              # This file
├── requirements.txt           # Python dependencies
├── demo_app.py               # Streamlit web interface
├── cli_demo.py               # Command-line interface
├── quick_demo.py             # Quick demo script
├── test_system.py            # System tests
├── src/                      # Main source code
│   ├── agents/               # LangGraph agent nodes
│   ├── models/               # Pydantic data models
│   ├── utils/                # Utility functions
│   └── workflows/            # LangGraph workflows
├── examples/                 # Sample files
│   └── sample_rfp.md        # Sample RFP document
└── rfp_template_definition_full.md  # Original template spec
```

## Environment Setup

After cloning the repository:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set OpenAI API key**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

3. **Run tests**:
   ```bash
   python test_system.py
   ```

4. **Start web interface**:
   ```bash
   streamlit run demo_app.py
   ```

## Usage Examples

### Web Interface
```bash
streamlit run demo_app.py
# Open browser to http://localhost:8501
```

### Command Line
```bash
# Process sample RFP
python cli_demo.py --sample

# Process your own file
python cli_demo.py --file path/to/your/rfp.pdf

# Generate only JSON
python cli_demo.py --sample --json-only
```

### Python API
```python
from src.workflows.rfp_workflow import process_rfp_document

result = process_rfp_document(
    document_path="examples/sample_rfp.md",
    config={"vendor_name": "Your Company"}
)

if result.proposal:
    print(f"Generated proposal for: {result.proposal.cover.client_name}")
```

## Features

✅ **Complete LangGraph Workflow**
- Document parsing (PDF, DOCX, TXT, MD)
- Data normalization and cleaning
- Proposal generation with template mapping
- Architecture diagram generation
- PowerPoint presentation creation

✅ **Multiple Interfaces**
- Streamlit web interface
- Command-line interface
- Python API

✅ **Professional Output**
- Structured JSON proposal data
- Professional PowerPoint presentations
- Architecture and deployment diagrams

✅ **Error Handling**
- Comprehensive validation
- Graceful error recovery
- Debug and logging capabilities

## System Requirements

- Python 3.8+
- OpenAI API key
- 2GB+ RAM (for document processing)
- Internet connection (for LLM API calls)

## Optional Dependencies

- GraphViz (for enhanced diagram generation)
- Additional document parsers for specialized formats

## Support

For issues or questions:
1. Check the README.md troubleshooting section
2. Run the test suite: `python test_system.py`
3. Enable debug mode: `python cli_demo.py --sample --debug`
4. Create an issue in the GitHub repository

---

**Note**: This system requires an OpenAI API key and generates costs based on usage. Monitor your API usage and set appropriate limits.