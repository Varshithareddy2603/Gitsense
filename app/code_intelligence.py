import ast
import os
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
# FILE DISCOVERY
# ============================================================

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
}


def get_project_files():

    files = []

    for root, dirs, filenames in os.walk(PROJECT_ROOT):

        dirs[:] = [
            directory
            for directory in dirs
            if directory not in IGNORED_DIRS
        ]

        for filename in filenames:

            if filename.endswith(".py"):

                files.append(
                    Path(root) / filename
                )

    return sorted(files)


def display_path(path):

    try:

        relative = path.relative_to(
            PROJECT_ROOT
        )

        return relative.as_posix()

    except ValueError:

        return path.as_posix()


def read_file(path):

    try:

        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

    except Exception:

        return ""


# ============================================================
# AST PARSING
# ============================================================

def parse_python_file(path):

    source = read_file(path)

    if not source:

        return None, ""

    try:

        tree = ast.parse(source)

        return tree, source

    except SyntaxError:

        return None, source


# ============================================================
# MODULE MAP
# ============================================================

def build_module_map():

    module_map = {}

    for path in get_project_files():

        relative = path.relative_to(
            PROJECT_ROOT
        )

        parts = list(
            relative.parts
        )

        if parts[-1] == "__init__.py":

            parts = parts[:-1]

        else:

            parts[-1] = Path(
                parts[-1]
            ).stem

        if not parts:

            continue

        module_name = ".".join(
            parts
        )

        module_map[
            module_name
        ] = path

    return module_map


# ============================================================
# IMPORT EXTRACTION
# ============================================================

def get_import_names(tree):

    imports = []

    if tree is None:

        return imports

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Import
        ):

            for alias in node.names:

                imports.append(
                    alias.name
                )

        elif isinstance(
            node,
            ast.ImportFrom
        ):

            if node.module:

                imports.append(
                    node.module
                )

    return imports


# ============================================================
# PROJECT MODULE RESOLUTION
# ============================================================

def resolve_project_module(
    import_name,
    current_file,
    module_map
):

    if not import_name:

        return None

    candidates = [
        import_name
    ]

    if not import_name.startswith(
        "app."
    ):

        candidates.append(
            f"app.{import_name}"
        )

    current_relative = (
        current_file.relative_to(
            PROJECT_ROOT
        )
    )

    if current_relative.parent.parts:

        parent_module = ".".join(
            current_relative.parent.parts
        )

        candidates.append(
            f"{parent_module}.{import_name}"
        )

    for candidate in candidates:

        if candidate in module_map:

            return module_map[
                candidate
            ]

    return None


# ============================================================
# STANDARD LIBRARY
# ============================================================

def is_stdlib_module(name):

    root_name = name.split(
        "."
    )[0]

    try:

        return (
            root_name
            in sys.stdlib_module_names
        )

    except AttributeError:

        common_stdlib = {
            "os",
            "sys",
            "json",
            "ast",
            "pathlib",
            "typing",
            "re",
            "math",
            "time",
            "datetime",
            "base64",
            "html",
            "collections",
            "subprocess",
            "logging",
            "unittest",
            "functools",
            "itertools",
        }

        return (
            root_name
            in common_stdlib
        )


# ============================================================
# IMPORT ANALYSIS
# ============================================================

def analyze_imports(
    path,
    module_map
):

    tree, _ = parse_python_file(
        path
    )

    project_dependencies = []
    external_dependencies = []
    standard_library = []

    if tree is None:

        return (
            project_dependencies,
            external_dependencies,
            standard_library
        )

    imports = get_import_names(
        tree
    )

    for import_name in imports:

        resolved = resolve_project_module(
            import_name,
            path,
            module_map
        )

        if resolved:

            clean_path = display_path(
                resolved
            )

            if (
                clean_path
                != display_path(path)
            ):

                if (
                    clean_path
                    not in project_dependencies
                ):

                    project_dependencies.append(
                        clean_path
                    )

        elif is_stdlib_module(
            import_name
        ):

            root_name = (
                import_name.split(".")[0]
            )

            if (
                root_name
                not in standard_library
            ):

                standard_library.append(
                    root_name
                )

        else:

            root_name = (
                import_name.split(".")[0]
            )

            if (
                root_name
                not in external_dependencies
            ):

                external_dependencies.append(
                    root_name
                )

    return (
        sorted(project_dependencies),
        sorted(external_dependencies),
        sorted(standard_library)
    )


# ============================================================
# FUNCTION ANALYSIS
# ============================================================

def get_functions(path):

    tree, _ = parse_python_file(
        path
    )

    if tree is None:

        return []

    functions = []

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.FunctionDef,
                ast.AsyncFunctionDef
            )
        ):

            end_line = getattr(
                node,
                "end_lineno",
                node.lineno
            )

            docstring = ast.get_docstring(
                node
            )

            calls = []

            for child in ast.walk(
                node
            ):

                if isinstance(
                    child,
                    ast.Call
                ):

                    if isinstance(
                        child.func,
                        ast.Name
                    ):

                        calls.append(
                            child.func.id
                        )

                    elif isinstance(
                        child.func,
                        ast.Attribute
                    ):

                        calls.append(
                            child.func.attr
                        )

            functions.append(
                {
                    "name": node.name,
                    "line": node.lineno,
                    "end_line": end_line,
                    "docstring": docstring,
                    "calls": sorted(
                        set(calls)
                    )
                }
            )

    functions.sort(
        key=lambda item: item["line"]
    )

    return functions


# ============================================================
# FUNCTION CALLERS
# ============================================================

def find_function_callers(
    selected_file,
    function_name
):

    callers = []

    for path in get_project_files():

        if path == selected_file:

            continue

        tree, _ = parse_python_file(
            path
        )

        if tree is None:

            continue

        found = False

        for node in ast.walk(
            tree
        ):

            if isinstance(
                node,
                ast.Call
            ):

                if isinstance(
                    node.func,
                    ast.Name
                ):

                    if (
                        node.func.id
                        == function_name
                    ):

                        found = True

                elif isinstance(
                    node.func,
                    ast.Attribute
                ):

                    if (
                        node.func.attr
                        == function_name
                    ):

                        found = True

        if found:

            callers.append(
                display_path(path)
            )

    return sorted(
        set(callers)
    )


# ============================================================
# DEPENDENCIES
# ============================================================

def find_dependencies(
    path,
    module_map
):

    project_dependencies, _, _ = (
        analyze_imports(
            path,
            module_map
        )
    )

    return project_dependencies


def find_dependents(
    path,
    module_map
):

    selected_display = display_path(
        path
    )

    dependents = []

    for other_file in get_project_files():

        if other_file == path:

            continue

        dependencies = find_dependencies(
            other_file,
            module_map
        )

        if (
            selected_display
            in dependencies
        ):

            dependents.append(
                display_path(
                    other_file
                )
            )

    return sorted(
        set(dependents)
    )


# ============================================================
# RELATED TESTS
# ============================================================

def find_related_tests(
    selected_file,
    module_map
):

    related_tests = []

    selected_stem = (
        selected_file.stem.lower()
    )

    selected_display = display_path(
        selected_file
    )

    functions = get_functions(
        selected_file
    )

    function_names = {
        function["name"].lower()
        for function in functions
    }

    module_name = (
        selected_file.stem.lower()
    )

    for path in get_project_files():

        if path == selected_file:

            continue

        path_text = str(path).lower()

        if (
            "test" not in path.name.lower()
            and "tests" not in path_text
        ):

            continue

        tree, source = parse_python_file(
            path
        )

        if tree is None:

            continue

        related = False

        dependencies = find_dependencies(
            path,
            module_map
        )

        if (
            selected_display
            in dependencies
        ):

            related = True

        if (
            selected_stem
            in path.stem.lower()
        ):

            related = True

        source_lower = source.lower()

        if module_name in source_lower:

            related = True

        for function_name in function_names:

            if (
                function_name
                in source_lower
            ):

                related = True

                break

        if related:

            related_tests.append(
                display_path(path)
            )

    return sorted(
        set(related_tests)
    )


# ============================================================
# FILE PURPOSE
# ============================================================

def get_file_purpose(path):

    tree, _ = parse_python_file(
        path
    )

    if tree is None:

        return "Python source file."

    module_doc = ast.get_docstring(
        tree
    )

    if module_doc:

        first_line = (
            module_doc.strip()
            .splitlines()[0]
        )

        if len(first_line) > 120:

            first_line = (
                first_line[:117]
                + "..."
            )

        return first_line

    name = path.stem.lower()

    purpose_map = {

        "github_api":
            "Handles communication with the GitHub API and retrieves repository data.",

        "repository_service":
            "Processes repository information and connects GitHub data with GitSense features.",

        "streamlit_app":
            "Provides the main Streamlit interface for GitSense.",

        "code_intelligence":
            "Analyzes source code structure, relationships, dependencies, and change impact.",

        "main":
            "Provides the application's main execution logic.",

        "app":
            "Acts as an application entry point."
    }

    if name in purpose_map:

        return purpose_map[name]

    if (
        "test" in name
        or "tests" in name
    ):

        return (
            "Contains automated tests "
            "for project behavior."
        )

    if any(
        word in name
        for word in [
            "api",
            "client",
            "request"
        ]
    ):

        return (
            "Handles communication "
            "with an external API or service."
        )

    if any(
        word in name
        for word in [
            "service",
            "repository"
        ]
    ):

        return (
            "Contains reusable application "
            "or repository logic."
        )

    if any(
        word in name
        for word in [
            "util",
            "helper"
        ]
    ):

        return (
            "Contains reusable helper functions."
        )

    functions = get_functions(
        path
    )

    function_names = [
        function["name"].lower()
        for function in functions
    ]

    if any(
        "load" in function
        or "read" in function
        or "save" in function
        for function in function_names
    ):

        return (
            "Handles data reading, loading, "
            "or persistence operations."
        )

    if any(
        "get_" in function
        or "fetch" in function
        for function in function_names
    ):

        return (
            "Provides data retrieval "
            "and processing functions."
        )

    return (
        "Contains reusable Python "
        "application logic."
    )


# ============================================================
# COMPLEXITY
# ============================================================

def calculate_complexity(path):

    tree, _ = parse_python_file(
        path
    )

    if tree is None:

        return 0

    score = 0

    for node in ast.walk(tree):

        if isinstance(
            node,
            (
                ast.If,
                ast.For,
                ast.While,
                ast.Try,
                ast.With,
                ast.ExceptHandler,
                ast.BoolOp,
                ast.IfExp,
                ast.Match
            )
        ):

            score += 1

    return score


def get_complexity_label(score):

    if score <= 5:

        return "Low"

    if score <= 15:

        return "Moderate"

    return "High"


# ============================================================
# IMPACT
# ============================================================

def get_impact_level(
    dependents
):

    count = len(
        dependents
    )

    if count == 0:

        return "Low"

    if count <= 2:

        return "Moderate"

    return "High"


def get_impact_explanation(
    impact,
    dependents
):

    count = len(
        dependents
    )

    if count == 0:

        return (
            "No project files currently "
            "depend directly on this file."
        )

    if impact == "Moderate":

        return (
            f"{count} project file(s) depend directly "
            "on this file. Changes should be checked "
            "against its callers."
        )

    return (
        f"{count} project files depend directly "
        "on this file. Changes may affect several "
        "parts of the application."
    )


# ============================================================
# GRAPH
# ============================================================

def build_relationship_graph(
    selected_file,
    dependencies,
    dependents
):

    selected = display_path(
        selected_file
    )

    lines = [
        "digraph G {",
        "rankdir=LR;",
        'node [shape=box, style="rounded"];',
        f'"selected" [label="{selected}", shape=box, style="rounded,filled"];'
    ]

    for index, dependency in enumerate(
        dependencies
    ):

        node_id = f"dep{index}"

        safe_label = (
            dependency
            .replace('"', '\\"')
        )

        lines.append(
            f'"{node_id}" [label="{safe_label}"];'
        )

        lines.append(
            f'"selected" -> "{node_id}";'
        )

    for index, dependent in enumerate(
        dependents
    ):

        node_id = f"user{index}"

        safe_label = (
            dependent
            .replace('"', '\\"')
        )

        lines.append(
            f'"{node_id}" [label="{safe_label}"];'
        )

        lines.append(
            f'"{node_id}" -> "selected";'
        )

    lines.append("}")

    return "\n".join(
        lines
    )


# ============================================================
# RECOMMENDATIONS
# ============================================================

def get_recommendations(
    dependencies,
    dependents,
    related_tests,
    functions,
    external_dependencies
):

    recommendations = []

    if dependents:

        recommendations.append(
            "Check detected callers before changing "
            "function names, parameters, or return values."
        )

    if functions:

        recommendations.append(
            "Review function-level callers when "
            "changing individual functions."
        )

    if related_tests:

        recommendations.append(
            "Run the related tests after making changes."
        )

    else:

        recommendations.append(
            "No related test file was detected automatically."
        )

    if dependencies:

        recommendations.append(
            "Check project dependencies when changing "
            "imports or module boundaries."
        )

    if external_dependencies:

        recommendations.append(
            "Changes involving external libraries may "
            "affect runtime behavior or environment setup."
        )

    return recommendations


# ============================================================
# FILE ANALYSIS
# ============================================================

def analyze_file(
    path,
    module_map
):

    functions = get_functions(
        path
    )

    (
        project_dependencies,
        external_dependencies,
        standard_library
    ) = analyze_imports(
        path,
        module_map
    )

    dependents = find_dependents(
        path,
        module_map
    )

    related_tests = find_related_tests(
        path,
        module_map
    )

    complexity_score = calculate_complexity(
        path
    )

    complexity_label = (
        get_complexity_label(
            complexity_score
        )
    )

    impact = get_impact_level(
        dependents
    )

    return {
        "functions": functions,

        "project_dependencies":
            project_dependencies,

        "external_dependencies":
            external_dependencies,

        "standard_library":
            standard_library,

        "dependents":
            dependents,

        "related_tests":
            related_tests,

        "complexity_score":
            complexity_score,

        "complexity_label":
            complexity_label,

        "impact":
            impact,

        "impact_explanation":
            get_impact_explanation(
                impact,
                dependents
            ),

        "purpose":
            get_file_purpose(
                path
            ),

        "recommendations":
            get_recommendations(
                project_dependencies,
                dependents,
                related_tests,
                functions,
                external_dependencies
            )
    }


# ============================================================
# MAIN RENDER FUNCTION
# ============================================================

def render_code_intelligence():

    st.header(
        "🧠 Code Intelligence"
    )

    st.write(
        "Understand your code before you edit it."
    )

    project_files = get_project_files()

    module_map = build_module_map()

    if not project_files:

        st.info(
            "No Python files were found."
        )

        return

    display_files = [
        display_path(path)
        for path in project_files
    ]

    selected_display = st.selectbox(
        "🔍 Select a Python file",
        display_files,
        key="code_intelligence_file"
    )

    selected_file = (
        PROJECT_ROOT
        / selected_display
    )

    analysis = analyze_file(
        selected_file,
        module_map
    )

    # ========================================================
    # FILE HEADER
    # ========================================================

    st.subheader(
        "📄 File Understanding"
    )

    header_col1, header_col2 = st.columns(
        [3, 1]
    )

    with header_col1:

        st.markdown(
            f"### `{selected_display}`"
        )

        st.write(
            analysis["purpose"]
        )

    with header_col2:

        st.caption(
            "CHANGE IMPACT"
        )

        if analysis["impact"] == "Low":

            st.success(
                "🟢 Low"
            )

        elif analysis["impact"] == "Moderate":

            st.warning(
                "🟡 Moderate"
            )

        else:

            st.error(
                "🔴 High"
            )

    st.caption(
        analysis["impact_explanation"]
    )

    st.divider()

    # ========================================================
    # RESPONSIBILITIES
    # ========================================================

    st.subheader(
        "🎯 What does this file do?"
    )

    if analysis["functions"]:

        columns = st.columns(
            min(
                3,
                len(
                    analysis["functions"]
                )
            )
        )

        for index, function in enumerate(
            analysis["functions"]
        ):

            with columns[
                index % len(columns)
            ]:

                st.info(
                    f"⚙️ `{function['name']}()`"
                )

    else:

        st.info(
            "No functions detected."
        )

    st.divider()

    # ========================================================
    # RELATIONSHIPS
    # ========================================================

    st.subheader(
        "🔗 How is this file connected?"
    )

    relation_col1, relation_col2 = (
        st.columns(2)
    )

    with relation_col1:

        st.markdown(
            "### 📥 Depends on"
        )

        if analysis[
            "project_dependencies"
        ]:

            for dependency in analysis[
                "project_dependencies"
            ]:

                st.write(
                    f"→ `{dependency}`"
                )

        else:

            st.caption(
                "No project-level dependencies."
            )

    with relation_col2:

        st.markdown(
            "### 📤 Used by"
        )

        if analysis[
            "dependents"
        ]:

            for dependent in analysis[
                "dependents"
            ]:

                st.write(
                    f"← `{dependent}`"
                )

        else:

            st.caption(
                "No direct project dependents."
            )

    if (
        analysis["project_dependencies"]
        or analysis["dependents"]
    ):

        st.markdown(
            "### 🗺️ Relationship Map"
        )

        graph = build_relationship_graph(
            selected_file,
            analysis[
                "project_dependencies"
            ],
            analysis[
                "dependents"
            ]
        )

        st.graphviz_chart(
            graph,
            use_container_width=True
        )

    st.divider()

    # ========================================================
    # FUNCTION INTELLIGENCE
    # ========================================================

    st.subheader(
        "⚙️ Function Intelligence"
    )

    if analysis["functions"]:

        for function in analysis[
            "functions"
        ]:

            with st.expander(
                f"`{function['name']}()` "
                f"• line {function['line']}"
            ):

                if function["docstring"]:

                    st.write(
                        function["docstring"]
                    )

                else:

                    st.caption(
                        "No docstring found."
                    )

                if function["calls"]:

                    st.write(
                        "Calls:"
                    )

                    for call in function[
                        "calls"
                    ]:

                        st.write(
                            f"→ `{call}()`"
                        )

                callers = find_function_callers(
                    selected_file,
                    function["name"]
                )

                st.write(
                    "Detected callers:"
                )

                if callers:

                    for caller in callers:

                        st.write(
                            f"← `{caller}`"
                        )

                else:

                    st.caption(
                        "No callers detected automatically."
                    )

    else:

        st.info(
            "No functions detected."
        )

    st.divider()

    # ========================================================
    # DEPENDENCIES
    # ========================================================

    st.subheader(
        "📦 Dependencies"
    )

    dependency_col1, dependency_col2 = (
        st.columns(2)
    )

    with dependency_col1:

        st.markdown(
            "### 🏠 Project"
        )

        if analysis[
            "project_dependencies"
        ]:

            for dependency in analysis[
                "project_dependencies"
            ]:

                st.write(
                    f"• `{dependency}`"
                )

        else:

            st.caption(
                "None detected."
            )

    with dependency_col2:

        st.markdown(
            "### 🌐 External"
        )

        if analysis[
            "external_dependencies"
        ]:

            for dependency in analysis[
                "external_dependencies"
            ]:

                st.write(
                    f"• `{dependency}`"
                )

        else:

            st.caption(
                "None detected."
            )

    if analysis[
        "standard_library"
    ]:

        with st.expander(
            "🐍 Standard library imports"
        ):

            st.write(
                ", ".join(
                    f"`{item}`"
                    for item in analysis[
                        "standard_library"
                    ]
                )
            )

    st.divider()

    # ========================================================
    # TEST INTELLIGENCE
    # ========================================================

    st.subheader(
        "🧪 Related Tests"
    )

    if analysis[
        "related_tests"
    ]:

        st.success(
            f"{len(analysis['related_tests'])} "
            "related test file(s) detected."
        )

        for test_file in analysis[
            "related_tests"
        ]:

            st.write(
                f"🧪 `{test_file}`"
            )

    else:

        st.info(
            "No related test file was detected automatically."
        )

    st.divider()

    # ========================================================
    # COMPLEXITY
    # ========================================================

    st.subheader(
        "📐 Structural Complexity"
    )

    complexity_col1, complexity_col2 = (
        st.columns(2)
    )

    with complexity_col1:

        st.metric(
            "Complexity",
            analysis[
                "complexity_label"
            ]
        )

    with complexity_col2:

        st.metric(
            "Control-flow points",
            analysis[
                "complexity_score"
            ]
        )

    st.caption(
        "Based on structural control-flow constructs "
        "such as conditions, loops, and exception handling."
    )

    st.divider()

    # ========================================================
    # BEFORE YOU EDIT
    # ========================================================

    st.subheader(
        "💡 Before You Edit"
    )

    for recommendation in analysis[
        "recommendations"
    ]:

        st.info(
            f"💡 {recommendation}"
        )

    st.divider()

    st.caption(
        "GitSense Code Intelligence • "
        "Explain Before You Edit"
    )