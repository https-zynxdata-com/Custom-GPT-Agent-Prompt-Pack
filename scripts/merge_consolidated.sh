#!/bin/bash

# Zynx Consolidation Merge Script
# ===============================
#
# Handles the consolidation of automation workflows and creates pull requests.

set -e

# Configuration
WORKSPACE_PATH="${WORKSPACE_PATH:-C:/Users/Zynxdata}"
OUTPUT_DIR="${OUTPUT_DIR:-./consolidated}"
BRANCH_NAME="zynx-consolidation-$(date +%Y%m%d-%H%M%S)"
PR_TITLE="Zynx Automation Consolidation"
PR_DESCRIPTION="Consolidated automation workflows for improved maintainability"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are available
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check for Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check for git
    if ! command -v git &> /dev/null; then
        log_error "Git is required but not installed"
        exit 1
    fi
    
    # Check for required Python packages
    python3 -c "import yaml, json, sklearn" 2>/dev/null || {
        log_error "Required Python packages not installed. Please install: yaml, json, sklearn"
        exit 1
    }
    
    log_success "All dependencies are available"
}

# Create output directory
setup_output_dir() {
    log_info "Setting up output directory: $OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR"
    mkdir -p "$OUTPUT_DIR/scripts"
    mkdir -p "$OUTPUT_DIR/workflows"
    mkdir -p "$OUTPUT_DIR/reports"
}

# Run the consolidation agent
run_consolidation_agent() {
    log_info "Running Zynx Consolidation Agent..."
    
    # Run the main agent
    python3 zynx_consolidation_agent.py --workspace "$WORKSPACE_PATH" || {
        log_error "Failed to run consolidation agent"
        exit 1
    }
    
    log_success "Consolidation agent completed"
}

# Extract task types
extract_task_types() {
    log_info "Extracting task types..."
    
    python3 scripts/extract_task_types.py --workspace "$WORKSPACE_PATH" --output "$OUTPUT_DIR/reports" || {
        log_warning "Task type extraction failed, continuing..."
    }
    
    log_success "Task type extraction completed"
}

# Cluster automation workflows
cluster_automation() {
    log_info "Clustering automation workflows..."
    
    # Check if we have workflow data
    if [ ! -f "workflows_data.json" ]; then
        log_warning "No workflow data found, skipping clustering"
        return
    fi
    
    python3 scripts/cluster_automation.py --input workflows_data.json --output "$OUTPUT_DIR/reports" || {
        log_warning "Clustering failed, continuing..."
    }
    
    log_success "Clustering completed"
}

# Generate master index
generate_master_index() {
    log_info "Generating master index..."
    
    # Check if we have workflow data
    if [ ! -f "workflows_data.json" ]; then
        log_warning "No workflow data found, skipping index generation"
        return
    fi
    
    python3 scripts/generate_master_index.py --input workflows_data.json --output "$OUTPUT_DIR/reports" || {
        log_warning "Index generation failed, continuing..."
    }
    
    log_success "Master index generated"
}

# Create consolidated workflows
create_consolidated_workflows() {
    log_info "Creating consolidated workflows..."
    
    # Look for consolidated workflow files
    for file in consolidated_*.yml; do
        if [ -f "$file" ]; then
            log_info "Moving $file to workflows directory"
            mv "$file" "$OUTPUT_DIR/workflows/"
        fi
    done
    
    # Move other output files
    for file in overlap_matrix.md Zynx_Automation_Index.md; do
        if [ -f "$file" ]; then
            log_info "Moving $file to reports directory"
            mv "$file" "$OUTPUT_DIR/reports/"
        fi
    done
    
    log_success "Consolidated workflows created"
}

# Initialize git repository if needed
init_git_repo() {
    log_info "Initializing git repository..."
    
    if [ ! -d ".git" ]; then
        git init
        log_info "Git repository initialized"
    fi
    
    # Add all files
    git add .
    
    # Check if there are changes to commit
    if git diff --cached --quiet; then
        log_warning "No changes to commit"
        return
    fi
    
    # Create branch
    git checkout -b "$BRANCH_NAME" 2>/dev/null || git checkout "$BRANCH_NAME"
    
    # Commit changes
    git commit -m "Zynx Automation Consolidation

- Consolidated automation workflows
- Generated overlap matrix and automation index
- Created consolidated workflow files
- Updated documentation

Generated on: $(date)" || {
        log_warning "No changes to commit"
    }
    
    log_success "Git repository updated"
}

# Create pull request (placeholder)
create_pull_request() {
    log_info "Creating pull request..."
    
    # This is a placeholder for PR creation
    # In a real implementation, you would use GitHub CLI or API
    log_warning "Pull request creation not implemented"
    log_info "To create a PR manually:"
    log_info "1. Push the branch: git push origin $BRANCH_NAME"
    log_info "2. Create PR with title: '$PR_TITLE'"
    log_info "3. Add description: '$PR_DESCRIPTION'"
}

# Generate summary report
generate_summary_report() {
    log_info "Generating summary report..."
    
    cat > "$OUTPUT_DIR/consolidation_summary.md" << EOF
# Zynx Consolidation Summary

Generated on: $(date)

## Overview

This consolidation process analyzed automation workflows in the Zynx workspace and created consolidated versions for improved maintainability.

## Files Generated

### Reports
- \`overlap_matrix.md\` - Analysis of workflow overlaps
- \`Zynx_Automation_Index.md\` - Comprehensive automation index
- \`task_analysis_report.md\` - Task type analysis
- \`cluster_report.md\` - Workflow clustering results

### Consolidated Workflows
EOF
    
    # List consolidated workflow files
    if [ -d "$OUTPUT_DIR/workflows" ]; then
        for file in "$OUTPUT_DIR/workflows"/*.yml; do
            if [ -f "$file" ]; then
                echo "- \`$(basename "$file")\`" >> "$OUTPUT_DIR/consolidation_summary.md"
            fi
        done
    fi
    
    cat >> "$OUTPUT_DIR/consolidation_summary.md" << EOF

## Next Steps

1. Review the generated reports
2. Test consolidated workflows
3. Create pull request for review
4. Merge after approval

## Branch Information

- **Branch**: $BRANCH_NAME
- **PR Title**: $PR_TITLE
- **PR Description**: $PR_DESCRIPTION
EOF
    
    log_success "Summary report generated: $OUTPUT_DIR/consolidation_summary.md"
}

# Main execution
main() {
    log_info "Starting Zynx Consolidation Process..."
    
    # Check dependencies
    check_dependencies
    
    # Setup output directory
    setup_output_dir
    
    # Run consolidation process
    run_consolidation_agent
    extract_task_types
    cluster_automation
    generate_master_index
    create_consolidated_workflows
    
    # Git operations
    init_git_repo
    
    # Generate summary
    generate_summary_report
    
    # Create PR (placeholder)
    create_pull_request
    
    log_success "Zynx consolidation process completed!"
    log_info "Output directory: $OUTPUT_DIR"
    log_info "Branch: $BRANCH_NAME"
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --workspace PATH    Workspace path to scan (default: C:/Users/Zynxdata)"
        echo "  --output DIR        Output directory (default: ./consolidated)"
        echo "  --help, -h          Show this help message"
        echo ""
        echo "Environment variables:"
        echo "  WORKSPACE_PATH      Workspace path to scan"
        echo "  OUTPUT_DIR          Output directory"
        exit 0
        ;;
    --workspace)
        WORKSPACE_PATH="$2"
        shift 2
        ;;
    --output)
        OUTPUT_DIR="$2"
        shift 2
        ;;
esac

# Run main function
main "$@"