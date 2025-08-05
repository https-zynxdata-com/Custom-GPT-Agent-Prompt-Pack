# Zynx Automation Overlap Matrix

## Workflow Clusters Analysis

### PR Management

**Total Workflows**: 3

#### triggers:push|actions:npm run build,docker-compose up -d

- **Deploy to Production** (`/tmp/zynx_test_yjowht77/workflow_2.yml`)
  - Deploy application to production environment
  - Triggers: push
  - Actions: 2 steps

#### triggers:schedule|actions:python memory_profiler.py,python generate_report.py

- **Memory Analysis** (`/tmp/zynx_test_yjowht77/workflow_3.yml`)
  - Analyze memory usage and performance
  - Triggers: schedule
  - Actions: 2 steps

#### triggers:pull_request|actions:actions/checkout@v3,npm test,npm run lint

- **PR Review Workflow** (`/tmp/zynx_test_yjowht77/workflow_1.yml`)
  - Automated pull request review and testing
  - Triggers: pull_request
  - Actions: 3 steps

### General Automation

**Total Workflows**: 1

#### triggers:## Triggers|actions:## Actions

- **Documentation Workflow** (`/tmp/zynx_test_yjowht77/docs_workflow.md`)
  - Triggers: ## Triggers
  - Actions: 1 steps

### MVP Testing

**Total Workflows**: 1

#### triggers:workflow_dispatch|actions:npm run test:mvp,python validate_mvp.py

- **MVP Validation** (`/tmp/zynx_test_yjowht77/workflow_4.yml`)
  - Run MVP validation tests
  - Triggers: workflow_dispatch
  - Actions: 2 steps

