#!/usr/bin/env python3
"""
Zynx Dispatcher Enhanced
========================

Enhanced dispatcher that uses emotion consolidated index and MCP reasoning map.
"""

import os
import yaml
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse

class ZynxDispatcherEnhanced:
    """Enhanced dispatcher with emotion-aware routing and MCP prompt injection."""
    
    def __init__(self):
        self.emotion_index = {}
        self.mcp_reasoning_map = {}
        self.overlap_matrix = {}
        self.memory_data = []
        self.prompt_templates = {}
        
    def load_emotion_consolidated_index(self, index_file: str = "Zynx_Emotion_Consolidated_Index.md") -> Dict:
        """Load emotion consolidated index."""
        print("📊 Loading emotion consolidated index...")
        
        if not os.path.exists(index_file):
            print(f"  ⚠️  Index file not found: {index_file}")
            return {}
        
        # Parse markdown index to extract emotion data
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract emotion groups
        emotion_groups = {}
        current_emotion = None
        current_workflows = []
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('### ') and 'Workflows' in line:
                if current_emotion and current_workflows:
                    emotion_groups[current_emotion] = current_workflows
                
                current_emotion = line.replace('### ', '').replace(' Workflows', '').lower()
                current_workflows = []
            
            elif line.startswith('#### ') and current_emotion:
                workflow_name = line.replace('#### ', '').strip()
                current_workflows.append(workflow_name)
        
        # Add last group
        if current_emotion and current_workflows:
            emotion_groups[current_emotion] = current_workflows
        
        self.emotion_index = emotion_groups
        print(f"  ✅ Loaded {len(emotion_groups)} emotion groups")
        return emotion_groups
    
    def load_mcp_reasoning_map(self, map_file: str = "MCP_Prompt_Reasoning_Map.md") -> Dict:
        """Load MCP prompt reasoning map."""
        print("🔧 Loading MCP prompt reasoning map...")
        
        if not os.path.exists(map_file):
            print(f"  ⚠️  Reasoning map not found: {map_file}")
            return {}
        
        # Parse markdown map to extract reasoning data
        with open(map_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract workflow-prompt relationships
        reasoning_map = {}
        current_workflow = None
        
        lines = content.split('\n')
        for line in lines:
            if line.startswith('#### ') and 'Workflow' not in line:
                current_workflow = line.replace('#### ', '').strip()
                reasoning_map[current_workflow] = {}
            
            elif line.startswith('- **Prompt ID**:') and current_workflow:
                prompt_id = line.replace('- **Prompt ID**: ', '').strip()
                reasoning_map[current_workflow]['prompt_id'] = prompt_id
            
            elif line.startswith('- **Reasoning Score**:') and current_workflow:
                score_str = line.replace('- **Reasoning Score**: ', '').strip()
                try:
                    score = float(score_str)
                    reasoning_map[current_workflow]['reasoning_score'] = score
                except ValueError:
                    reasoning_map[current_workflow]['reasoning_score'] = 0.0
        
        self.mcp_reasoning_map = reasoning_map
        print(f"  ✅ Loaded {len(reasoning_map)} workflow-prompt relationships")
        return reasoning_map
    
    def load_memory_data(self, memory_file: str = "memory_logs/injected_workflow_memories.json") -> List[Dict]:
        """Load Deeja memory data."""
        print("🧠 Loading Deeja memory data...")
        
        if not os.path.exists(memory_file):
            print(f"  ⚠️  Memory file not found: {memory_file}")
            return []
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            memory_data = json.load(f)
        
        self.memory_data = memory_data
        print(f"  ✅ Loaded {len(memory_data)} memory entries")
        return memory_data
    
    def load_prompt_templates(self, template_file: str = "mcp_prompt_injector_template.yaml") -> Dict:
        """Load MCP prompt injector templates."""
        print("📝 Loading prompt templates...")
        
        if not os.path.exists(template_file):
            print(f"  ⚠️  Template file not found: {template_file}")
            return {}
        
        with open(template_file, 'r', encoding='utf-8') as f:
            templates = yaml.safe_load(f)
        
        self.prompt_templates = templates
        print(f"  ✅ Loaded prompt templates")
        return templates
    
    def find_workflow_suggestion(self, task_description: str, user_emotion: str = None) -> Tuple[str, Dict]:
        """Find workflow suggestion based on task and emotion."""
        print(f"🔍 Finding workflow suggestion for: {task_description}")
        
        # Score workflows based on task similarity and emotion match
        workflow_scores = {}
        
        for workflow_name, emotion in self.emotion_index.items():
            for workflow in emotion:
                score = self._calculate_workflow_score(workflow, task_description, user_emotion)
                workflow_scores[workflow] = score
        
        # Get top suggestion
        if workflow_scores:
            best_workflow = max(workflow_scores.items(), key=lambda x: x[1])
            return best_workflow[0], {
                'score': best_workflow[1],
                'emotion': self._get_workflow_emotion(best_workflow[0]),
                'reasoning_score': self._get_workflow_reasoning_score(best_workflow[0])
            }
        
        return None, {}
    
    def _calculate_workflow_score(self, workflow_name: str, task_description: str, user_emotion: str = None) -> float:
        """Calculate workflow suggestion score."""
        score = 0.0
        
        # Task similarity (simple keyword matching)
        task_lower = task_description.lower()
        workflow_lower = workflow_name.lower()
        
        # Check for keyword matches
        keywords = ['pr', 'pull request', 'deploy', 'test', 'debug', 'docs', 'automation']
        for keyword in keywords:
            if keyword in task_lower and keyword in workflow_lower:
                score += 0.3
        
        # Emotion matching
        if user_emotion:
            workflow_emotion = self._get_workflow_emotion(workflow_name)
            if workflow_emotion == user_emotion:
                score += 0.4
        
        # Reasoning score boost
        reasoning_score = self._get_workflow_reasoning_score(workflow_name)
        if reasoning_score > 0.7:
            score += 0.2
        
        return score
    
    def _get_workflow_emotion(self, workflow_name: str) -> Optional[str]:
        """Get emotion for a workflow."""
        for emotion, workflows in self.emotion_index.items():
            if workflow_name in workflows:
                return emotion
        return None
    
    def _get_workflow_reasoning_score(self, workflow_name: str) -> float:
        """Get reasoning score for a workflow."""
        return self.mcp_reasoning_map.get(workflow_name, {}).get('reasoning_score', 0.0)
    
    def generate_emotion_triggered_response(self, workflow_name: str, trigger: str, emotion: str) -> str:
        """Generate emotion-triggered response using templates."""
        print(f"🎭 Generating emotion-triggered response for {workflow_name}")
        
        # Find matching template
        template_key = None
        for key in self.prompt_templates.get('workflow_prompt_mappings', {}):
            if key in workflow_name.lower():
                template_key = key
                break
        
        if not template_key:
            return f"หนูเห็นว่า {workflow_name} น่าจะเหมาะกับ task นี้ค่ะ ต้องการให้หนูช่วย setup ไหมคะ?"
        
        template = self.prompt_templates['workflow_prompt_mappings'][template_key]
        
        # Find matching trigger
        for prompt in template.get('inject_prompts', []):
            if prompt.get('trigger') == trigger:
                return prompt.get('deeja_response', f"หนูจะช่วยจัดการ {workflow_name} ให้ค่ะ")
        
        # Fallback to emotion pattern
        emotion_patterns = self.prompt_templates.get('emotion_response_patterns', {})
        if emotion in emotion_patterns:
            pattern = emotion_patterns[emotion]
            return f"{pattern.get('response_prefix', '')} {workflow_name} ให้เรียบร้อยนะคะ {pattern.get('emotion_icon', '')}"
        
        return f"หนูจะช่วยจัดการ {workflow_name} ให้ค่ะ"
    
    def get_memory_context(self, workflow_name: str) -> Optional[Dict]:
        """Get memory context for a workflow."""
        for memory in self.memory_data:
            if memory.get('workflow_name') == workflow_name:
                return memory
        return None
    
    def suggest_workflow_with_context(self, task_description: str, user_emotion: str = None) -> Dict:
        """Suggest workflow with full context."""
        workflow_name, metadata = self.find_workflow_suggestion(task_description, user_emotion)
        
        if not workflow_name:
            return {
                'suggestion': "ขออภัยค่ะ หนูไม่พบ workflow ที่เหมาะสมกับ task นี้",
                'workflow': None,
                'emotion': None,
                'reasoning_score': 0.0
            }
        
        # Get memory context
        memory_context = self.get_memory_context(workflow_name)
        
        # Generate response
        emotion = metadata.get('emotion', 'neutral')
        reasoning_score = metadata.get('reasoning_score', 0.0)
        
        response = f"หนูเห็นว่า {workflow_name} น่าจะเหมาะกับ task นี้ค่ะ"
        response += f" (emotion: {emotion}, reasoning: {reasoning_score:.2f})"
        response += " ต้องการให้หนูช่วย setup ไหมคะ?"
        
        if memory_context:
            response += f"\n\nจากที่หนูจำได้: {memory_context.get('context', '')}"
        
        return {
            'suggestion': response,
            'workflow': workflow_name,
            'emotion': emotion,
            'reasoning_score': reasoning_score,
            'memory_context': memory_context
        }
    
    def handle_workflow_trigger(self, workflow_name: str, trigger: str) -> str:
        """Handle workflow trigger with emotion-aware response."""
        print(f"🎯 Handling trigger '{trigger}' for workflow '{workflow_name}'")
        
        # Get workflow emotion
        emotion = self._get_workflow_emotion(workflow_name)
        
        # Generate emotion-triggered response
        response = self.generate_emotion_triggered_response(workflow_name, trigger, emotion)
        
        return response
    
    def run_interactive_mode(self):
        """Run dispatcher in interactive mode."""
        print("🚀 Starting Zynx Dispatcher Enhanced (Interactive Mode)")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n🎯 Enter task description (or 'quit' to exit): ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Get user emotion (optional)
                emotion_input = input("😊 Enter your emotion (optional): ").strip()
                user_emotion = emotion_input if emotion_input else None
                
                # Get suggestion
                result = self.suggest_workflow_with_context(user_input, user_emotion)
                
                print(f"\n💡 Suggestion:")
                print(f"   {result['suggestion']}")
                
                if result['workflow']:
                    # Ask if user wants to trigger the workflow
                    trigger_input = input(f"\n🎯 Trigger '{result['workflow']}'? (y/n): ").strip().lower()
                    
                    if trigger_input in ['y', 'yes']:
                        trigger = input("🔧 Enter trigger (pull_request/push/schedule/manual): ").strip()
                        if trigger:
                            trigger_response = self.handle_workflow_trigger(result['workflow'], trigger)
                            print(f"\n🎭 Response: {trigger_response}")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def run_batch_mode(self, task_file: str):
        """Run dispatcher in batch mode."""
        print(f"🚀 Starting Zynx Dispatcher Enhanced (Batch Mode)")
        print(f"📁 Processing tasks from: {task_file}")
        
        if not os.path.exists(task_file):
            print(f"❌ Task file not found: {task_file}")
            return
        
        with open(task_file, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        results = []
        for task in tasks:
            task_desc = task.get('description', '')
            user_emotion = task.get('emotion')
            
            result = self.suggest_workflow_with_context(task_desc, user_emotion)
            results.append({
                'task': task_desc,
                'emotion': user_emotion,
                'suggestion': result
            })
        
        # Save results
        output_file = f"dispatcher_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Results saved to: {output_file}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Zynx Dispatcher Enhanced')
    parser.add_argument('--mode', choices=['interactive', 'batch'], default='interactive',
                       help='Run mode: interactive or batch')
    parser.add_argument('--task-file', 
                       help='Task file for batch mode')
    parser.add_argument('--emotion-index', default='Zynx_Emotion_Consolidated_Index.md',
                       help='Emotion consolidated index file')
    parser.add_argument('--mcp-map', default='MCP_Prompt_Reasoning_Map.md',
                       help='MCP reasoning map file')
    parser.add_argument('--memory-file', default='memory_logs/injected_workflow_memories.json',
                       help='Memory data file')
    parser.add_argument('--template-file', default='mcp_prompt_injector_template.yaml',
                       help='Prompt template file')
    
    args = parser.parse_args()
    
    dispatcher = ZynxDispatcherEnhanced()
    
    # Load all data
    dispatcher.load_emotion_consolidated_index(args.emotion_index)
    dispatcher.load_mcp_reasoning_map(args.mcp_map)
    dispatcher.load_memory_data(args.memory_file)
    dispatcher.load_prompt_templates(args.template_file)
    
    # Run in appropriate mode
    if args.mode == 'interactive':
        dispatcher.run_interactive_mode()
    elif args.mode == 'batch':
        if not args.task_file:
            print("❌ Task file required for batch mode")
            return
        dispatcher.run_batch_mode(args.task_file)

if __name__ == '__main__':
    main()