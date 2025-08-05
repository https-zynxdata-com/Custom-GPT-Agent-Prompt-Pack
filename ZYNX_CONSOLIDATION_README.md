# Zynx Consolidation Agent

📦 **Zynx Consolidation Agent** - สแกนและรวม automation workflows ใน workspace เพื่อปรับปรุงการบำรุงรักษา

## 🎯 วัตถุประสงค์

Agent นี้จะ:
- สแกน workspace ที่ `"C:/Users/Zynxdata"` เพื่อหา YAML/Markdown/Workflow files
- ข้าม dependency folders เช่น `node_modules`, `.venv`, `.git`, `build`, `dist`
- จัดกลุ่ม workflows ที่คล้ายกัน (PR, Deploy, Memory Debugger, MVP)
- เปรียบเทียบ logic และสรุปเป็น `overlap_matrix.md` และ `Zynx_Automation_Index.md`
- เมื่อพิมพ์ `apply` → รวมไฟล์ workflows และเปิด PR

## 🛠️ การติดตั้ง

### 1. Clone Repository
```bash
git clone <repository-url>
cd zynx-consolidation-agent
```

### 2. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 3. ตรวจสอบ Dependencies
```bash
python3 -c "import yaml, sklearn, numpy; print('✅ All dependencies installed')"
```

## 🚀 การใช้งาน

### การใช้งานพื้นฐาน

```bash
# รัน agent พื้นฐาน
python3 zynx_consolidation_agent.py

# ระบุ workspace path
python3 zynx_consolidation_agent.py --workspace /path/to/workspace

# รันพร้อม apply (สร้าง PR)
python3 zynx_consolidation_agent.py --apply
```

### การใช้งาน Scripts แยก

```bash
# 1. Extract task types
python3 scripts/extract_task_types.py --workspace C:/Users/Zynxdata

# 2. Cluster automation workflows
python3 scripts/cluster_automation.py --input workflows_data.json --method kmeans

# 3. Generate master index
python3 scripts/generate_master_index.py --input workflows_data.json

# 4. Run complete consolidation
bash scripts/merge_consolidated.sh
```

## 📁 โครงสร้างไฟล์

```
zynx-consolidation-agent/
├── zynx_consolidation_agent.py    # Main agent
├── scripts/
│   ├── extract_task_types.py      # Extract task types
│   ├── cluster_automation.py      # Cluster workflows
│   ├── generate_master_index.py   # Generate master index
│   └── merge_consolidated.sh      # Merge and create PR
├── requirements.txt               # Python dependencies
└── README.md                     # This file
```

## 🔧 Features

### 1. Workspace Scanning
- สแกนไฟล์ `.yml`, `.yaml`, `.md`, `.workflow`
- ข้าม excluded directories
- แยกแยะ workflow types (GitHub Actions, Azure DevOps, etc.)

### 2. Workflow Analysis
- Extract triggers, actions, dependencies
- Detect workflow patterns
- Categorize by functionality

### 3. Clustering
- Group similar workflows
- Calculate similarity scores
- Identify consolidation opportunities

### 4. Consolidation
- Merge similar workflows
- Create master workflows
- Generate comprehensive reports

## 📊 Output Files

### Reports
- `overlap_matrix.md` - Analysis of workflow overlaps
- `Zynx_Automation_Index.md` - Comprehensive automation index
- `task_analysis_report.md` - Task type analysis
- `cluster_report.md` - Workflow clustering results

### Consolidated Workflows
- `consolidated_pr_management.yml`
- `consolidated_deployment.yml`
- `consolidated_memory_debugger.yml`
- `consolidated_mvp_testing.yml`

## 🎯 Workflow Categories

### 1. PR Management
- Pull request reviews
- Code approval workflows
- Merge automation

### 2. Deployment
- Build and deploy processes
- Release automation
- Infrastructure deployment

### 3. Memory Debugger
- Performance monitoring
- Memory analysis
- Debugging workflows

### 4. MVP Testing
- Test automation
- Validation workflows
- Quality assurance

## 🔍 การวิเคราะห์

### Task Type Detection
```python
# ตัวอย่างการตรวจจับ task types
task_patterns = {
    'PR Management': ['pull request', 'pr', 'review', 'merge'],
    'Deployment': ['deploy', 'release', 'build', 'publish'],
    'Testing': ['test', 'validate', 'check', 'verify'],
    'Memory Debugger': ['debug', 'memory', 'log', 'monitor']
}
```

### Clustering Methods
- **K-means**: สำหรับ workflows ที่มีจำนวนแน่นอน
- **DBSCAN**: สำหรับ workflows ที่มีขนาดไม่แน่นอน

### Similarity Calculation
- TF-IDF vectorization
- Cosine similarity
- Content-based matching

## 📈 การใช้งานขั้นสูง

### Custom Workspace Path
```bash
export WORKSPACE_PATH="/custom/path/to/workspace"
python3 zynx_consolidation_agent.py
```

### Custom Output Directory
```bash
export OUTPUT_DIR="./custom_output"
bash scripts/merge_consolidated.sh
```

### Batch Processing
```bash
# Process multiple workspaces
for workspace in workspace1 workspace2 workspace3; do
    python3 zynx_consolidation_agent.py --workspace "$workspace"
done
```

## 🔧 Configuration

### Environment Variables
```bash
WORKSPACE_PATH=C:/Users/Zynxdata
OUTPUT_DIR=./consolidated
BRANCH_NAME=zynx-consolidation-$(date +%Y%m%d-%H%M%S)
```

### Excluded Directories
```python
excluded_dirs = {
    'node_modules', '.venv', '.git', 'build', 'dist',
    '__pycache__', '.pytest_cache', '.vscode', '.idea'
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Python dependencies not found**
   ```bash
   pip install -r requirements.txt
   ```

2. **Workspace path not found**
   ```bash
   # Check if path exists
   ls -la "C:/Users/Zynxdata"
   ```

3. **Git not initialized**
   ```bash
   git init
   git config user.name "Your Name"
   git config user.email "your.email@example.com"
   ```

### Debug Mode
```bash
# Enable debug output
python3 zynx_consolidation_agent.py --debug
```

## 📝 Examples

### Example Workflow Analysis
```yaml
# Input workflow
name: "PR Review Workflow"
on:
  pull_request:
    branches: [main]
jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Run tests
        run: npm test
```

### Generated Consolidated Workflow
```yaml
# Output consolidated workflow
name: "Zynx PR Management Master Workflow"
description: "Consolidated workflow for PR Management operations"
on:
  pull_request:
    branches: [main, develop]
jobs:
  pr_review_0:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Run tests
        run: npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

หากมีปัญหาหรือคำถาม:
- สร้าง Issue ใน GitHub
- ติดต่อทีมพัฒนา
- ดู Documentation เพิ่มเติม

---

**Zynx Consolidation Agent** - ทำให้ automation workflows ง่ายขึ้นและมีประสิทธิภาพมากขึ้น! 🚀