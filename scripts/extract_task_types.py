#!/usr/bin/env python3
"""
Extract Task Types Script
========================

Analyzes workflow files to extract and categorize different types of automation tasks.
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import argparse
import json

class TaskTypeExtractor:
    """Extracts and categorizes task types from automation workflows."""
    
    def __init__(self):
        self.task_patterns = {
            'PR Management': [
                r'pull.?request', r'pr.?review', r'merge', r'code.?review',
                r'approval', r'checkout', r'fetch'
            ],
            'Deployment': [
                r'deploy', r'release', r'build', r'publish', r'push',
                r'docker', r'kubernetes', r'helm', r'terraform'
            ],
            'Testing': [
                r'test', r'validate', r'check', r'verify', r'assert',
                r'unit.?test', r'integration.?test', r'e2e', r'cypress'
            ],
            'Memory Debugger': [
                r'debug', r'memory', r'log', r'monitor', r'profile',
                r'analyze', r'inspect', r'trace', r'heap'
            ],
            'Security': [
                r'security', r'scan', r'vulnerability', r'audit',
                r'sast', r'dast', r'secrets', r'compliance'
            ],
            'Documentation': [
                r'docs', r'documentation', r'readme', r'api.?docs',
                r'generate', r'build.?docs', r'publish.?docs'
            ],
            'Dependency Management': [
                r'npm', r'yarn', r'pip', r'composer', r'gradle',
                r'update', r'upgrade', r'install', r'lock'
            ]
        }
        
        self.task_types = defaultdict(list)
        self.task_stats = defaultdict(int)
    
    def extract_from_file(self, file_path: str) -> Dict[str, List[str]]:
        """Extract task types from a single file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.extract_from_content(content, file_path)
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
            return {}
    
    def extract_from_content(self, content: str, file_path: str = '') -> Dict[str, List[str]]:
        """Extract task types from content."""
        content_lower = content.lower()
        extracted_tasks = defaultdict(list)
        
        for task_type, patterns in self.task_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content_lower, re.IGNORECASE)
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 50)
                    end = min(len(content), match.end() + 50)
                    context = content[start:end].strip()
                    
                    extracted_tasks[task_type].append({
                        'pattern': pattern,
                        'match': match.group(),
                        'context': context,
                        'file': file_path,
                        'position': match.start()
                    })
        
        return dict(extracted_tasks)
    
    def analyze_workspace(self, workspace_path: str, excluded_dirs: Set[str] = None) -> Dict[str, any]:
        """Analyze entire workspace for task types."""
        if excluded_dirs is None:
            excluded_dirs = {'node_modules', '.venv', '.git', 'build', 'dist'}
        
        workspace = Path(workspace_path)
        all_tasks = defaultdict(list)
        file_stats = {}
        
        print(f"🔍 Analyzing workspace: {workspace_path}")
        
        for root, dirs, files in os.walk(workspace):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for file in files:
                if self._is_workflow_file(file):
                    file_path = os.path.join(root, file)
                    tasks = self.extract_from_file(file_path)
                    
                    if tasks:
                        file_stats[file_path] = {
                            'total_tasks': sum(len(task_list) for task_list in tasks.values()),
                            'task_types': list(tasks.keys())
                        }
                        
                        for task_type, task_list in tasks.items():
                            all_tasks[task_type].extend(task_list)
        
        # Generate statistics
        stats = {
            'total_files': len(file_stats),
            'total_tasks': sum(len(tasks) for tasks in all_tasks.values()),
            'task_type_distribution': {task_type: len(tasks) for task_type, tasks in all_tasks.items()},
            'files_with_tasks': len([f for f in file_stats.values() if f['total_tasks'] > 0]),
            'most_common_tasks': self._get_most_common_tasks(all_tasks)
        }
        
        return {
            'tasks': dict(all_tasks),
            'file_stats': file_stats,
            'statistics': stats
        }
    
    def _is_workflow_file(self, filename: str) -> bool:
        """Check if file is a workflow file."""
        workflow_extensions = {'.yml', '.yaml', '.md', '.workflow', '.json'}
        return any(filename.endswith(ext) for ext in workflow_extensions)
    
    def _get_most_common_tasks(self, all_tasks: Dict[str, List]) -> List[Tuple[str, int]]:
        """Get most common task types."""
        task_counts = {task_type: len(tasks) for task_type, tasks in all_tasks.items()}
        return sorted(task_counts.items(), key=lambda x: x[1], reverse=True)
    
    def generate_report(self, analysis_result: Dict[str, any]) -> str:
        """Generate a comprehensive report of task types."""
        tasks = analysis_result['tasks']
        stats = analysis_result['statistics']
        
        report = """# Task Types Analysis Report

## Summary Statistics
"""
        
        report += f"- **Total Files Analyzed**: {stats['total_files']}\n"
        report += f"- **Files with Tasks**: {stats['files_with_tasks']}\n"
        report += f"- **Total Tasks Found**: {stats['total_tasks']}\n\n"
        
        report += "## Task Type Distribution\n\n"
        for task_type, count in stats['task_type_distribution'].items():
            if count > 0:
                percentage = (count / stats['total_tasks']) * 100 if stats['total_tasks'] > 0 else 0
                report += f"- **{task_type}**: {count} tasks ({percentage:.1f}%)\n"
        
        report += "\n## Detailed Task Analysis\n\n"
        
        for task_type, task_list in tasks.items():
            if task_list:
                report += f"### {task_type}\n\n"
                report += f"**Total Tasks**: {len(task_list)}\n\n"
                
                # Group by file
                tasks_by_file = defaultdict(list)
                for task in task_list:
                    tasks_by_file[task['file']].append(task)
                
                for file_path, file_tasks in tasks_by_file.items():
                    report += f"#### {file_path}\n\n"
                    for task in file_tasks[:5]:  # Show first 5 tasks per file
                        report += f"- **Pattern**: `{task['pattern']}`\n"
                        report += f"  - **Match**: `{task['match']}`\n"
                        report += f"  - **Context**: `{task['context'][:100]}...`\n\n"
                    
                    if len(file_tasks) > 5:
                        report += f"*... and {len(file_tasks) - 5} more tasks*\n\n"
        
        return report
    
    def save_analysis(self, analysis_result: Dict[str, any], output_dir: str = '.'):
        """Save analysis results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save JSON data
        with open(output_path / 'task_analysis.json', 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, indent=2, default=str)
        
        # Save report
        report = self.generate_report(analysis_result)
        with open(output_path / 'task_analysis_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✅ Analysis saved to {output_path}")
        return output_path

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Extract task types from automation workflows')
    parser.add_argument('--workspace', default='C:/Users/Zynxdata', 
                       help='Workspace path to analyze')
    parser.add_argument('--output', default='.', 
                       help='Output directory for analysis results')
    parser.add_argument('--file', 
                       help='Analyze single file instead of workspace')
    
    args = parser.parse_args()
    
    extractor = TaskTypeExtractor()
    
    if args.file:
        # Analyze single file
        tasks = extractor.extract_from_file(args.file)
        print(f"📄 Analysis of {args.file}:")
        for task_type, task_list in tasks.items():
            print(f"  {task_type}: {len(task_list)} tasks")
    else:
        # Analyze workspace
        analysis_result = extractor.analyze_workspace(args.workspace)
        extractor.save_analysis(analysis_result, args.output)
        
        # Print summary
        stats = analysis_result['statistics']
        print(f"\n📊 Analysis Summary:")
        print(f"  Files analyzed: {stats['total_files']}")
        print(f"  Files with tasks: {stats['files_with_tasks']}")
        print(f"  Total tasks found: {stats['total_tasks']}")
        
        print(f"\n🔝 Most common task types:")
        for task_type, count in stats['most_common_tasks'][:5]:
            print(f"  {task_type}: {count} tasks")

if __name__ == '__main__':
    main()