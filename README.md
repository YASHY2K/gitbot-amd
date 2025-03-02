# GitBot - AI-Powered Git Repository Assistant 🤖

![AMD Ryzen AI](https://img.shields.io/badge/AMD-Ryzen%20AI-ED1C24?logo=amd&logoColor=white)
![Git Assistant](https://img.shields.io/badge/Type-Git%20Assistant-blue)
![CLI Tool](https://img.shields.io/badge/Interface-CLI-lightgrey)

A specialized AI agent for Git repository management, optimized for AMD Ryzen™ AI PCs with NPU acceleration.

## 🚀 Features

- **Natural Language Processing**: Ask Git questions in plain English
- **Smart Command Generation**: Get context-aware Git command suggestions
- **Safe Execution**: Interactive confirmation before running commands
- **NPU Accelerated**: Optimized for AMD Ryzen AI processors
- **Real-time Analysis**: Instant repository context awareness
- **Educational Explanations**: Understand the "why" behind commands

## 📋 Prerequisites

- AMD Ryzen™ AI PC with NPU and iGPU
- Windows 10 or newer
- Python 3.10
- Git 2.40.1+
- [Ryzen AI Software](https://github.com/amd/RyzenAI-SW)

## ⚙️ Installation

1. **Setup Ryzen AI Environment**  
   Follow the official [Qwen1.5-7B-Chat Setup Guide](https://github.com/amd/RyzenAI-SW/blob/main/example/llm/hybrid/Qwen1_5_7B_Chat.md)

2. **Clone Repository**
   ```bash
   git clone https://github.com/yourusername/gitbot-amd.git
   cd gitbot-amd
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🖥️ Usage

Start the GitBot:
```bash
python main.py
```

### Interaction Flow:
```
User: How to add all untracked files and enter custom commit message 'add new gamma branch'?

LLM: To add all untracked files and create a commit...
Cleaned commands: ['git add .', 'git commit -m "Add new gamma branch"']

Do you want to run: `git add .`? [Y/N] y
Running: git add .

Do you want to run: `git commit -m "Add new gamma branch"`? [Y/N] y
Running: git commit -m "Add new gamma branch"
```

### Commands:
- `quit`: Exit the program
- `exec`: Execute extracted commands from previous response

## � How It Works

### Architecture Overview
1. **Context Analysis**  
   - Scans repository using `GitRepoParser`
   - Builds detailed context snapshot

2. **AI Processing**  
   - Utilizes Qwen1.5-7B-Chat model
   - NPU-accelerated inference
   - Hybrid ONNX runtime

3. **Command Handling**  
   ```mermaid
   sequenceDiagram
       User->>+GitBot: Natural Language Query
       GitBot->>+NPU: Process Query
       NPU-->>-GitBot: Formatted Response
       GitBot->>User: Show Commands
       User->>GitBot: exec/confirm
       GitBot->>Git: Execute Verified Commands
   ```

4. **Safety Features**  
   - Regex-based command validation
   - Interactive confirmation flow
   - Command sanitization

## 📌 Limitations

- Currently CLI-only interface
- Requires specific AMD hardware
- Limited to Git operations
- English-only queries (v1.0)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📜 License

Apache 2.0 - See [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

- AMD Ryzen AI Software Team
- Hugging Face Transformers Library
- ONNX Runtime Team
