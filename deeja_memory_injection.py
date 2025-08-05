#!/usr/bin/env python3
"""
Deeja Memory Injection Script
=============================

Maps workflows with emotion labels and injects them into Deeja Memory.
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import argparse

class DeejaMemoryInjector:
    """Injects workflow data into Deeja Memory with emotion context."""
    
    def __init__(self, memory_path: str = "memory_logs"):
        self.memory_path = Path(memory_path)
        self.workflows = []
        self.memories = []
        
    def load_consolidated_workflows(self, workflow_dir: str = ".") -> List[Dict]:
        """Load consolidated workflow files."""
        print("📁 Loading consolidated workflows...")
        
        workflows = []
        workflow_path = Path(workflow_dir)
        
        # Look for consolidated workflow files
        for yml_file in workflow_path.glob("consolidated_*.yml"):
            try:
                with open(yml_file, 'r', encoding='utf-8') as f:
                    workflow_data = yaml.safe_load(f)
                    workflow_data['file_path'] = str(yml_file)
                    workflows.append(workflow_data)
                    print(f"  📄 Loaded: {yml_file.name}")
            except Exception as e:
                print(f"  ⚠️  Error loading {yml_file}: {e}")
        
        self.workflows = workflows
        print(f"  ✅ Loaded {len(workflows)} consolidated workflows")
        return workflows
    
    def extract_emotion_from_workflow(self, workflow_data: Dict) -> Optional[str]:
        """Extract emotion from workflow metadata."""
        # Check environment variables for emotion
        env = workflow_data.get('env', {})
        for key, value in env.items():
            if 'EMOTION' in key.upper():
                return value
        
        # Check memory context
        memory_context = workflow_data.get('memory_context', {})
        emotions = memory_context.get('emotions', [])
        if emotions:
            return emotions[0]
        
        # Check workflow name for emotion hints
        name = workflow_data.get('name', '').lower()
        if any(emotion in name for emotion in ['frustrated', 'excited', 'focused', 'hopeful', 'satisfied']):
            for emotion in ['frustrated', 'excited', 'focused', 'hopeful', 'satisfied']:
                if emotion in name:
                    return emotion
        
        return None
    
    def extract_trigger_from_workflow(self, workflow_data: Dict) -> List[str]:
        """Extract triggers from workflow."""
        triggers = []
        on_section = workflow_data.get('on', {})
        
        if isinstance(on_section, dict):
            triggers.extend(on_section.keys())
        
        return triggers
    
    def summarize_steps(self, workflow_data: Dict) -> str:
        """Summarize workflow steps."""
        jobs = workflow_data.get('jobs', {})
        steps_summary = []
        
        for job_name, job_data in jobs.items():
            if isinstance(job_data, dict):
                steps = job_data.get('steps', [])
                for step in steps:
                    if isinstance(step, dict):
                        step_name = step.get('name', 'Unknown step')
                        steps_summary.append(step_name)
        
        return " → ".join(steps_summary[:5])  # First 5 steps
    
    def create_memory_entry(self, workflow_data: Dict) -> Dict:
        """Create a Deeja memory entry from workflow data."""
        emotion = self.extract_emotion_from_workflow(workflow_data)
        triggers = self.extract_trigger_from_workflow(workflow_data)
        summary = self.summarize_steps(workflow_data)
        
        memory_entry = {
            "memory_id": f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "workflow_path": workflow_data.get('file_path', ''),
            "workflow_name": workflow_data.get('name', ''),
            "emotion": emotion or "neutral",
            "trigger": ", ".join(triggers) if triggers else "manual",
            "summary": summary,
            "timestamp": datetime.now().isoformat(),
            "user_context": f"Consolidated workflow: {workflow_data.get('description', '')}",
            "deeja_tag": self._determine_deeja_tag(workflow_data),
            "context": self._create_context_description(workflow_data, emotion)
        }
        
        return memory_entry
    
    def _determine_deeja_tag(self, workflow_data: Dict) -> str:
        """Determine Deeja tag based on workflow content."""
        name = workflow_data.get('name', '').lower()
        description = workflow_data.get('description', '').lower()
        
        if any(keyword in name or keyword in description for keyword in ['pr', 'pull request', 'review']):
            return "code_review"
        elif any(keyword in name or keyword in description for keyword in ['deploy', 'release', 'build']):
            return "deployment"
        elif any(keyword in name or keyword in description for keyword in ['test', 'validate', 'mvp']):
            return "testing"
        elif any(keyword in name or keyword in description for keyword in ['debug', 'memory', 'profile']):
            return "debugging"
        elif any(keyword in name or keyword in description for keyword in ['docs', 'documentation']):
            return "documentation"
        else:
            return "general_automation"
    
    def _create_context_description(self, workflow_data: Dict, emotion: Optional[str]) -> str:
        """Create context description for memory entry."""
        name = workflow_data.get('name', '')
        description = workflow_data.get('description', '')
        
        emotion_context = {
            "frustrated": "User was frustrated with current process, wanted to automate and streamline",
            "excited": "User was excited about new automation capabilities, wanted to implement quickly",
            "focused": "User was focused on specific problem, needed targeted automation",
            "hopeful": "User was hopeful about solution, wanted to validate and test thoroughly",
            "satisfied": "User was satisfied with current state, wanted to maintain and improve"
        }
        
        context = f"Workflow: {name}"
        if description:
            context += f" - {description}"
        
        if emotion and emotion in emotion_context:
            context += f" | {emotion_context[emotion]}"
        
        return context
    
    def inject_workflows_to_memory(self) -> List[Dict]:
        """Inject all workflows into Deeja memory."""
        print("🧠 Injecting workflows into Deeja memory...")
        
        memory_entries = []
        
        for workflow in self.workflows:
            memory_entry = self.create_memory_entry(workflow)
            memory_entries.append(memory_entry)
            
            emotion = memory_entry.get('emotion', 'neutral')
            print(f"  📎 Created memory for '{workflow.get('name', 'Unknown')}' (emotion: {emotion})")
        
        self.memories = memory_entries
        print(f"  ✅ Created {len(memory_entries)} memory entries")
        return memory_entries
    
    def save_memories(self, output_file: str = "memory_logs/injected_workflow_memories.json"):
        """Save memory entries to file."""
        print(f"💾 Saving memory entries to {output_file}...")
        
        # Ensure directory exists
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.memories, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ Saved {len(self.memories)} memory entries")
        return output_path
    
    def generate_memory_report(self) -> str:
        """Generate a report of injected memories."""
        print("📊 Generating memory injection report...")
        
        report = f"""# Deeja Memory Injection Report

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Summary

- **Total Workflows Processed**: {len(self.workflows)}
- **Memory Entries Created**: {len(self.memories)}
- **Emotion Tags**: {len(set(m.get('emotion') for m in self.memories))}

## Memory Entries

"""
        
        for i, memory in enumerate(self.memories, 1):
            report += f"### {i}. {memory.get('workflow_name', 'Unknown Workflow')}\n\n"
            report += f"- **Memory ID**: {memory.get('memory_id')}\n"
            report += f"- **Emotion**: {memory.get('emotion')}\n"
            report += f"- **Deeja Tag**: {memory.get('deeja_tag')}\n"
            report += f"- **Trigger**: {memory.get('trigger')}\n"
            report += f"- **Summary**: {memory.get('summary')}\n"
            report += f"- **Context**: {memory.get('context')}\n"
            report += "\n"
        
        return report
    
    def save_report(self, report: str, output_file: str = "deeja_memory_injection_report.md"):
        """Save the memory injection report."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"  ✅ Saved report to {output_file}")
    
    def run(self, workflow_dir: str = "."):
        """Main execution method."""
        print("🚀 Starting Deeja Memory Injection...")
        
        # Step 1: Load consolidated workflows
        self.load_consolidated_workflows(workflow_dir)
        
        # Step 2: Inject workflows to memory
        self.inject_workflows_to_memory()
        
        # Step 3: Save memories
        memory_file = self.save_memories()
        
        # Step 4: Generate and save report
        report = self.generate_memory_report()
        self.save_report(report)
        
        print("✅ Deeja Memory Injection completed successfully!")
        print(f"📁 Memory file: {memory_file}")
        print(f"📊 Report: deeja_memory_injection_report.md")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Deeja Memory Injection for Workflows')
    parser.add_argument('--workflow-dir', default='.',
                       help='Directory containing consolidated workflow files')
    parser.add_argument('--memory-path', default='memory_logs',
                       help='Path to save memory files')
    parser.add_argument('--output-file', default='memory_logs/injected_workflow_memories.json',
                       help='Output file for memory entries')
    
    args = parser.parse_args()
    
    injector = DeejaMemoryInjector(args.memory_path)
    injector.run(args.workflow_dir)
    
    # Print summary
    print(f"\n📊 Injection Summary:")
    print(f"  Workflows processed: {len(injector.workflows)}")
    print(f"  Memory entries created: {len(injector.memories)}")
    
    emotion_counts = {}
    for memory in injector.memories:
        emotion = memory.get('emotion', 'neutral')
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    print(f"  Emotion distribution:")
    for emotion, count in emotion_counts.items():
        print(f"    {emotion}: {count}")

if __name__ == '__main__':
    main()