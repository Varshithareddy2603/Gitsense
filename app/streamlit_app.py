import os
import sys
import html
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import streamlit.components.v1 as components
from app.repository_service import (
    get_repository_summary,
    get_repository_files,
    get_all_repository_files,
    get_source_code,
    get_readme,
    get_recent_commits,
    get_file_statistics
)

from app.code_intelligence import render_code_intelligence
# ============================================================
# Get Language From File
# ============================================================

def get_language_from_file(filename):

    if "." not in filename:
        return "text"

    extension = filename.rsplit(
        ".",
        1
    )[1].lower()

    language_map = {
        "py": "python",
        "js": "javascript",
        "jsx": "javascript",
        "ts": "typescript",
        "tsx": "typescript",
        "java": "java",
        "c": "c",
        "cpp": "cpp",
        "h": "c",
        "hpp": "cpp",
        "cs": "csharp",
        "html": "html",
        "css": "css",
        "json": "json",
        "xml": "xml",
        "sql": "sql",
        "md": "markdown",
        "yaml": "yaml",
        "yml": "yaml",
        "sh": "bash",
        "bat": "batch",
        "txt": "text"
    }

    return language_map.get(
        extension,
        "text"
    )


# ============================================================
# Open Source File
# ============================================================

def open_source_file(file_path, line_number=None):

    try:

        source_code = get_source_code(
            st.session_state.username,
            st.session_state.repository,
            file_path
        )

        st.session_state.selected_file = file_path

        st.session_state.source_code = source_code

        st.session_state.selected_line = line_number

        # Create a NEW scroll event every time Open is clicked.
        st.session_state.scroll_id += 1

        st.session_state.scroll_to_code = True

        st.rerun()

    except Exception as e:

        st.error(
            f"Unable to load file: {e}"
        )


# ============================================================
# Search Mode Change Handler
# ============================================================

def switch_search_mode():

    mode = st.session_state.repository_search_mode

    if mode == "🔎 Code Search":

        st.session_state.repository_file_search = ""

        st.session_state.selected_file = None

        st.session_state.source_code = None

        st.session_state.selected_line = None

        st.session_state.scroll_to_code = False

        st.session_state.code_search_results = []

        st.session_state.code_search_match_index = 0

        st.session_state.last_code_search_query = ""

    else:

        st.session_state.code_search_query = ""

        st.session_state.selected_file = None

        st.session_state.source_code = None

        st.session_state.selected_line = None

        st.session_state.scroll_to_code = False

        st.session_state.code_search_results = []

        st.session_state.code_search_match_index = 0

        st.session_state.last_code_search_query = ""


# ============================================================
# Session State
# ============================================================

if "repository_analyzed" not in st.session_state:
    st.session_state.repository_analyzed = False

if "summary" not in st.session_state:
    st.session_state.summary = None

if "username" not in st.session_state:
    st.session_state.username = ""

if "repository" not in st.session_state:
    st.session_state.repository = ""

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

if "source_code" not in st.session_state:
    st.session_state.source_code = None

if "scroll_to_code" not in st.session_state:
    st.session_state.scroll_to_code = False

if "selected_line" not in st.session_state:
    st.session_state.selected_line = None

if "scroll_id" not in st.session_state:
    st.session_state.scroll_id = 0

if "readme" not in st.session_state:
    st.session_state.readme = None

if "commits" not in st.session_state:
    st.session_state.commits = []

if "show_all_commits" not in st.session_state:
    st.session_state.show_all_commits = False

if "file_statistics" not in st.session_state:
    st.session_state.file_statistics = {}

if "repository_file_search" not in st.session_state:
    st.session_state.repository_file_search = ""

if "code_search_query" not in st.session_state:
    st.session_state.code_search_query = ""

if "search_mode" not in st.session_state:
    st.session_state.search_mode = "file"

if "repository_search_mode" not in st.session_state:
    st.session_state.repository_search_mode = "📂 File Explorer"

# ============================================================
# NEW CODE SEARCH NAVIGATION STATE
# ============================================================

if "code_search_results" not in st.session_state:
    st.session_state.code_search_results = []

if "code_search_match_index" not in st.session_state:
    st.session_state.code_search_match_index = 0

if "last_code_search_query" not in st.session_state:
    st.session_state.last_code_search_query = ""


# ============================================================
# Page Configuration
# ============================================================

st.set_page_config(
    page_title="GitSense",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# Title
# ============================================================

st.title("📊 GitSense")

st.write(
    "Analyze GitHub repositories and explore "
    "their structure, source code, README, "
    "commits, and file statistics."
)


# ============================================================
# Repository Input
# ============================================================

col1, col2 = st.columns(2)

with col1:

    username = st.text_input(
        "GitHub Username",
        value=st.session_state.username,
        placeholder="Enter GitHub username"
    )

with col2:

    repository = st.text_input(
        "Repository Name",
        value=st.session_state.repository,
        placeholder="Example: GitSense"
    )


# ============================================================
# Analyze Repository
# ============================================================

if st.button(
    "🔍 Analyze Repository",
    key="analyze_repository"
):

    if not username or not repository:

        st.warning(
            "Please enter both GitHub username "
            "and repository name."
        )

    else:

        with st.spinner(
            "Analyzing repository..."
        ):

            try:

                summary = get_repository_summary(
                    username,
                    repository
                )

                readme = get_readme(
                    username,
                    repository
                )

                commits = get_recent_commits(
                    username,
                    repository
                )

                file_statistics = get_file_statistics(
                    username,
                    repository
                )

                st.session_state.repository_analyzed = True

                st.session_state.summary = summary

                st.session_state.username = username

                st.session_state.repository = repository

                st.session_state.readme = readme

                st.session_state.commits = commits or []

                st.session_state.file_statistics = (
                    file_statistics or {}
                )

                st.session_state.show_all_commits = False

                st.session_state.selected_file = None

                st.session_state.source_code = None

                st.session_state.scroll_to_code = False

                st.session_state.selected_line = None

                st.session_state.scroll_id += 1

                st.session_state.repository_file_search = ""

                st.session_state.code_search_query = ""

                st.session_state.search_mode = "file"

                st.session_state.repository_search_mode = (
                    "📂 File Explorer"
                )

                # Reset code search navigation
                st.session_state.code_search_results = []

                st.session_state.code_search_match_index = 0

                st.session_state.last_code_search_query = ""

                st.success(
                    "Repository analyzed successfully!"
                )

            except Exception as e:

                st.error(
                    f"Error analyzing repository: {e}"
                )


# ============================================================
# Display Repository
# ============================================================

if st.session_state.repository_analyzed:

    summary = st.session_state.summary

    username = st.session_state.username

    repository = st.session_state.repository


    # ========================================================
    # Repository Header
    # ========================================================

    st.header(
        f"📦 {summary['name']}"
    )

    if summary["description"]:

        st.write(
            summary["description"]
        )

    else:

        st.write(
            "No repository description available."
        )


    # ========================================================
    # Main Statistics
    # ========================================================

    st.subheader(
        "📈 Repository Statistics"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "⭐ Stars",
            summary["stars"]
        )

    with col2:

        st.metric(
            "🍴 Forks",
            summary["forks"]
        )

    with col3:

        st.metric(
            "👁 Watchers",
            summary["watchers"]
        )

    with col4:

        st.metric(
            "🐛 Open Issues",
            summary["open_issues"]
        )


    # ========================================================
    # Repository Information
    # ========================================================

    st.subheader(
        "ℹ️ Repository Information"
    )

    info_col1, info_col2 = st.columns(2)

    with info_col1:

        st.write(
            f"**Primary Language:** "
            f"{summary['language'] or 'Not specified'}"
        )

        st.write(
            f"**Default Branch:** "
            f"{summary['default_branch']}"
        )

        st.write(
            f"**Visibility:** "
            f"{summary['visibility']}"
        )

        st.write(
            f"**Repository Size:** "
            f"{summary['size']} KB"
        )

    with info_col2:

        st.write(
            f"**Created:** "
            f"{summary['created_at']}"
        )

        st.write(
            f"**Last Updated:** "
            f"{summary['updated_at']}"
        )

        st.write(
            f"**Full Name:** "
            f"{summary['full_name']}"
        )

        if summary["html_url"]:

            st.markdown(
                f"[🔗 Open Repository on GitHub]"
                f"({summary['html_url']})"
            )


    # ========================================================
    # Repository Overview
    # ========================================================

    st.subheader(
        "📊 Repository Overview"
    )

    overview_statistics = (
        st.session_state.file_statistics
    )

    if overview_statistics:

        total_files = sum(
            overview_statistics.values()
        )

        total_file_types = len(
            overview_statistics
        )

        most_common_type = max(
            overview_statistics,
            key=overview_statistics.get
        )

        most_common_count = (
            overview_statistics[
                most_common_type
            ]
        )

        overview_col1, overview_col2, overview_col3 = (
            st.columns(3)
        )

        with overview_col1:

            st.metric(
                "📁 Total Files",
                total_files
            )

        with overview_col2:

            st.metric(
                "🔤 File Types",
                total_file_types
            )

        with overview_col3:

            st.metric(
                "🏆 Most Common Type",
                most_common_type,
                f"{most_common_count} files"
            )

    else:

        st.info(
            "Repository overview data is not available."
        )


    # ========================================================
    # Repository Health Dashboard
    # ========================================================

    st.subheader(
        "🩺 Repository Health Dashboard"
    )

    health_col1, health_col2, health_col3 = (
        st.columns(3)
    )

    with health_col1:

        if summary["description"]:

            st.success(
                "✅ Description available"
            )

        else:

            st.warning(
                "⚠️ No description"
            )

        if st.session_state.readme:

            st.success(
                "✅ README available"
            )

        else:

            st.warning(
                "⚠️ README missing"
            )

    with health_col2:

        if summary["language"]:

            st.success(
                f"✅ Language: {summary['language']}"
            )

        else:

            st.warning(
                "⚠️ Language not specified"
            )

        if summary["default_branch"]:

            st.success(
                f"🌿 Branch: {summary['default_branch']}"
            )

    with health_col3:

        if summary["open_issues"] == 0:

            st.success(
                "✅ No open issues"
            )

        else:

            st.warning(
                f"⚠️ {summary['open_issues']} open issues"
            )

        if st.session_state.commits:

            st.success(
                "✅ Commit history available"
            )

        else:

            st.warning(
                "⚠️ No commits found"
            )

    st.divider()


    # ========================================================
    # File Statistics
    # ========================================================

    st.subheader(
        "📊 File Statistics"
    )

    file_statistics = (
        st.session_state.file_statistics
    )

    if file_statistics:

        sorted_statistics = dict(
            sorted(
                file_statistics.items(),
                key=lambda item: item[1],
                reverse=True
            )
        )

        total_files = sum(
            sorted_statistics.values()
        )

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "📁 Total Files",
                total_files
            )

        with col2:

            st.metric(
                "🔤 File Types",
                len(sorted_statistics)
            )

        st.write(
            "Number of files grouped by "
            "programming language or file type:"
        )

        for language, count in (
            sorted_statistics.items()
        ):

            file_word = (
                "file"
                if count == 1
                else "files"
            )

            st.write(
                f"**{language}** — "
                f"{count} {file_word}"
            )

        st.write(
            "### 📈 File Type Distribution"
        )

        chart_data = {
            "File Type": list(
                sorted_statistics.keys()
            ),
            "Files": list(
                sorted_statistics.values()
            )
        }

        st.bar_chart(
            chart_data,
            x="File Type",
            y="Files"
        )

    else:

        st.info(
            "No file statistics available."
        )


    # ========================================================
    # README
    # ========================================================

    st.subheader(
        "📖 README"
    )

    readme = st.session_state.readme

    if readme:

        st.markdown(
            readme
        )

    else:

        st.info(
            "No README.md file found."
        )


    # ========================================================
    # Commits
    # ========================================================

    st.subheader(
        "🕐 Recent Commits"
    )

    commits = st.session_state.get(
        "commits",
        []
    )

    if commits:

        if not st.session_state.show_all_commits:

            latest_commit = commits[0]

            st.markdown(
                f"### `{latest_commit.get('sha', 'Unknown')}`"
            )

            st.write(
                f"**{latest_commit.get('message', 'No commit message')}**"
            )

            st.write(
                f"Author: "
                f"{latest_commit.get('author', 'Unknown')}"
            )

            st.write(
                f"Date: "
                f"{latest_commit.get('date', 'Unknown')}"
            )

            if latest_commit.get("url"):

                st.markdown(
                    f"[View Commit on GitHub]"
                    f"({latest_commit['url']})"
                )

            st.divider()

            if st.button(
                "📜 View all commits",
                key="view_all_commits"
            ):

                st.session_state.show_all_commits = True

                st.rerun()

        else:

            st.write(
                f"Showing {len(commits)} commits"
            )

            if st.button(
                "⬆️ Show latest commit",
                key="show_latest_commit"
            ):

                st.session_state.show_all_commits = False

                st.rerun()

            st.divider()

            for commit in commits:

                st.markdown(
                    f"### `{commit.get('sha', 'Unknown')}`"
                )

                st.write(
                    f"**{commit.get('message', 'No commit message')}**"
                )

                st.write(
                    f"Author: "
                    f"{commit.get('author', 'Unknown')}"
                )

                st.write(
                    f"Date: "
                    f"{commit.get('date', 'Unknown')}"
                )

                if commit.get("url"):

                    st.markdown(
                        f"[View Commit on GitHub]"
                        f"({commit['url']})"
                    )

                st.divider()

    else:

        st.info(
            "No recent commits are available."
        )


    # ========================================================
    # Repository Search
    # ========================================================

    st.subheader(
        "🔎 Repository Search"
    )

    st.write(
        "Choose a search mode:"
    )


    # ========================================================
    # Search Mode Selection
    # ========================================================

    selected_mode = st.radio(
        "Search mode",
        [
            "📂 File Explorer",
            "🔎 Code Search"
        ],
        horizontal=True,
        key="repository_search_mode",
        on_change=switch_search_mode
    )


    # ========================================================
    # FILE EXPLORER MODE
    # ========================================================

    if selected_mode == "📂 File Explorer":

        st.subheader(
            "📂 Repository File Explorer"
        )

        try:

            all_files = get_all_repository_files(
                username,
                repository
            )

            if all_files:

                search_col, filter_col = st.columns(2)

                with search_col:

                    search_text = st.text_input(
                        "🔎 Search files",
                        placeholder=(
                            "Example: github_api.py"
                        ),
                        key="repository_file_search"
                    )

                with filter_col:

                    file_types = sorted(
                        set(
                            get_language_from_file(
                                file["path"]
                            )
                            for file in all_files
                        )
                    )

                    selected_type = st.selectbox(
                        "🔤 Filter by file type",
                        ["All"] + file_types,
                        key="repository_file_type"
                    )

                filtered_files = all_files

                if search_text:

                    filtered_files = [

                        file

                        for file in filtered_files

                        if search_text.lower()
                        in file["path"].lower()

                    ]

                if selected_type != "All":

                    filtered_files = [

                        file

                        for file in filtered_files

                        if get_language_from_file(
                            file["path"]
                        ) == selected_type

                    ]

                st.write(
                    f"Showing "
                    f"**{len(filtered_files)}** "
                    f"of "
                    f"**{len(all_files)} files**"
                )

                if not filtered_files:

                    st.info(
                        "No files match your search/filter."
                    )

                for file in filtered_files:

                    file_path = file["path"]

                    file_language = (
                        get_language_from_file(
                            file_path
                        )
                    )

                    if st.button(
                        f"📄 {file_path}  •  {file_language}",
                        key=f"file_{file_path}"
                    ):

                        open_source_file(
                            file_path
                        )

            else:

                st.info(
                    "No files found."
                )

        except Exception as e:

            st.error(
                f"Unable to load repository files: {e}"
            )


    # ========================================================
    # CODE SEARCH MODE
    # ========================================================

    else:

        st.subheader(
            "🔎 Repository Code Search"
        )

        search_query = st.text_input(
            "Search inside repository source code",
            placeholder=(
                "Example: def, import, "
                "st.session_state, streamlit"
            ),
            key="code_search_query"
        )

        # ----------------------------------------------------
        # Detect New Search Query
        # ----------------------------------------------------

        if (
            search_query
            != st.session_state.last_code_search_query
        ):

            st.session_state.code_search_results = []

            st.session_state.code_search_match_index = 0

            st.session_state.last_code_search_query = (
                search_query
            )

        # ----------------------------------------------------
        # Perform Code Search
        # ----------------------------------------------------

        if search_query:

            # Only perform the expensive GitHub search
            # when results are not already stored for
            # this exact query.
            if not st.session_state.code_search_results:

                with st.spinner(
                    "Searching repository code..."
                ):

                    search_results = []

                    all_code_files = (
                        get_all_repository_files(
                            st.session_state.username,
                            st.session_state.repository
                        )
                    )

                    code_extensions = (
                        ".py",
                        ".js",
                        ".jsx",
                        ".ts",
                        ".tsx",
                        ".java",
                        ".c",
                        ".cpp",
                        ".h",
                        ".hpp",
                        ".cs",
                        ".html",
                        ".css",
                        ".sql",
                        ".sh",
                        ".bat"
                    )

                    for file_item in all_code_files:

                        if isinstance(
                            file_item,
                            dict
                        ):

                            file_path = (
                                file_item.get("path")
                                or file_item.get("name")
                                or ""
                            )

                        else:

                            file_path = str(
                                file_item
                            )

                        if not file_path:
                            continue

                        if not file_path.lower().endswith(
                            code_extensions
                        ):
                            continue

                        try:

                            source_code = get_source_code(
                                st.session_state.username,
                                st.session_state.repository,
                                file_path
                            )

                            if not source_code:
                                continue

                            lines = source_code.splitlines()

                            for line_number, line in enumerate(
                                lines,
                                start=1
                            ):

                                if (
                                    search_query.lower()
                                    in line.lower()
                                ):

                                    search_results.append(
                                        {
                                            "file": file_path,
                                            "line": line_number,
                                            "code": line.strip()
                                        }
                                    )

                        except Exception:

                            continue

                    st.session_state.code_search_results = (
                        search_results
                    )

                    st.session_state.code_search_match_index = 0

            # ------------------------------------------------
            # Display Results
            # ------------------------------------------------

            search_results = (
                st.session_state.code_search_results
            )

            if search_results:

                total_matches = len(
                    search_results
                )

                # Make sure the index is always valid.
                if (
                    st.session_state.code_search_match_index
                    < 0
                ):

                    st.session_state.code_search_match_index = (
                        0
                    )

                if (
                    st.session_state.code_search_match_index
                    >= total_matches
                ):

                    st.session_state.code_search_match_index = (
                        total_matches - 1
                    )

                current_match_index = (
                    st.session_state.code_search_match_index
                )

                current_match = (
                    search_results[
                        current_match_index
                    ]
                )

                # ------------------------------------------------
                # Search Summary
                # ------------------------------------------------

                st.success(
                    f"Found "
                    f"{total_matches} "
                    f"matching line(s)."
                )

                # ------------------------------------------------
                # Navigation
                # ------------------------------------------------

                st.markdown(
                    "### 🔎 Search Result Navigation"
                )

                nav_col1, nav_col2, nav_col3, nav_col4 = (
                    st.columns(
                        [1, 1, 2, 2]
                    )
                )

                with nav_col1:

                    previous_clicked = st.button(
                        "⬆️ Previous",
                        key="code_search_previous"
                    )

                with nav_col2:

                    next_clicked = st.button(
                        "⬇️ Next",
                        key="code_search_next"
                    )

                with nav_col3:

                    st.markdown(
                        f"""
                        <div style="
                            padding-top: 8px;
                            text-align: center;
                            font-weight: 600;
                        ">
                            Match
                            {current_match_index + 1}
                            of
                            {total_matches}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with nav_col4:

                    if st.button(
                        "📂 Open Current Match",
                        key="open_current_code_match"
                    ):

                        open_source_file(
                            current_match["file"],
                            current_match["line"]
                        )

                # ------------------------------------------------
                # Handle Previous
                # ------------------------------------------------

                if previous_clicked:

                    if current_match_index > 0:

                        st.session_state.code_search_match_index = (
                            current_match_index - 1
                        )

                    else:

                        st.session_state.code_search_match_index = (
                            total_matches - 1
                        )

                    st.rerun()

                # ------------------------------------------------
                # Handle Next
                # ------------------------------------------------

                if next_clicked:

                    if current_match_index < (
                        total_matches - 1
                    ):

                        st.session_state.code_search_match_index = (
                            current_match_index + 1
                        )

                    else:

                        st.session_state.code_search_match_index = (
                            0
                        )

                    st.rerun()

                st.divider()

                # ------------------------------------------------
                # Current Match Preview
                # ------------------------------------------------

                st.info(
                    f"Current match: "
                    f"**{current_match['file']}** "
                    f"— Line "
                    f"**{current_match['line']}**"
                )

                # ------------------------------------------------
                # Display All Search Results
                # ------------------------------------------------

                for index, result in enumerate(
                    search_results
                ):

                    result_col1, result_col2 = (
                        st.columns([5, 1])
                    )

                    with result_col1:

                        if index == current_match_index:

                            st.markdown(
                                f"""
                                <div style="
                                    padding: 8px;
                                    border-left: 4px solid #ffc107;
                                    background: rgba(255,193,7,0.12);
                                    border-radius: 4px;
                                    margin-bottom: 8px;
                                ">
                                    <b>📍 Current Match</b>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                        st.markdown(
                            f"**📄 {result['file']} "
                            f"— Line {result['line']}**"
                        )

                        st.code(
                            result["code"],
                            language=get_language_from_file(
                                result["file"]
                            )
                        )

                    with result_col2:

                        st.write("")

                        if st.button(
                            "📂 Open",
                            key=(
                                f"open_search_result_"
                                f"{index}_"
                                f"{result['file']}_"
                                f"{result['line']}"
                            )
                        ):

                            # Keep navigation position
                            # synchronized with the opened result.
                            st.session_state.code_search_match_index = (
                                index
                            )

                            open_source_file(
                                result["file"],
                                result["line"]
                            )

                    st.markdown("---")

            else:

                st.warning(
                    f'No matches found for '
                    f'"{search_query}".'
                )


    # ========================================================
    # Source Code Viewer
    # ========================================================

    if (
        st.session_state.selected_file
        and st.session_state.source_code
    ):

        st.divider()

        # ----------------------------------------------------
        # Unique Source Code Anchor
        # ----------------------------------------------------

        st.markdown(
            f"""
            <div
                id="source-code-section-{st.session_state.scroll_id}"
                style="
                    scroll-margin-top: 30px;
                    height: 1px;
                ">
            </div>
            """,
            unsafe_allow_html=True
        )

        st.subheader(
            "💻 Source Code"
        )

        # ----------------------------------------------------
        # Selected Search Line
        # ----------------------------------------------------

        if st.session_state.selected_line:

            st.info(
                f"🔎 Search match found at "
                f"**line {st.session_state.selected_line}**"
            )

        # ----------------------------------------------------
        # Automatic Page Scroll
        # ----------------------------------------------------

        if st.session_state.scroll_to_code:

            current_scroll_id = (
                st.session_state.scroll_id
            )

            components.html(
                f"""
                <script>
                (function() {{

                    const scrollId =
                        {current_scroll_id};

                    function moveToSourceCode() {{

                        try {{

                            const parentDocument =
                                window.parent.document;

                            const sourceSection =
                                parentDocument.getElementById(
                                    "source-code-section-" +
                                    scrollId
                                );

                            if (!sourceSection) {{
                                return false;
                            }}

                            sourceSection.scrollIntoView({{
                                behavior: "smooth",
                                block: "start",
                                inline: "nearest"
                            }});

                            return true;

                        }} catch (error) {{

                            return false;
                        }}
                    }}


                    /*
                     * The unique scroll ID makes this a
                     * completely new DOM target on every
                     * Open click.
                     */
                    setTimeout(
                        function() {{
                            moveToSourceCode();
                        }},
                        350
                    );

                }})();
                </script>
                """,
                height=1
            )

            st.session_state.scroll_to_code = False

        # ----------------------------------------------------
        # Selected File
        # ----------------------------------------------------

        st.write(
            f"File: "
            f"**{st.session_state.selected_file}**"
        )

        # ----------------------------------------------------
        # Programming Language
        # ----------------------------------------------------

        language = get_language_from_file(
            st.session_state.selected_file
        )

        # ----------------------------------------------------
        # Prepare Code
        # ----------------------------------------------------

        source_lines = (
            st.session_state.source_code.splitlines()
        )

        selected_line = (
            st.session_state.selected_line
        )

        code_html_parts = []

        for line_number, line in enumerate(
            source_lines,
            start=1
        ):

            escaped_line = html.escape(
                line
            )

            if line_number == selected_line:

                line_class = (
                    "git-sense-code-line "
                    "git-sense-selected-line"
                )

            else:

                line_class = (
                    "git-sense-code-line"
                )

            code_html_parts.append(
                f"""
                <div
                    id="source-code-line-{line_number}"
                    class="{line_class}">
                    <span
                        class="git-sense-line-number">
                        {line_number}
                    </span>
                    <span
                        class="git-sense-line-code">
                        {escaped_line}
                    </span>
                </div>
                """
            )

        code_html = "".join(
            code_html_parts
        )

        # ----------------------------------------------------
        # Code Viewer
        # ----------------------------------------------------

        components.html(
            f"""
            <style>

                .git-sense-code-container {{
                    background: #0e1117;
                    border: 1px solid
                        rgba(250, 250, 250, 0.2);
                    border-radius: 0.5rem;
                    padding: 12px 0;
                    overflow-x: auto;
                    overflow-y: auto;
                    width: 100%;
                    height: 650px;
                    box-sizing: border-box;
                    font-family:
                        "Source Code Pro",
                        "Consolas",
                        "Monaco",
                        monospace;
                    font-size: 14px;
                    line-height: 1.5;
                }}

                .git-sense-code-line {{
                    display: flex;
                    min-height: 21px;
                    width: max-content;
                    min-width: 100%;
                    box-sizing: border-box;
                    padding-right: 20px;
                }}

                .git-sense-code-line:hover {{
                    background: rgba(
                        255,
                        255,
                        255,
                        0.04
                    );
                }}

                .git-sense-selected-line {{
                    background: rgba(
                        255,
                        193,
                        7,
                        0.30
                    ) !important;

                    border-left: 4px solid
                        #ffc107;
                }}

                .git-sense-line-number {{
                    display: inline-block;
                    width: 60px;
                    min-width: 60px;
                    padding-right: 15px;
                    text-align: right;
                    color: #8b949e;
                    user-select: none;
                    box-sizing: border-box;
                }}

                .git-sense-selected-line
                .git-sense-line-number {{
                    color: #ffc107;
                    font-weight: bold;
                }}

                .git-sense-line-code {{
                    white-space: pre;
                    color: #e6edf3;
                }}

            </style>

            <div
                id="git-sense-code-container"
                class="git-sense-code-container">

                {code_html}

            </div>

            <script>

                const selectedLine =
                    {selected_line or 0};


                function scrollInsideCode() {{

                    if (selectedLine <= 0) {{
                        return false;
                    }}

                    const lineElement =
                        document.getElementById(
                            "source-code-line-" +
                            selectedLine
                        );

                    const codeContainer =
                        document.getElementById(
                            "git-sense-code-container"
                        );

                    if (
                        !lineElement ||
                        !codeContainer
                    ) {{
                        return false;
                    }}

                    const lineTop =
                        lineElement.offsetTop;

                    const lineHeight =
                        lineElement.offsetHeight;

                    const containerHeight =
                        codeContainer.clientHeight;

                    const targetScroll =
                        lineTop -
                        (containerHeight / 2) +
                        (lineHeight / 2);

                    codeContainer.scrollTo({{
                        top: Math.max(
                            targetScroll,
                            0
                        ),
                        behavior: "smooth"
                    }});

                    return true;
                }}


                /*
                 * Move to the matching line inside
                 * the code viewer.
                 */
                setTimeout(
                    function() {{
                        scrollInsideCode();
                    }},
                    400
                );

            </script>
            """,
            height=680,
            scrolling=False
        )
# ============================================================
# CODE INTELLIGENCE
# ============================================================

st.divider()

render_code_intelligence()
