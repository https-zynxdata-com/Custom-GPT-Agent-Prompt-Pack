#!/usr/bin/env python3
"""
Zynx Consolidation Agent v2
===========================

Enhanced agent with Deeja Memory and MCP Prompt Injector integration.
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
import argparse
import subprocess
import sys
from datetime import datetime
import hashlib

@dataclass
class DeejaMemory:
    """Represents a Deeja memory entry."""
    memory_id: str
    task_id: str
    emotion: str
    tag: str
    context: str
    timestamp: str
    trigger_pattern: str = ""
    workflow_name: str = ""

@dataclass
class MCPPrompt:
    """Represents an MCP prompt entry."""
    prompt_id: str
    task_type: str
    workflow_tag: str
    prompt: str
    reasoning_score: float
    injected_context: str
    timestamp: str

@dataclass
class EnhancedAutomationWorkflow:
    """Enhanced workflow with memory and prompt integration."""
    file_path: str
    workflow_type: str
    name: str
    description: str
    triggers: List[str]
    actions: List[str]
    dependencies: List[str]
    tags: List[str]
    similarity_score: float = 0.0
    
    # Deeja Memory integration
    emotion: str = ""
    deeja_tag: str = ""
    memory_id: str = ""
    memory_context: str = ""
    
    # MCP Prompt integration
    injected_prompt: str = ""
    reasoning_score: float = 0.0
    prompt_id: str = ""
    mcp_context: str = ""

class ZynxConsolidationAgentV2:
    """Enhanced agent with Deeja Memory and MCP Prompt Injector integration."""
    
    def __init__(self, workspace_path: str = "C:/Users/Zynxdata"):
        self.workspace_path = Path(workspace_path)
        self.excluded_dirs = {
            'node_modules', '.venv', '.git', 'build', 'dist', 
            '__pycache__', '.pytest_cache', '.vscode', '.idea'
        }
        self.workflow_files = []
        self.workflows = []
        self.clusters = {}
        
        # Memory and Prompt data
        self.deeja_memories = []
        self.mcp_prompts = []
        
        # Configuration
        self.memory_path = "memory_logs"
        self.prompt_path = "mcp_prompts"
        
    def load_deeja_memories(self) -> List[DeejaMemory]:
        """Load Deeja memory logs."""
        print("🧠 Loading Deeja memories...")
        
        memories = []
        memory_dir = Path(self.memory_path)
        
        if not memory_dir.exists():
            print(f"  ⚠️  Memory directory not found: {memory_dir}")
            return memories
        
        # Load all JSON files from memory_logs/**/*.json
        for json_file in memory_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    memory_data = json.load(f)
                    
                    # Handle both single memory and array of memories
                    if isinstance(memory_data, list):
                        for mem in memory_data:
                            memories.append(self._parse_memory_entry(mem, json_file))
                    else:
                        memories.append(self._parse_memory_entry(memory_data, json_file))
                        
            except Exception as e:
                print(f"  ⚠️  Error loading memory {json_file}: {e}")
        
        self.deeja_memories = memories
        print(f"  ✅ Loaded {len(memories)} Deeja memories")
        return memories
    
    def _parse_memory_entry(self, memory_data: dict, file_path: Path) -> DeejaMemory:
        """Parse a single memory entry."""
        return DeejaMemory(
            memory_id=memory_data.get('memory_id', ''),
            task_id=memory_data.get('task_id', ''),
            emotion=memory_data.get('emotion', ''),
            tag=memory_data.get('tag', ''),
            context=memory_data.get('context', ''),
            timestamp=memory_data.get('timestamp', ''),
            trigger_pattern=memory_data.get('trigger_pattern', ''),
            workflow_name=memory_data.get('workflow_name', '')
        )
    
    def load_mcp_prompts(self) -> List[MCPPrompt]:
        """Load MCP prompt data."""
        print("🔧 Loading MCP prompts...")
        
        prompts = []
        prompt_dir = Path(self.prompt_path)
        
        if not prompt_dir.exists():
            print(f"  ⚠️  Prompt directory not found: {prompt_dir}")
            return prompts
        
        # Load all JSON files from mcp_prompts/**/*.json
        for json_file in prompt_dir.rglob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    prompt_data = json.load(f)
                    
                    # Handle both single prompt and array of prompts
                    if isinstance(prompt_data, list):
                        for prompt in prompt_data:
                            prompts.append(self._parse_prompt_entry(prompt, json_file))
                    else:
                        prompts.append(self._parse_prompt_entry(prompt_data, json_file))
                        
            except Exception as e:
                print(f"  ⚠️  Error loading prompt {json_file}: {e}")
        
        self.mcp_prompts = prompts
        print(f"  ✅ Loaded {len(prompts)} MCP prompts")
        return prompts
    
    def _parse_prompt_entry(self, prompt_data: dict, file_path: Path) -> MCPPrompt:
        """Parse a single prompt entry."""
        return MCPPrompt(
            prompt_id=prompt_data.get('prompt_id', ''),
            task_type=prompt_data.get('task_type', ''),
            workflow_tag=prompt_data.get('workflow_tag', ''),
            prompt=prompt_data.get('prompt', ''),
            reasoning_score=prompt_data.get('reasoning_score', 0.0),
            injected_context=prompt_data.get('injected_context', ''),
            timestamp=prompt_data.get('timestamp', '')
        )
    
    def enrich_workflows_with_memory(self, workflows: List[EnhancedAutomationWorkflow]) -> List[EnhancedAutomationWorkflow]:
        """Enrich workflows with Deeja memory data."""
        print("🔗 Enriching workflows with Deeja memories...")
        
        for workflow in workflows:
            # Find matching memories by task_id or workflow name similarity
            matching_memories = self._find_matching_memories(workflow)
            
            if matching_memories:
                # Use the best matching memory
                best_memory = matching_memories[0]
                workflow.emotion = best_memory.emotion
                workflow.deeja_tag = best_memory.tag
                workflow.memory_id = best_memory.memory_id
                workflow.memory_context = best_memory.context
                print(f"  📎 Matched workflow '{workflow.name}' with memory '{best_memory.memory_id}' (emotion: {best_memory.emotion})")
        
        return workflows
    
    def _find_matching_memories(self, workflow: EnhancedAutomationWorkflow) -> List[DeejaMemory]:
        """Find memories that match a workflow."""
        matches = []
        
        for memory in self.deeja_memories:
            # Check for exact task_id match
            if memory.task_id and memory.task_id in workflow.name:
                matches.append((memory, 1.0))  # Exact match
                continue
            
            # Check for workflow name similarity
            if memory.workflow_name and self._similarity_score(workflow.name, memory.workflow_name) > 0.7:
                matches.append((memory, 0.8))  # High similarity
                continue
            
            # Check for trigger pattern match
            if memory.trigger_pattern and any(trigger in memory.trigger_pattern for trigger in workflow.triggers):
                matches.append((memory, 0.6))  # Trigger match
                continue
            
            # Check for context similarity
            if memory.context and self._similarity_score(workflow.description, memory.context) > 0.5:
                matches.append((memory, 0.5))  # Context similarity
        
        # Sort by match score and return top matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return [memory for memory, score in matches[:3]]  # Top 3 matches
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity score."""
        if not text1 or not text2:
            return 0.0
        
        # Simple word overlap similarity
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def enrich_workflows_with_prompts(self, workflows: List[EnhancedAutomationWorkflow]) -> List[EnhancedAutomationWorkflow]:
        """Enrich workflows with MCP prompt data."""
        print("🔧 Enriching workflows with MCP prompts...")
        
        for workflow in workflows:
            # Find matching prompts by task_type, workflow_tag, or content similarity
            matching_prompts = self._find_matching_prompts(workflow)
            
            if matching_prompts:
                # Use the best matching prompt
                best_prompt = matching_prompts[0]
                workflow.injected_prompt = best_prompt.prompt
                workflow.reasoning_score = best_prompt.reasoning_score
                workflow.prompt_id = best_prompt.prompt_id
                workflow.mcp_context = best_prompt.injected_context
                print(f"  🔧 Matched workflow '{workflow.name}' with prompt '{best_prompt.prompt_id}' (score: {best_prompt.reasoning_score})")
        
        return workflows
    
    def _find_matching_prompts(self, workflow: EnhancedAutomationWorkflow) -> List[MCPPrompt]:
        """Find prompts that match a workflow."""
        matches = []
        
        for prompt in self.mcp_prompts:
            # Check for task_type match
            if prompt.task_type and prompt.task_type.lower() in workflow.name.lower():
                matches.append((prompt, 1.0))  # Exact task type match
                continue
            
            # Check for workflow_tag match
            if prompt.workflow_tag and prompt.workflow_tag.lower() in workflow.name.lower():
                matches.append((prompt, 0.9))  # Workflow tag match
                continue
            
            # Check for content similarity
            if prompt.prompt and self._similarity_score(workflow.description, prompt.prompt) > 0.3:
                matches.append((prompt, 0.6))  # Content similarity
                continue
            
            # Check for injected context match
            if prompt.injected_context and self._similarity_score(workflow.description, prompt.injected_context) > 0.3:
                matches.append((prompt, 0.5))  # Context similarity
        
        # Sort by match score and return top matches
        matches.sort(key=lambda x: x[1], reverse=True)
        return [prompt for prompt, score in matches[:3]]  # Top 3 matches
    
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
    
    def parse_workflows(self) -> List[EnhancedAutomationWorkflow]:
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
    
    def _parse_single_workflow(self, file_path: str) -> Optional[EnhancedAutomationWorkflow]:
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
    
    def _extract_from_yaml(self, file_path: str, data: dict) -> Optional[EnhancedAutomationWorkflow]:
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
        
        return EnhancedAutomationWorkflow(
            file_path=file_path,
            workflow_type=workflow_type,
            name=name,
            description=description,
            triggers=triggers,
            actions=actions,
            dependencies=dependencies,
            tags=tags
        )
    
    def _extract_from_markdown(self, file_path: str, content: str) -> Optional[EnhancedAutomationWorkflow]:
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
            return EnhancedAutomationWorkflow(
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
    
    def cluster_workflows(self) -> Dict[str, List[EnhancedAutomationWorkflow]]:
        """Cluster workflows by similarity with memory and prompt context."""
        print("🔗 Clustering workflows by similarity...")
        
        clusters = defaultdict(list)
        
        for workflow in self.workflows:
            cluster_key = self._determine_enhanced_cluster(workflow)
            clusters[cluster_key].append(workflow)
        
        self.clusters = dict(clusters)
        
        for cluster_name, workflows in self.clusters.items():
            print(f"  📊 Cluster '{cluster_name}': {len(workflows)} workflows")
        
        return self.clusters
    
    def _determine_enhanced_cluster(self, workflow: EnhancedAutomationWorkflow) -> str:
        """Determine cluster with memory and prompt context."""
        # Analyze workflow content to determine cluster
        content = f"{workflow.name} {workflow.description} {' '.join(workflow.actions)}"
        content_lower = content.lower()
        
        # Add memory context to analysis
        if workflow.memory_context:
            content_lower += f" {workflow.memory_context.lower()}"
        
        # Add prompt context to analysis
        if workflow.mcp_context:
            content_lower += f" {workflow.mcp_context.lower()}"
        
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
    
    def generate_emotion_consolidated_index(self) -> str:
        """Generate emotion-aware consolidated index."""
        print("📊 Generating emotion consolidated index...")
        
        index_content = f"""# Zynx Emotion Consolidated Index

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

This index provides an emotion-aware view of all automation workflows, enriched with Deeja memory data and MCP prompt context.

## Summary Statistics

- **Total Workflows**: {len(self.workflows)}
- **Deeja Memories**: {len(self.deeja_memories)}
- **MCP Prompts**: {len(self.mcp_prompts)}
- **Emotion Tags**: {len(set(wf.emotion for wf in self.workflows if wf.emotion))}
- **Clusters**: {len(self.clusters)}

## Emotion Analysis

"""
        
        # Group workflows by emotion
        emotion_groups = defaultdict(list)
        for workflow in self.workflows:
            if workflow.emotion:
                emotion_groups[workflow.emotion].append(workflow)
        
        for emotion, workflows in emotion_groups.items():
            index_content += f"### {emotion.title()} Workflows\n\n"
            index_content += f"**Count**: {len(workflows)} workflows\n\n"
            
            for workflow in workflows:
                index_content += f"#### {workflow.name}\n\n"
                index_content += f"- **File**: `{workflow.file_path}`\n"
                index_content += f"- **Emotion**: {workflow.emotion}\n"
                index_content += f"- **Deeja Tag**: {workflow.deeja_tag}\n"
                if workflow.memory_context:
                    index_content += f"- **Memory Context**: {workflow.memory_context[:100]}...\n"
                if workflow.reasoning_score > 0:
                    index_content += f"- **Reasoning Score**: {workflow.reasoning_score:.2f}\n"
                index_content += "\n"
        
        return index_content
    
    def generate_mcp_prompt_reasoning_map(self) -> str:
        """Generate MCP prompt reasoning map."""
        print("🔧 Generating MCP prompt reasoning map...")
        
        map_content = f"""# MCP Prompt Reasoning Map

*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

This map shows how MCP prompts relate to automation workflows and their reasoning patterns.

## Prompt-Workflow Relationships

"""
        
        # Group by task type
        task_type_groups = defaultdict(list)
        for workflow in self.workflows:
            if workflow.prompt_id:
                task_type_groups[workflow.workflow_type].append(workflow)
        
        for task_type, workflows in task_type_groups.items():
            map_content += f"### {task_type}\n\n"
            
            for workflow in workflows:
                map_content += f"#### {workflow.name}\n\n"
                map_content += f"- **Prompt ID**: {workflow.prompt_id}\n"
                map_content += f"- **Reasoning Score**: {workflow.reasoning_score:.2f}\n"
                if workflow.injected_prompt:
                    map_content += f"- **Injected Prompt**: {workflow.injected_prompt[:100]}...\n"
                if workflow.mcp_context:
                    map_content += f"- **MCP Context**: {workflow.mcp_context[:100]}...\n"
                map_content += "\n"
        
        return map_content
    
    def generate_overlap_matrix(self) -> str:
        """Generate enhanced overlap matrix with memory and prompt context."""
        print("📊 Generating enhanced overlap matrix...")
        
        matrix_content = """# Zynx Enhanced Automation Overlap Matrix

## Workflow Clusters Analysis with Memory & Prompt Context

"""
        
        for cluster_name, workflows in self.clusters.items():
            matrix_content += f"### {cluster_name}\n\n"
            matrix_content += f"**Total Workflows**: {len(workflows)}\n\n"
            
            # Group by similarity with memory context
            similar_workflows = self._group_similar_workflows_enhanced(workflows)
            
            for group_name, group_workflows in similar_workflows.items():
                matrix_content += f"#### {group_name}\n\n"
                for workflow in group_workflows:
                    matrix_content += f"- **{workflow.name}** (`{workflow.file_path}`)\n"
                    if workflow.description:
                        matrix_content += f"  - {workflow.description}\n"
                    if workflow.emotion:
                        matrix_content += f"  - **Emotion**: {workflow.emotion}\n"
                    if workflow.deeja_tag:
                        matrix_content += f"  - **Deeja Tag**: {workflow.deeja_tag}\n"
                    if workflow.reasoning_score > 0:
                        matrix_content += f"  - **Reasoning Score**: {workflow.reasoning_score:.2f}\n"
                    if workflow.triggers:
                        matrix_content += f"  - Triggers: {', '.join(workflow.triggers)}\n"
                    if workflow.actions:
                        matrix_content += f"  - Actions: {len(workflow.actions)} steps\n"
                matrix_content += "\n"
        
        return matrix_content
    
    def _group_similar_workflows_enhanced(self, workflows: List[EnhancedAutomationWorkflow]) -> Dict[str, List[EnhancedAutomationWorkflow]]:
        """Group workflows by similarity with enhanced context."""
        groups = defaultdict(list)
        
        for workflow in workflows:
            # Create enhanced signature including memory and prompt context
            signature = self._create_enhanced_workflow_signature(workflow)
            groups[signature].append(workflow)
        
        return dict(groups)
    
    def _create_enhanced_workflow_signature(self, workflow: EnhancedAutomationWorkflow) -> str:
        """Create enhanced signature for workflow similarity."""
        signature_parts = []
        
        if workflow.triggers:
            signature_parts.append(f"triggers:{','.join(sorted(workflow.triggers))}")
        
        if workflow.actions:
            action_sigs = [action[:50] for action in workflow.actions[:3]]
            signature_parts.append(f"actions:{','.join(action_sigs)}")
        
        # Add emotion context
        if workflow.emotion:
            signature_parts.append(f"emotion:{workflow.emotion}")
        
        # Add reasoning score
        if workflow.reasoning_score > 0:
            signature_parts.append(f"reasoning:{workflow.reasoning_score:.1f}")
        
        return "|".join(signature_parts) if signature_parts else "unknown"
    
    def consolidate_workflows(self) -> Dict[str, str]:
        """Consolidate workflows with memory and prompt context."""
        print("🔧 Consolidating workflows with enhanced context...")
        
        consolidated = {}
        
        for cluster_name, workflows in self.clusters.items():
            if len(workflows) > 1:
                # Consolidate workflows in this cluster with memory context
                consolidated_workflow = self._create_enhanced_consolidated_workflow(cluster_name, workflows)
                consolidated[cluster_name] = consolidated_workflow
        
        return consolidated
    
    def _create_enhanced_consolidated_workflow(self, cluster_name: str, workflows: List[EnhancedAutomationWorkflow]) -> str:
        """Create enhanced consolidated workflow with memory and prompt context."""
        # Create a master workflow that combines all similar workflows
        consolidated = {
            'name': f'Zynx {cluster_name} Master Workflow',
            'description': f'Consolidated workflow for {cluster_name} operations with memory context',
            'on': self._merge_triggers(workflows),
            'jobs': self._merge_jobs(workflows),
            'env': self._merge_environment(workflows),
            'memory_context': self._extract_memory_context(workflows),
            'prompt_context': self._extract_prompt_context(workflows)
        }
        
        return yaml.dump(consolidated, default_flow_style=False, sort_keys=False)
    
    def _extract_memory_context(self, workflows: List[EnhancedAutomationWorkflow]) -> dict:
        """Extract memory context from workflows."""
        memory_context = {
            'emotions': list(set(wf.emotion for wf in workflows if wf.emotion)),
            'deeja_tags': list(set(wf.deeja_tag for wf in workflows if wf.deeja_tag)),
            'memory_ids': list(set(wf.memory_id for wf in workflows if wf.memory_id))
        }
        return memory_context
    
    def _extract_prompt_context(self, workflows: List[EnhancedAutomationWorkflow]) -> dict:
        """Extract prompt context from workflows."""
        prompt_context = {
            'prompt_ids': list(set(wf.prompt_id for wf in workflows if wf.prompt_id)),
            'reasoning_scores': [wf.reasoning_score for wf in workflows if wf.reasoning_score > 0],
            'average_reasoning_score': sum(wf.reasoning_score for wf in workflows if wf.reasoning_score > 0) / max(1, len([wf for wf in workflows if wf.reasoning_score > 0]))
        }
        return prompt_context
    
    def _merge_triggers(self, workflows: List[EnhancedAutomationWorkflow]) -> dict:
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
    
    def _merge_jobs(self, workflows: List[EnhancedAutomationWorkflow]) -> dict:
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
    
    def _merge_environment(self, workflows: List[EnhancedAutomationWorkflow]) -> dict:
        """Merge environment variables from multiple workflows."""
        env = {}
        
        for workflow in workflows:
            # Add workflow-specific environment variables
            env[f'{workflow.name.upper()}_ENABLED'] = 'true'
            
            # Add emotion context
            if workflow.emotion:
                env[f'{workflow.name.upper()}_EMOTION'] = workflow.emotion
            
            # Add reasoning score
            if workflow.reasoning_score > 0:
                env[f'{workflow.name.upper()}_REASONING_SCORE'] = str(workflow.reasoning_score)
        
        return env
    
    def save_outputs(self, overlap_matrix: str, emotion_index: str, mcp_map: str, consolidated_workflows: Dict[str, str]):
        """Save all enhanced outputs to files."""
        print("💾 Saving enhanced outputs...")
        
        # Save overlap matrix
        with open('overlap_matrix.md', 'w', encoding='utf-8') as f:
            f.write(overlap_matrix)
        print("  ✅ Saved: overlap_matrix.md")
        
        # Save emotion consolidated index
        with open('Zynx_Emotion_Consolidated_Index.md', 'w', encoding='utf-8') as f:
            f.write(emotion_index)
        print("  ✅ Saved: Zynx_Emotion_Consolidated_Index.md")
        
        # Save MCP prompt reasoning map
        with open('MCP_Prompt_Reasoning_Map.md', 'w', encoding='utf-8') as f:
            f.write(mcp_map)
        print("  ✅ Saved: MCP_Prompt_Reasoning_Map.md")
        
        # Save consolidated workflows
        for cluster_name, workflow_content in consolidated_workflows.items():
            filename = f"consolidated_{cluster_name.lower().replace(' ', '_')}.yml"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(workflow_content)
            print(f"  ✅ Saved: {filename}")
    
    def run(self):
        """Main execution method with memory and prompt integration."""
        print("🚀 Starting Zynx Consolidation Agent v2...")
        
        # Step 1: Load memory and prompt data
        self.load_deeja_memories()
        self.load_mcp_prompts()
        
        # Step 2: Scan workspace
        self.scan_workspace()
        
        # Step 3: Parse workflows
        self.parse_workflows()
        
        # Step 4: Enrich workflows with memory and prompt data
        self.workflows = self.enrich_workflows_with_memory(self.workflows)
        self.workflows = self.enrich_workflows_with_prompts(self.workflows)
        
        # Step 5: Cluster workflows
        self.cluster_workflows()
        
        # Step 6: Generate enhanced outputs
        overlap_matrix = self.generate_overlap_matrix()
        emotion_index = self.generate_emotion_consolidated_index()
        mcp_map = self.generate_mcp_prompt_reasoning_map()
        consolidated_workflows = self.consolidate_workflows()
        
        # Step 7: Save outputs
        self.save_outputs(overlap_matrix, emotion_index, mcp_map, consolidated_workflows)
        
        print("✅ Zynx Consolidation Agent v2 completed successfully!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Zynx Consolidation Agent v2 with Memory & Prompt Integration')
    parser.add_argument('--workspace', default='C:/Users/Zynxdata', 
                       help='Workspace path to scan')
    parser.add_argument('--apply', action='store_true',
                       help='Apply consolidation and create PR')
    parser.add_argument('--memory-path', default='memory_logs',
                       help='Path to Deeja memory logs')
    parser.add_argument('--prompt-path', default='mcp_prompts',
                       help='Path to MCP prompt data')
    
    args = parser.parse_args()
    
    agent = ZynxConsolidationAgentV2(args.workspace)
    agent.memory_path = args.memory_path
    agent.prompt_path = args.prompt_path
    agent.run()
    
    if args.apply:
        print("🔄 Applying consolidation...")
        # TODO: Implement PR creation logic
        print("  📝 Creating pull request...")

if __name__ == '__main__':
    main()