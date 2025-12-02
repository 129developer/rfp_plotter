#!/usr/bin/env python3
"""
Unit tests for diagram and solution output generation
Tests the Designer Agent and Solution Architect Agent file saving functionality
"""
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.designer_agent import DesignerAgent, DiagramSpecification, GeneratedDiagram
from src.agents.solution_architect_agent import SolutionArchitectAgent, ArchitectureDesign
from src.models.rfp_models import WorkflowState, RFPExtractedData


def test_designer_agent_saves_diagrams():
    """Test that Designer Agent saves diagrams to output folder"""
    print("\n" + "="*70)
    print("TEST 1: Designer Agent - Diagram Saving")
    print("="*70)
    
    # Create temporary output directory
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Temporary output directory: {temp_dir}")
    
    try:
        # Create mock LLM
        mock_llm = Mock()
        mock_llm.invoke = Mock(return_value=Mock(content="graph TB\n    A[Test] --> B[Diagram]"))
        
        # Create designer agent
        designer = DesignerAgent(llm=mock_llm)
        
        # Create sample diagrams
        sample_diagrams = [
            GeneratedDiagram(
                name="System Overview",
                description="Test system overview diagram",
                mermaid_spec="graph TB\n    A[Web App] --> B[API]\n    B --> C[(Database)]",
                svg_content="<svg>Test SVG Content</svg>",
                png_base64=None,
                metadata={"target_audience": "executive", "has_svg": True, "has_png": False}
            ),
            GeneratedDiagram(
                name="Technical Architecture",
                description="Test technical architecture",
                mermaid_spec="graph TB\n    Frontend --> Backend\n    Backend --> Database",
                svg_content="<svg>Technical SVG</svg>",
                png_base64=None,
                metadata={"target_audience": "technical", "has_svg": True, "has_png": False}
            )
        ]
        
        # Test the save method
        print("\n🔧 Testing _save_diagrams_to_folder method...")
        designer._save_diagrams_to_folder(sample_diagrams, temp_dir)
        
        # Check if diagrams directory was created
        diagrams_dir = os.path.join(temp_dir, "diagrams")
        assert os.path.exists(diagrams_dir), "❌ Diagrams directory not created"
        print(f"✅ Diagrams directory created: {diagrams_dir}")
        
        # Check if files were created
        expected_files = [
            "system_overview.mmd",
            "system_overview.svg",
            "system_overview_metadata.json",
            "technical_architecture.mmd",
            "technical_architecture.svg",
            "technical_architecture_metadata.json"
        ]
        
        created_files = os.listdir(diagrams_dir)
        print(f"\n📄 Files created ({len(created_files)}):")
        for file in sorted(created_files):
            file_path = os.path.join(diagrams_dir, file)
            file_size = os.path.getsize(file_path)
            print(f"   ✓ {file} ({file_size} bytes)")
        
        # Verify expected files exist
        for expected_file in expected_files:
            file_path = os.path.join(diagrams_dir, expected_file)
            assert os.path.exists(file_path), f"❌ Expected file not found: {expected_file}"
        
        print(f"\n✅ All {len(expected_files)} expected files created successfully")
        
        # Verify file contents
        mermaid_file = os.path.join(diagrams_dir, "system_overview.mmd")
        with open(mermaid_file, 'r') as f:
            content = f.read()
            assert "graph TB" in content, "❌ Mermaid file doesn't contain expected content"
            print(f"✅ Mermaid file contains valid content")
        
        svg_file = os.path.join(diagrams_dir, "system_overview.svg")
        with open(svg_file, 'r') as f:
            content = f.read()
            assert "<svg>" in content, "❌ SVG file doesn't contain expected content"
            print(f"✅ SVG file contains valid content")
        
        print("\n" + "="*70)
        print("✅ TEST 1 PASSED: Designer Agent saves diagrams correctly")
        print("="*70)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST 1 FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ TEST 1 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary directory")


def test_solution_architect_saves_markdown():
    """Test that Solution Architect Agent saves solution to Markdown"""
    print("\n" + "="*70)
    print("TEST 2: Solution Architect Agent - Markdown Saving")
    print("="*70)
    
    # Create temporary output directory
    temp_dir = tempfile.mkdtemp()
    print(f"📁 Temporary output directory: {temp_dir}")
    
    try:
        # Create mock LLM
        mock_llm = Mock()
        
        # Create solution architect agent
        architect = SolutionArchitectAgent(llm=mock_llm)
        
        # Create sample architecture design
        sample_architecture = ArchitectureDesign(
            solution_overview="## Test Solution Overview\n\nThis is a test solution for a web application.",
            architecture_pattern={
                "name": "Monolithic Architecture",
                "description": "Single deployable unit for simplicity",
                "benefits": ["Simple deployment", "Easy to develop", "Cost-effective"]
            },
            technology_stack={
                "technologies": {
                    "frontend": type('Tech', (), {'name': 'React'})(),
                    "backend": type('Tech', (), {'name': 'Node.js'})(),
                    "database": type('Tech', (), {'name': 'PostgreSQL'})()
                }
            },
            system_components=[
                {
                    "name": "Web Application",
                    "type": "frontend",
                    "technology": "React",
                    "responsibilities": ["User interface", "Client-side logic"]
                },
                {
                    "name": "API Server",
                    "type": "backend",
                    "technology": "Node.js",
                    "responsibilities": ["Business logic", "API endpoints"]
                }
            ],
            integration_points=[
                {
                    "name": "External API",
                    "type": "REST API",
                    "purpose": "Third-party integration",
                    "pattern": "API Gateway"
                }
            ],
            scalability_strategy={
                "horizontal_scaling": {
                    "strategy": "Container orchestration",
                    "triggers": "CPU > 70%"
                }
            },
            security_considerations={
                "authentication": {
                    "method": "OAuth 2.0",
                    "providers": "Internal + SSO"
                }
            },
            deployment_strategy={
                "deployment_model": {
                    "approach": "Cloud-native",
                    "environments": ["Dev", "Staging", "Production"]
                }
            },
            design_rationale={
                "architecture_pattern": {
                    "choice": "Monolithic",
                    "rationale": "Simplicity and team size"
                }
            }
        )
        
        # Test the save method
        print("\n🔧 Testing _save_solution_to_markdown method...")
        architect._save_solution_to_markdown(sample_architecture, temp_dir)
        
        # Check if markdown file was created
        markdown_file = os.path.join(temp_dir, "solution_architecture.md")
        assert os.path.exists(markdown_file), "❌ Solution architecture markdown file not created"
        print(f"✅ Markdown file created: {markdown_file}")
        
        # Check file size
        file_size = os.path.getsize(markdown_file)
        print(f"📄 File size: {file_size:,} bytes")
        assert file_size > 100, "❌ Markdown file is too small"
        
        # Verify file contents
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Check for key sections
            required_sections = [
                "# Technical Solution Architecture",
                "## Test Solution Overview",
                "## Architecture Pattern",
                "## Technology Stack",
                "## System Components",
                "## Integration Points",
                "## Scalability Strategy",
                "## Security Considerations",
                "## Deployment Strategy"
            ]
            
            print(f"\n📋 Verifying required sections:")
            for section in required_sections:
                if section in content:
                    print(f"   ✓ {section}")
                else:
                    raise AssertionError(f"Missing section: {section}")
            
            # Check for specific content
            assert "React" in content, "❌ Technology stack not included"
            assert "Node.js" in content, "❌ Backend technology not included"
            assert "Web Application" in content, "❌ Components not included"
            assert "OAuth 2.0" in content, "❌ Security details not included"
            
            print(f"\n✅ All required sections and content present")
            
            # Show a preview
            lines = content.split('\n')
            print(f"\n📖 File preview (first 15 lines):")
            for i, line in enumerate(lines[:15], 1):
                print(f"   {i:2d}: {line}")
        
        print("\n" + "="*70)
        print("✅ TEST 2 PASSED: Solution Architect saves markdown correctly")
        print("="*70)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST 2 FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ TEST 2 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary directory")


def test_workflow_integration():
    """Test that workflow correctly passes output_dir to agents"""
    print("\n" + "="*70)
    print("TEST 3: Workflow Integration - Output Directory Passing")
    print("="*70)
    
    try:
        from src.workflows.enhanced_rfp_workflow import EnhancedRFPWorkflow, WorkflowConfig
        
        # Create temporary output directory
        temp_dir = tempfile.mkdtemp()
        print(f"📁 Temporary output directory: {temp_dir}")
        
        # Create workflow with custom output directory
        config = WorkflowConfig()
        workflow = EnhancedRFPWorkflow(config, output_dir=temp_dir)
        
        # Verify output_dir is stored
        assert hasattr(workflow, 'output_dir'), "❌ Workflow doesn't have output_dir attribute"
        assert workflow.output_dir == temp_dir, "❌ output_dir not set correctly"
        print(f"✅ Workflow output_dir set correctly: {workflow.output_dir}")
        
        # Verify agents are initialized
        assert workflow.solution_architect_agent is not None, "❌ Solution Architect agent not initialized"
        assert workflow.designer_agent is not None, "❌ Designer agent not initialized"
        print(f"✅ Agents initialized successfully")
        
        print("\n" + "="*70)
        print("✅ TEST 3 PASSED: Workflow integration correct")
        print("="*70)
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST 3 FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ TEST 3 ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            print(f"\n🧹 Cleaned up temporary directory")


def run_all_tests():
    """Run all unit tests"""
    print("\n" + "="*70)
    print("🧪 RUNNING OUTPUT GENERATION UNIT TESTS")
    print("="*70)
    
    results = {
        "Designer Agent - Diagram Saving": test_designer_agent_saves_diagrams(),
        "Solution Architect - Markdown Saving": test_solution_architect_saves_markdown(),
        "Workflow Integration": test_workflow_integration()
    }
    
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print("\n" + "="*70)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - passed} test(s) failed")
    
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
