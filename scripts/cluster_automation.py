#!/usr/bin/env python3
"""
Cluster Automation Script
========================

Groups similar automation workflows using clustering algorithms.
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import pickle

@dataclass
class WorkflowCluster:
    """Represents a cluster of similar workflows."""
    cluster_id: str
    workflows: List[dict]
    centroid: Optional[np.ndarray] = None
    similarity_score: float = 0.0
    cluster_type: str = 'unknown'

class AutomationClusterer:
    """Clusters automation workflows by similarity."""
    
    def __init__(self):
        self.workflows = []
        self.clusters = []
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.feature_vectors = None
    
    def load_workflows(self, workflows_data: List[dict]):
        """Load workflows for clustering."""
        self.workflows = workflows_data
        print(f"📥 Loaded {len(self.workflows)} workflows for clustering")
    
    def extract_features(self) -> np.ndarray:
        """Extract features from workflows for clustering."""
        print("🔍 Extracting features from workflows...")
        
        # Combine workflow text features
        workflow_texts = []
        for workflow in self.workflows:
            text_parts = []
            
            # Add name and description
            if workflow.get('name'):
                text_parts.append(workflow['name'])
            if workflow.get('description'):
                text_parts.append(workflow['description'])
            
            # Add actions
            if workflow.get('actions'):
                text_parts.extend(workflow['actions'])
            
            # Add triggers
            if workflow.get('triggers'):
                text_parts.extend(workflow['triggers'])
            
            # Add tags
            if workflow.get('tags'):
                text_parts.extend(workflow['tags'])
            
            # Combine all text
            workflow_text = ' '.join(text_parts)
            workflow_texts.append(workflow_text)
        
        # Vectorize text features
        self.feature_vectors = self.vectorizer.fit_transform(workflow_texts)
        print(f"✅ Extracted {self.feature_vectors.shape[1]} features")
        
        return self.feature_vectors
    
    def cluster_by_similarity(self, method: str = 'kmeans', n_clusters: int = 5) -> List[WorkflowCluster]:
        """Cluster workflows by similarity."""
        print(f"🔗 Clustering workflows using {method}...")
        
        if self.feature_vectors is None:
            self.extract_features()
        
        if method == 'kmeans':
            clusters = self._kmeans_clustering(n_clusters)
        elif method == 'dbscan':
            clusters = self._dbscan_clustering()
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
        self.clusters = clusters
        print(f"✅ Created {len(clusters)} clusters")
        
        return clusters
    
    def _kmeans_clustering(self, n_clusters: int) -> List[WorkflowCluster]:
        """Perform K-means clustering."""
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(self.feature_vectors)
        
        # Group workflows by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            clusters[label].append(self.workflows[i])
        
        # Create WorkflowCluster objects
        workflow_clusters = []
        for cluster_id, workflows in clusters.items():
            # Calculate centroid
            cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
            centroid = kmeans.cluster_centers_[cluster_id]
            
            # Determine cluster type
            cluster_type = self._determine_cluster_type(workflows)
            
            # Calculate average similarity
            similarity_score = self._calculate_cluster_similarity(workflows)
            
            workflow_clusters.append(WorkflowCluster(
                cluster_id=f"cluster_{cluster_id}",
                workflows=workflows,
                centroid=centroid,
                similarity_score=similarity_score,
                cluster_type=cluster_type
            ))
        
        return workflow_clusters
    
    def _dbscan_clustering(self, eps: float = 0.3, min_samples: int = 2) -> List[WorkflowCluster]:
        """Perform DBSCAN clustering."""
        dbscan = DBSCAN(eps=eps, min_samples=min_samples)
        cluster_labels = dbscan.fit_predict(self.feature_vectors)
        
        # Group workflows by cluster
        clusters = defaultdict(list)
        for i, label in enumerate(cluster_labels):
            if label != -1:  # Skip noise points
                clusters[label].append(self.workflows[i])
        
        # Create WorkflowCluster objects
        workflow_clusters = []
        for cluster_id, workflows in clusters.items():
            # Calculate cluster type
            cluster_type = self._determine_cluster_type(workflows)
            
            # Calculate average similarity
            similarity_score = self._calculate_cluster_similarity(workflows)
            
            workflow_clusters.append(WorkflowCluster(
                cluster_id=f"cluster_{cluster_id}",
                workflows=workflows,
                similarity_score=similarity_score,
                cluster_type=cluster_type
            ))
        
        return workflow_clusters
    
    def _determine_cluster_type(self, workflows: List[dict]) -> str:
        """Determine the type of a cluster based on its workflows."""
        # Combine all text from workflows in the cluster
        all_text = ' '.join([
            f"{w.get('name', '')} {w.get('description', '')} {' '.join(w.get('actions', []))}"
            for w in workflows
        ]).lower()
        
        # Define type patterns
        type_patterns = {
            'PR Management': ['pull request', 'pr', 'review', 'merge', 'approval'],
            'Deployment': ['deploy', 'release', 'build', 'publish', 'docker'],
            'Testing': ['test', 'validate', 'check', 'verify', 'assert'],
            'Memory Debugger': ['debug', 'memory', 'log', 'monitor', 'profile'],
            'Security': ['security', 'scan', 'vulnerability', 'audit'],
            'Documentation': ['docs', 'documentation', 'readme'],
            'Dependency Management': ['npm', 'yarn', 'pip', 'install', 'update']
        }
        
        # Find the most common type
        type_scores = {}
        for cluster_type, keywords in type_patterns.items():
            score = sum(1 for keyword in keywords if keyword in all_text)
            type_scores[cluster_type] = score
        
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        
        return 'General Automation'
    
    def _calculate_cluster_similarity(self, workflows: List[dict]) -> float:
        """Calculate average similarity within a cluster."""
        if len(workflows) < 2:
            return 1.0
        
        # Get indices of workflows in this cluster
        cluster_indices = []
        for workflow in workflows:
            try:
                index = self.workflows.index(workflow)
                cluster_indices.append(index)
            except ValueError:
                continue
        
        if len(cluster_indices) < 2:
            return 1.0
        
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(cluster_indices)):
            for j in range(i + 1, len(cluster_indices)):
                sim = cosine_similarity(
                    self.feature_vectors[cluster_indices[i]:cluster_indices[i]+1],
                    self.feature_vectors[cluster_indices[j]:cluster_indices[j]+1]
                )[0][0]
                similarities.append(sim)
        
        return np.mean(similarities) if similarities else 0.0
    
    def find_similar_workflows(self, target_workflow: dict, top_k: int = 5) -> List[Tuple[dict, float]]:
        """Find workflows similar to a target workflow."""
        if self.feature_vectors is None:
            self.extract_features()
        
        # Find target workflow index
        try:
            target_index = self.workflows.index(target_workflow)
        except ValueError:
            print("⚠️  Target workflow not found in loaded workflows")
            return []
        
        # Calculate similarities with all other workflows
        similarities = []
        target_vector = self.feature_vectors[target_index]
        
        for i, workflow in enumerate(self.workflows):
            if i != target_index:
                sim = cosine_similarity(target_vector, self.feature_vectors[i])[0][0]
                similarities.append((workflow, sim))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def generate_cluster_report(self) -> str:
        """Generate a comprehensive cluster report."""
        if not self.clusters:
            return "No clusters available. Run clustering first."
        
        report = """# Automation Workflow Clusters Report

## Summary
"""
        
        report += f"- **Total Workflows**: {len(self.workflows)}\n"
        report += f"- **Total Clusters**: {len(self.clusters)}\n"
        report += f"- **Average Cluster Size**: {len(self.workflows) / len(self.clusters):.1f}\n\n"
        
        # Cluster details
        report += "## Cluster Details\n\n"
        
        for cluster in self.clusters:
            report += f"### {cluster.cluster_id} - {cluster.cluster_type}\n\n"
            report += f"- **Size**: {len(cluster.workflows)} workflows\n"
            report += f"- **Similarity Score**: {cluster.similarity_score:.3f}\n"
            report += f"- **Type**: {cluster.cluster_type}\n\n"
            
            # List workflows in cluster
            report += "**Workflows**:\n"
            for workflow in cluster.workflows:
                report += f"- {workflow.get('name', 'Unnamed')} (`{workflow.get('file_path', 'Unknown')}`)\n"
                if workflow.get('description'):
                    report += f"  - {workflow['description'][:100]}...\n"
            report += "\n"
        
        # Similarity matrix
        report += "## Inter-Cluster Similarity Matrix\n\n"
        report += self._generate_similarity_matrix()
        
        return report
    
    def _generate_similarity_matrix(self) -> str:
        """Generate similarity matrix between clusters."""
        if len(self.clusters) < 2:
            return "Not enough clusters for similarity matrix."
        
        matrix = "| Cluster |"
        for cluster in self.clusters:
            matrix += f" {cluster.cluster_id} |"
        matrix += "\n|---------|"
        for _ in self.clusters:
            matrix += "---------|"
        matrix += "\n"
        
        for i, cluster1 in enumerate(self.clusters):
            matrix += f"| {cluster1.cluster_id} |"
            for j, cluster2 in enumerate(self.clusters):
                if i == j:
                    matrix += " 1.000 |"
                else:
                    # Calculate similarity between clusters
                    similarity = self._calculate_cluster_similarity_between(cluster1, cluster2)
                    matrix += f" {similarity:.3f} |"
            matrix += "\n"
        
        return matrix
    
    def _calculate_cluster_similarity_between(self, cluster1: WorkflowCluster, cluster2: WorkflowCluster) -> float:
        """Calculate similarity between two clusters."""
        if not cluster1.workflows or not cluster2.workflows:
            return 0.0
        
        # Calculate average similarity between workflows from different clusters
        similarities = []
        for workflow1 in cluster1.workflows:
            for workflow2 in cluster2.workflows:
                try:
                    idx1 = self.workflows.index(workflow1)
                    idx2 = self.workflows.index(workflow2)
                    sim = cosine_similarity(
                        self.feature_vectors[idx1:idx1+1],
                        self.feature_vectors[idx2:idx2+1]
                    )[0][0]
                    similarities.append(sim)
                except (ValueError, IndexError):
                    continue
        
        return np.mean(similarities) if similarities else 0.0
    
    def save_clusters(self, output_dir: str = '.'):
        """Save clustering results."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save clusters as JSON
        clusters_data = []
        for cluster in self.clusters:
            cluster_data = {
                'cluster_id': cluster.cluster_id,
                'cluster_type': cluster.cluster_type,
                'similarity_score': cluster.similarity_score,
                'workflows': cluster.workflows
            }
            clusters_data.append(cluster_data)
        
        with open(output_path / 'workflow_clusters.json', 'w', encoding='utf-8') as f:
            json.dump(clusters_data, f, indent=2, default=str)
        
        # Save cluster report
        report = self.generate_cluster_report()
        with open(output_path / 'cluster_report.md', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # Save vectorizer for later use
        with open(output_path / 'vectorizer.pkl', 'wb') as f:
            pickle.dump(self.vectorizer, f)
        
        print(f"✅ Clustering results saved to {output_path}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Cluster automation workflows by similarity')
    parser.add_argument('--input', required=True,
                       help='Input JSON file with workflows data')
    parser.add_argument('--output', default='.',
                       help='Output directory for clustering results')
    parser.add_argument('--method', default='kmeans',
                       choices=['kmeans', 'dbscan'],
                       help='Clustering method to use')
    parser.add_argument('--clusters', type=int, default=5,
                       help='Number of clusters for K-means')
    
    args = parser.parse_args()
    
    # Load workflows
    with open(args.input, 'r', encoding='utf-8') as f:
        workflows_data = json.load(f)
    
    # Create clusterer and run clustering
    clusterer = AutomationClusterer()
    clusterer.load_workflows(workflows_data)
    
    if args.method == 'kmeans':
        clusters = clusterer.cluster_by_similarity('kmeans', args.clusters)
    else:
        clusters = clusterer.cluster_by_similarity('dbscan')
    
    # Save results
    clusterer.save_clusters(args.output)
    
    # Print summary
    print(f"\n📊 Clustering Summary:")
    print(f"  Method: {args.method}")
    print(f"  Clusters created: {len(clusters)}")
    print(f"  Average cluster size: {len(workflows_data) / len(clusters):.1f}")
    
    print(f"\n🔝 Cluster types:")
    for cluster in clusters:
        print(f"  {cluster.cluster_id}: {cluster.cluster_type} ({len(cluster.workflows)} workflows)")

if __name__ == '__main__':
    main()