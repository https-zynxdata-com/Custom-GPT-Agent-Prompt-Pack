#!/usr/bin/env python3
"""
Test Script for Zynx Consolidation Agent
========================================

Demonstrates the agent functionality with sample data.
"""

import os
import yaml
import json
import tempfile
from pathlib import Path

def create_sample_workflows():
    """Create sample workflow files for testing."""
    
    # Sample workflow 1: PR Review
    pr_workflow = {
        'name': 'PR Review Workflow',
        'description': 'Automated pull request review and testing',
        'on': {
            'pull_request': {
                'branches': ['main', 'develop']
            }
        },
        'jobs': {
            'review': {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'name': 'Checkout code',
                        'uses': 'actions/checkout@v3'
                    },
                    {
                        'name': 'Run tests',
                        'run': 'npm test'
                    },
                    {
                        'name': 'Code quality check',
                        'run': 'npm run lint'
                    }
                ]
            }
        }
    }
    
    # Sample workflow 2: Deployment
    deploy_workflow = {
        'name': 'Deploy to Production',
        'description': 'Deploy application to production environment',
        'on': {
            'push': {
                'branches': ['main']
            }
        },
        'jobs': {
            'deploy': {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'name': 'Build application',
                        'run': 'npm run build'
                    },
                    {
                        'name': 'Deploy to server',
                        'run': 'docker-compose up -d'
                    }
                ]
            }
        }
    }
    
    # Sample workflow 3: Memory Debug
    debug_workflow = {
        'name': 'Memory Analysis',
        'description': 'Analyze memory usage and performance',
        'on': {
            'schedule': [
                {'cron': '0 2 * * *'}  # Daily at 2 AM
            ]
        },
        'jobs': {
            'analyze': {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'name': 'Run memory profiler',
                        'run': 'python memory_profiler.py'
                    },
                    {
                        'name': 'Generate report',
                        'run': 'python generate_report.py'
                    }
                ]
            }
        }
    }
    
    # Sample workflow 4: MVP Testing
    test_workflow = {
        'name': 'MVP Validation',
        'description': 'Run MVP validation tests',
        'on': {
            'workflow_dispatch': {}
        },
        'jobs': {
            'validate': {
                'runs-on': 'ubuntu-latest',
                'steps': [
                    {
                        'name': 'Run MVP tests',
                        'run': 'npm run test:mvp'
                    },
                    {
                        'name': 'Validate requirements',
                        'run': 'python validate_mvp.py'
                    }
                ]
            }
        }
    }
    
    return [pr_workflow, deploy_workflow, debug_workflow, test_workflow]

def create_test_workspace():
    """Create a test workspace with sample workflows."""
    
    # Create temporary workspace
    workspace = Path(tempfile.mkdtemp(prefix='zynx_test_'))
    
    # Create workflow files
    workflows = create_sample_workflows()
    
    for i, workflow in enumerate(workflows):
        file_path = workspace / f'workflow_{i+1}.yml'
        with open(file_path, 'w') as f:
            yaml.dump(workflow, f, default_flow_style=False)
    
    # Create a markdown workflow
    md_workflow = """# Documentation Workflow

## Description
Automated documentation generation and deployment.

## Triggers
- On documentation updates
- Weekly scheduled runs

## Actions
- Generate API docs
- Update README
- Deploy to docs site

## Dependencies
- Node.js
- Documentation tools
"""
    
    with open(workspace / 'docs_workflow.md', 'w') as f:
        f.write(md_workflow)
    
    print(f"✅ Created test workspace: {workspace}")
    return workspace

def test_agent_functionality():
    """Test the main agent functionality."""
    
    print("🧪 Testing Zynx Consolidation Agent...")
    
    # Create test workspace
    workspace = create_test_workspace()
    
    try:
        # Import and test the agent
        from zynx_consolidation_agent import ZynxConsolidationAgent
        
        # Create agent instance
        agent = ZynxConsolidationAgent(str(workspace))
        
        # Test scanning
        print("\n1. Testing workspace scanning...")
        workflow_files = agent.scan_workspace()
        print(f"   Found {len(workflow_files)} workflow files")
        
        # Test parsing
        print("\n2. Testing workflow parsing...")
        workflows = agent.parse_workflows()
        print(f"   Parsed {len(workflows)} workflows")
        
        # Test clustering
        print("\n3. Testing workflow clustering...")
        clusters = agent.cluster_workflows()
        print(f"   Created {len(clusters)} clusters")
        
        # Test output generation
        print("\n4. Testing output generation...")
        overlap_matrix = agent.generate_overlap_matrix()
        automation_index = agent.generate_automation_index()
        consolidated_workflows = agent.consolidate_workflows()
        
        print(f"   Generated overlap matrix: {len(overlap_matrix)} characters")
        print(f"   Generated automation index: {len(automation_index)} characters")
        print(f"   Created {len(consolidated_workflows)} consolidated workflows")
        
        # Save outputs
        print("\n5. Testing output saving...")
        agent.save_outputs(overlap_matrix, automation_index, consolidated_workflows)
        print("   ✅ Outputs saved successfully")
        
        # Display results
        print("\n📊 Test Results:")
        print(f"   Workspace: {workspace}")
        print(f"   Workflow files: {len(workflow_files)}")
        print(f"   Parsed workflows: {len(workflows)}")
        print(f"   Clusters: {len(clusters)}")
        
        for cluster_name, cluster_workflows in clusters.items():
            print(f"     - {cluster_name}: {len(cluster_workflows)} workflows")
        
        print("\n✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        raise
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(workspace)
        print(f"🧹 Cleaned up test workspace")

def test_scripts():
    """Test individual scripts."""
    
    print("\n🧪 Testing individual scripts...")
    
    # Create test workspace
    workspace = create_test_workspace()
    
    try:
        # Test extract_task_types.py
        print("\n1. Testing task type extraction...")
        from scripts.extract_task_types import TaskTypeExtractor
        
        extractor = TaskTypeExtractor()
        analysis_result = extractor.analyze_workspace(str(workspace))
        
        print(f"   Found {analysis_result['statistics']['total_tasks']} tasks")
        print(f"   Task types: {list(analysis_result['tasks'].keys())}")
        
        # Test cluster_automation.py
        print("\n2. Testing clustering...")
        from scripts.cluster_automation import AutomationClusterer
        
        # Convert workflows to JSON format
        workflows_data = []
        for workflow_file in workspace.glob('*.yml'):
            with open(workflow_file, 'r') as f:
                workflow_data = yaml.safe_load(f)
                workflows_data.append({
                    'name': workflow_data.get('name', 'Unnamed'),
                    'description': workflow_data.get('description', ''),
                    'file_path': str(workflow_file),
                    'workflow_type': 'GitHub Actions',
                    'triggers': list(workflow_data.get('on', {}).keys()),
                    'actions': [],
                    'dependencies': [],
                    'tags': []
                })
        
        clusterer = AutomationClusterer()
        clusterer.load_workflows(workflows_data)
        clusters = clusterer.cluster_by_similarity('kmeans', 3)
        
        print(f"   Created {len(clusters)} clusters")
        for cluster in clusters:
            print(f"     - {cluster.cluster_id}: {cluster.cluster_type}")
        
        # Test generate_master_index.py
        print("\n3. Testing master index generation...")
        from scripts.generate_master_index import MasterIndexGenerator
        
        generator = MasterIndexGenerator()
        generator.load_workflows(workflows_data)
        generator.save_index('.')
        
        print("   ✅ Master index generated")
        
        print("\n✅ All script tests passed!")
        
    except Exception as e:
        print(f"❌ Script test failed: {e}")
        raise
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(workspace)
        print(f"🧹 Cleaned up test workspace")

def main():
    """Main test function."""
    
    print("🚀 Starting Zynx Consolidation Agent Tests")
    print("=" * 50)
    
    # Test main agent
    test_agent_functionality()
    
    # Test individual scripts
    test_scripts()
    
    print("\n🎉 All tests completed successfully!")
    print("\n📝 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Run the agent: python3 zynx_consolidation_agent.py")
    print("3. Apply consolidation: python3 zynx_consolidation_agent.py --apply")

if __name__ == '__main__':
    main()