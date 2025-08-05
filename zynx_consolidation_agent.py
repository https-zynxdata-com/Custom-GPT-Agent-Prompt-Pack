#!/usr/bin/env python3
"""
Zynx Consolidation Agent
========================

Scans workspace for automation workflows and consolidates similar agents.
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import argparse
import subprocess
import sys

@dataclass
class AutomationWorkflow:
    """Represents an automation workflow found in the workspace."""
    file_path: str
    workflow_type: str
    name: str
    description: str
    triggers: List[str]
    actions: List[str]
    dependencies: List[str]
    tags: List[str]
    similarity_score: float = 0.0

class ZynxConsolidationAgent:
    """Main agent for consolidating automation workflows."""
    
    def __init__(self, workspace_path: str = "C:/Users/Zynxdata"):
        self.workspace_path = Path(workspace_path)
        self.excluded_dirs = {
            'node_modules', '.venv', '.git', 'build', 'dist', 
            '__pycache__', '.pytest_cache', '.vscode', '.idea'
        }
        self.workflow_files = []
        self.workflows = []
        self.clusters = {}
        
    def scan_workspace(self) -> List[str]:
        """Scan workspace for YAML/Markdown/Workflow files."""
        print(f"🔍 Scanning workspace: {self.workspace_path}")
        
        workflow_files = []
        for root, dirs, files in os.walk(self.workspace_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.excluded_dirs]
            
            for file in files:
                if self._is_workflow_file(file):
                    file_path = os.path.join(root, file)
                    workflow_files.append(file_path)
                    print(f"  📄 Found: {file_path}")
        
        self.workflow_files = workflow_files
        print(f"✅ Found {len(workflow_files)} workflow files")
        return workflow_files
    
    def _is_workflow_file(self, filename: str) -> bool:
        """Check if file is a workflow file."""
        workflow_extensions = {'.yml', '.yaml', '.md', '.workflow'}
        return any(filename.endswith(ext) for ext in workflow_extensions)
    
    def parse_workflows(self) -> List[AutomationWorkflow]:
        """Parse workflow files and extract automation information."""
        workflows = []
        
        for file_path in self.workflow_files:
            try:
                workflow = self._parse_single_workflow(file_path)
                if workflow:
                    workflows.append(workflow)
            except Exception as e:
                print(f"⚠️  Error parsing {file_path}: {e}")
        
        self.workflows = workflows
        print(f"✅ Parsed {len(workflows)} workflows")
        return workflows
    
    def _parse_single_workflow(self, file_path: str) -> Optional[AutomationWorkflow]:
        """Parse a single workflow file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Try to parse as YAML first
        try:
            data = yaml.safe_load(content)
            return self._extract_from_yaml(file_path, data)
        except yaml.YAMLError:
            pass
        
        # Try to parse as Markdown
        return self._extract_from_markdown(file_path, content)
    
    def _extract_from_yaml(self, file_path: str, data: dict) -> Optional[AutomationWorkflow]:
        """Extract workflow info from YAML data."""
        if not data:
            return None
        
        # Common workflow patterns
        name = data.get('name', '')
        description = data.get('description', '')
        
        # Detect workflow type
        workflow_type = self._detect_workflow_type(data)
        
        # Extract triggers and actions
        triggers = self._extract_triggers(data)
        actions = self._extract_actions(data)
        dependencies = self._extract_dependencies(data)
        tags = self._extract_tags(data)
        
        return AutomationWorkflow(
            file_path=file_path,
            workflow_type=workflow_type,
            name=name,
            description=description,
            triggers=triggers,
            actions=actions,
            dependencies=dependencies,
            tags=tags
        )
    
    def _extract_from_markdown(self, file_path: str, content: str) -> Optional[AutomationWorkflow]:
        """Extract workflow info from Markdown content."""
        # Look for automation patterns in markdown
        lines = content.split('\n')
        name = ''
        description = ''
        triggers = []
        actions = []
        dependencies = []
        tags = []
        
        for line in lines:
            # Extract name from headers
            if line.startswith('# '):
                name = line[2:].strip()
            elif line.startswith('## '):
                if not name:
                    name = line[3:].strip()
            
            # Extract triggers and actions
            if 'trigger' in line.lower() or 'on:' in line.lower():
                triggers.append(line.strip())
            if 'action' in line.lower() or 'run:' in line.lower():
                actions.append(line.strip())
            
            # Extract dependencies
            if 'depend' in line.lower() or 'require' in line.lower():
                dependencies.append(line.strip())
            
            # Extract tags
            if 'tag:' in line.lower() or 'label:' in line.lower():
                tags.append(line.strip())
        
        workflow_type = self._detect_workflow_type_from_content(content)
        
        if name or description or triggers or actions:
            return AutomationWorkflow(
                file_path=file_path,
                workflow_type=workflow_type,
                name=name,
                description=description,
                triggers=triggers,
                actions=actions,
                dependencies=dependencies,
                tags=tags
            )
        
        return None
    
    def _detect_workflow_type(self, data: dict) -> str:
        """Detect workflow type from YAML data."""
        if 'on' in data:
            return 'GitHub Actions'
        elif 'triggers' in data:
            return 'Azure DevOps'
        elif 'jobs' in data:
            return 'CI/CD Pipeline'
        elif 'steps' in data:
            return 'Automation Workflow'
        else:
            return 'Unknown'
    
    def _detect_workflow_type_from_content(self, content: str) -> str:
        """Detect workflow type from content."""
        content_lower = content.lower()
        if 'github' in content_lower or 'on:' in content_lower:
            return 'GitHub Actions'
        elif 'azure' in content_lower or 'devops' in content_lower:
            return 'Azure DevOps'
        elif 'jenkins' in content_lower or 'pipeline' in content_lower:
            return 'Jenkins Pipeline'
        elif 'gitlab' in content_lower:
            return 'GitLab CI'
        else:
            return 'Automation Workflow'
    
    def _extract_triggers(self, data: dict) -> List[str]:
        """Extract triggers from workflow data."""
        triggers = []
        if 'on' in data:
            triggers.extend(data['on'].keys())
        if 'triggers' in data:
            triggers.extend(data['triggers'])
        return triggers
    
    def _extract_actions(self, data: dict) -> List[str]:
        """Extract actions from workflow data."""
        actions = []
        if 'jobs' in data:
            for job_name, job_data in data['jobs'].items():
                if 'steps' in job_data:
                    for step in job_data['steps']:
                        if 'run' in step:
                            actions.append(step['run'])
                        if 'uses' in step:
                            actions.append(step['uses'])
        if 'steps' in data:
            for step in data['steps']:
                if 'run' in step:
                    actions.append(step['run'])
                if 'uses' in step:
                    actions.append(step['uses'])
        return actions
    
    def _extract_dependencies(self, data: dict) -> List[str]:
        """Extract dependencies from workflow data."""
        dependencies = []
        if 'needs' in data:
            dependencies.extend(data['needs'])
        if 'dependencies' in data:
            dependencies.extend(data['dependencies'])
        return dependencies
    
    def _extract_tags(self, data: dict) -> List[str]:
        """Extract tags from workflow data."""
        tags = []
        if 'tags' in data:
            tags.extend(data['tags'])
        if 'labels' in data:
            tags.extend(data['labels'])
        return tags
    
    def cluster_workflows(self) -> Dict[str, List[AutomationWorkflow]]:
        """Cluster workflows by similarity."""
        print("🔗 Clustering workflows by similarity...")
        
        clusters = defaultdict(list)
        
        for workflow in self.workflows:
            cluster_key = self._determine_cluster(workflow)
            clusters[cluster_key].append(workflow)
        
        self.clusters = dict(clusters)
        
        for cluster_name, workflows in self.clusters.items():
            print(f"  📊 Cluster '{cluster_name}': {len(workflows)} workflows")
        
        return self.clusters
    
    def _determine_cluster(self, workflow: AutomationWorkflow) -> str:
        """Determine which cluster a workflow belongs to."""
        # Analyze workflow content to determine cluster
        content = f"{workflow.name} {workflow.description} {' '.join(workflow.actions)}"
        content_lower = content.lower()
        
        # PR-related workflows
        if any(keyword in content_lower for keyword in ['pull request', 'pr', 'review', 'merge']):
            return 'PR Management'
        
        # Deploy-related workflows
        if any(keyword in content_lower for keyword in ['deploy', 'release', 'build', 'publish']):
            return 'Deployment'
        
        # Memory/Debug workflows
        if any(keyword in content_lower for keyword in ['debug', 'memory', 'log', 'monitor']):
            return 'Memory Debugger'
        
        # MVP-related workflows
        if any(keyword in content_lower for keyword in ['test', 'validate', 'check', 'verify']):
            return 'MVP Testing'
        
        # Default cluster
        return 'General Automation'
    
    def generate_overlap_matrix(self) -> str:
        """Generate overlap matrix markdown."""
        print("📊 Generating overlap matrix...")
        
        matrix_content = """# Zynx Automation Overlap Matrix

## Workflow Clusters Analysis

"""
        
        for cluster_name, workflows in self.clusters.items():
            matrix_content += f"### {cluster_name}\n\n"
            matrix_content += f"**Total Workflows**: {len(workflows)}\n\n"
            
            # Group by similarity
            similar_workflows = self._group_similar_workflows(workflows)
            
            for group_name, group_workflows in similar_workflows.items():
                matrix_content += f"#### {group_name}\n\n"
                for workflow in group_workflows:
                    matrix_content += f"- **{workflow.name}** (`{workflow.file_path}`)\n"
                    if workflow.description:
                        matrix_content += f"  - {workflow.description}\n"
                    if workflow.triggers:
                        matrix_content += f"  - Triggers: {', '.join(workflow.triggers)}\n"
                    if workflow.actions:
                        matrix_content += f"  - Actions: {len(workflow.actions)} steps\n"
                matrix_content += "\n"
        
        return matrix_content
    
    def _group_similar_workflows(self, workflows: List[AutomationWorkflow]) -> Dict[str, List[AutomationWorkflow]]:
        """Group workflows by similarity within a cluster."""
        groups = defaultdict(list)
        
        for workflow in workflows:
            # Create a signature based on actions and triggers
            signature = self._create_workflow_signature(workflow)
            groups[signature].append(workflow)
        
        return dict(groups)
    
    def _create_workflow_signature(self, workflow: AutomationWorkflow) -> str:
        """Create a signature for workflow similarity."""
        # Combine key characteristics
        signature_parts = []
        
        if workflow.triggers:
            signature_parts.append(f"triggers:{','.join(sorted(workflow.triggers))}")
        
        if workflow.actions:
            # Use first few actions as signature
            action_sigs = [action[:50] for action in workflow.actions[:3]]
            signature_parts.append(f"actions:{','.join(action_sigs)}")
        
        return "|".join(signature_parts) if signature_parts else "unknown"
    
    def generate_automation_index(self) -> str:
        """Generate comprehensive automation index."""
        print("📋 Generating automation index...")
        
        index_content = """# Zynx Automation Index

## Overview
This index provides a comprehensive view of all automation workflows in the Zynx workspace.

## Summary Statistics
"""
        
        total_workflows = len(self.workflows)
        total_files = len(self.workflow_files)
        
        index_content += f"- **Total Workflow Files**: {total_files}\n"
        index_content += f"- **Parsed Workflows**: {total_workflows}\n"
        index_content += f"- **Clusters**: {len(self.clusters)}\n\n"
        
        # Add cluster summaries
        for cluster_name, workflows in self.clusters.items():
            index_content += f"### {cluster_name}\n\n"
            index_content += f"**Count**: {len(workflows)} workflows\n\n"
            
            # List all workflows in this cluster
            for i, workflow in enumerate(workflows, 1):
                index_content += f"#### {i}. {workflow.name}\n\n"
                index_content += f"- **File**: `{workflow.file_path}`\n"
                if workflow.description:
                    index_content += f"- **Description**: {workflow.description}\n"
                if workflow.workflow_type:
                    index_content += f"- **Type**: {workflow.workflow_type}\n"
                if workflow.triggers:
                    index_content += f"- **Triggers**: {', '.join(workflow.triggers)}\n"
                if workflow.actions:
                    index_content += f"- **Actions**: {len(workflow.actions)} steps\n"
                if workflow.dependencies:
                    index_content += f"- **Dependencies**: {', '.join(workflow.dependencies)}\n"
                if workflow.tags:
                    index_content += f"- **Tags**: {', '.join(workflow.tags)}\n"
                index_content += "\n"
        
        return index_content
    
    def consolidate_workflows(self) -> Dict[str, str]:
        """Consolidate similar workflows into master workflows."""
        print("🔧 Consolidating workflows...")
        
        consolidated = {}
        
        for cluster_name, workflows in self.clusters.items():
            if len(workflows) > 1:
                # Consolidate workflows in this cluster
                consolidated_workflow = self._create_consolidated_workflow(cluster_name, workflows)
                consolidated[cluster_name] = consolidated_workflow
        
        return consolidated
    
    def _create_consolidated_workflow(self, cluster_name: str, workflows: List[AutomationWorkflow]) -> str:
        """Create a consolidated workflow from multiple similar workflows."""
        # Create a master workflow that combines all similar workflows
        consolidated = {
            'name': f'Zynx {cluster_name} Master Workflow',
            'description': f'Consolidated workflow for {cluster_name} operations',
            'on': self._merge_triggers(workflows),
            'jobs': self._merge_jobs(workflows),
            'env': self._merge_environment(workflows)
        }
        
        return yaml.dump(consolidated, default_flow_style=False, sort_keys=False)
    
    def _merge_triggers(self, workflows: List[AutomationWorkflow]) -> dict:
        """Merge triggers from multiple workflows."""
        all_triggers = set()
        for workflow in workflows:
            all_triggers.update(workflow.triggers)
        
        merged = {}
        for trigger in all_triggers:
            if trigger in ['push', 'pull_request']:
                merged[trigger] = {'branches': ['main', 'develop']}
            else:
                merged[trigger] = {}
        
        return merged
    
    def _merge_jobs(self, workflows: List[AutomationWorkflow]) -> dict:
        """Merge jobs from multiple workflows."""
        jobs = {}
        
        for i, workflow in enumerate(workflows):
            job_name = f"{workflow.name.lower().replace(' ', '_')}_{i}"
            jobs[job_name] = {
                'runs-on': 'ubuntu-latest',
                'steps': self._create_steps_from_actions(workflow.actions)
            }
        
        return jobs
    
    def _create_steps_from_actions(self, actions: List[str]) -> List[dict]:
        """Create GitHub Actions steps from workflow actions."""
        steps = []
        
        for action in actions:
            if 'run:' in action:
                # Extract the command
                command = action.split('run:')[1].strip()
                steps.append({
                    'name': f'Run: {command[:50]}...',
                    'run': command
                })
            else:
                steps.append({
                    'name': f'Action: {action[:50]}...',
                    'run': action
                })
        
        return steps
    
    def _merge_environment(self, workflows: List[AutomationWorkflow]) -> dict:
        """Merge environment variables from multiple workflows."""
        env = {}
        
        for workflow in workflows:
            # Add workflow-specific environment variables
            env[f'{workflow.name.upper()}_ENABLED'] = 'true'
        
        return env
    
    def save_outputs(self, overlap_matrix: str, automation_index: str, consolidated_workflows: Dict[str, str]):
        """Save all outputs to files."""
        print("💾 Saving outputs...")
        
        # Save overlap matrix
        with open('overlap_matrix.md', 'w', encoding='utf-8') as f:
            f.write(overlap_matrix)
        print("  ✅ Saved: overlap_matrix.md")
        
        # Save automation index
        with open('Zynx_Automation_Index.md', 'w', encoding='utf-8') as f:
            f.write(automation_index)
        print("  ✅ Saved: Zynx_Automation_Index.md")
        
        # Save consolidated workflows
        for cluster_name, workflow_content in consolidated_workflows.items():
            filename = f"consolidated_{cluster_name.lower().replace(' ', '_')}.yml"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(workflow_content)
            print(f"  ✅ Saved: {filename}")
    
    def run(self):
        """Main execution method."""
        print("🚀 Starting Zynx Consolidation Agent...")
        
        # Step 1: Scan workspace
        self.scan_workspace()
        
        # Step 2: Parse workflows
        self.parse_workflows()
        
        # Step 3: Cluster workflows
        self.cluster_workflows()
        
        # Step 4: Generate outputs
        overlap_matrix = self.generate_overlap_matrix()
        automation_index = self.generate_automation_index()
        consolidated_workflows = self.consolidate_workflows()
        
        # Step 5: Save outputs
        self.save_outputs(overlap_matrix, automation_index, consolidated_workflows)
        
        print("✅ Zynx Consolidation Agent completed successfully!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Zynx Consolidation Agent')
    parser.add_argument('--workspace', default='C:/Users/Zynxdata', 
                       help='Workspace path to scan')
    parser.add_argument('--apply', action='store_true',
                       help='Apply consolidation and create PR')
    
    args = parser.parse_args()
    
    agent = ZynxConsolidationAgent(args.workspace)
    agent.run()
    
    if args.apply:
        print("🔄 Applying consolidation...")
        # TODO: Implement PR creation logic
        print("  📝 Creating pull request...")

if __name__ == '__main__':
    main()