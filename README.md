# GitSense

GitSense is a developer-focused GitHub repository analysis and Code Intelligence tool built with Python and Streamlit.

It helps developers understand any repository, explore its source code across multiple programming languages, and understand how files and functions are connected before making changes.

## ✨ Features

### 📊 Repository Analysis

GitSense provides an overview of any GitHub repository, including:

- Repository information & health
- Stars, forks, watchers, and open issues
- Fast single-request Git Trees directory structure exploration (up to 100,000 files)
- Comprehensive multi-language file statistics
- Formatted README viewer
- Branch and recent commit history

### 🔎 Repository Search & Code Viewer

The application provides tools to explore repository code:

- File Explorer with language icons
- Full-text Code Search with query highlighting
- Direct line jumping and smooth scrolling
- Syntax-highlighted source code viewer

### 🧠 Multi-Language Code Intelligence

GitSense includes a universal Code Intelligence engine that supports **Python, JavaScript, TypeScript, Go, Rust, Java, Kotlin, C, C++, C#, Ruby, PHP, Swift, Shell, SQL, HTML/CSS, and more**.

For any selected source file, it analyzes:

- **File Purpose**: Auto-extracted functional description from docstrings, JSDoc, and architecture conventions
- **Language Identification**: Automatic language detection with language filtering
- **Functions & Declarations**: Extracted functions, methods, async functions, classes, and line numbers
- **Function Intelligence**: Call traces and project-wide caller detection
- **Project Dependencies**: Internal files and modules imported by the file
- **Dependents & Reverse Dependencies**: Project files that depend on this file
- **External Dependencies**: 3rd-party packages (npm, PyPI, crates.io, Go modules, Maven, etc.)
- **Standard-Library Imports**: Standard libraries built into the language
- **Related Test Files**: Automated test suites linked by dependencies or naming conventions
- **Structural Complexity**: Control-flow rating (Low, Moderate, High) and branching count
- **Change Impact**: Impact level calculation (Low, Moderate, High) based on dependents
- **Before You Edit**: Actionable development guidance tailored to the file's callers and dependencies

### 🗺️ Relationship Map

GitSense renders an interactive Graphviz relationship diagram visualizing:
- All files the selected file depends on
- All project files that import or depend on the selected file

### 💡 Before You Edit

Instead of simply displaying code statistics, GitSense provides development-oriented guidance based on detected relationships. For example, when other files depend on a selected module, GitSense recommends checking callers before changing exported functions, parameters, or return values.

## 🛠️ Technologies

- Python 3
- Streamlit
- GitHub REST API & Git Trees API
- Python AST & Multi-Language Static Analysis
- Graphviz
- Pytest

## 🏗️ Project Structure

```text
GitSense/
│
├── app/
│   ├── github_api.py          # GitHub API integration & Git Trees API
│   ├── repository_service.py  # Repository metrics & file processing
│   ├── streamlit_app.py       # Streamlit UI & Code Viewer
│   └── code_intelligence.py   # Multi-language Code Intelligence engine
│
├── tests/
│   ├── test_main.py
│   └── test_code_intelligence.py
│
├── requirements.txt
├── README.md
└── .gitignore
```