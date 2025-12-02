#!/usr/bin/env python3
"""
Demonstration of the Enhanced Multi-Agent RFP System
Shows the 7 specialized agents working together with external search capabilities.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def demonstrate_agents():
    """Demonstrate each specialized agent individually"""
    
    print("🎭 Enhanced Multi-Agent RFP System Demonstration")
    print("=" * 60)
    
    # Sample RFP content for testing
    sample_rfp = """
    RFP: E-Commerce Platform Development
    
    Client: TechCorp Solutions
    Industry: Retail Technology
    
    Project Overview:
    We need a modern e-commerce platform that can handle high traffic volumes,
    integrate with existing ERP systems, and provide excellent user experience.
    
    Requirements:
    - Web-based platform with mobile responsiveness
    - Payment gateway integration
    - Inventory management system
    - User authentication and authorization
    - Analytics and reporting dashboard
    - API for third-party integrations
    
    Technical Constraints:
    - Must use cloud infrastructure
    - Prefer microservices architecture
    - Security compliance (PCI DSS)
    - Scalable to handle 10,000+ concurrent users
    
    Timeline: 6 months
    Budget: $200,000 - $300,000
    """
    
    # 1. Deep Researcher Agent Demo
    print("\n🔍 1. DEEP RESEARCHER AGENT")
    print("-" * 40)
    try:
        from src.agents.deep_researcher_agent import DeepResearcherAgent
        from src.tools.search_tools import GoogleSearchTool
        
        # Initialize search tool with API key
        search_tool = GoogleSearchTool(
            api_key=os.getenv("GOOGLE_API_KEY"),
            search_engine_id="your-search-engine-id"  # You'll need to create this
        )
        
        researcher = DeepResearcherAgent()
        print("✅ Deep Researcher Agent initialized")
        print("   - Conducts external research on clients and technologies")
        print("   - Extracts comprehensive requirements from RFP documents")
        print("   - Analyzes market trends and competitive landscape")
        
        # Demo search capability
        if os.getenv("GOOGLE_API_KEY"):
            print("   - Google Search API configured ✅")
            # search_results = search_tool.search("e-commerce platform development trends 2024")
            # print(f"   - Sample search returned {len(search_results)} results")
        else:
            print("   - Google Search API not configured (using mock data)")
            
    except Exception as e:
        print(f"❌ Deep Researcher Agent error: {e}")
    
    # 2. Solution Architect Agent Demo
    print("\n🏗️ 2. SOLUTION ARCHITECT AGENT")
    print("-" * 40)
    try:
        from src.agents.solution_architect_agent import SolutionArchitectAgent
        from src.tools.tech_stack_tools import TechStackDatabase
        
        architect = SolutionArchitectAgent()
        tech_db = TechStackDatabase()
        
        print("✅ Solution Architect Agent initialized")
        print("   - Designs comprehensive technical architecture")
        print("   - Recommends optimal technology stacks")
        print("   - Creates detailed system specifications")
        
        # Demo tech stack recommendation
        recommendations = tech_db.get_recommendations("e-commerce", ["scalability", "security"])
        print(f"   - Tech stack recommendations: {len(recommendations)} technologies")
        for tech in recommendations[:3]:
            print(f"     • {tech['name']}: {tech['description'][:50]}...")
            
    except Exception as e:
        print(f"❌ Solution Architect Agent error: {e}")
    
    # 3. Designer Agent Demo
    print("\n🎨 3. DESIGNER AGENT")
    print("-" * 40)
    try:
        from src.agents.designer_agent import DesignerAgent
        from src.utils.diagram_generator import DiagramGenerator
        
        designer = DesignerAgent()
        diagram_gen = DiagramGenerator()
        
        print("✅ Designer Agent initialized")
        print("   - Creates professional architectural diagrams")
        print("   - Generates presentation-ready visualizations")
        print("   - Supports multiple output formats (SVG, PNG, Mermaid)")
        
        # Demo diagram generation capability
        sample_mermaid = """
        graph TD
            A[User] --> B[Load Balancer]
            B --> C[Web Server]
            C --> D[Application Server]
            D --> E[Database]
        """
        
        print("   - Mermaid diagram generation capability available")
        if diagram_gen.mermaid_available:
            print("   - Mermaid CLI available ✅")
        else:
            print("   - Using fallback SVG generation")
            
    except Exception as e:
        print(f"❌ Designer Agent error: {e}")
    
    # 4. Project Manager Agent Demo
    print("\n📊 4. PROJECT MANAGER AGENT")
    print("-" * 40)
    try:
        from src.agents.project_manager_agent import ProjectManagerAgent
        from src.tools.estimation_tools import EstimationEngine
        
        pm = ProjectManagerAgent()
        estimator = EstimationEngine()
        
        print("✅ Project Manager Agent initialized")
        print("   - Creates detailed project plans and timelines")
        print("   - Performs effort estimation and resource allocation")
        print("   - Conducts comprehensive risk assessment")
        
        # Demo estimation
        sample_features = ["User Authentication", "Payment Gateway", "Inventory Management"]
        estimates = estimator.estimate_features(sample_features)
        total_effort = sum(est['effort_hours'] for est in estimates)
        print(f"   - Sample estimation: {total_effort} hours for {len(sample_features)} features")
        
    except Exception as e:
        print(f"❌ Project Manager Agent error: {e}")
    
    # 5. CTO Agent Demo
    print("\n👨‍💼 5. CTO AGENT")
    print("-" * 40)
    try:
        from src.agents.cto_agent import CTOAgent
        from src.tools.security_tools import SecurityAuditor
        
        cto = CTOAgent()
        security_auditor = SecurityAuditor()
        
        print("✅ CTO Agent initialized")
        print("   - Validates technical solutions and architecture")
        print("   - Conducts security audits and compliance checks")
        print("   - Has authority to approve/reject technical proposals")
        
        # Demo security assessment
        sample_architecture = {
            "components": ["web_server", "database", "api_gateway"],
            "technologies": ["React", "Node.js", "PostgreSQL"]
        }
        security_score = security_auditor.audit_architecture(sample_architecture)
        print(f"   - Security assessment score: {security_score['overall_score']}/100")
        
    except Exception as e:
        print(f"❌ CTO Agent error: {e}")
    
    # 6. QA + CEO Agent Demo
    print("\n✅ 6. QA + CEO AGENT")
    print("-" * 40)
    try:
        from src.agents.qa_ceo_agent import QACEOAgent
        from src.tools.quality_tools import QualityAssessment
        
        qa_ceo = QACEOAgent()
        quality_tool = QualityAssessment()
        
        print("✅ QA + CEO Agent initialized")
        print("   - Performs comprehensive quality assurance")
        print("   - Conducts executive-level strategic review")
        print("   - Provides final approval with detailed feedback")
        
        # Demo quality assessment
        sample_proposal = {
            "technical_quality": 85,
            "business_alignment": 90,
            "risk_level": "medium"
        }
        quality_score = quality_tool.assess_document_quality("Sample proposal content for quality assessment")
        print(f"   - Quality assessment: {quality_score['overall_score']:.1f}% overall quality")
        
    except Exception as e:
        print(f"❌ QA + CEO Agent error: {e}")
    
    # 7. Supervisor Agent Demo
    print("\n🎭 7. SUPERVISOR AGENT")
    print("-" * 40)
    try:
        from src.agents.supervisor_agent import SupervisorAgent
        
        supervisor = SupervisorAgent()
        
        print("✅ Supervisor Agent initialized")
        print("   - Orchestrates workflow between all specialized agents")
        print("   - Manages state transitions and quality gates")
        print("   - Handles error recovery and retry mechanisms")
        print("   - Ensures proper workflow progression")
        
    except Exception as e:
        print(f"❌ Supervisor Agent error: {e}")
    
    print("\n" + "=" * 60)
    print("🎯 ENHANCED SYSTEM CAPABILITIES")
    print("=" * 60)
    
    capabilities = [
        "✅ 7 Specialized Agents with distinct expertise",
        "✅ External Research via Google Search API",
        "✅ Comprehensive Technology Stack Database",
        "✅ Professional Diagram Generation",
        "✅ Advanced Project Estimation",
        "✅ Security Auditing and Compliance",
        "✅ Quality Assurance and Executive Review",
        "✅ Supervisor-based Workflow Orchestration",
        "✅ Multi-level Validation and Quality Gates",
        "✅ Error Recovery and Retry Mechanisms"
    ]
    
    for capability in capabilities:
        print(f"  {capability}")
    
    print("\n🚀 USAGE EXAMPLES")
    print("-" * 20)
    print("# Enhanced workflow with external research:")
    print("python cli_demo.py --enhanced --sample \\")
    print("  --google-api-key 'your-key' \\")
    print("  --search-engine-id 'your-id' \\")
    print("  --output ./output")
    print()
    print("# Debug mode with intermediate results:")
    print("python cli_demo.py --enhanced --sample --debug --save-intermediate")
    print()
    print("# JSON-only output for API integration:")
    print("python cli_demo.py --enhanced --sample --json-only")
    
    print("\n📊 SYSTEM ARCHITECTURE")
    print("-" * 25)
    architecture_flow = [
        "1. 📄 Document Input → Supervisor Agent",
        "2. 🔍 Deep Researcher → External research & requirement extraction",
        "3. 🏗️ Solution Architect → Technical design & technology selection",
        "4. 🎨 Designer → Professional diagram generation",
        "5. 📊 Project Manager → Planning, estimation & risk assessment",
        "6. 👨‍💼 CTO → Technical validation & security audit",
        "7. ✅ QA + CEO → Quality assurance & final approval",
        "8. 📋 Supervisor → Final output generation"
    ]
    
    for step in architecture_flow:
        print(f"  {step}")
    
    print(f"\n🎉 Enhanced Multi-Agent RFP System Ready!")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   API Keys: {'✅ Configured' if os.getenv('OPENAI_API_KEY') and os.getenv('GOOGLE_API_KEY') else '❌ Missing'}")

if __name__ == "__main__":
    print("🚀 Starting Enhanced Multi-Agent RFP System Demo...")
    
    # Check required API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not set")
        sys.exit(1)
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️ GOOGLE_API_KEY not set - external research will use mock data")
    
    demonstrate_agents()