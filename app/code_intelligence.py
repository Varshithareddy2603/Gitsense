import ast
import os
import re
import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT SETUP
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# SETTINGS & CONSTANTS
# ============================================================

IGNORED_DIRS = {
    ".git",
    ".github",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
    "out",
    ".next",
    ".nuxt",
    "target",
    "vendor",
    "bin",
    "obj",
    ".idea",
    ".vscode",
}

# Supported file extensions mapped to language identifiers
LANGUAGE_MAP = {
    # Python
    ".py": "python",
    ".pyw": "python",
    ".pyi": "python",
    # JavaScript & TypeScript
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".mts": "typescript",
    ".cts": "typescript",
    # Go
    ".go": "go",
    # Rust
    ".rs": "rust",
    # Java & Kotlin
    ".java": "java",
    ".kt": "kotlin",
    ".kts": "kotlin",
    # C / C++ / C#
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".cxx": "cpp",
    ".h": "c_header",
    ".hpp": "cpp_header",
    ".cs": "csharp",
    # Other Languages
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".scala": "scala",
    ".sh": "shell",
    ".bash": "shell",
    ".zsh": "shell",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".json": "json",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".toml": "toml",
    ".md": "markdown",
    ".txt": "text",
}

LANGUAGE_DISPLAY = {
    "python": "🐍 Python",
    "javascript": "🟨 JavaScript",
    "typescript": "🔷 TypeScript",
    "go": "🐹 Go",
    "rust": "🦀 Rust",
    "java": "☕ Java",
    "kotlin": "🟣 Kotlin",
    "c": "⚡ C",
    "cpp": "⚡ C++",
    "c_header": "📄 C Header",
    "cpp_header": "📄 C++ Header",
    "csharp": "🔷 C#",
    "ruby": "💎 Ruby",
    "php": "🐘 PHP",
    "swift": "🔶 Swift",
    "scala": "🔴 Scala",
    "shell": "🐚 Shell",
    "sql": "🗄️ SQL",
    "html": "🌐 HTML",
    "css": "🎨 CSS",
    "scss": "🎨 SCSS",
    "json": "📋 JSON",
    "yaml": "⚙️ YAML",
    "toml": "⚙️ TOML",
    "markdown": "📝 Markdown",
    "text": "📄 Text",
    "generic": "📄 Code File",
}

# Standard library modules for common languages
STDLIB_MODULES = {
    "python": {
        "os", "sys", "json", "ast", "pathlib", "typing", "re", "math",
        "time", "datetime", "base64", "html", "collections", "subprocess",
        "logging", "unittest", "functools", "itertools", "io", "shutil",
        "hashlib", "urllib", "http", "socket", "threading", "multiprocessing",
        "asyncio", "dataclasses", "enum", "copy", "tempfile", "glob",
        "pickle", "sqlite3", "csv", "random", "struct", "traceback",
    },
    "javascript": {
        "fs", "path", "http", "https", "url", "crypto", "events",
        "child_process", "os", "util", "stream", "buffer", "assert",
        "querystring", "zlib", "net", "tls", "dns", "readline", "perf_hooks",
        "worker_threads", "v8", "vm", "timers", "process",
    },
    "typescript": {
        "fs", "path", "http", "https", "url", "crypto", "events",
        "child_process", "os", "util", "stream", "buffer", "assert",
        "querystring", "zlib", "net", "tls", "dns", "readline",
    },
    "go": {
        "fmt", "os", "io", "time", "sync", "strings", "bytes", "errors",
        "net", "net/http", "context", "math", "sort", "path", "path/filepath",
        "encoding/json", "encoding/xml", "log", "regexp", "testing", "flag",
        "bufio", "database/sql", "crypto", "strconv", "reflect",
    },
    "java": {
        "java.lang", "java.util", "java.io", "java.nio", "java.net",
        "java.math", "java.time", "java.sql", "java.security", "java.text",
        "javax.swing", "java.awt",
    },
    "c": {
        "stdio.h", "stdlib.h", "string.h", "math.h", "time.h", "ctype.h",
        "stdbool.h", "stdint.h", "stddef.h", "errno.h", "assert.h", "limits.h",
        "unistd.h", "pthread.h", "sys/types.h", "sys/stat.h", "fcntl.h",
    },
    "cpp": {
        "iostream", "vector", "string", "map", "set", "unordered_map",
        "unordered_set", "algorithm", "memory", "utility", "chrono",
        "thread", "mutex", "future", "functional", "cmath", "cstdio",
        "cstdlib", "cstring", "fstream", "sstream", "queue", "stack", "deque",
    },
    "rust": {
        "std", "core", "alloc", "std::io", "std::fs", "std::path",
        "std::collections", "std::sync", "std::time", "std::thread",
        "std::env", "std::fmt", "std::str", "std::vec", "std::result",
    },
}


# ============================================================
# PATH HELPERS
# ============================================================

def normalize_path(path):
    return str(path).replace("\\", "/")


def is_ignored_path(path):
    normalized = normalize_path(path)
    parts = normalized.split("/")
    return any(part in IGNORED_DIRS for part in parts)


def get_language(path):
    """
    Detect programming language from file path extension.
    """
    normalized = normalize_path(path)
    stem_lower = Path(normalized).name.lower()

    if stem_lower in ("dockerfile", "containerfile"):
        return "docker"
    if stem_lower in ("makefile", "gnumakefile"):
        return "makefile"

    ext = Path(normalized).suffix.lower()
    return LANGUAGE_MAP.get(ext, "generic")


def is_source_code_file(path):
    """
    Determine whether a file is a source code or markup file that can be analyzed.
    """
    lang = get_language(path)
    return lang not in ("text", "generic") or path.lower().endswith(
        (".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java",
         ".c", ".cpp", ".h", ".hpp", ".cs", ".rb", ".php", ".swift",
         ".kt", ".sh", ".sql", ".html", ".css", ".json", ".yaml", ".yml", ".md")
    )


# ============================================================
# REPOSITORY FILE LIST
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def get_repository_file_list(username, repository):
    """
    Get all repository files in a single fast call.
    """
    from app.repository_service import get_all_repository_files

    repository_files = get_all_repository_files(username, repository)
    files = []

    for file_item in repository_files:
        if isinstance(file_item, dict):
            file_path = file_item.get("path") or file_item.get("name") or ""
        else:
            file_path = str(file_item)

        if not file_path:
            continue

        normalized = normalize_path(file_path)

        if is_ignored_path(normalized):
            continue

        files.append(normalized)

    return sorted(set(files))


# ============================================================
# SOURCE CODE CACHE
# ============================================================

@st.cache_data(ttl=600, show_spinner=False)
def get_remote_source(username, repository, file_path):
    """
    Download one source file only when needed.
    """
    from app.repository_service import get_source_code

    try:
        source = get_source_code(username, repository, file_path)
        return source or ""
    except Exception:
        return ""


def read_local_file(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def get_source(path, username=None, repository=None, repository_sources=None):
    normalized = normalize_path(path)

    if repository_sources is not None:
        if normalized in repository_sources:
            return repository_sources[normalized]

    if username and repository:
        return get_remote_source(username, repository, normalized)

    return read_local_file(normalized)


def read_file(path, username=None, repository=None, repository_sources=None):
    return get_source(path, username, repository, repository_sources)


# ============================================================
# FILE DISCOVERY
# ============================================================

def get_project_files(username=None, repository=None, repository_sources=None, language_filter=None):
    """
    Retrieve project files for analysis, optionally filtered by language.
    """
    if repository_sources is not None:
        all_files = sorted(repository_sources.keys())
    elif username and repository:
        all_files = get_repository_file_list(username, repository)
    else:
        # Local fallback
        files = []
        for root, dirs, filenames in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
            for filename in filenames:
                normalized = normalize_path(Path(root) / filename)
                if not is_ignored_path(normalized):
                    files.append(normalized)
        all_files = sorted(files)

    # Filter out ignored paths
    valid_files = [f for f in all_files if not is_ignored_path(f)]

    # Filter for source code files
    code_files = [f for f in valid_files if is_source_code_file(f)]

    if language_filter and language_filter != "all":
        code_files = [f for f in code_files if get_language(f) == language_filter]

    return code_files if code_files else valid_files


def display_path(path, repository_sources=None):
    if isinstance(path, Path):
        try:
            relative = path.relative_to(PROJECT_ROOT)
            return relative.as_posix()
        except ValueError:
            return path.as_posix()
    return normalize_path(path)


# ============================================================
# UNIVERSAL MODULE MAP
# ============================================================

def path_to_module(path):
    """
    Convert file path to module name representation for Python, JS/TS, Go, Java, etc.
    """
    normalized = normalize_path(path)
    p = Path(normalized)

    # Strip standard extensions
    clean_stem = p.stem
    if clean_stem in ("__init__", "index", "mod", "main"):
        parent_module = p.parent.as_posix().replace("/", ".").strip(".")
        return parent_module if parent_module else clean_stem

    return normalized.replace("/", ".").rsplit(".", 1)[0].strip(".")


def build_module_map(project_files):
    """
    Build a multi-level lookup map of module identifiers, relative paths,
    and file names to their full repository file paths.
    """
    module_map = {}

    for path in project_files:
        norm = normalize_path(path)
        p = Path(norm)
        stem = p.stem
        filename = p.name

        # 1. Exact path
        module_map[norm] = norm

        # 2. Path without extension
        no_ext = norm.rsplit(".", 1)[0] if "." in norm else norm
        module_map[no_ext] = norm

        # 3. Dotted module name
        dotted = norm.replace("/", ".")
        module_map[dotted] = norm
        if "." in norm:
            module_map[dotted.rsplit(".", 1)[0]] = norm

        # 4. Filename & Stem
        module_map[filename] = norm
        module_map[stem] = norm

        # 5. Dotted stem module
        mod_name = path_to_module(norm)
        if mod_name:
            module_map[mod_name] = norm

    return module_map


# ============================================================
# MULTI-LANGUAGE PARSERS
# ============================================================

def parse_python(source):
    """
    Parse Python source using AST with regex fallback for version/syntax mismatches.
    """
    functions = []
    imports = []
    complexity_score = 0
    docstring = None

    # Try native AST first
    try:
        tree = ast.parse(source)
        docstring = ast.get_docstring(tree)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                end_line = getattr(node, "end_lineno", node.lineno)
                fn_doc = ast.get_docstring(node)
                calls = []

                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            calls.append(child.func.id)
                        elif isinstance(child.func, ast.Attribute):
                            calls.append(child.func.attr)

                functions.append({
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": end_line,
                    "docstring": fn_doc,
                    "calls": sorted(set(calls))
                })

            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

            elif isinstance(node, (
                ast.If, ast.For, ast.While, ast.Try, ast.With,
                ast.ExceptHandler, ast.BoolOp, ast.IfExp, ast.Match
            )):
                complexity_score += 1

        functions.sort(key=lambda item: item["line"])
        return functions, imports, complexity_score, docstring
    except Exception:
        # Fallback to regex parser on syntax errors / incompatible Python versions
        pass

    # Regex Fallback for Python
    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Match function defs
        fn_match = re.match(r"^\s*(?:async\s+)?def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", line)
        if fn_match:
            fn_name = fn_match.group(1)
            functions.append({
                "name": fn_name,
                "line": idx,
                "end_line": idx,
                "docstring": None,
                "calls": []
            })

        # Match imports
        imp_match = re.match(r"^\s*(?:from\s+([a-zA-Z0-9_.]+)\s+import|import\s+([a-zA-Z0-9_.,\s]+))", line)
        if imp_match:
            mod = imp_match.group(1) or imp_match.group(2)
            if mod:
                for part in mod.split(","):
                    clean = part.strip().split()[0]
                    if clean:
                        imports.append(clean)

        # Complexity points
        if re.search(r"\b(if|elif|for|while|try|except|with|match|case)\b", line):
            complexity_score += 1

    return functions, imports, complexity_score, docstring


def parse_javascript_typescript(source):
    """
    Parse JavaScript / TypeScript source for functions, imports, calls, docstrings, and complexity.
    """
    functions = []
    imports = []
    complexity_score = 0
    docstring = None

    lines = source.splitlines()

    # Extract top header comment as docstring if available
    header_comment = re.match(r"^\s*/\*\*\s*([\s\S]*?)\*/", source)
    if header_comment:
        clean_doc = "\n".join(
            re.sub(r"^\s*\*+\s?", "", l) for l in header_comment.group(1).splitlines()
        ).strip()
        if clean_doc:
            docstring = clean_doc

    # Regex patterns for JS/TS
    import_patterns = [
        re.compile(r"""(?:import\s+.*?from\s+['"]([^'"]+)['"]|import\s+['"]([^'"]+)['"]|require\s*\(\s*['"]([^'"]+)['"]\)|export\s+.*?from\s+['"]([^'"]+)['"])"""),
    ]

    fn_patterns = [
        # function name(...)
        re.compile(r"""^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s+([a-zA-Z0-9_$]+)\s*\("""),
        # const name = (...) => or const name = function(...)
        re.compile(r"""^\s*(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[a-zA-Z0-9_$]+)\s*=>"""),
        re.compile(r"""^\s*(?:export\s+)?(?:const|let|var)\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?function\s*"""),
        # Class method: methodName(...) {
        re.compile(r"""^\s*(?:public|private|protected|static|async|\*)*\s*([a-zA-Z0-9_$]+)\s*\([^)]*\)\s*(?::\s*[^{]+)?\s*\{"""),
        # Class declaration
        re.compile(r"""^\s*(?:export\s+)?(?:default\s+)?class\s+([a-zA-Z0-9_$]+)"""),
    ]

    for idx, line in enumerate(lines, start=1):
        # Imports
        for pat in import_patterns:
            for match in pat.finditer(line):
                for group in match.groups():
                    if group:
                        imports.append(group)

        # Functions
        for pat in fn_patterns:
            fn_match = pat.match(line)
            if fn_match:
                fn_name = fn_match.group(1)
                # Filter out language keywords matched by method regex
                if fn_name not in ("if", "for", "while", "switch", "catch", "return", "function", "constructor"):
                    # Find calls inside approximate block
                    calls = []
                    # Check next 15 lines for calls
                    sub_text = "\n".join(lines[idx:min(len(lines), idx + 20)])
                    found_calls = re.findall(r"\b([a-zA-Z0-9_$]+)\s*\(", sub_text)
                    for c in found_calls:
                        if c not in ("if", "for", "while", "catch", "switch", "require", "import", fn_name):
                            calls.append(c)

                    functions.append({
                        "name": fn_name,
                        "line": idx,
                        "end_line": idx,
                        "docstring": None,
                        "calls": sorted(set(calls[:10]))
                    })
                break

        # Complexity
        if re.search(r"\b(if|else\s+if|for|while|switch|case|catch|try|\?\?)\b|\?|&&|\|\|", line):
            complexity_score += 1

    return functions, imports, complexity_score, docstring


def parse_go(source):
    """
    Parse Go source for functions, imports, calls, and complexity.
    """
    functions = []
    imports = []
    complexity_score = 0
    docstring = None

    lines = source.splitlines()

    # Package doc comment
    pkg_match = re.search(r"//\s*(Package\s+[a-zA-Z0-9_]+[\s\S]*?)\npackage", source)
    if pkg_match:
        docstring = pkg_match.group(1).strip()

    in_import_block = False

    for idx, line in enumerate(lines, start=1):
        # Go multi-line imports
        if re.match(r"^\s*import\s*\(", line):
            in_import_block = True
            continue
        if in_import_block:
            if re.match(r"^\s*\)", line):
                in_import_block = False
            else:
                imp_match = re.search(r'["\']([^"\']+)["\']', line)
                if imp_match:
                    imports.append(imp_match.group(1))
            continue

        # Go single-line import
        single_imp = re.match(r'^\s*import\s+["\']([^"\']+)["\']', line)
        if single_imp:
            imports.append(single_imp.group(1))

        # Go functions: func FuncName(...) or func (r *Recv) MethodName(...)
        fn_match = re.match(r"^\s*func\s+(?:\([^)]+\)\s+)?([a-zA-Z0-9_]+)\s*\(", line)
        if fn_match:
            fn_name = fn_match.group(1)
            functions.append({
                "name": fn_name,
                "line": idx,
                "end_line": idx,
                "docstring": None,
                "calls": []
            })

        # Complexity
        if re.search(r"\b(if|for|switch|case|select|go|defer)\b|&&|\|\|", line):
            complexity_score += 1

    return functions, imports, complexity_score, docstring


def parse_java_kotlin_csharp(source, lang):
    """
    Parse Java, Kotlin, or C# source files.
    """
    functions = []
    imports = []
    complexity_score = 0
    docstring = None

    lines = source.splitlines()

    # Top comment
    header = re.match(r"^\s*/\*\*\s*([\s\S]*?)\*/", source)
    if header:
        docstring = "\n".join(re.sub(r"^\s*\*+\s?", "", l) for l in header.group(1).splitlines()).strip()

    for idx, line in enumerate(lines, start=1):
        # Imports / Using
        imp_match = re.match(r"^\s*(?:import\s+(?:static\s+)?([a-zA-Z0-9_.*]+)|using\s+([a-zA-Z0-9_.]+))\s*;", line)
        if imp_match:
            mod = imp_match.group(1) or imp_match.group(2)
            if mod:
                imports.append(mod)

        # Methods
        # Java / C#: [modifiers] ReturnType methodName(...)
        method_match = re.match(
            r"^\s*(?:public|protected|private|static|final|abstract|async|override|fun|void)*\s*(?:<[^>]+>\s*)?(?:[a-zA-Z0-9_<>[\],\s]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*(?:throws\s+[^{]+)?\s*[{;]",
            line
        )
        if method_match:
            fn_name = method_match.group(1)
            if fn_name not in ("if", "for", "while", "switch", "catch", "class", "interface", "enum", "record", "return"):
                functions.append({
                    "name": fn_name,
                    "line": idx,
                    "end_line": idx,
                    "docstring": None,
                    "calls": []
                })

        # Complexity
        if re.search(r"\b(if|else\s+if|for|while|switch|case|catch|try|\?\?)\b|\?|&&|\|\|", line):
            complexity_score += 1

    return functions, imports, complexity_score, docstring


def parse_c_cpp(source):
    """
    Parse C/C++ source and header files.
    """
    functions = []
    imports = []
    complexity_score = 0
    docstring = None

    lines = source.splitlines()

    for idx, line in enumerate(lines, start=1):
        # #include
        inc_match = re.match(r'^\s*#include\s*[<"]([^>"]+)[>"]', line)
        if inc_match:
            imports.append(inc_match.group(1))

        # Functions: ReturnType FuncName(...) {
        fn_match = re.match(r"^\s*(?:[a-zA-Z0-9_*&:]+)\s+([a-zA-Z0-9_]+)\s*\([^)]*\)\s*(?:const)?\s*\{", line)
        if fn_match:
            fn_name = fn_match.group(1)
            if fn_name not in ("if", "for", "while", "switch", "catch", "return"):
                functions.append({
                    "name": fn_name,
                    "line": idx,
                    "end_line": idx,
                    "docstring": None,
                    "calls": []
                })

        # Complexity
        if re.search(r"\b(if|else\s+if|for|while|switch|case|catch|try)\b|\?|&&|\|\|", line):
            complexity_score += 1

    return functions, imports, complexity_score, docstring


def parse_rust(source):
    """
    Parse Rust source files.
    """
    functions = []
    imports = []
    complexity_score = 0
    docstring = None

    lines = source.splitlines()

    for idx, line in enumerate(lines, start=1):
        # use crate::...;
        use_match = re.match(r"^\s*(?:pub\s+)?use\s+([a-zA-Z0-9_:{},\s*]+);", line)
        if use_match:
            imports.append(use_match.group(1).split("::")[0].strip())

        # fn func_name(...)
        fn_match = re.match(r"^\s*(?:pub(?:\([^)]+\))?\s+)?(?:async\s+)?fn\s+([a-zA-Z0-9_]+)\s*(?:<[^>]+>)?\s*\(", line)
        if fn_match:
            fn_name = fn_match.group(1)
            functions.append({
                "name": fn_name,
                "line": idx,
                "end_line": idx,
                "docstring": None,
                "calls": []
            })

        # Complexity
        if re.search(r"\b(if|else\s+if|for|while|loop|match|try)\b|\?|&&|\|\|", line):
            complexity_score += 1

    return functions, imports, complexity_score, docstring


def parse_generic_source(source):
    """
    Generic fallback parser for any other programming language.
    """
    functions = []
    imports = []
    complexity_score = 0
    docstring = None

    lines = source.splitlines()
    for idx, line in enumerate(lines, start=1):
        # Look for function / def / sub / fn patterns
        fn_match = re.match(r"^\s*(?:function|def|sub|fn|func|procedure)\s+([a-zA-Z0-9_]+)", line, re.IGNORECASE)
        if fn_match:
            functions.append({
                "name": fn_match.group(1),
                "line": idx,
                "end_line": idx,
                "docstring": None,
                "calls": []
            })

        # Look for import / include / require / use patterns
        imp_match = re.match(r"^\s*(?:import|include|require|require_relative|use|using)\s+['\"]?([a-zA-Z0-9_./\\-]+)", line, re.IGNORECASE)
        if imp_match:
            imports.append(imp_match.group(1))

        if re.search(r"\b(if|else|for|while|switch|case|catch|try)\b", line, re.IGNORECASE):
            complexity_score += 1

    return functions, imports, complexity_score, docstring


# ============================================================
# UNIFIED FILE PARSER
# ============================================================

def parse_code_file(path, username=None, repository=None, repository_sources=None):
    """
    Parse any source code file according to its language.
    Returns: (functions, imports, complexity_score, docstring, source_code)
    """
    source = read_file(path, username, repository, repository_sources)

    if not source:
        return [], [], 0, None, ""

    lang = get_language(path)

    if lang == "python":
        functions, imports, score, doc = parse_python(source)
    elif lang in ("javascript", "typescript"):
        functions, imports, score, doc = parse_javascript_typescript(source)
    elif lang == "go":
        functions, imports, score, doc = parse_go(source)
    elif lang in ("java", "kotlin", "csharp"):
        functions, imports, score, doc = parse_java_kotlin_csharp(source, lang)
    elif lang in ("c", "cpp", "c_header", "cpp_header"):
        functions, imports, score, doc = parse_c_cpp(source)
    elif lang == "rust":
        functions, imports, score, doc = parse_rust(source)
    else:
        functions, imports, score, doc = parse_generic_source(source)

    return functions, imports, score, doc, source


# ============================================================
# UNIVERSAL MODULE RESOLUTION & DEPENDENCY ANALYSIS
# ============================================================

def resolve_project_module(import_name, current_file, module_map):
    """
    Resolve an imported module name / relative path to a file in the project.
    Works for Python, JS/TS, Go, Java, C/C++, Rust, etc.
    """
    if not import_name:
        return None

    clean_import = import_name.strip().strip("'\"")

    # 1. Direct match in module map
    if clean_import in module_map:
        return module_map[clean_import]

    current_norm = normalize_path(current_file)
    current_dir = Path(current_norm).parent.as_posix()

    # 2. Relative imports (e.g. ./utils, ../components/Header, ./styles.css)
    if clean_import.startswith("."):
        try:
            target_path = (Path(current_dir) / clean_import).resolve()
            # Normalize relative to workspace/repo
            rel_path = normalize_path(Path(current_dir) / clean_import)
            # Remove './' or parent artifacts
            rel_parts = [p for p in rel_path.split("/") if p != "."]
            clean_rel = "/".join(rel_parts)

            # Try exact match, extensions, and index files
            extensions = ["", ".js", ".ts", ".jsx", ".tsx", ".py", ".vue", ".json", ".css"]
            for ext in extensions:
                candidate = f"{clean_rel}{ext}"
                if candidate in module_map:
                    return module_map[candidate]
                candidate_index = f"{clean_rel}/index{ext}"
                if candidate_index in module_map:
                    return module_map[candidate_index]
        except Exception:
            pass

    # 3. Python package candidate resolutions
    candidates = [
        clean_import,
        f"app.{clean_import}",
        f"src.{clean_import}",
    ]

    current_parts = current_norm.split("/")
    if len(current_parts) > 1:
        parent_module = ".".join(current_parts[:-1])
        if parent_module:
            candidates.append(f"{parent_module}.{clean_import}")

    for candidate in candidates:
        if candidate in module_map:
            return module_map[candidate]

    # 4. Prefix search (e.g., 'package.submodule.symbol' -> 'package.submodule')
    import_parts = clean_import.replace("/", ".").split(".")
    for length in range(len(import_parts), 0, -1):
        candidate = ".".join(import_parts[:length])
        if candidate in module_map:
            return module_map[candidate]

    return None


def is_stdlib_module(name, lang):
    """
    Check if a module is part of the standard library for the specified language.
    """
    root_name = name.split(".")[0].split("/")[0].strip()

    if lang == "python":
        try:
            return root_name in sys.stdlib_module_names
        except AttributeError:
            return root_name in STDLIB_MODULES.get("python", set())

    stdlib = STDLIB_MODULES.get(lang, set())
    return root_name in stdlib or name in stdlib


def analyze_imports(path, module_map, username=None, repository=None, repository_sources=None):
    """
    Analyze dependencies of a file, categorizing them into:
    - Project dependencies (files in the same repo)
    - External dependencies (3rd-party libraries)
    - Standard library imports
    """
    lang = get_language(path)
    _, raw_imports, _, _, _ = parse_code_file(path, username, repository, repository_sources)

    project_dependencies = []
    external_dependencies = []
    standard_library = []

    for import_name in raw_imports:
        if not import_name:
            continue

        resolved = resolve_project_module(import_name, path, module_map)

        if resolved:
            clean_path = display_path(resolved, repository_sources)
            current_path = display_path(path, repository_sources)

            if clean_path != current_path:
                if clean_path not in project_dependencies:
                    project_dependencies.append(clean_path)

        elif is_stdlib_module(import_name, lang):
            root_name = import_name.split(".")[0].split("/")[0]
            if root_name not in standard_library:
                standard_library.append(root_name)

        else:
            # Clean package root name (e.g. 'react-dom/client' -> 'react-dom', '@mui/material' -> '@mui/material')
            parts = import_name.split("/")
            if import_name.startswith("@") and len(parts) >= 2:
                root_name = f"{parts[0]}/{parts[1]}"
            else:
                root_name = parts[0].split(".")[0]

            if root_name and root_name not in external_dependencies:
                external_dependencies.append(root_name)

    return (
        sorted(project_dependencies),
        sorted(external_dependencies),
        sorted(standard_library)
    )


# ============================================================
# FUNCTION CALLERS
# ============================================================

def find_function_callers(selected_file, function_name, project_files, username, repository, repository_sources=None):
    """
    Find files in the project that invoke the given function.
    """
    callers = []

    for path in project_files:
        if path == selected_file:
            continue

        functions, _, _, _, source = parse_code_file(path, username, repository, repository_sources)

        # Fast string search before deeper AST/regex inspection
        if function_name not in source:
            continue

        found = False
        # Check if function call is in extracted calls
        for fn in functions:
            if function_name in fn.get("calls", []):
                found = True
                break

        # Check regex invocation
        if not found and re.search(rf"\b{re.escape(function_name)}\s*\(", source):
            found = True

        if found:
            callers.append(display_path(path, repository_sources))

    return sorted(set(callers))


# ============================================================
# DEPENDENTS & RELATED TESTS
# ============================================================

def find_dependencies(path, module_map, username, repository, repository_sources=None):
    project_deps, _, _ = analyze_imports(path, module_map, username, repository, repository_sources)
    return project_deps


def find_dependents(path, project_files, module_map, username, repository, repository_sources=None):
    """
    Find files in the project that depend on the selected file.
    """
    selected_display = display_path(path, repository_sources)
    selected_stem = Path(path).stem.lower()
    dependents = []

    for other_file in project_files:
        if other_file == path:
            continue

        dependencies = find_dependencies(other_file, module_map, username, repository, repository_sources)

        if selected_display in dependencies:
            dependents.append(display_path(other_file, repository_sources))
        elif any(Path(dep).stem.lower() == selected_stem for dep in dependencies):
            dependents.append(display_path(other_file, repository_sources))

    return sorted(set(dependents))


def find_related_tests(selected_file, project_files, module_map, username, repository, repository_sources=None):
    """
    Find automated tests related to the selected file across multiple languages.
    """
    related_tests = []
    selected_stem = Path(selected_file).stem.lower()
    selected_display = display_path(selected_file, repository_sources)

    functions, _, _, _, _ = parse_code_file(selected_file, username, repository, repository_sources)
    function_names = {f["name"].lower() for f in functions}

    for path in project_files:
        if path == selected_file:
            continue

        path_lower = str(path).lower()
        path_name_lower = Path(path).name.lower()

        # Check if this other file is a test file
        is_test_file = (
            "test" in path_name_lower
            or "spec" in path_name_lower
            or "/tests/" in path_lower
            or "/__tests__/" in path_lower
            or "/test/" in path_lower
        )

        if not is_test_file:
            continue

        _, _, _, _, source = parse_code_file(path, username, repository, repository_sources)
        source_lower = source.lower()

        related = False

        # 1. Direct dependency
        deps = find_dependencies(path, module_map, username, repository, repository_sources)
        if selected_display in deps or any(Path(d).stem.lower() == selected_stem for d in deps):
            related = True

        # 2. Filename match (e.g. Button.tsx -> Button.test.tsx or user_service.py -> test_user_service.py)
        if selected_stem in path_name_lower:
            related = True

        # 3. Source contains module stem or function names
        if selected_stem in source_lower:
            related = True

        for fn_name in function_names:
            if fn_name in source_lower:
                related = True
                break

        if related:
            related_tests.append(display_path(path, repository_sources))

    return sorted(set(related_tests))


# ============================================================
# FILE PURPOSE EXTRACTION
# ============================================================

def get_file_purpose(path, username=None, repository=None, repository_sources=None):
    """
    Determine the functional purpose of a file from docstrings, framework conventions,
    and exported symbols.
    """
    functions, imports, _, docstring, source = parse_code_file(path, username, repository, repository_sources)

    # 1. Use explicit docstring / header comment if available
    if docstring:
        first_line = docstring.strip().splitlines()[0]
        if len(first_line) > 120:
            first_line = first_line[:117] + "..."
        return first_line

    name = Path(path).stem.lower()
    full_path = normalize_path(path).lower()
    lang = get_language(path)

    # 2. Framework & Pattern mapping
    if "dockerfile" in name:
        return "Defines the container image build and execution environment."
    if "docker-compose" in name:
        return "Defines multi-container Docker services and configurations."
    if "package.json" in full_path:
        return "Defines project dependencies, scripts, and package metadata."
    if "cargo.toml" in full_path or "go.mod" in full_path or "requirements.txt" in full_path:
        return "Declares project dependencies and build configuration."
    if "readme" in name:
        return "Provides documentation and an overview of the project."

    # Web & UI Components
    if lang in ("javascript", "typescript") and (
        "component" in full_path or full_path.endswith((".jsx", ".tsx"))
    ):
        return "Implements a UI component and view rendering logic."

    # Routes & API Controllers
    if any(k in full_path for k in ["routes", "router", "controller", "endpoint", "api"]):
        return "Handles API routes, request processing, and endpoint handling."

    # Services & Business Logic
    if any(k in full_path for k in ["service", "repository", "provider", "manager"]):
        return "Contains reusable business logic, domain services, or data access."

    # Models & Database Schema
    if any(k in full_path for k in ["model", "schema", "entity", "dto", "types"]):
        return "Defines data models, type definitions, or database schemas."

    # Utilities & Helpers
    if any(k in full_path for k in ["util", "helper", "common", "shared"]):
        return "Provides reusable utility functions and helpers."

    # Tests
    if any(k in full_path for k in ["test", "spec", "__test__"]):
        return "Contains automated tests for validating project behavior."

    # Configs
    if any(k in full_path for k in ["config", "settings", "env", "constant"]):
        return "Provides application configuration and global settings."

    # Middleware
    if "middleware" in full_path or "guard" in full_path:
        return "Provides request middleware, authentication, or interceptors."

    # Functions heuristic
    fn_names = [f["name"].lower() for f in functions]
    if any("load" in f or "read" in f or "save" in f or "write" in f for f in fn_names):
        return "Handles data reading, loading, or persistence operations."
    if any("get" in f or "fetch" in f or "query" in f for f in fn_names):
        return "Provides data retrieval and processing logic."
    if any("render" in f or "view" in f or "draw" in f for f in fn_names):
        return "Renders user interface views or visualization elements."

    return f"Contains {LANGUAGE_DISPLAY.get(lang, 'application')} source logic."


# ============================================================
# COMPLEXITY & IMPACT
# ============================================================

def get_complexity_label(score):
    if score <= 5:
        return "Low"
    if score <= 15:
        return "Moderate"
    return "High"


def get_impact_level(dependents):
    count = len(dependents)
    if count == 0:
        return "Low"
    if count <= 2:
        return "Moderate"
    return "High"


def get_impact_explanation(impact, dependents):
    count = len(dependents)
    if count == 0:
        return "No project files currently depend directly on this file."
    if impact == "Moderate":
        return f"{count} project file(s) depend directly on this file. Changes should be checked against its callers."
    return f"{count} project files depend directly on this file. Changes may affect several parts of the application."


# ============================================================
# GRAPHVIZ RELATIONSHIP GRAPH
# ============================================================

def build_relationship_graph(selected_file, dependencies, dependents):
    selected = display_path(selected_file)

    lines = [
        "digraph G {",
        "rankdir=LR;",
        'node [shape=box, style="rounded,filled", fillcolor="#1e293b", fontcolor="#ffffff", color="#475569"];',
        'edge [color="#94a3b8", fontcolor="#94a3b8"];',
        f'"selected" [label="{selected}", shape=box, style="rounded,filled", fillcolor="#3b82f6", fontcolor="#ffffff", color="#2563eb"];'
    ]

    for index, dependency in enumerate(dependencies):
        node_id = f"dep{index}"
        safe_label = dependency.replace('"', '\\"')
        lines.append(f'"{node_id}" [label="{safe_label}", fillcolor="#0f172a"];')
        lines.append(f'"selected" -> "{node_id}" [color="#60a5fa", label="depends on"];')

    for index, dependent in enumerate(dependents):
        node_id = f"user{index}"
        safe_label = dependent.replace('"', '\\"')
        lines.append(f'"{node_id}" [label="{safe_label}", fillcolor="#0f172a"];')
        lines.append(f'"{node_id}" -> "selected" [color="#34d399", label="used by"];')

    lines.append("}")
    return "\n".join(lines)


# ============================================================
# RECOMMENDATIONS
# ============================================================

def get_recommendations(dependencies, dependents, related_tests, functions, external_dependencies, lang):
    recommendations = []

    if dependents:
        recommendations.append(
            f"Check detected callers in {len(dependents)} dependent file(s) before altering signatures, exports, or return values."
        )

    if functions:
        recommendations.append(
            f"Review {len(functions)} detected function(s) when refactoring internal logic."
        )

    if related_tests:
        recommendations.append(
            f"Run the {len(related_tests)} detected test suite(s) after modifying this file."
        )
    else:
        recommendations.append(
            "No related test files detected automatically — consider writing unit tests for critical code paths."
        )

    if dependencies:
        recommendations.append(
            "Verify internal module imports if refactoring or moving file paths."
        )

    if external_dependencies:
        recommendations.append(
            f"External packages ({', '.join(external_dependencies[:4])}) are referenced — ensure correct environment dependencies."
        )

    return recommendations


# ============================================================
# FILE ANALYSIS
# ============================================================

def analyze_file(path, project_files, module_map, username=None, repository=None, repository_sources=None):
    lang = get_language(path)
    functions, _, complexity_score, _, _ = parse_code_file(path, username, repository, repository_sources)

    project_dependencies, external_dependencies, standard_library = analyze_imports(
        path, module_map, username, repository, repository_sources
    )

    dependents = find_dependents(path, project_files, module_map, username, repository, repository_sources)
    related_tests = find_related_tests(path, project_files, module_map, username, repository, repository_sources)

    complexity_label = get_complexity_label(complexity_score)
    impact = get_impact_level(dependents)

    return {
        "language": lang,
        "language_display": LANGUAGE_DISPLAY.get(lang, "📄 Code File"),
        "functions": functions,
        "project_dependencies": project_dependencies,
        "external_dependencies": external_dependencies,
        "standard_library": standard_library,
        "dependents": dependents,
        "related_tests": related_tests,
        "complexity_score": complexity_score,
        "complexity_label": complexity_label,
        "impact": impact,
        "impact_explanation": get_impact_explanation(impact, dependents),
        "purpose": get_file_purpose(path, username, repository, repository_sources),
        "recommendations": get_recommendations(
            project_dependencies, dependents, related_tests, functions, external_dependencies, lang
        )
    }


# ============================================================
# MAIN STREAMLIT RENDER FUNCTION
# ============================================================

def render_code_intelligence(username=None, repository=None):
    st.header("🧠 Code Intelligence")
    st.write("Understand any repository's architecture, dependencies, functions, and impact before you edit.")

    if not username or not repository:
        st.info("Analyze a GitHub repository above to use Code Intelligence.")
        return

    # ========================================================
    # LOAD FILE LIST
    # ========================================================
    with st.spinner("Loading repository file list..."):
        try:
            all_repository_files = get_repository_file_list(username, repository)
        except Exception as e:
            st.error(f"Unable to load repository files: {e}")
            return

    if not all_repository_files:
        st.info("No files were found in this repository.")
        return

    # All candidate source files
    source_files = [f for f in all_repository_files if is_source_code_file(f)]
    if not source_files:
        source_files = all_repository_files

    module_map = build_module_map(source_files)

    # Detect available languages in repository
    detected_languages = {}
    for f in source_files:
        l = get_language(f)
        detected_languages[l] = detected_languages.get(l, 0) + 1

    # ========================================================
    # LANGUAGE FILTER & FILE SELECTION
    # ========================================================
    col_lang, col_file = st.columns([1, 2])

    with col_lang:
        lang_options = ["all"] + sorted(detected_languages.keys())
        lang_labels = {
            "all": f"🌐 All Languages ({len(source_files)})",
            **{k: f"{LANGUAGE_DISPLAY.get(k, k.capitalize())} ({v})" for k, v in detected_languages.items()}
        }
        selected_lang = st.selectbox(
            "Filter by Language",
            lang_options,
            format_func=lambda x: lang_labels.get(x, x),
            key="code_intelligence_lang_filter"
        )

    # Filter files based on language selection
    if selected_lang != "all":
        filtered_files = [f for f in source_files if get_language(f) == selected_lang]
    else:
        filtered_files = source_files

    if not filtered_files:
        st.info(f"No {LANGUAGE_DISPLAY.get(selected_lang, selected_lang)} files found.")
        return

    with col_file:
        selected_file = st.selectbox(
            "🔍 Select a File to Analyze",
            filtered_files,
            key="code_intelligence_file"
        )

    # ========================================================
    # ANALYSIS
    # ========================================================
    with st.spinner("Analyzing selected file structure and relationships..."):
        analysis = analyze_file(
            selected_file,
            source_files,
            module_map,
            username,
            repository
        )

    # ========================================================
    # FILE HEADER & IMPACT
    # ========================================================
    st.subheader("📄 File Understanding")

    header_col1, header_col2, header_col3 = st.columns([3, 1, 1])

    with header_col1:
        st.markdown(f"### `{selected_file}`")
        st.write(analysis["purpose"])

    with header_col2:
        st.caption("LANGUAGE")
        st.info(analysis["language_display"])

    with header_col3:
        st.caption("CHANGE IMPACT")
        if analysis["impact"] == "Low":
            st.success("🟢 Low")
        elif analysis["impact"] == "Moderate":
            st.warning("🟡 Moderate")
        else:
            st.error("🔴 High")

    st.caption(analysis["impact_explanation"])
    st.divider()

    # ========================================================
    # RESPONSIBILITIES & FUNCTIONS
    # ========================================================
    st.subheader("🎯 Functions & Declarations")

    if analysis["functions"]:
        num_cols = min(3, max(1, len(analysis["functions"])))
        columns = st.columns(num_cols)

        for index, function in enumerate(analysis["functions"]):
            with columns[index % num_cols]:
                st.info(f"⚙️ `{function['name']}()` • line {function['line']}")
    else:
        st.caption("No explicit function declarations detected in this file.")

    st.divider()

    # ========================================================
    # RELATIONSHIPS & DEPENDENCY MAP
    # ========================================================
    st.subheader("🔗 How is this file connected?")

    relation_col1, relation_col2 = st.columns(2)

    with relation_col1:
        st.markdown("### 📥 Depends on (Project)")
        if analysis["project_dependencies"]:
            for dependency in analysis["project_dependencies"]:
                st.write(f"→ `{dependency}`")
        else:
            st.caption("No project-level internal dependencies.")

    with relation_col2:
        st.markdown("### 📤 Used by (Dependents)")
        if analysis["dependents"]:
            for dependent in analysis["dependents"]:
                st.write(f"← `{dependent}`")
        else:
            st.caption("No direct project dependents detected.")

    if analysis["project_dependencies"] or analysis["dependents"]:
        st.markdown("### 🗺️ Relationship Map")
        graph = build_relationship_graph(
            selected_file,
            analysis["project_dependencies"],
            analysis["dependents"]
        )
        st.graphviz_chart(graph, use_container_width=True)

    st.divider()

    # ========================================================
    # FUNCTION INTELLIGENCE (DETAILED)
    # ========================================================
    if analysis["functions"]:
        st.subheader("⚙️ Function Intelligence")

        for function in analysis["functions"]:
            with st.expander(f"`{function['name']}()` • line {function['line']}"):
                if function["docstring"]:
                    st.write(function["docstring"])
                else:
                    st.caption("No docstring found.")

                if function["calls"]:
                    st.write("Calls:")
                    for call in function["calls"]:
                        st.write(f"→ `{call}()`")

                callers = find_function_callers(
                    selected_file,
                    function["name"],
                    source_files,
                    username,
                    repository
                )

                st.write("Detected callers across repository:")
                if callers:
                    for caller in callers:
                        st.write(f"← `{caller}`")
                else:
                    st.caption("No callers detected automatically.")

        st.divider()

    # ========================================================
    # DEPENDENCIES (PROJECT, EXTERNAL, STDLIB)
    # ========================================================
    st.subheader("📦 Dependencies")

    dep_col1, dep_col2 = st.columns(2)

    with dep_col1:
        st.markdown("### 🏠 Project Modules")
        if analysis["project_dependencies"]:
            for dep in analysis["project_dependencies"]:
                st.write(f"• `{dep}`")
        else:
            st.caption("None detected.")

    with dep_col2:
        st.markdown("### 🌐 External Packages")
        if analysis["external_dependencies"]:
            for dep in analysis["external_dependencies"]:
                st.write(f"• `{dep}`")
        else:
            st.caption("None detected.")

    if analysis["standard_library"]:
        with st.expander(f"📚 Standard Library Imports ({len(analysis['standard_library'])})"):
            st.write(", ".join(f"`{item}`" for item in analysis["standard_library"]))

    st.divider()

    # ========================================================
    # TEST INTELLIGENCE
    # ========================================================
    st.subheader("🧪 Related Tests")

    if analysis["related_tests"]:
        st.success(f"{len(analysis['related_tests'])} related test file(s) detected.")
        for test_file in analysis["related_tests"]:
            st.write(f"🧪 `{test_file}`")
    else:
        st.info("No related test file was detected automatically.")

    st.divider()

    # ========================================================
    # STRUCTURAL COMPLEXITY
    # ========================================================
    st.subheader("📐 Structural Complexity")

    complexity_col1, complexity_col2 = st.columns(2)

    with complexity_col1:
        st.metric("Complexity Rating", analysis["complexity_label"])

    with complexity_col2:
        st.metric("Control-Flow Points", analysis["complexity_score"])

    st.caption("Calculated from branching, loops, pattern matching, conditionals, and exception handling.")
    st.divider()

    # ========================================================
    # BEFORE YOU EDIT RECOMMENDATIONS
    # ========================================================
    st.subheader("💡 Before You Edit")

    for recommendation in analysis["recommendations"]:
        st.info(f"💡 {recommendation}")

    st.divider()
    st.caption("GitSense Multi-Language Code Intelligence • Explain Before You Edit")
