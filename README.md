# GitSense

GitSense is a developer-focused GitHub repository analysis tool built with Python and Streamlit.

It helps developers understand a repository, explore its source code, and understand how files and functions are connected before making changes.

## ✨ Features

### 📊 Repository Analysis

GitSense provides an overview of a GitHub repository, including:

- Repository information
- Stars and forks
- Repository structure
- File statistics
- README content
- Recent commits
- Project health information

### 🔎 Repository Search

The application provides tools to explore repository code:

- File Explorer
- Code Search
- Search result navigation
- Source-code viewer
- Direct navigation to matching code lines

### 🧠 Code Intelligence

GitSense includes an AST-based Code Intelligence system that helps developers understand source files before editing them.

For a selected Python file, it can analyze:

- File purpose
- Functions
- Function callers
- Project dependencies
- Files that depend on the selected file
- External dependencies
- Standard-library imports
- Related test files
- Structural complexity
- Change impact
- Before You Edit recommendations

### 🗺️ Relationship Map

GitSense visualizes relationships between a selected file and other project files.

This helps answer questions such as:

> What does this file depend on?

and

> Which files depend on this file?

### 💡 Before You Edit

Instead of simply displaying code statistics, GitSense provides development-oriented guidance based on the detected relationships.

For example, when other files depend on a selected module, GitSense can recommend checking callers before changing its functions, parameters, or return values.

## 🛠️ Technologies

- Python
- Streamlit
- Git
- GitHub API
- Python AST
- Graphviz
- REST APIs

## 🏗️ Project Structure

```text
GitSense/
│
├── app/
│   ├── github_api.py
│   ├── repository_service.py
│   ├── streamlit_app.py
│   └── code_intelligence.py
│
├── tests/
│   └── test_main.py
│
├── requirements.txt
├── README.md
└── .gitignore