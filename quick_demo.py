#!/usr/bin/env python3
"""
Quick demo script to show the RFP LangGraph Agent in action.
This script demonstrates the core functionality with the sample RFP.
"""

import os
import json
from pathlib import Path

def main():
    """Run a quick demo of the system"""
    print("🚀 RFP LangGraph Agent - Quick Demo")
    print("=" * 50)
    
    # Check if API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not found!")
        print("To run the full demo with LLM processing:")
        print("1. Set your API key: export OPENAI_API_KEY='your-key'")
        print("2. Run: python cli_demo.py --sample")
        print("\nFor now, showing system structure and capabilities...")
        print()
    
    # Show project structure
    print("📁 Project Structure:")
    print("├── src/")
    print("│   ├── agents/          # LangGraph agent nodes")
    print("│   ├── models/          # Pydantic data models")
    print("│   ├── utils/           # Utility functions")
    print("│   └── workflows/       # LangGraph workflows")
    print("├── examples/")
    print("│   └── sample_rfp.md    # Sample RFP document")
    print("├── demo_app.py          # Streamlit web interface")
    print("├── cli_demo.py          # Command-line interface")
    print("└── test_system.py       # System tests")
    print()
    
    # Show sample RFP preview
    sample_path = "examples/sample_rfp.md"
    if os.path.exists(sample_path):
        print("📄 Sample RFP Preview:")
        with open(sample_path, 'r') as f:
            content = f.read()
        
        # Show first few lines
        lines = content.split('\n')[:15]
        for line in lines:
            print(f"   {line}")
        print("   ...")
        print(f"   [Total: {len(content)} characters, {len(lines)} lines]")
        print()
    
    # Show workflow steps
    print("🔄 Processing Workflow:")
    print("1. 📄 Document Parsing    - Extract structured info from RFP")
    print("2. 🧹 Data Normalization  - Clean and standardize data")
    print("3. 📋 Proposal Generation - Map to template structure")
    print("4. 🏗️  Architecture Design - Generate solution diagrams")
    print("5. ✅ Validation         - Check completeness")
    print("6. 📊 Output Generation  - Create JSON + PowerPoint")
    print()
    
    # Show available interfaces
    print("🖥️  Available Interfaces:")
    print("1. Web Interface:    streamlit run demo_app.py")
    print("2. Command Line:     python cli_demo.py --sample")
    print("3. Python API:       from src.workflows.rfp_workflow import process_rfp_document")
    print()
    
    # Show expected outputs
    print("📤 Generated Outputs:")
    print("• JSON Structure:")
    print("  - Cover information (title, client, vendor)")
    print("  - Background and objectives")
    print("  - Project phases with deliverables")
    print("  - Solution architecture with diagrams")
    print("  - Commercial proposal with costs")
    print()
    print("• PowerPoint Presentation:")
    print("  - Professional cover slide")
    print("  - Phase-by-phase breakdown")
    print("  - Architecture overview")
    print("  - Cost tables and timeline")
    print()
    
    # Show next steps
    print("🎯 Next Steps:")
    if not os.getenv("OPENAI_API_KEY"):
        print("1. Get an OpenAI API key from https://platform.openai.com/")
        print("2. Set it: export OPENAI_API_KEY='your-key'")
        print("3. Run full demo: python cli_demo.py --sample")
    else:
        print("1. Run web demo: streamlit run demo_app.py")
        print("2. Or CLI demo: python cli_demo.py --sample")
        print("3. Try with your own RFP: python cli_demo.py --file your_rfp.pdf")
    
    print("\n✨ The system is ready to process RFP documents!")

if __name__ == "__main__":
    main()