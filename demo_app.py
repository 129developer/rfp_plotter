"""
Streamlit demo application for the RFP LangGraph Agent.
Provides a web interface to test the complete RFP processing pipeline.
"""

import streamlit as st
import os
import json
import tempfile
from pathlib import Path
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from src.workflows.rfp_workflow import process_rfp_document
    from src.utils.ppt_generator import generate_ppt_from_proposal
    from src.utils.document_parser import validate_document_file
    from src.models.rfp_models import WorkflowState
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.error("Please ensure you're running from the project root directory and all dependencies are installed.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="RFP LangGraph Agent Demo",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Main application function"""
    
    st.title("🤖 RFP LangGraph Agent Demo")
    st.markdown("---")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # OpenAI API Key input
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key to use the LLM agents"
        )
        
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ Please enter your OpenAI API key to proceed")
        
        st.markdown("---")
        
        # Vendor information
        st.subheader("Vendor Information")
        vendor_name = st.text_input("Vendor Name", value="TechSolutions Inc.")
        contact_email = st.text_input("Contact Email", value="proposals@techsolutions.com")
        
        st.markdown("---")
        
        # Processing options
        st.subheader("Processing Options")
        generate_ppt = st.checkbox("Generate PowerPoint", value=True)
        show_debug = st.checkbox("Show Debug Information", value=False)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📄 Input RFP Document")
        
        # Document input options
        input_method = st.radio(
            "Choose input method:",
            ["Upload File", "Use Sample RFP", "Paste Text"]
        )
        
        document_content = None
        document_path = None
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload RFP Document",
                type=['pdf', 'docx', 'txt', 'md'],
                help="Upload a PDF, DOCX, TXT, or Markdown file"
            )
            
            if uploaded_file is not None:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    document_path = tmp_file.name
                
                st.success(f"✅ File uploaded: {uploaded_file.name}")
                
        elif input_method == "Use Sample RFP":
            sample_path = "examples/sample_rfp.md"
            if os.path.exists(sample_path):
                document_path = sample_path
                st.success("✅ Using sample RFP document")
                
                # Show preview of sample RFP
                with st.expander("Preview Sample RFP"):
                    with open(sample_path, 'r') as f:
                        sample_content = f.read()
                    st.markdown(sample_content[:1000] + "..." if len(sample_content) > 1000 else sample_content)
            else:
                st.error("❌ Sample RFP file not found")
                
        elif input_method == "Paste Text":
            document_content = st.text_area(
                "Paste RFP Content",
                height=300,
                placeholder="Paste your RFP document content here..."
            )
            
            if document_content:
                st.success("✅ Text content provided")
        
        # Process button
        if st.button("🚀 Process RFP", type="primary", disabled=not api_key):
            if not document_path and not document_content:
                st.error("❌ Please provide an RFP document")
            else:
                process_rfp(document_path, document_content, vendor_name, contact_email, generate_ppt, show_debug)
    
    with col2:
        st.header("📊 Processing Results")
        
        # Results will be displayed here after processing
        if 'processing_results' not in st.session_state:
            st.info("👆 Upload an RFP document and click 'Process RFP' to see results here")
        else:
            display_results(st.session_state.processing_results, show_debug)

def process_rfp(document_path: Optional[str], document_content: Optional[str], 
               vendor_name: str, contact_email: str, generate_ppt: bool, show_debug: bool):
    """Process the RFP document through the workflow"""
    
    with st.spinner("🔄 Processing RFP document..."):
        try:
            # Validate document if path provided
            if document_path and not validate_document_file(document_path):
                st.error("❌ Invalid or unsupported document format")
                return
            
            # Process through workflow
            config = {
                "vendor_name": vendor_name,
                "contact_email": contact_email
            }
            
            result = process_rfp_document(
                document_path=document_path,
                document_content=document_content,
                config=config
            )
            
            # Store results in session state
            st.session_state.processing_results = {
                'workflow_state': result,
                'generate_ppt': generate_ppt,
                'show_debug': show_debug
            }
            
            # Clean up temporary file
            if document_path and document_path.startswith('/tmp'):
                try:
                    os.unlink(document_path)
                except:
                    pass
            
            st.success("✅ RFP processing completed!")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Error processing RFP: {str(e)}")
            if show_debug:
                st.exception(e)

def display_results(results: dict, show_debug: bool):
    """Display the processing results"""
    
    workflow_state: WorkflowState = results['workflow_state']
    generate_ppt = results['generate_ppt']
    
    # Status indicator
    status_colors = {
        'completed': '🟢',
        'completed_with_warnings': '🟡',
        'partial_success': '🟡',
        'failed': '🔴',
        'error': '🔴'
    }
    
    status_color = status_colors.get(workflow_state.processing_status, '⚪')
    st.markdown(f"**Status:** {status_color} {workflow_state.processing_status.replace('_', ' ').title()}")
    
    # Show errors if any
    if workflow_state.processing_errors:
        with st.expander("⚠️ Processing Errors", expanded=True):
            for error in workflow_state.processing_errors:
                st.error(error)
    
    # Show proposal summary if available
    if workflow_state.proposal:
        st.subheader("📋 Proposal Summary")
        
        proposal = workflow_state.proposal
        
        # Basic info
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Project Title", proposal.cover.project_title or "N/A")
            st.metric("Client", proposal.cover.client_name or "N/A")
        with col2:
            st.metric("Number of Phases", len(proposal.phases))
            st.metric("Cost Items", len(proposal.commercials.cost_table))
        
        # Phases overview
        if proposal.phases:
            st.subheader("📅 Project Phases")
            for phase in proposal.phases:
                with st.expander(f"Phase {phase.phase_number}: {phase.title}"):
                    st.write(f"**Scope:** {phase.scope_summary}")
                    if phase.deliverables:
                        st.write("**Deliverables:**")
                        for deliverable in phase.deliverables:
                            st.write(f"• {deliverable}")
        
        # Architecture overview
        if proposal.solution_architecture.architecture_summary:
            st.subheader("🏗️ Solution Architecture")
            st.write(proposal.solution_architecture.architecture_summary)
            
            if proposal.solution_architecture.key_technology_choices:
                st.write("**Key Technologies:**")
                for tech in proposal.solution_architecture.key_technology_choices:
                    st.write(f"• {tech}")
        
        # Cost summary
        if proposal.commercials.cost_table:
            st.subheader("💰 Cost Summary")
            
            cost_data = []
            total_cost = 0
            for item in proposal.commercials.cost_table:
                cost_data.append({
                    "Item": item.item,
                    "Cost": f"${item.cost:,.2f}",
                    "Description": item.description
                })
                total_cost += item.cost
            
            st.dataframe(cost_data, use_container_width=True)
            st.metric("Total Cost", f"${total_cost:,.2f}")
        
        # Download options
        st.subheader("📥 Downloads")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # JSON download
            json_data = json.dumps(workflow_state.proposal.model_dump(), indent=2)
            st.download_button(
                label="📄 Download JSON",
                data=json_data,
                file_name=f"{proposal.cover.client_name or 'proposal'}_data.json",
                mime="application/json"
            )
        
        with col2:
            # PowerPoint generation and download
            if generate_ppt:
                if st.button("📊 Generate PowerPoint"):
                    with st.spinner("Generating PowerPoint presentation..."):
                        try:
                            ppt_path = generate_ppt_from_proposal(proposal)
                            
                            with open(ppt_path, 'rb') as f:
                                ppt_data = f.read()
                            
                            st.download_button(
                                label="📊 Download PowerPoint",
                                data=ppt_data,
                                file_name=f"{proposal.cover.client_name or 'proposal'}_presentation.pptx",
                                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation"
                            )
                            
                            # Clean up
                            try:
                                os.unlink(ppt_path)
                            except:
                                pass
                                
                            st.success("✅ PowerPoint generated successfully!")
                            
                        except Exception as e:
                            st.error(f"❌ Error generating PowerPoint: {str(e)}")
    
    # Debug information
    if show_debug:
        st.subheader("🐛 Debug Information")
        
        with st.expander("Workflow State Details"):
            st.json({
                "current_step": workflow_state.current_step,
                "processing_status": workflow_state.processing_status,
                "has_extracted_data": bool(workflow_state.extracted_data),
                "has_normalized_data": bool(workflow_state.normalized_data),
                "has_proposal": bool(workflow_state.proposal),
                "processing_errors": workflow_state.processing_errors
            })
        
        if workflow_state.extracted_data:
            with st.expander("Extracted Data"):
                st.json(workflow_state.extracted_data.model_dump())
        
        if workflow_state.normalized_data:
            with st.expander("Normalized Data"):
                st.json(workflow_state.normalized_data.model_dump())

if __name__ == "__main__":
    main()