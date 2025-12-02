"""
Security auditing and analysis tools for the CTO Agent
"""
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class SecurityRiskLevel(Enum):
    """Security risk levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ComplianceStandard(Enum):
    """Compliance standards"""
    OWASP_TOP_10 = "owasp_top_10"
    GDPR = "gdpr"
    HIPAA = "hipaa"
    SOC2 = "soc2"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"

@dataclass
class SecurityFinding:
    """Represents a security finding"""
    category: str
    risk_level: SecurityRiskLevel
    title: str
    description: str
    recommendation: str
    compliance_impact: List[ComplianceStandard]
    remediation_effort: str  # "low", "medium", "high"

class SecurityAuditorTool:
    """Tool for auditing proposed architecture against security best practices"""
    
    def __init__(self):
        self.security_checks = self._initialize_security_checks()
        self.compliance_requirements = self._initialize_compliance_requirements()
    
    def _initialize_security_checks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security check definitions"""
        return {
            "authentication": {
                "name": "Authentication & Authorization",
                "checks": [
                    {
                        "id": "auth_001",
                        "title": "Multi-factor Authentication",
                        "description": "System should implement MFA for user authentication",
                        "risk_if_missing": SecurityRiskLevel.HIGH,
                        "owasp_category": "A07:2021 – Identification and Authentication Failures"
                    },
                    {
                        "id": "auth_002", 
                        "title": "Role-Based Access Control",
                        "description": "Implement proper RBAC with principle of least privilege",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A01:2021 – Broken Access Control"
                    },
                    {
                        "id": "auth_003",
                        "title": "Session Management",
                        "description": "Secure session handling with proper timeout and invalidation",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A07:2021 – Identification and Authentication Failures"
                    }
                ]
            },
            "data_protection": {
                "name": "Data Protection",
                "checks": [
                    {
                        "id": "data_001",
                        "title": "Data Encryption at Rest",
                        "description": "Sensitive data must be encrypted when stored",
                        "risk_if_missing": SecurityRiskLevel.HIGH,
                        "owasp_category": "A02:2021 – Cryptographic Failures"
                    },
                    {
                        "id": "data_002",
                        "title": "Data Encryption in Transit",
                        "description": "All data transmission must use TLS/SSL encryption",
                        "risk_if_missing": SecurityRiskLevel.HIGH,
                        "owasp_category": "A02:2021 – Cryptographic Failures"
                    },
                    {
                        "id": "data_003",
                        "title": "Data Classification",
                        "description": "Implement proper data classification and handling procedures",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A09:2021 – Security Logging and Monitoring Failures"
                    }
                ]
            },
            "input_validation": {
                "name": "Input Validation",
                "checks": [
                    {
                        "id": "input_001",
                        "title": "SQL Injection Prevention",
                        "description": "Use parameterized queries and input validation",
                        "risk_if_missing": SecurityRiskLevel.CRITICAL,
                        "owasp_category": "A03:2021 – Injection"
                    },
                    {
                        "id": "input_002",
                        "title": "XSS Prevention",
                        "description": "Implement proper output encoding and CSP headers",
                        "risk_if_missing": SecurityRiskLevel.HIGH,
                        "owasp_category": "A03:2021 – Injection"
                    },
                    {
                        "id": "input_003",
                        "title": "File Upload Security",
                        "description": "Validate file types, scan for malware, limit file sizes",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A04:2021 – Insecure Design"
                    }
                ]
            },
            "infrastructure": {
                "name": "Infrastructure Security",
                "checks": [
                    {
                        "id": "infra_001",
                        "title": "Network Segmentation",
                        "description": "Implement proper network segmentation and firewalls",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A05:2021 – Security Misconfiguration"
                    },
                    {
                        "id": "infra_002",
                        "title": "Container Security",
                        "description": "Secure container images and runtime configuration",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A05:2021 – Security Misconfiguration"
                    },
                    {
                        "id": "infra_003",
                        "title": "Secrets Management",
                        "description": "Use dedicated secrets management system",
                        "risk_if_missing": SecurityRiskLevel.HIGH,
                        "owasp_category": "A02:2021 – Cryptographic Failures"
                    }
                ]
            },
            "monitoring": {
                "name": "Security Monitoring",
                "checks": [
                    {
                        "id": "monitor_001",
                        "title": "Security Logging",
                        "description": "Comprehensive logging of security events",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A09:2021 – Security Logging and Monitoring Failures"
                    },
                    {
                        "id": "monitor_002",
                        "title": "Intrusion Detection",
                        "description": "Implement IDS/IPS for threat detection",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A09:2021 – Security Logging and Monitoring Failures"
                    },
                    {
                        "id": "monitor_003",
                        "title": "Vulnerability Scanning",
                        "description": "Regular automated vulnerability assessments",
                        "risk_if_missing": SecurityRiskLevel.MEDIUM,
                        "owasp_category": "A06:2021 – Vulnerable and Outdated Components"
                    }
                ]
            }
        }
    
    def _initialize_compliance_requirements(self) -> Dict[ComplianceStandard, Dict[str, Any]]:
        """Initialize compliance requirement mappings"""
        return {
            ComplianceStandard.GDPR: {
                "name": "General Data Protection Regulation",
                "key_requirements": [
                    "Data encryption and pseudonymization",
                    "Right to be forgotten implementation",
                    "Data breach notification procedures",
                    "Privacy by design principles",
                    "Consent management system"
                ],
                "applicable_checks": ["data_001", "data_002", "data_003", "monitor_001"]
            },
            ComplianceStandard.HIPAA: {
                "name": "Health Insurance Portability and Accountability Act",
                "key_requirements": [
                    "PHI encryption at rest and in transit",
                    "Access controls and audit logs",
                    "Business associate agreements",
                    "Risk assessments and safeguards",
                    "Incident response procedures"
                ],
                "applicable_checks": ["data_001", "data_002", "auth_001", "auth_002", "monitor_001"]
            },
            ComplianceStandard.SOC2: {
                "name": "Service Organization Control 2",
                "key_requirements": [
                    "Security controls and monitoring",
                    "Availability and processing integrity",
                    "Confidentiality controls",
                    "Privacy protection measures",
                    "Change management procedures"
                ],
                "applicable_checks": ["auth_001", "auth_002", "data_001", "monitor_001", "monitor_002"]
            },
            ComplianceStandard.PCI_DSS: {
                "name": "Payment Card Industry Data Security Standard",
                "key_requirements": [
                    "Cardholder data encryption",
                    "Secure network architecture",
                    "Access control measures",
                    "Regular security testing",
                    "Information security policy"
                ],
                "applicable_checks": ["data_001", "data_002", "auth_001", "infra_001", "monitor_003"]
            }
        }
    
    def audit_architecture(self, architecture_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Audit the proposed architecture against security best practices
        
        Args:
            architecture_spec: Architecture specification to audit
            
        Returns:
            Security audit results with findings and recommendations
        """
        try:
            audit_results = {
                'overall_risk_level': SecurityRiskLevel.LOW,
                'findings': [],
                'compliance_gaps': {},
                'recommendations': [],
                'security_score': 100,
                'audit_summary': {}
            }
            
            # Extract architecture components
            components = architecture_spec.get('components', [])
            technologies = architecture_spec.get('technologies', {})
            data_handling = architecture_spec.get('data_handling', {})
            
            # Perform security checks
            findings = []
            
            # Check authentication mechanisms
            auth_findings = self._check_authentication(architecture_spec)
            findings.extend(auth_findings)
            
            # Check data protection
            data_findings = self._check_data_protection(architecture_spec)
            findings.extend(data_findings)
            
            # Check input validation
            input_findings = self._check_input_validation(architecture_spec)
            findings.extend(input_findings)
            
            # Check infrastructure security
            infra_findings = self._check_infrastructure_security(architecture_spec)
            findings.extend(infra_findings)
            
            # Check monitoring and logging
            monitor_findings = self._check_monitoring(architecture_spec)
            findings.extend(monitor_findings)
            
            audit_results['findings'] = findings
            
            # Calculate overall risk level and security score
            risk_levels = [f.risk_level for f in findings]
            if SecurityRiskLevel.CRITICAL in risk_levels:
                audit_results['overall_risk_level'] = SecurityRiskLevel.CRITICAL
                audit_results['security_score'] = 30
            elif SecurityRiskLevel.HIGH in risk_levels:
                audit_results['overall_risk_level'] = SecurityRiskLevel.HIGH
                audit_results['security_score'] = 50
            elif SecurityRiskLevel.MEDIUM in risk_levels:
                audit_results['overall_risk_level'] = SecurityRiskLevel.MEDIUM
                audit_results['security_score'] = 70
            else:
                audit_results['security_score'] = 90
            
            # Generate recommendations
            audit_results['recommendations'] = self._generate_security_recommendations(findings)
            
            # Check compliance gaps
            audit_results['compliance_gaps'] = self._check_compliance_gaps(findings)
            
            # Create audit summary
            audit_results['audit_summary'] = {
                'total_findings': len(findings),
                'critical_findings': len([f for f in findings if f.risk_level == SecurityRiskLevel.CRITICAL]),
                'high_findings': len([f for f in findings if f.risk_level == SecurityRiskLevel.HIGH]),
                'medium_findings': len([f for f in findings if f.risk_level == SecurityRiskLevel.MEDIUM]),
                'low_findings': len([f for f in findings if f.risk_level == SecurityRiskLevel.LOW])
            }
            
            return audit_results
            
        except Exception as e:
            logger.error(f"Security audit failed: {e}")
            return self._get_default_audit_results()
    
    def _check_authentication(self, arch_spec: Dict[str, Any]) -> List[SecurityFinding]:
        """Check authentication and authorization mechanisms"""
        findings = []
        
        auth_config = arch_spec.get('authentication', {})
        
        if not auth_config.get('mfa_enabled', False):
            findings.append(SecurityFinding(
                category="authentication",
                risk_level=SecurityRiskLevel.HIGH,
                title="Multi-Factor Authentication Missing",
                description="The architecture does not specify multi-factor authentication implementation",
                recommendation="Implement MFA using TOTP, SMS, or hardware tokens for enhanced security",
                compliance_impact=[ComplianceStandard.SOC2, ComplianceStandard.HIPAA],
                remediation_effort="medium"
            ))
        
        if not auth_config.get('rbac_enabled', False):
            findings.append(SecurityFinding(
                category="authentication",
                risk_level=SecurityRiskLevel.MEDIUM,
                title="Role-Based Access Control Missing",
                description="No role-based access control mechanism specified",
                recommendation="Implement RBAC with principle of least privilege",
                compliance_impact=[ComplianceStandard.SOC2],
                remediation_effort="medium"
            ))
        
        return findings
    
    def _check_data_protection(self, arch_spec: Dict[str, Any]) -> List[SecurityFinding]:
        """Check data protection mechanisms"""
        findings = []
        
        data_config = arch_spec.get('data_protection', {})
        
        if not data_config.get('encryption_at_rest', False):
            findings.append(SecurityFinding(
                category="data_protection",
                risk_level=SecurityRiskLevel.HIGH,
                title="Data Encryption at Rest Missing",
                description="Sensitive data is not encrypted when stored",
                recommendation="Implement AES-256 encryption for all sensitive data at rest",
                compliance_impact=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA, ComplianceStandard.PCI_DSS],
                remediation_effort="medium"
            ))
        
        if not data_config.get('encryption_in_transit', False):
            findings.append(SecurityFinding(
                category="data_protection",
                risk_level=SecurityRiskLevel.HIGH,
                title="Data Encryption in Transit Missing",
                description="Data transmission is not properly encrypted",
                recommendation="Implement TLS 1.3 for all data transmission",
                compliance_impact=[ComplianceStandard.GDPR, ComplianceStandard.HIPAA, ComplianceStandard.PCI_DSS],
                remediation_effort="low"
            ))
        
        return findings
    
    def _check_input_validation(self, arch_spec: Dict[str, Any]) -> List[SecurityFinding]:
        """Check input validation mechanisms"""
        findings = []
        
        input_config = arch_spec.get('input_validation', {})
        
        if not input_config.get('sql_injection_prevention', False):
            findings.append(SecurityFinding(
                category="input_validation",
                risk_level=SecurityRiskLevel.CRITICAL,
                title="SQL Injection Prevention Missing",
                description="No SQL injection prevention mechanisms specified",
                recommendation="Use parameterized queries and input validation for all database interactions",
                compliance_impact=[ComplianceStandard.OWASP_TOP_10],
                remediation_effort="medium"
            ))
        
        return findings
    
    def _check_infrastructure_security(self, arch_spec: Dict[str, Any]) -> List[SecurityFinding]:
        """Check infrastructure security configurations"""
        findings = []
        
        infra_config = arch_spec.get('infrastructure_security', {})
        
        if not infra_config.get('network_segmentation', False):
            findings.append(SecurityFinding(
                category="infrastructure",
                risk_level=SecurityRiskLevel.MEDIUM,
                title="Network Segmentation Missing",
                description="No network segmentation strategy specified",
                recommendation="Implement network segmentation with firewalls and VPCs",
                compliance_impact=[ComplianceStandard.SOC2],
                remediation_effort="high"
            ))
        
        return findings
    
    def _check_monitoring(self, arch_spec: Dict[str, Any]) -> List[SecurityFinding]:
        """Check security monitoring and logging"""
        findings = []
        
        monitor_config = arch_spec.get('security_monitoring', {})
        
        if not monitor_config.get('security_logging', False):
            findings.append(SecurityFinding(
                category="monitoring",
                risk_level=SecurityRiskLevel.MEDIUM,
                title="Security Logging Missing",
                description="No comprehensive security logging specified",
                recommendation="Implement centralized security logging with SIEM integration",
                compliance_impact=[ComplianceStandard.SOC2, ComplianceStandard.HIPAA],
                remediation_effort="medium"
            ))
        
        return findings
    
    def _generate_security_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate prioritized security recommendations"""
        recommendations = []
        
        # Group findings by risk level
        critical_findings = [f for f in findings if f.risk_level == SecurityRiskLevel.CRITICAL]
        high_findings = [f for f in findings if f.risk_level == SecurityRiskLevel.HIGH]
        
        if critical_findings:
            recommendations.append("IMMEDIATE ACTION REQUIRED: Address critical security vulnerabilities")
            for finding in critical_findings:
                recommendations.append(f"- {finding.recommendation}")
        
        if high_findings:
            recommendations.append("HIGH PRIORITY: Address high-risk security issues")
            for finding in high_findings:
                recommendations.append(f"- {finding.recommendation}")
        
        # Add general recommendations
        recommendations.extend([
            "Conduct regular security assessments and penetration testing",
            "Implement security awareness training for development team",
            "Establish incident response procedures",
            "Regular security updates and patch management"
        ])
        
        return recommendations
    
    def _check_compliance_gaps(self, findings: List[SecurityFinding]) -> Dict[str, List[str]]:
        """Check compliance gaps based on findings"""
        compliance_gaps = {}
        
        for finding in findings:
            for standard in finding.compliance_impact:
                if standard.value not in compliance_gaps:
                    compliance_gaps[standard.value] = []
                compliance_gaps[standard.value].append(finding.title)
        
        return compliance_gaps
    
    def _get_default_audit_results(self) -> Dict[str, Any]:
        """Get default audit results for error cases"""
        return {
            'overall_risk_level': SecurityRiskLevel.MEDIUM,
            'findings': [],
            'compliance_gaps': {},
            'recommendations': ['Manual security review recommended due to audit failure'],
            'security_score': 50,
            'audit_summary': {
                'total_findings': 0,
                'critical_findings': 0,
                'high_findings': 0,
                'medium_findings': 0,
                'low_findings': 0
            }
        }

# Alias for compatibility
SecurityAuditor = SecurityAuditorTool

class TechDebtAnalyzer:
    """Tool for analyzing technical debt and maintainability"""
    
    def analyze_tech_debt(self, architecture_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze technical debt risks in the proposed architecture
        
        Args:
            architecture_spec: Architecture specification to analyze
            
        Returns:
            Technical debt analysis results
        """
        try:
            analysis = {
                'overall_debt_risk': 'medium',
                'debt_factors': [],
                'maintainability_score': 70,
                'operational_complexity': 'medium',
                'vendor_lock_in_risk': 'low',
                'recommendations': []
            }
            
            technologies = architecture_spec.get('technologies', {})
            architecture_pattern = architecture_spec.get('architecture_pattern', {})
            
            # Analyze technology choices
            debt_factors = []
            
            # Check for emerging technologies
            emerging_techs = []
            for tech_name, tech_spec in technologies.items():
                if hasattr(tech_spec, 'maturity') and tech_spec.maturity == 'emerging':
                    emerging_techs.append(tech_name)
            
            if emerging_techs:
                debt_factors.append({
                    'factor': 'Emerging Technologies',
                    'risk': 'medium',
                    'description': f"Using emerging technologies: {', '.join(emerging_techs)}",
                    'impact': 'May require frequent updates and have limited community support'
                })
            
            # Check vendor lock-in
            high_lockin_techs = []
            for tech_name, tech_spec in technologies.items():
                if hasattr(tech_spec, 'vendor_lock_in') and tech_spec.vendor_lock_in == 'high':
                    high_lockin_techs.append(tech_name)
            
            if high_lockin_techs:
                debt_factors.append({
                    'factor': 'Vendor Lock-in',
                    'risk': 'high',
                    'description': f"High vendor lock-in technologies: {', '.join(high_lockin_techs)}",
                    'impact': 'Difficult and expensive to migrate to alternatives'
                })
                analysis['vendor_lock_in_risk'] = 'high'
            
            # Check architectural complexity
            pattern_name = architecture_pattern.get('name', '')
            if 'microservices' in pattern_name.lower():
                debt_factors.append({
                    'factor': 'Microservices Complexity',
                    'risk': 'high',
                    'description': 'Microservices architecture increases operational complexity',
                    'impact': 'Requires sophisticated monitoring, deployment, and debugging capabilities'
                })
                analysis['operational_complexity'] = 'high'
            
            analysis['debt_factors'] = debt_factors
            
            # Calculate overall debt risk
            high_risk_factors = [f for f in debt_factors if f['risk'] == 'high']
            if len(high_risk_factors) >= 2:
                analysis['overall_debt_risk'] = 'high'
                analysis['maintainability_score'] = 40
            elif high_risk_factors:
                analysis['overall_debt_risk'] = 'medium'
                analysis['maintainability_score'] = 60
            else:
                analysis['overall_debt_risk'] = 'low'
                analysis['maintainability_score'] = 80
            
            # Generate recommendations
            recommendations = []
            if analysis['overall_debt_risk'] == 'high':
                recommendations.append("Consider simplifying the architecture to reduce technical debt")
                recommendations.append("Implement comprehensive monitoring and observability")
                recommendations.append("Plan for regular architecture reviews and refactoring")
            
            if analysis['vendor_lock_in_risk'] == 'high':
                recommendations.append("Evaluate open-source alternatives to reduce vendor dependency")
                recommendations.append("Implement abstraction layers to minimize lock-in impact")
            
            recommendations.extend([
                "Establish coding standards and automated quality checks",
                "Plan for regular dependency updates and security patches",
                "Document architectural decisions and trade-offs"
            ])
            
            analysis['recommendations'] = recommendations
            
            return analysis
            
        except Exception as e:
            logger.error(f"Tech debt analysis failed: {e}")
            return {
                'overall_debt_risk': 'medium',
                'debt_factors': [],
                'maintainability_score': 50,
                'operational_complexity': 'medium',
                'vendor_lock_in_risk': 'medium',
                'recommendations': ['Manual technical debt review recommended']
            }

# Factory function to create security tools
def create_security_tools() -> Dict[str, Any]:
    """Create and configure security tools"""
    security_auditor = SecurityAuditorTool()
    tech_debt_analyzer = TechDebtAnalyzer()
    
    return {
        'security_auditor': security_auditor,
        'tech_debt_analyzer': tech_debt_analyzer,
        'audit_architecture': security_auditor.audit_architecture,
        'analyze_tech_debt': tech_debt_analyzer.analyze_tech_debt
    }