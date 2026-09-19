
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


# --------------------------------
# Get Language From File
# --------------------------------

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


# --------------------------------
# Session State
# --------------------------------

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

if "readme" not in st.session_state:
    st.session_state.readme = None

if "commits" not in st.session_state:
    st.session_state.commits = []

if "show_all_commits" not in st.session_state:
    st.session_state.show_all_commits = False

if "file_statistics" not in st.session_state:
    st.session_state.file_statistics = {}


# --------------------------------
# Page Configuration
# --------------------------------

st.set_page_config(
    page_title="GitSense",
    page_icon="📊",
    layout="wide"
)


# --------------------------------
# Title
# --------------------------------

st.title("📊 GitSense")

st.write(
    "Analyze GitHub repositories and explore "
    "their structure, source code, README, "
    "commits, and file statistics."
)


# --------------------------------
# Repository Input
# --------------------------------

col1, col2 = st.columns(2)

with col1:

    username = st.text_input(
        "GitHub Username",
        value=st.session_state.username,
        placeholder="Example: Varshithareddy2603"
    )

with col2:

    repository = st.text_input(
        "Repository Name",
        value=st.session_state.repository,
        placeholder="Example: GitSense"
    )


# --------------------------------
# Analyze Repository
# --------------------------------

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

                st.session_state.commits = commits

                st.session_state.file_statistics = (
                    file_statistics
                )

                # Reset commit view when analyzing
                # a new repository
                st.session_state.show_all_commits = False

                st.session_state.selected_file = None

                st.session_state.source_code = None

                st.session_state.scroll_to_code = False

                st.success(
                    "Repository analyzed successfully!"
                )

            except Exception as e:

                st.error(
                    f"Error analyzing repository: {e}"
                )


# --------------------------------
# Display Repository
# --------------------------------

if st.session_state.repository_analyzed:

    summary = st.session_state.summary

    username = st.session_state.username

    repository = st.session_state.repository


    # --------------------------------
    # Repository Header
    # --------------------------------

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


    # --------------------------------
    # Main Statistics
    # --------------------------------

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


    # --------------------------------
    # Repository Information
    # --------------------------------

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

        # --------------------------------
    # Repository Health Dashboard
    # --------------------------------

    st.subheader(
        "🩺 Repository Health Dashboard"
    )

    health_col1, health_col2, health_col3 = st.columns(3)

    with health_col1:

        if summary["description"]:
            st.success("✅ Description available")
        else:
            st.warning("⚠️ No description")

        if st.session_state.readme:
            st.success("✅ README available")
        else:
            st.warning("⚠️ README missing")

    with health_col2:

        if summary["language"]:
            st.success(
                f"✅ Language: {summary['language']}"
            )
        else:
            st.warning("⚠️ Language not specified")

        if summary["default_branch"]:
            st.success(
                f"🌿 Branch: {summary['default_branch']}"
            )

    with health_col3:

        if summary["open_issues"] == 0:
            st.success("✅ No open issues")
        else:
            st.warning(
                f"⚠️ {summary['open_issues']} open issues"
            )

        if st.session_state.commits:
            st.success("✅ Commit history available")
        else:
            st.warning("⚠️ No commits found")

    st.divider()
    # --------------------------------
    # File Statistics
    # --------------------------------

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


    # --------------------------------
    # README
    # --------------------------------

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


    # --------------------------------
    # Commits
    # --------------------------------

    st.subheader(
        "🕐 Commits"
    )

    commits = st.session_state.commits

    if commits:

        # --------------------------------
        # Latest Commit
        # --------------------------------

        if not st.session_state.show_all_commits:

            latest_commit = commits[0]

            st.markdown(
                f"### `{latest_commit['sha']}`"
            )

            st.write(
                f"**{latest_commit['message']}**"
            )

            st.write(
                f"Author: {latest_commit['author']}"
            )

            st.write(
                f"Date: {latest_commit['date']}"
            )

            if latest_commit["url"]:

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


        # --------------------------------
        # All Commits
        # --------------------------------

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
                    f"### `{commit['sha']}`"
                )

                st.write(
                    f"**{commit['message']}**"
                )

                st.write(
                    f"Author: {commit['author']}"
                )

                st.write(
                    f"Date: {commit['date']}"
                )

                if commit["url"]:

                    st.markdown(
                        f"[View Commit on GitHub]"
                        f"({commit['url']})"
                    )

                st.divider()

    else:

        st.info(
            "No commits found."
        )


        # --------------------------------
    # Repository File Explorer
    # --------------------------------

    st.subheader(
        "📂 Repository File Explorer"
    )

    try:

        all_files = get_all_repository_files(
            username,
            repository
        )

        if all_files:

            # --------------------------------
            # Search and Filter
            # --------------------------------

            search_col, filter_col = st.columns(2)

            with search_col:

                search_text = st.text_input(
                    "🔎 Search files",
                    placeholder=(
                        "Example: streamlit_app.py"
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


            # --------------------------------
            # Apply Filters
            # --------------------------------

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


            # --------------------------------
            # File Count
            # --------------------------------

            st.write(
                f"Showing "
                f"**{len(filtered_files)}** "
                f"of "
                f"**{len(all_files)}** files"
            )


            # --------------------------------
            # No Results
            # --------------------------------

            if not filtered_files:

                st.info(
                    "No files match your search/filter."
                )


            # --------------------------------
            # File List
            # --------------------------------

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

                    try:

                        source_code = (
                            get_source_code(
                                username,
                                repository,
                                file_path
                            )
                        )

                        st.session_state.selected_file = (
                            file_path
                        )

                        st.session_state.source_code = (
                            source_code
                        )

                        st.session_state.scroll_to_code = (
                            True
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            f"Unable to load file: {e}"
                        )


        else:

            st.info(
                "No files found."
            )

    except Exception as e:

        st.error(
            f"Unable to load repository files: {e}"
        )

    # --------------------------------
    # Source Code Viewer
    # --------------------------------

    if (
        st.session_state.selected_file
        and st.session_state.source_code
    ):

        st.divider()

        # --------------------------------
        # Source Code Anchor
        # --------------------------------

        st.markdown(
            """
            <div id="source-code-section"></div>
            """,
            unsafe_allow_html=True
        )

        st.subheader(
            "💻 Source Code"
        )


        # --------------------------------
        # Automatic Scroll
        # --------------------------------

        if st.session_state.scroll_to_code:

            components.html(
        """
        <script>

        function scrollToSourceCode() {

            const parentDocument =
                window.parent.document;

            const element =
                parentDocument.getElementById(
                    "source-code-section"
                );

            if (element) {

                element.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

                return true;
            }

            return false;
        }


        let attempts = 0;

        const scrollInterval = setInterval(
            function() {

                attempts++;

                const success =
                    scrollToSourceCode();

                if (
                    success ||
                    attempts >= 20
                ) {

                    clearInterval(
                        scrollInterval
                    );

                }

            },
            200
        );

        </script>
        """,
        height=1
    )

            st.session_state.scroll_to_code = False
            


        # --------------------------------
        # Selected File
        # --------------------------------

        st.write(
            f"File: "
            f"**{st.session_state.selected_file}**"
        )


        # --------------------------------
        # Detect Programming Language
        # --------------------------------

        language = get_language_from_file(
            st.session_state.selected_file
        )


        # --------------------------------
        # Display Source Code
        # --------------------------------

        st.code(
            st.session_state.source_code,
            language=language
        )

