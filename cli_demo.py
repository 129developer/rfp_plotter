#!/usr/bin/env python3
"""
Command-line interface for the RFP LangGraph Agent.
Provides a simple CLI to test the RFP processing pipeline.
"""

import argparse
import os
import json
import sys
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import our modules
try:
    from src.workflows.rfp_workflow import process_rfp_document
    from src.workflows.enhanced_rfp_workflow import create_enhanced_rfp_workflow, WorkflowConfig
    from src.utils.ppt_generator import generate_ppt_from_proposal
    from src.utils.document_parser import validate_document_file
    from src.models.rfp_models import WorkflowState
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure you're running from the project root directory and all dependencies are installed.")
    sys.exit(1)


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="RFP LangGraph Agent - Process RFP documents and generate proposals"
    )
    
    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "--file", "-f",
        type=str,
        help="Path to RFP document file (PDF, DOCX, TXT, MD)"
    )
    input_group.add_argument(
        "--sample",
        action="store_true",
        help="Use the sample RFP document"
    )
    input_group.add_argument(
        "--text", "-t",
        type=str,
        help="RFP content as text string"
    )
    
    # Output options
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output directory for generated files (default: current directory)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Only generate JSON output, skip PowerPoint"
    )
    parser.add_argument(
        "--ppt-only",
        action="store_true",
        help="Only generate PowerPoint, skip JSON file"
    )
    
    # Configuration options
    parser.add_argument(
        "--vendor-name",
        type=str,
        default="TechSolutions Inc.",
        help="Vendor company name (default: TechSolutions Inc.)"
    )
    parser.add_argument(
        "--contact-email",
        type=str,
        default="proposals@techsolutions.com",
        help="Contact email (default: proposals@techsolutions.com)"
    )
    parser.add_argument(
        "--api-key",
        type=str,
        help="OpenAI API key (can also be set via OPENAI_API_KEY environment variable)"
    )
    
    # Workflow options
    parser.add_argument(
        "--enhanced",
        action="store_true",
        help="Use enhanced multi-agent workflow (7 specialized agents)"
    )
    parser.add_argument(
        "--google-api-key",
        type=str,
        help="Google API key for external research (enhanced workflow only)"
    )
    parser.add_argument(
        "--search-engine-id",
        type=str,
        help="Google Custom Search Engine ID (enhanced workflow only)"
    )
    
    # Debug options
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    parser.add_argument(
        "--save-intermediate",
        action="store_true",
        help="Save intermediate processing results"
    )
    
    args = parser.parse_args()
    
    # Configure debug logging
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Set up API key
    if args.api_key:
        os.environ["OPENAI_API_KEY"] = args.api_key
    elif not os.getenv("OPENAI_API_KEY"):
        print("Error: OpenAI API key not provided.")
        print("Please set the OPENAI_API_KEY environment variable or use --api-key option.")
        sys.exit(1)
    
    # Determine input
    document_path = None
    document_content = None
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
        
        if not validate_document_file(args.file):
            print(f"Error: Invalid or unsupported file format: {args.file}")
            sys.exit(1)
        
        document_path = args.file
        print(f"Processing file: {args.file}")
        
    elif args.sample:
        sample_path = "examples/sample_rfp.md"
        if not os.path.exists(sample_path):
            print(f"Error: Sample RFP file not found: {sample_path}")
            sys.exit(1)
        
        document_path = sample_path
        print("Processing sample RFP document")
        
    elif args.text:
        document_content = args.text
        print("Processing provided text content")
    
    # Set up output directory
    output_dir = Path(args.output) if args.output else Path.cwd()
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Process RFP
        if args.enhanced:
            print("\n🔄 Starting enhanced multi-agent RFP processing...")
            print("   Using 7 specialized agents: Supervisor, Deep Researcher, Solution Architect,")
            print("   Designer, Project Manager, CTO, and QA + CEO")
            
            # Create enhanced workflow configuration
            workflow_config = WorkflowConfig(
                google_api_key=args.google_api_key or os.getenv("GOOGLE_API_KEY"),
                search_engine_id=args.search_engine_id or os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            )
            
            # Create enhanced workflow
            enhanced_workflow = create_enhanced_rfp_workflow(workflow_config)
            
            # Prepare raw documents
            raw_documents = []
            if document_path:
                raw_documents.append({
                    'type': 'file',
                    'path': document_path,
                    'content': None
                })
            elif document_content:
                raw_documents.append({
                    'type': 'text',
                    'path': None,
                    'content': document_content
                })
            
            # Process with enhanced workflow
            result = enhanced_workflow.process_rfp(raw_documents)
            
        else:
            print("\n🔄 Starting standard RFP processing...")
            
            config = {
                "vendor_name": args.vendor_name,
                "contact_email": args.contact_email
            }
            
            result = process_rfp_document(
                document_path=document_path,
                document_content=document_content,
                config=config
            )
        
        # Display results
        if args.enhanced:
            # Enhanced workflow results
            print(f"\n📊 Enhanced workflow completed!")
            
            if result.errors:
                print("\n⚠️ Processing errors:")
                for error in result.errors:
                    print(f"  • {error}")
            
            # Display workflow status
            if hasattr(result, 'metadata') and result.metadata:
                completion_status = result.metadata.get('completion_status', 'unknown')
                iteration_count = result.metadata.get('iteration_count', 0)
                print(f"   Status: {completion_status}")
                print(f"   Iterations: {iteration_count}")
            
            # Display agent execution summary
            if hasattr(result, 'last_agent_executed') and result.last_agent_executed:
                print(f"   Last agent: {result.last_agent_executed}")
            
            # Display approval status
            if result.final_approval:
                if isinstance(result.final_approval, dict):
                    approval_status = result.final_approval.get('approval_status')
                    if hasattr(approval_status, 'value'):
                        approval_status = approval_status.value
                    quality_score = result.final_approval.get('overall_quality_score', 0)
                else:
                    approval_status = result.final_approval.approval_status.value
                    quality_score = result.final_approval.overall_quality_score
                print(f"   Final approval: {approval_status} (Quality: {quality_score}%)")
            
            proposal = result.proposal
        else:
            # Standard workflow results
            print(f"\n📊 Processing completed with status: {result.processing_status}")
            
            if result.processing_errors:
                print("\n⚠️ Processing errors:")
                for error in result.processing_errors:
                    print(f"  • {error}")
            
            proposal = result.proposal
        
        if proposal:
            print(f"\n✅ Proposal generated successfully!")
            
            # Handle different proposal structures
            if args.enhanced:
                # Enhanced workflow proposal structure
                if hasattr(proposal, 'client_info') and proposal.client_info:
                    client_name = proposal.client_info.get('organization_name', 'Unknown Client')
                    print(f"   Client: {client_name}")
                
                if hasattr(proposal, 'project_overview') and proposal.project_overview:
                    project_title = proposal.project_overview.get('project_title', 'RFP Project')
                    print(f"   Project: {project_title}")
                
                if hasattr(proposal, 'project_plan') and proposal.project_plan:
                    phases = getattr(proposal.project_plan, 'phases', [])
                    print(f"   Phases: {len(phases)}")
                
                if hasattr(proposal, 'cost_estimate') and proposal.cost_estimate:
                    total_cost = proposal.cost_estimate.get('total_cost', 'TBD')
                    print(f"   Total cost: ${total_cost:,}" if isinstance(total_cost, (int, float)) else f"   Total cost: {total_cost}")
            else:
                # Standard workflow proposal structure
                print(f"   Project: {proposal.cover.project_title}")
                print(f"   Client: {proposal.cover.client_name}")
                print(f"   Phases: {len(proposal.phases)}")
                print(f"   Cost items: {len(proposal.commercials.cost_table)}")
            
            # Calculate total cost for standard workflow
            if not args.enhanced and hasattr(proposal, 'commercials') and proposal.commercials.cost_table:
                total_cost = sum(item.cost for item in proposal.commercials.cost_table)
                print(f"   Total cost: ${total_cost:,.2f}")
            
            # Save outputs
            if args.enhanced:
                # Enhanced workflow client name
                client_name = "Client"
                if hasattr(proposal, 'client_info') and proposal.client_info:
                    client_name = proposal.client_info.get('organization_name', 'Client')
                    client_name = client_name.replace(' ', '_')
            else:
                # Standard workflow client name
                client_name = proposal.cover.client_name.replace(' ', '_') if proposal.cover.client_name else "Client"
            
            # Save JSON
            if not args.ppt_only:
                json_path = output_dir / f"{client_name}_proposal.json"
                with open(json_path, 'w') as f:
                    if args.enhanced:
                        # Enhanced workflow - save the proposal directly
                        if hasattr(proposal, 'model_dump'):
                            json.dump(proposal.model_dump(), f, indent=2)
                        else:
                            # Fallback for non-Pydantic objects
                            json.dump(proposal.__dict__, f, indent=2, default=str)
                    else:
                        # Standard workflow
                        json.dump(result.proposal.model_dump(), f, indent=2)
                print(f"\n📄 JSON saved to: {json_path}")
            
            # Generate PowerPoint (only for standard workflow for now)
            if not args.json_only and not args.enhanced:
                print("\n📊 Generating PowerPoint presentation...")
                ppt_path = output_dir / f"{client_name}_proposal.pptx"
                
                try:
                    generated_ppt_path = generate_ppt_from_proposal(proposal, str(ppt_path))
                    print(f"📊 PowerPoint saved to: {generated_ppt_path}")
                except Exception as e:
                    print(f"❌ Error generating PowerPoint: {e}")
            elif not args.json_only and args.enhanced:
                print("\n📊 PowerPoint generation for enhanced workflow not yet implemented")
                print("   Use --json-only flag to save proposal data")
            
            # Save intermediate results if requested
            if args.save_intermediate:
                if args.enhanced:
                    # Enhanced workflow intermediate results
                    if result.extracted_data:
                        extracted_path = output_dir / f"{client_name}_extracted_data.json"
                        with open(extracted_path, 'w') as f:
                            if hasattr(result.extracted_data, 'model_dump'):
                                json.dump(result.extracted_data.model_dump(), f, indent=2)
                            elif isinstance(result.extracted_data, dict):
                                json.dump(result.extracted_data, f, indent=2, default=str)
                            else:
                                json.dump(result.extracted_data.__dict__, f, indent=2, default=str)
                        print(f"📄 Extracted data saved to: {extracted_path}")
                    
                    if result.architecture_design:
                        arch_path = output_dir / f"{client_name}_architecture_design.json"
                        with open(arch_path, 'w') as f:
                            if hasattr(result.architecture_design, 'model_dump'):
                                json.dump(result.architecture_design.model_dump(), f, indent=2)
                            elif isinstance(result.architecture_design, dict):
                                json.dump(result.architecture_design, f, indent=2, default=str)
                            else:
                                json.dump(result.architecture_design.__dict__, f, indent=2, default=str)
                        print(f"📄 Architecture design saved to: {arch_path}")
                    
                    if result.cto_validation:
                        cto_path = output_dir / f"{client_name}_cto_validation.json"
                        with open(cto_path, 'w') as f:
                            if hasattr(result.cto_validation, 'model_dump'):
                                json.dump(result.cto_validation.model_dump(), f, indent=2)
                            elif isinstance(result.cto_validation, dict):
                                json.dump(result.cto_validation, f, indent=2, default=str)
                            else:
                                json.dump(result.cto_validation.__dict__, f, indent=2, default=str)
                        print(f"📄 CTO validation saved to: {cto_path}")
                else:
                    # Standard workflow intermediate results
                    if result.extracted_data:
                        extracted_path = output_dir / f"{client_name}_extracted_data.json"
                        with open(extracted_path, 'w') as f:
                            json.dump(result.extracted_data.model_dump(), f, indent=2)
                        print(f"📄 Extracted data saved to: {extracted_path}")
                    
                    if result.normalized_data:
                        normalized_path = output_dir / f"{client_name}_normalized_data.json"
                        with open(normalized_path, 'w') as f:
                            json.dump(result.normalized_data.model_dump(), f, indent=2)
                        print(f"📄 Normalized data saved to: {normalized_path}")
        
        else:
            print("\n❌ No proposal was generated")
            if result.extracted_data:
                print("   However, extracted data is available")
                print(result.extracted_data)
            
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n⏹️ Processing interrupted by user")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    print("\n✅ Processing completed successfully!")


if __name__ == "__main__":
    main()