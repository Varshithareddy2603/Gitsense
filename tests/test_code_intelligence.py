import pytest
from app.code_intelligence import (
    get_language,
    parse_code_file,
    build_module_map,
    analyze_file,
    find_function_callers,
    find_dependents,
    find_related_tests,
    get_file_purpose,
    get_complexity_label
)


def test_get_language():
    assert get_language("src/index.js") == "javascript"
    assert get_language("components/Header.tsx") == "typescript"
    assert get_language("main.go") == "go"
    assert get_language("src/lib.rs") == "rust"
    assert get_language("App.java") == "java"
    assert get_language("server.cpp") == "cpp"
    assert get_language("app/main.py") == "python"
    assert get_language("Dockerfile") == "docker"


def test_python_analysis():
    source = '''"""Module for user operations."""
import os
import requests
from app.db import get_db

def create_user(name, email):
    if not name:
        return None
    db = get_db()
    return db.insert({"name": name, "email": email})
'''
    sources = {"app/user.py": source}
    functions, imports, score, docstring, _ = parse_code_file(
        "app/user.py", repository_sources=sources
    )

    assert docstring == "Module for user operations."
    assert len(functions) == 1
    assert functions[0]["name"] == "create_user"
    assert "os" in imports
    assert "requests" in imports
    assert score >= 1


def test_javascript_typescript_analysis():
    js_source = '''import React from 'react';
import axios from 'axios';
import { formatDate } from './utils';

export function UserCard({ user }) {
    if (!user) {
        return null;
    }
    const formatted = formatDate(user.createdAt);
    return <div>{user.name} - {formatted}</div>;
}

export const fetchUser = async (id) => {
    return await axios.get(`/api/users/${id}`);
};
'''
    sources = {"src/UserCard.jsx": js_source}
    functions, imports, score, _, _ = parse_code_file(
        "src/UserCard.jsx", repository_sources=sources
    )

    fn_names = [f["name"] for f in functions]
    assert "UserCard" in fn_names
    assert "fetchUser" in fn_names
    assert "react" in imports
    assert "axios" in imports
    assert "./utils" in imports
    assert score >= 1


def test_go_analysis():
    go_source = '''package main

import (
    "fmt"
    "net/http"
    "github.com/gin-gonic/gin"
)

func HandleRequest(c *gin.Context) {
    if c == nil {
        return
    }
    fmt.Println("Processing request")
}
'''
    sources = {"main.go": go_source}
    functions, imports, score, _, _ = parse_code_file(
        "main.go", repository_sources=sources
    )

    fn_names = [f["name"] for f in functions]
    assert "HandleRequest" in fn_names
    assert "fmt" in imports
    assert "github.com/gin-gonic/gin" in imports
    assert score >= 1


def test_multi_language_dependency_graph():
    sources = {
        "src/utils.ts": "export function helper() { return 42; }",
        "src/api.ts": "import { helper } from './utils'; export function callApi() { return helper(); }",
        "src/App.tsx": "import { callApi } from './api'; export function App() { callApi(); }",
        "src/api.test.ts": "import { callApi } from './api'; test('api', () => { callApi(); });"
    }

    project_files = list(sources.keys())
    module_map = build_module_map(project_files)

    analysis_api = analyze_file("src/api.ts", project_files, module_map, repository_sources=sources)

    assert "src/utils.ts" in analysis_api["project_dependencies"]
    assert "src/App.tsx" in analysis_api["dependents"]
    assert "src/api.test.ts" in analysis_api["related_tests"]
    assert analysis_api["impact"] in ("Moderate", "High")


def test_file_purpose_multi_language():
    assert "UI component" in get_file_purpose("src/components/Button.tsx")
    assert "API routes" in get_file_purpose("routes/userController.js")
    assert "container image" in get_file_purpose("Dockerfile")
    assert "dependencies" in get_file_purpose("package.json")


def test_complexity_rating():
    assert get_complexity_label(2) == "Low"
    assert get_complexity_label(8) == "Moderate"
    assert get_complexity_label(25) == "High"
