"""
Technology stack database and analysis tools for the Solution Architect Agent
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class TechCategory(Enum):
    """Technology categories"""
    FRONTEND = "frontend"
    BACKEND = "backend"
    DATABASE = "database"
    CLOUD = "cloud"
    CONTAINER = "container"
    MESSAGING = "messaging"
    MONITORING = "monitoring"
    SECURITY = "security"
    DEVOPS = "devops"
    INTEGRATION = "integration"

@dataclass
class TechnologySpec:
    """Specification for a technology component"""
    name: str
    category: TechCategory
    description: str
    use_cases: List[str]
    pros: List[str]
    cons: List[str]
    complexity: str  # "low", "medium", "high"
    cost_factor: float  # 1.0 = baseline, >1.0 = more expensive
    maturity: str  # "emerging", "stable", "mature", "legacy"
    vendor_lock_in: str  # "none", "low", "medium", "high"
    learning_curve: str  # "easy", "moderate", "steep"
    community_support: str  # "limited", "good", "excellent"

class TechStackDatabase:
    """Database of approved technology stacks and components"""
    
    def __init__(self):
        self.technologies = self._initialize_tech_database()
        self.patterns = self._initialize_architecture_patterns()
        
    def _initialize_tech_database(self) -> Dict[str, TechnologySpec]:
        """Initialize the technology database with common technologies"""
        techs = {}
        
        # Frontend Technologies
        techs["react"] = TechnologySpec(
            name="React",
            category=TechCategory.FRONTEND,
            description="Popular JavaScript library for building user interfaces",
            use_cases=["Web applications", "Single-page applications", "Component-based UIs"],
            pros=["Large ecosystem", "Strong community", "Flexible", "Good performance"],
            cons=["Steep learning curve", "Rapid changes", "JSX complexity"],
            complexity="medium",
            cost_factor=1.0,
            maturity="mature",
            vendor_lock_in="none",
            learning_curve="moderate",
            community_support="excellent"
        )
        
        techs["angular"] = TechnologySpec(
            name="Angular",
            category=TechCategory.FRONTEND,
            description="Full-featured TypeScript framework for web applications",
            use_cases=["Enterprise applications", "Complex web apps", "Progressive web apps"],
            pros=["Full framework", "TypeScript support", "Enterprise-ready", "Good tooling"],
            cons=["Heavy framework", "Steep learning curve", "Opinionated"],
            complexity="high",
            cost_factor=1.2,
            maturity="mature",
            vendor_lock_in="low",
            learning_curve="steep",
            community_support="excellent"
        )
        
        techs["vue"] = TechnologySpec(
            name="Vue.js",
            category=TechCategory.FRONTEND,
            description="Progressive JavaScript framework for building user interfaces",
            use_cases=["Web applications", "Prototyping", "Progressive enhancement"],
            pros=["Easy to learn", "Flexible", "Good documentation", "Lightweight"],
            cons=["Smaller ecosystem", "Less enterprise adoption"],
            complexity="low",
            cost_factor=0.9,
            maturity="stable",
            vendor_lock_in="none",
            learning_curve="easy",
            community_support="good"
        )
        
        # Backend Technologies
        techs["nodejs"] = TechnologySpec(
            name="Node.js",
            category=TechCategory.BACKEND,
            description="JavaScript runtime for server-side development",
            use_cases=["API development", "Real-time applications", "Microservices"],
            pros=["JavaScript everywhere", "Fast development", "Large ecosystem", "Good for I/O"],
            cons=["Single-threaded", "CPU-intensive limitations", "Callback complexity"],
            complexity="medium",
            cost_factor=0.9,
            maturity="mature",
            vendor_lock_in="none",
            learning_curve="moderate",
            community_support="excellent"
        )
        
        techs["python"] = TechnologySpec(
            name="Python",
            category=TechCategory.BACKEND,
            description="High-level programming language for backend development",
            use_cases=["Web APIs", "Data processing", "Machine learning", "Automation"],
            pros=["Easy to learn", "Versatile", "Great libraries", "Readable code"],
            cons=["Performance limitations", "GIL constraints", "Runtime errors"],
            complexity="low",
            cost_factor=0.8,
            maturity="mature",
            vendor_lock_in="none",
            learning_curve="easy",
            community_support="excellent"
        )
        
        techs["java"] = TechnologySpec(
            name="Java",
            category=TechCategory.BACKEND,
            description="Enterprise-grade programming language and platform",
            use_cases=["Enterprise applications", "Microservices", "Large-scale systems"],
            pros=["Enterprise-ready", "Strong typing", "JVM ecosystem", "Scalable"],
            cons=["Verbose syntax", "Slower development", "Memory usage"],
            complexity="high",
            cost_factor=1.3,
            maturity="mature",
            vendor_lock_in="low",
            learning_curve="steep",
            community_support="excellent"
        )
        
        # Database Technologies
        techs["postgresql"] = TechnologySpec(
            name="PostgreSQL",
            category=TechCategory.DATABASE,
            description="Advanced open-source relational database",
            use_cases=["OLTP applications", "Complex queries", "JSON data", "Analytics"],
            pros=["Feature-rich", "ACID compliance", "Extensible", "Open source"],
            cons=["Complex configuration", "Memory usage", "Learning curve"],
            complexity="medium",
            cost_factor=0.7,
            maturity="mature",
            vendor_lock_in="none",
            learning_curve="moderate",
            community_support="excellent"
        )
        
        techs["mongodb"] = TechnologySpec(
            name="MongoDB",
            category=TechCategory.DATABASE,
            description="Document-oriented NoSQL database",
            use_cases=["Document storage", "Rapid prototyping", "Flexible schemas"],
            pros=["Flexible schema", "Easy scaling", "JSON-like documents", "Fast development"],
            cons=["Memory usage", "Consistency trade-offs", "Query limitations"],
            complexity="medium",
            cost_factor=1.0,
            maturity="stable",
            vendor_lock_in="medium",
            learning_curve="moderate",
            community_support="good"
        )
        
        # Cloud Technologies
        techs["aws"] = TechnologySpec(
            name="Amazon Web Services",
            category=TechCategory.CLOUD,
            description="Comprehensive cloud computing platform",
            use_cases=["Cloud hosting", "Serverless", "Enterprise applications", "Scalable systems"],
            pros=["Comprehensive services", "Market leader", "Global presence", "Mature"],
            cons=["Complex pricing", "Vendor lock-in", "Learning curve", "Cost management"],
            complexity="high",
            cost_factor=1.2,
            maturity="mature",
            vendor_lock_in="high",
            learning_curve="steep",
            community_support="excellent"
        )
        
        techs["gcp"] = TechnologySpec(
            name="Google Cloud Platform",
            category=TechCategory.CLOUD,
            description="Google's cloud computing platform",
            use_cases=["Machine learning", "Data analytics", "Kubernetes", "Modern applications"],
            pros=["AI/ML services", "Kubernetes native", "Competitive pricing", "Innovation"],
            cons=["Smaller market share", "Service changes", "Limited enterprise features"],
            complexity="medium",
            cost_factor=1.0,
            maturity="stable",
            vendor_lock_in="medium",
            learning_curve="moderate",
            community_support="good"
        )
        
        techs["azure"] = TechnologySpec(
            name="Microsoft Azure",
            category=TechCategory.CLOUD,
            description="Microsoft's cloud computing platform",
            use_cases=["Enterprise applications", "Microsoft stack", "Hybrid cloud", "DevOps"],
            pros=["Microsoft integration", "Enterprise features", "Hybrid capabilities", "DevOps tools"],
            cons=["Complex pricing", "Microsoft dependency", "Learning curve"],
            complexity="high",
            cost_factor=1.1,
            maturity="mature",
            vendor_lock_in="high",
            learning_curve="steep",
            community_support="excellent"
        )
        
        # Container Technologies
        techs["docker"] = TechnologySpec(
            name="Docker",
            category=TechCategory.CONTAINER,
            description="Containerization platform for applications",
            use_cases=["Application packaging", "Development environments", "Microservices"],
            pros=["Consistent environments", "Easy deployment", "Resource efficient", "Portable"],
            cons=["Security considerations", "Complexity for simple apps", "Storage management"],
            complexity="medium",
            cost_factor=0.9,
            maturity="mature",
            vendor_lock_in="low",
            learning_curve="moderate",
            community_support="excellent"
        )
        
        techs["kubernetes"] = TechnologySpec(
            name="Kubernetes",
            category=TechCategory.CONTAINER,
            description="Container orchestration platform",
            use_cases=["Container orchestration", "Microservices", "Auto-scaling", "Cloud-native apps"],
            pros=["Industry standard", "Auto-scaling", "Self-healing", "Vendor neutral"],
            cons=["Complex setup", "Steep learning curve", "Operational overhead"],
            complexity="high",
            cost_factor=1.4,
            maturity="mature",
            vendor_lock_in="none",
            learning_curve="steep",
            community_support="excellent"
        )
        
        return techs
    
    def _initialize_architecture_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common architecture patterns"""
        return {
            "microservices": {
                "name": "Microservices Architecture",
                "description": "Distributed architecture with loosely coupled services",
                "use_cases": ["Large applications", "Team scalability", "Technology diversity"],
                "components": ["API Gateway", "Service Discovery", "Load Balancer", "Message Queue"],
                "complexity": "high",
                "team_size": "large",
                "recommended_techs": ["kubernetes", "docker", "nodejs", "postgresql"]
            },
            "monolith": {
                "name": "Monolithic Architecture",
                "description": "Single deployable unit containing all functionality",
                "use_cases": ["Small to medium applications", "Simple deployment", "Rapid development"],
                "components": ["Web Server", "Application Logic", "Database"],
                "complexity": "low",
                "team_size": "small",
                "recommended_techs": ["python", "postgresql", "docker"]
            },
            "serverless": {
                "name": "Serverless Architecture",
                "description": "Event-driven architecture using cloud functions",
                "use_cases": ["Event processing", "APIs", "Cost optimization", "Auto-scaling"],
                "components": ["Functions", "API Gateway", "Event Sources", "Managed Services"],
                "complexity": "medium",
                "team_size": "small",
                "recommended_techs": ["aws", "nodejs", "mongodb"]
            },
            "jamstack": {
                "name": "JAMstack Architecture",
                "description": "JavaScript, APIs, and Markup static site architecture",
                "use_cases": ["Static sites", "Content sites", "Fast loading", "CDN distribution"],
                "components": ["Static Site Generator", "CDN", "APIs", "CMS"],
                "complexity": "low",
                "team_size": "small",
                "recommended_techs": ["react", "nodejs", "aws"]
            }
        }
    
    def get_technology(self, tech_name: str) -> Optional[TechnologySpec]:
        """Get technology specification by name"""
        return self.technologies.get(tech_name.lower())
    
    def get_technologies_by_category(self, category: TechCategory) -> List[TechnologySpec]:
        """Get all technologies in a specific category"""
        return [tech for tech in self.technologies.values() if tech.category == category]
    
    def get_recommendations(self, project_type: str, criteria: List[str]) -> List[Dict[str, Any]]:
        """
        Get technology recommendations based on project type and criteria
        
        Args:
            project_type: Type of project (e.g., 'e-commerce', 'web-app', 'api')
            criteria: List of criteria (e.g., ['scalability', 'security', 'performance'])
            
        Returns:
            List of recommended technologies with details
        """
        try:
            recommendations = []
            
            # Filter technologies based on project type and criteria
            for tech in self.technologies.values():
                score = 0
                reasons = []
                
                # Score based on project type
                if project_type.lower() in ['e-commerce', 'web-app']:
                    if tech.category in [TechCategory.FRONTEND, TechCategory.BACKEND, TechCategory.DATABASE]:
                        score += 2
                        reasons.append(f"Suitable for {project_type} applications")
                elif project_type.lower() == 'api':
                    if tech.category in [TechCategory.BACKEND, TechCategory.DATABASE, TechCategory.CLOUD]:
                        score += 2
                        reasons.append(f"Excellent for API development")
                
                # Score based on criteria
                for criterion in criteria:
                    if criterion.lower() == 'scalability':
                        if 'scalable' in tech.description.lower() or 'scale' in ' '.join(tech.pros).lower():
                            score += 1
                            reasons.append("Excellent scalability features")
                    elif criterion.lower() == 'security':
                        if 'security' in tech.description.lower() or 'secure' in ' '.join(tech.pros).lower():
                            score += 1
                            reasons.append("Strong security capabilities")
                    elif criterion.lower() == 'performance':
                        if 'fast' in tech.description.lower() or 'performance' in ' '.join(tech.pros).lower():
                            score += 1
                            reasons.append("High performance characteristics")
                
                # Add to recommendations if score is high enough
                if score > 0:
                    recommendations.append({
                        'name': tech.name,
                        'category': tech.category.value,
                        'description': tech.description,
                        'score': score,
                        'reasons': reasons,
                        'complexity': tech.complexity,
                        'maturity': tech.maturity,
                        'pros': tech.pros[:3],  # Top 3 pros
                        'learning_curve': tech.learning_curve
                    })
            
            # Sort by score (highest first) and return top recommendations
            recommendations.sort(key=lambda x: x['score'], reverse=True)
            return recommendations[:10]  # Return top 10
            
        except Exception as e:
            logger.error(f"Failed to get recommendations: {e}")
            return [
                {
                    'name': 'React',
                    'category': 'frontend',
                    'description': 'Popular JavaScript library for building user interfaces',
                    'score': 3,
                    'reasons': ['Widely adopted', 'Strong ecosystem', 'Good for web apps'],
                    'complexity': 'medium',
                    'maturity': 'mature',
                    'pros': ['Component-based', 'Virtual DOM', 'Large community'],
                    'learning_curve': 'moderate'
                },
                {
                    'name': 'Node.js',
                    'category': 'backend',
                    'description': 'JavaScript runtime for server-side development',
                    'score': 3,
                    'reasons': ['Fast development', 'JavaScript ecosystem', 'Good for APIs'],
                    'complexity': 'medium',
                    'maturity': 'mature',
                    'pros': ['Fast development', 'NPM ecosystem', 'Non-blocking I/O'],
                    'learning_curve': 'moderate'
                },
                {
                    'name': 'PostgreSQL',
                    'category': 'database',
                    'description': 'Advanced open-source relational database',
                    'score': 2,
                    'reasons': ['Reliable', 'Feature-rich', 'ACID compliance'],
                    'complexity': 'medium',
                    'maturity': 'mature',
                    'pros': ['ACID compliance', 'JSON support', 'Extensible'],
                    'learning_curve': 'moderate'
                }
            ]
    
    def recommend_tech_stack(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recommend a technology stack based on requirements
        
        Args:
            requirements: Dictionary with project requirements
            
        Returns:
            Recommended technology stack with rationale
        """
        try:
            # Extract key requirements
            project_size = requirements.get('project_size', 'medium')  # small, medium, large
            team_size = requirements.get('team_size', 'small')  # small, medium, large
            complexity = requirements.get('complexity', 'medium')  # low, medium, high
            budget = requirements.get('budget', 'medium')  # low, medium, high
            timeline = requirements.get('timeline', 'medium')  # short, medium, long
            scalability = requirements.get('scalability', 'medium')  # low, medium, high
            
            # Determine architecture pattern
            if project_size == 'large' and team_size == 'large':
                pattern = "microservices"
            elif complexity == 'low' and timeline == 'short':
                pattern = "jamstack"
            elif budget == 'low' and scalability == 'high':
                pattern = "serverless"
            else:
                pattern = "monolith"
            
            architecture = self.patterns[pattern]
            
            # Select technologies based on pattern and requirements
            recommended_stack = {
                'architecture_pattern': architecture,
                'technologies': {},
                'rationale': {},
                'estimated_complexity': complexity,
                'estimated_cost_factor': 1.0
            }
            
            # Get recommended technologies for the pattern
            for tech_name in architecture['recommended_techs']:
                if tech_name in self.technologies:
                    tech = self.technologies[tech_name]
                    recommended_stack['technologies'][tech.category.value] = tech
                    recommended_stack['rationale'][tech_name] = f"Recommended for {pattern} architecture"
            
            # Calculate overall cost factor
            cost_factors = [tech.cost_factor for tech in recommended_stack['technologies'].values()]
            if cost_factors:
                recommended_stack['estimated_cost_factor'] = sum(cost_factors) / len(cost_factors)
            
            return recommended_stack
            
        except Exception as e:
            logger.error(f"Tech stack recommendation failed: {e}")
            return self._get_default_stack()
    
    def _get_default_stack(self) -> Dict[str, Any]:
        """Get a default technology stack"""
        return {
            'architecture_pattern': self.patterns['monolith'],
            'technologies': {
                'frontend': self.technologies['react'],
                'backend': self.technologies['nodejs'],
                'database': self.technologies['postgresql'],
                'cloud': self.technologies['aws'],
                'container': self.technologies['docker']
            },
            'rationale': {
                'react': 'Popular and well-supported frontend framework',
                'nodejs': 'Fast development with JavaScript ecosystem',
                'postgresql': 'Reliable and feature-rich database',
                'aws': 'Comprehensive cloud platform',
                'docker': 'Consistent deployment environments'
            },
            'estimated_complexity': 'medium',
            'estimated_cost_factor': 1.0
        }
    
    def analyze_tech_compatibility(self, tech_list: List[str]) -> Dict[str, Any]:
        """
        Analyze compatibility between selected technologies
        
        Args:
            tech_list: List of technology names
            
        Returns:
            Compatibility analysis results
        """
        try:
            analysis = {
                'compatible': True,
                'warnings': [],
                'recommendations': [],
                'overall_complexity': 'medium',
                'overall_cost_factor': 1.0
            }
            
            techs = [self.technologies.get(name.lower()) for name in tech_list if name.lower() in self.technologies]
            techs = [t for t in techs if t is not None]
            
            if not techs:
                analysis['warnings'].append("No recognized technologies found")
                return analysis
            
            # Check complexity compatibility
            complexities = [t.complexity for t in techs]
            if 'high' in complexities and 'low' in complexities:
                analysis['warnings'].append("Mixing high and low complexity technologies may create inconsistencies")
            
            # Check vendor lock-in
            high_lockin = [t.name for t in techs if t.vendor_lock_in == 'high']
            if len(high_lockin) > 1:
                analysis['warnings'].append(f"Multiple high vendor lock-in technologies: {', '.join(high_lockin)}")
            
            # Check maturity levels
            emerging = [t.name for t in techs if t.maturity == 'emerging']
            if emerging:
                analysis['warnings'].append(f"Emerging technologies may have stability risks: {', '.join(emerging)}")
            
            # Calculate overall metrics
            cost_factors = [t.cost_factor for t in techs]
            analysis['overall_cost_factor'] = sum(cost_factors) / len(cost_factors)
            
            # Determine overall complexity
            if 'high' in complexities:
                analysis['overall_complexity'] = 'high'
            elif 'low' in complexities and 'medium' not in complexities:
                analysis['overall_complexity'] = 'low'
            
            return analysis
            
        except Exception as e:
            logger.error(f"Tech compatibility analysis failed: {e}")
            return {
                'compatible': True,
                'warnings': ['Analysis failed, manual review recommended'],
                'recommendations': [],
                'overall_complexity': 'medium',
                'overall_cost_factor': 1.0
            }

# Factory function to create tech stack tools
def create_tech_stack_tools() -> Dict[str, Any]:
    """Create and configure technology stack tools"""
    tech_db = TechStackDatabase()
    
    return {
        'tech_stack_db': tech_db,
        'recommend_stack': tech_db.recommend_tech_stack,
        'analyze_compatibility': tech_db.analyze_tech_compatibility,
        'get_technology': tech_db.get_technology
    }