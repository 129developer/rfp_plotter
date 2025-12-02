"""
Diagram generation utilities for creating architecture and deployment diagrams.
Supports GraphViz, Mermaid, and simple SVG generation.
"""

import os
import tempfile
import subprocess
import base64
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    logging.warning("GraphViz not available. Diagram generation will be limited.")

logger = logging.getLogger(__name__)


class DiagramGenerator:
    """Utility class for generating diagrams from specifications"""
    
    def __init__(self):
        self.mermaid_cli_available = self._check_mermaid_cli()
        self.mermaid_available = self.mermaid_cli_available  # Alias for compatibility
    
    def _check_mermaid_cli(self) -> bool:
        """Check if Mermaid CLI is available"""
        try:
            result = subprocess.run(['mmdc', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            logger.warning("Mermaid CLI not available - diagram generation will use fallback methods")
            return False
    
    def generate_mermaid_svg(self, mermaid_spec: str) -> Optional[str]:
        """
        Generate SVG from Mermaid specification
        
        Args:
            mermaid_spec: Mermaid diagram specification
            
        Returns:
            SVG content as string, or None if generation fails
        """
        try:
            if self.mermaid_cli_available:
                return self._generate_svg_with_cli(mermaid_spec)
            else:
                return self._generate_svg_fallback(mermaid_spec)
                
        except Exception as e:
            logger.error(f"SVG generation failed: {e}")
            return None
    
    def generate_mermaid_png_base64(self, mermaid_spec: str) -> Optional[str]:
        """
        Generate PNG (base64 encoded) from Mermaid specification
        
        Args:
            mermaid_spec: Mermaid diagram specification
            
        Returns:
            Base64 encoded PNG data, or None if generation fails
        """
        try:
            if self.mermaid_cli_available:
                return self._generate_png_with_cli(mermaid_spec)
            else:
                logger.warning("PNG generation requires Mermaid CLI - not available")
                return None
                
        except Exception as e:
            logger.error(f"PNG generation failed: {e}")
            return None
    
    def _generate_svg_with_cli(self, mermaid_spec: str) -> Optional[str]:
        """Generate SVG using Mermaid CLI"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as input_file:
                input_file.write(mermaid_spec)
                input_file.flush()
                
                with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as output_file:
                    output_path = output_file.name
                
                # Run Mermaid CLI
                cmd = ['mmdc', '-i', input_file.name, '-o', output_path, '-f', 'svg']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    with open(output_path, 'r', encoding='utf-8') as svg_file:
                        svg_content = svg_file.read()
                    
                    # Cleanup
                    os.unlink(input_file.name)
                    os.unlink(output_path)
                    
                    return svg_content
                else:
                    logger.error(f"Mermaid CLI failed: {result.stderr}")
                    # Cleanup
                    if os.path.exists(input_file.name):
                        os.unlink(input_file.name)
                    if os.path.exists(output_path):
                        os.unlink(output_path)
                    return None
                    
        except Exception as e:
            logger.error(f"CLI SVG generation failed: {e}")
            return None
    
    def _generate_png_with_cli(self, mermaid_spec: str) -> Optional[str]:
        """Generate PNG using Mermaid CLI"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as input_file:
                input_file.write(mermaid_spec)
                input_file.flush()
                
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as output_file:
                    output_path = output_file.name
                
                # Run Mermaid CLI
                cmd = ['mmdc', '-i', input_file.name, '-o', output_path, '-f', 'png']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0 and os.path.exists(output_path):
                    with open(output_path, 'rb') as png_file:
                        png_data = png_file.read()
                    
                    # Cleanup
                    os.unlink(input_file.name)
                    os.unlink(output_path)
                    
                    return base64.b64encode(png_data).decode('utf-8')
                else:
                    logger.error(f"Mermaid CLI PNG failed: {result.stderr}")
                    # Cleanup
                    if os.path.exists(input_file.name):
                        os.unlink(input_file.name)
                    if os.path.exists(output_path):
                        os.unlink(output_path)
                    return None
                    
        except Exception as e:
            logger.error(f"CLI PNG generation failed: {e}")
            return None
    
    def _generate_svg_fallback(self, mermaid_spec: str) -> Optional[str]:
        """Generate fallback SVG when CLI is not available"""
        try:
            # Create a simple SVG representation of the diagram
            # This is a basic fallback - in production, you might use a web service
            
            # Extract diagram type
            diagram_type = "graph"
            if mermaid_spec.strip().startswith("sequenceDiagram"):
                diagram_type = "sequence"
            elif mermaid_spec.strip().startswith("flowchart"):
                diagram_type = "flowchart"
            elif mermaid_spec.strip().startswith("graph"):
                diagram_type = "graph"
            
            # Count nodes/elements for sizing
            lines = mermaid_spec.split('\n')
            element_count = len([line for line in lines if '-->' in line or '->' in line or line.strip().startswith('participant')])
            
            # Calculate SVG dimensions
            width = max(400, element_count * 100)
            height = max(300, element_count * 80)
            
            # Generate basic SVG
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .diagram-title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; }}
      .diagram-note {{ font-family: Arial, sans-serif; font-size: 12px; fill: #666; }}
      .diagram-box {{ fill: #f9f9f9; stroke: #333; stroke-width: 1; }}
    </style>
  </defs>
  
  <!-- Background -->
  <rect width="100%" height="100%" fill="white"/>
  
  <!-- Title -->
  <text x="{width//2}" y="30" text-anchor="middle" class="diagram-title">
    {diagram_type.title()} Diagram
  </text>
  
  <!-- Placeholder content -->
  <rect x="50" y="60" width="120" height="60" class="diagram-box"/>
  <text x="110" y="95" text-anchor="middle" class="diagram-note">Component 1</text>
  
  <rect x="{width-170}" y="60" width="120" height="60" class="diagram-box"/>
  <text x="{width-110}" y="95" text-anchor="middle" class="diagram-note">Component 2</text>
  
  <!-- Connection arrow -->
  <line x1="170" y1="90" x2="{width-170}" y2="90" stroke="#333" stroke-width="2" marker-end="url(#arrowhead)"/>
  
  <!-- Arrow marker -->
  <defs>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#333"/>
    </marker>
  </defs>
  
  <!-- Note about fallback -->
  <text x="{width//2}" y="{height-20}" text-anchor="middle" class="diagram-note">
    Diagram generated in fallback mode - install Mermaid CLI for full rendering
  </text>
</svg>'''
            
            return svg_content
            
        except Exception as e:
            logger.error(f"Fallback SVG generation failed: {e}")
            return None
    
    @staticmethod
    def generate_architecture_diagram(nodes: List[str], edges: List[List[str]], 
                                    title: str = "Solution Architecture",
                                    output_format: str = "svg") -> Optional[str]:
        """
        Generate an architecture diagram from nodes and edges.
        
        Args:
            nodes: List of node names
            edges: List of [from, to] edge pairs
            title: Diagram title
            output_format: Output format ('svg', 'png', 'pdf')
            
        Returns:
            Path to generated diagram file or None if generation failed
        """
        if not GRAPHVIZ_AVAILABLE:
            logger.warning("GraphViz not available, generating simple text diagram")
            return DiagramGenerator._generate_text_diagram(nodes, edges, title)
        
        try:
            # Create GraphViz diagram
            dot = graphviz.Digraph(comment=title, format=output_format)
            dot.attr(rankdir='TB', size='10,8')
            dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
            dot.attr('edge', color='darkblue')
            
            # Add title
            dot.attr(label=title, labelloc='t', fontsize='16', fontname='Arial Bold')
            
            # Add nodes
            for node in nodes:
                dot.node(DiagramGenerator._sanitize_node_name(node), node)
            
            # Add edges
            for edge in edges:
                if len(edge) >= 2:
                    from_node = DiagramGenerator._sanitize_node_name(edge[0])
                    to_node = DiagramGenerator._sanitize_node_name(edge[1])
                    dot.edge(from_node, to_node)
            
            # Generate diagram
            output_path = tempfile.mktemp(suffix=f'.{output_format}')
            dot.render(output_path, cleanup=True)
            
            # GraphViz adds the format extension, so we need to find the actual file
            actual_path = f"{output_path}.{output_format}"
            if os.path.exists(actual_path):
                return actual_path
            else:
                return output_path
                
        except Exception as e:
            logger.error(f"Error generating GraphViz diagram: {e}")
            return DiagramGenerator._generate_text_diagram(nodes, edges, title)
    
    @staticmethod
    def generate_deployment_diagram(environments: List[str], components: List[str],
                                  title: str = "Deployment Architecture",
                                  output_format: str = "svg") -> Optional[str]:
        """
        Generate a deployment diagram showing environments and components.
        
        Args:
            environments: List of deployment environments
            components: List of system components
            title: Diagram title
            output_format: Output format
            
        Returns:
            Path to generated diagram file
        """
        if not GRAPHVIZ_AVAILABLE:
            return DiagramGenerator._generate_text_deployment_diagram(environments, components, title)
        
        try:
            dot = graphviz.Digraph(comment=title, format=output_format)
            dot.attr(rankdir='LR', size='12,8')
            dot.attr(label=title, labelloc='t', fontsize='16', fontname='Arial Bold')
            
            # Create subgraphs for each environment
            for i, env in enumerate(environments):
                with dot.subgraph(name=f'cluster_{i}') as env_graph:
                    env_graph.attr(label=env, style='filled', fillcolor='lightgray')
                    env_graph.attr('node', shape='box', style='filled', fillcolor='lightgreen')
                    
                    # Add components to each environment
                    for component in components:
                        node_name = f"{env}_{component}".replace(' ', '_')
                        env_graph.node(node_name, component)
            
            # Add connections between environments (e.g., Dev -> Test -> Prod)
            for i in range(len(environments) - 1):
                current_env = environments[i]
                next_env = environments[i + 1]
                
                # Connect first component of current env to first component of next env
                if components:
                    current_node = f"{current_env}_{components[0]}".replace(' ', '_')
                    next_node = f"{next_env}_{components[0]}".replace(' ', '_')
                    dot.edge(current_node, next_node, style='dashed', label='promote')
            
            # Generate diagram
            output_path = tempfile.mktemp(suffix=f'.{output_format}')
            dot.render(output_path, cleanup=True)
            
            actual_path = f"{output_path}.{output_format}"
            if os.path.exists(actual_path):
                return actual_path
            else:
                return output_path
                
        except Exception as e:
            logger.error(f"Error generating deployment diagram: {e}")
            return DiagramGenerator._generate_text_deployment_diagram(environments, components, title)
    
    @staticmethod
    def generate_mermaid_diagram(nodes: List[str], edges: List[List[str]], 
                               diagram_type: str = "flowchart") -> str:
        """
        Generate a Mermaid diagram specification.
        
        Args:
            nodes: List of node names
            edges: List of [from, to] edge pairs
            diagram_type: Type of Mermaid diagram ('flowchart', 'graph')
            
        Returns:
            Mermaid diagram specification as string
        """
        mermaid_spec = f"{diagram_type} TD\n"
        
        # Add nodes with IDs
        node_ids = {}
        for i, node in enumerate(nodes):
            node_id = f"N{i}"
            node_ids[node] = node_id
            mermaid_spec += f"    {node_id}[{node}]\n"
        
        # Add edges
        for edge in edges:
            if len(edge) >= 2 and edge[0] in node_ids and edge[1] in node_ids:
                from_id = node_ids[edge[0]]
                to_id = node_ids[edge[1]]
                mermaid_spec += f"    {from_id} --> {to_id}\n"
        
        return mermaid_spec
    
    @staticmethod
    def _sanitize_node_name(name: str) -> str:
        """Sanitize node name for GraphViz"""
        return name.replace(' ', '_').replace('-', '_').replace('.', '_')
    
    @staticmethod
    def _generate_text_diagram(nodes: List[str], edges: List[List[str]], title: str) -> str:
        """Generate a simple text-based diagram as fallback"""
        try:
            output_path = tempfile.mktemp(suffix='.txt')
            
            with open(output_path, 'w') as f:
                f.write(f"{title}\n")
                f.write("=" * len(title) + "\n\n")
                
                f.write("Components:\n")
                for i, node in enumerate(nodes, 1):
                    f.write(f"{i}. {node}\n")
                
                f.write("\nConnections:\n")
                for edge in edges:
                    if len(edge) >= 2:
                        f.write(f"{edge[0]} -> {edge[1]}\n")
                
                f.write("\nDiagram Structure:\n")
                f.write("┌─────────────────┐\n")
                for node in nodes:
                    f.write(f"│ {node:<15} │\n")
                f.write("└─────────────────┘\n")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating text diagram: {e}")
            return None
    
    @staticmethod
    def _generate_text_deployment_diagram(environments: List[str], components: List[str], title: str) -> str:
        """Generate a simple text-based deployment diagram"""
        try:
            output_path = tempfile.mktemp(suffix='.txt')
            
            with open(output_path, 'w') as f:
                f.write(f"{title}\n")
                f.write("=" * len(title) + "\n\n")
                
                for env in environments:
                    f.write(f"{env} Environment:\n")
                    f.write("-" * (len(env) + 13) + "\n")
                    for component in components:
                        f.write(f"  • {component}\n")
                    f.write("\n")
                
                f.write("Deployment Flow:\n")
                f.write(" -> ".join(environments) + "\n")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating text deployment diagram: {e}")
            return None
    
    @staticmethod
    def create_simple_svg_diagram(nodes: List[str], edges: List[List[str]], 
                                title: str = "Architecture Diagram") -> str:
        """
        Create a simple SVG diagram as a fallback option.
        
        Args:
            nodes: List of node names
            edges: List of [from, to] edge pairs
            title: Diagram title
            
        Returns:
            Path to generated SVG file
        """
        try:
            output_path = tempfile.mktemp(suffix='.svg')
            
            # Calculate layout
            node_width = 120
            node_height = 40
            spacing_x = 200
            spacing_y = 100
            
            # Simple grid layout
            cols = min(3, len(nodes))
            rows = (len(nodes) + cols - 1) // cols
            
            svg_width = cols * spacing_x + 100
            svg_height = rows * spacing_y + 100
            
            # Generate SVG
            svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .node {{ fill: #e1f5fe; stroke: #0277bd; stroke-width: 2; }}
      .node-text {{ font-family: Arial, sans-serif; font-size: 12px; text-anchor: middle; }}
      .edge {{ stroke: #424242; stroke-width: 2; marker-end: url(#arrowhead); }}
      .title {{ font-family: Arial, sans-serif; font-size: 16px; font-weight: bold; text-anchor: middle; }}
    </style>
    <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
      <polygon points="0 0, 10 3.5, 0 7" fill="#424242" />
    </marker>
  </defs>
  
  <text x="{svg_width//2}" y="30" class="title">{title}</text>
'''
            
            # Add nodes
            node_positions = {}
            for i, node in enumerate(nodes):
                row = i // cols
                col = i % cols
                x = col * spacing_x + 50
                y = row * spacing_y + 70
                
                node_positions[node] = (x + node_width//2, y + node_height//2)
                
                svg_content += f'''
  <rect x="{x}" y="{y}" width="{node_width}" height="{node_height}" class="node" rx="5"/>
  <text x="{x + node_width//2}" y="{y + node_height//2 + 4}" class="node-text">{node}</text>'''
            
            # Add edges
            for edge in edges:
                if len(edge) >= 2 and edge[0] in node_positions and edge[1] in node_positions:
                    x1, y1 = node_positions[edge[0]]
                    x2, y2 = node_positions[edge[1]]
                    
                    svg_content += f'''
  <line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" class="edge"/>'''
            
            svg_content += '\n</svg>'
            
            with open(output_path, 'w') as f:
                f.write(svg_content)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating SVG diagram: {e}")
            return None


def validate_diagram_spec(nodes: List[str], edges: List[List[str]]) -> List[str]:
    """
    Validate a diagram specification.
    
    Args:
        nodes: List of node names
        edges: List of [from, to] edge pairs
        
    Returns:
        List of validation issues
    """
    issues = []
    
    if not nodes:
        issues.append("No nodes specified")
    
    # Check for duplicate nodes
    if len(nodes) != len(set(nodes)):
        issues.append("Duplicate nodes found")
    
    # Check edges reference valid nodes
    for edge in edges:
        if len(edge) < 2:
            issues.append(f"Invalid edge format: {edge}")
            continue
        
        if edge[0] not in nodes:
            issues.append(f"Edge references unknown node: {edge[0]}")
        
        if edge[1] not in nodes:
            issues.append(f"Edge references unknown node: {edge[1]}")
    
    return issues