#!/usr/bin/env python3
"""
Generate Master Index Script
===========================

Creates a comprehensive master index of all automation workflows.
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict
import argparse
from datetime import datetime
import hashlib

class MasterIndexGenerator:
    """Generates a comprehensive master index of automation workflows."""
    
    def __init__(self):
        self.workflows = []
        self.categories = defaultdict(list)
        self.tags = defaultdict(list)
        self.file_types = defaultdict(list)
        self.workflow_types = defaultdict(list)
        
    def load_workflows(self, workflows_data: List[dict]):
        """Load workflows for indexing."""
        self.workflows = workflows_data
        print(f"📥 Loaded {len(self.workflows)} workflows for indexing")
        
        # Categorize workflows
        self._categorize_workflows()
    
    def _categorize_workflows(self):
        """Categorize workflows by various criteria."""
        for workflow in self.workflows:
            # Categorize by file type
            file_path = workflow.get('file_path', '')
            file_ext = Path(file_path).suffix.lower()
            self.file_types[file_ext].append(workflow)
            
            # Categorize by workflow type
            workflow_type = workflow.get('workflow_type', 'Unknown')
            self.workflow_types[workflow_type].append(workflow)
            
            # Categorize by tags
            for tag in workflow.get('tags', []):
                self.tags[tag].append(workflow)
            
            # Categorize by content analysis
            category = self._determine_category(workflow)
            self.categories[category].append(workflow)
    
    def _determine_category(self, workflow: dict) -> str:
        """Determine the category of a workflow based on its content."""
        content = f"{workflow.get('name', '')} {workflow.get('description', '')} {' '.join(workflow.get('actions', []))}"
        content_lower = content.lower()
        
        # Define category patterns
        category_patterns = {
            'CI/CD Pipeline': ['ci', 'cd', 'pipeline', 'build', 'deploy'],
            'Code Quality': ['lint', 'format', 'quality', 'style', 'check'],
            'Testing': ['test', 'spec', 'unit', 'integration', 'e2e'],
            'Security': ['security', 'scan', 'vulnerability', 'audit'],
            'Documentation': ['docs', 'documentation', 'readme'],
            'Dependency Management': ['deps', 'dependency', 'update', 'upgrade'],
            'Monitoring': ['monitor', 'log', 'alert', 'metrics'],
            'Database': ['db', 'database', 'migration', 'seed'],
            'Infrastructure': ['terraform', 'docker', 'kubernetes', 'helm'],
            'Communication': ['notify', 'slack', 'email', 'webhook']
        }
        
        # Find the best matching category
        best_category = 'General Automation'
        best_score = 0
        
        for category, keywords in category_patterns.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            if score > best_score:
                best_score = score
                best_category = category
        
        return best_category
    
    def generate_master_index(self) -> str:
        """Generate the master index markdown."""
        print("📋 Generating master index...")
        
        index = f"""# Zynx Automation Master Index

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

This master index provides a comprehensive view of all automation workflows in the Zynx workspace.

### Summary Statistics

- **Total Workflows**: {len(self.workflows)}
- **Categories**: {len(self.categories)}
- **File Types**: {len(self.file_types)}
- **Workflow Types**: {len(self.workflow_types)}
- **Unique Tags**: {len(self.tags)}

"""
        
        # Add category breakdown
        index += self._generate_category_section()
        
        # Add file type breakdown
        index += self._generate_file_type_section()
        
        # Add workflow type breakdown
        index += self._generate_workflow_type_section()
        
        # Add tag breakdown
        index += self._generate_tag_section()
        
        # Add detailed workflow listing
        index += self._generate_detailed_listing()
        
        # Add search index
        index += self._generate_search_index()
        
        return index
    
    def _generate_category_section(self) -> str:
        """Generate category breakdown section."""
        section = "## Categories\n\n"
        
        for category, workflows in sorted(self.categories.items()):
            section += f"### {category}\n\n"
            section += f"**Count**: {len(workflows)} workflows\n\n"
            
            # List workflows in this category
            for workflow in workflows[:10]:  # Show first 10
                section += f"- **{workflow.get('name', 'Unnamed')}** (`{workflow.get('file_path', 'Unknown')}`)\n"
                if workflow.get('description'):
                    section += f"  - {workflow['description'][:100]}...\n"
            
            if len(workflows) > 10:
                section += f"*... and {len(workflows) - 10} more workflows*\n"
            
            section += "\n"
        
        return section
    
    def _generate_file_type_section(self) -> str:
        """Generate file type breakdown section."""
        section = "## File Types\n\n"
        
        for file_type, workflows in sorted(self.file_types.items()):
            section += f"### {file_type or 'No Extension'}\n\n"
            section += f"**Count**: {len(workflows)} workflows\n\n"
            
            # Show sample files
            sample_files = [w.get('file_path', 'Unknown') for w in workflows[:5]]
            for file_path in sample_files:
                section += f"- `{file_path}`\n"
            
            if len(workflows) > 5:
                section += f"*... and {len(workflows) - 5} more files*\n"
            
            section += "\n"
        
        return section
    
    def _generate_workflow_type_section(self) -> str:
        """Generate workflow type breakdown section."""
        section = "## Workflow Types\n\n"
        
        for workflow_type, workflows in sorted(self.workflow_types.items()):
            section += f"### {workflow_type}\n\n"
            section += f"**Count**: {len(workflows)} workflows\n\n"
            
            # Show sample workflows
            for workflow in workflows[:5]:
                section += f"- **{workflow.get('name', 'Unnamed')}** (`{workflow.get('file_path', 'Unknown')}`)\n"
                if workflow.get('description'):
                    section += f"  - {workflow['description'][:80]}...\n"
            
            if len(workflows) > 5:
                section += f"*... and {len(workflows) - 5} more workflows*\n"
            
            section += "\n"
        
        return section
    
    def _generate_tag_section(self) -> str:
        """Generate tag breakdown section."""
        section = "## Tags\n\n"
        
        if not self.tags:
            section += "No tags found in workflows.\n\n"
            return section
        
        for tag, workflows in sorted(self.tags.items()):
            section += f"### {tag}\n\n"
            section += f"**Count**: {len(workflows)} workflows\n\n"
            
            # Show sample workflows
            for workflow in workflows[:5]:
                section += f"- **{workflow.get('name', 'Unnamed')}** (`{workflow.get('file_path', 'Unknown')}`)\n"
            
            if len(workflows) > 5:
                section += f"*... and {len(workflows) - 5} more workflows*\n"
            
            section += "\n"
        
        return section
    
    def _generate_detailed_listing(self) -> str:
        """Generate detailed workflow listing."""
        section = "## Detailed Workflow Listing\n\n"
        
        # Sort workflows by name
        sorted_workflows = sorted(self.workflows, key=lambda w: w.get('name', ''))
        
        for i, workflow in enumerate(sorted_workflows, 1):
            section += f"### {i}. {workflow.get('name', 'Unnamed Workflow')}\n\n"
            
            # Basic info
            section += f"- **File**: `{workflow.get('file_path', 'Unknown')}`\n"
            section += f"- **Type**: {workflow.get('workflow_type', 'Unknown')}\n"
            
            if workflow.get('description'):
                section += f"- **Description**: {workflow['description']}\n"
            
            # Triggers
            if workflow.get('triggers'):
                section += f"- **Triggers**: {', '.join(workflow['triggers'])}\n"
            
            # Actions
            if workflow.get('actions'):
                section += f"- **Actions**: {len(workflow['actions'])} steps\n"
                # Show first few actions
                for j, action in enumerate(workflow['actions'][:3]):
                    section += f"  - {action[:80]}{'...' if len(action) > 80 else ''}\n"
                if len(workflow['actions']) > 3:
                    section += f"  - ... and {len(workflow['actions']) - 3} more actions\n"
            
            # Dependencies
            if workflow.get('dependencies'):
                section += f"- **Dependencies**: {', '.join(workflow['dependencies'])}\n"
            
            # Tags
            if workflow.get('tags'):
                section += f"- **Tags**: {', '.join(workflow['tags'])}\n"
            
            # Hash for identification
            workflow_hash = self._generate_workflow_hash(workflow)
            section += f"- **Hash**: `{workflow_hash[:8]}`\n"
            
            section += "\n"
        
        return section
    
    def _generate_workflow_hash(self, workflow: dict) -> str:
        """Generate a hash for workflow identification."""
        content = f"{workflow.get('name', '')}{workflow.get('file_path', '')}{workflow.get('description', '')}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _generate_search_index(self) -> str:
        """Generate search index for quick lookup."""
        section = "## Search Index\n\n"
        
        # Create searchable terms
        search_terms = defaultdict(list)
        
        for workflow in self.workflows:
            # Add name terms
            name = workflow.get('name', '').lower()
            for word in name.split():
                if len(word) > 2:
                    search_terms[word].append(workflow)
            
            # Add description terms
            description = workflow.get('description', '').lower()
            for word in description.split():
                if len(word) > 2:
                    search_terms[word].append(workflow)
            
            # Add action terms
            for action in workflow.get('actions', []):
                for word in action.lower().split():
                    if len(word) > 2:
                        search_terms[word].append(workflow)
        
        # Show most common search terms
        common_terms = sorted(search_terms.items(), key=lambda x: len(x[1]), reverse=True)[:20]
        
        section += "### Common Search Terms\n\n"
        for term, workflows in common_terms:
            if len(workflows) > 1:  # Only show terms that match multiple workflows
                section += f"- **{term}**: {len(workflows)} workflows\n"
        
        section += "\n### Quick Lookup\n\n"
        section += "Use Ctrl+F to search for specific terms in this document.\n\n"
        
        return section
    
    def generate_json_index(self) -> dict:
        """Generate JSON format index for programmatic access."""
        index_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'total_workflows': len(self.workflows),
                'categories': len(self.categories),
                'file_types': len(self.file_types),
                'workflow_types': len(self.workflow_types),
                'tags': len(self.tags)
            },
            'statistics': {
                'categories': {cat: len(workflows) for cat, workflows in self.categories.items()},
                'file_types': {ft: len(workflows) for ft, workflows in self.file_types.items()},
                'workflow_types': {wt: len(workflows) for wt, workflows in self.workflow_types.items()},
                'tags': {tag: len(workflows) for tag, workflows in self.tags.items()}
            },
            'workflows': self.workflows,
            'search_index': self._generate_search_index_data()
        }
        
        return index_data
    
    def _generate_search_index_data(self) -> dict:
        """Generate search index data."""
        search_index = defaultdict(list)
        
        for i, workflow in enumerate(self.workflows):
            # Add workflow to search index by various criteria
            search_index['name'].append({
                'term': workflow.get('name', ''),
                'workflow_index': i
            })
            
            search_index['file_path'].append({
                'term': workflow.get('file_path', ''),
                'workflow_index': i
            })
            
            search_index['type'].append({
                'term': workflow.get('workflow_type', ''),
                'workflow_index': i
            })
            
            for tag in workflow.get('tags', []):
                search_index['tags'].append({
                    'term': tag,
                    'workflow_index': i
                })
        
        return dict(search_index)
    
    def save_index(self, output_dir: str = '.'):
        """Save the master index to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate markdown index
        markdown_index = self.generate_master_index()
        with open(output_path / 'Zynx_Automation_Index.md', 'w', encoding='utf-8') as f:
            f.write(markdown_index)
        
        # Generate JSON index
        json_index = self.generate_json_index()
        with open(output_path / 'Zynx_Automation_Index.json', 'w', encoding='utf-8') as f:
            json.dump(json_index, f, indent=2, default=str)
        
        # Generate summary report
        summary = self._generate_summary_report()
        with open(output_path / 'index_summary.md', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print(f"✅ Master index saved to {output_path}")
        return output_path
    
    def _generate_summary_report(self) -> str:
        """Generate a summary report."""
        summary = f"""# Zynx Automation Index Summary

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Quick Stats

- **Total Workflows**: {len(self.workflows)}
- **Categories**: {len(self.categories)}
- **File Types**: {len(self.file_types)}
- **Workflow Types**: {len(self.workflow_types)}
- **Tags**: {len(self.tags)}

## Top Categories

"""
        
        # Show top categories
        sorted_categories = sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True)
        for category, workflows in sorted_categories[:10]:
            summary += f"- **{category}**: {len(workflows)} workflows\n"
        
        summary += "\n## Top File Types\n\n"
        
        # Show top file types
        sorted_file_types = sorted(self.file_types.items(), key=lambda x: len(x[1]), reverse=True)
        for file_type, workflows in sorted_file_types[:10]:
            summary += f"- **{file_type or 'No Extension'}**: {len(workflows)} workflows\n"
        
        summary += "\n## Top Workflow Types\n\n"
        
        # Show top workflow types
        sorted_workflow_types = sorted(self.workflow_types.items(), key=lambda x: len(x[1]), reverse=True)
        for workflow_type, workflows in sorted_workflow_types[:10]:
            summary += f"- **{workflow_type}**: {len(workflows)} workflows\n"
        
        return summary

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate master index of automation workflows')
    parser.add_argument('--input', required=True,
                       help='Input JSON file with workflows data')
    parser.add_argument('--output', default='.',
                       help='Output directory for index files')
    
    args = parser.parse_args()
    
    # Load workflows
    with open(args.input, 'r', encoding='utf-8') as f:
        workflows_data = json.load(f)
    
    # Generate master index
    generator = MasterIndexGenerator()
    generator.load_workflows(workflows_data)
    generator.save_index(args.output)
    
    # Print summary
    print(f"\n📊 Index Generation Summary:")
    print(f"  Workflows processed: {len(workflows_data)}")
    print(f"  Categories found: {len(generator.categories)}")
    print(f"  File types: {len(generator.file_types)}")
    print(f"  Workflow types: {len(generator.workflow_types)}")
    print(f"  Tags: {len(generator.tags)}")
    
    print(f"\n🔝 Top categories:")
    sorted_categories = sorted(generator.categories.items(), key=lambda x: len(x[1]), reverse=True)
    for category, workflows in sorted_categories[:5]:
        print(f"  {category}: {len(workflows)} workflows")

if __name__ == '__main__':
    main()