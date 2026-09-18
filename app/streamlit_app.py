import streamlit as st
import streamlit.components.v1 as components

from app.repository_service import (
    get_repository_summary,
    get_repository_files,
    get_all_repository_files,
    get_source_code,
    get_readme,
    get_recent_commits
)


# --------------------------------
# Language Detection
# --------------------------------

def get_language_from_file(filename):

    extension = filename.lower().split(".")[-1]

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
    st.session_state.commits = None


# --------------------------------
# Page
# --------------------------------

st.title("🔍 GitSense")

st.write(
    "Analyze a GitHub repository and explore its key statistics."
)


# --------------------------------
# Inputs
# --------------------------------

username = st.text_input(
    "GitHub Username",
    value=st.session_state.username,
    placeholder="e.g. Varshithareddy2603"
)

repository = st.text_input(
    "Repository Name",
    value=st.session_state.repository,
    placeholder="e.g. GitSense"
)


# --------------------------------
# Analyze Repository
# --------------------------------

if st.button(
    "Analyze Repository",
    key="analyze_repository"
):

    if not username or not repository:

        st.warning(
            "Please enter both username and repository name."
        )

    else:

        try:

            summary = get_repository_summary(
                username,
                repository
            )

            st.session_state.repository_analyzed = True
            st.session_state.summary = summary
            st.session_state.username = username
            st.session_state.repository = repository

            st.session_state.selected_file = None
            st.session_state.source_code = None
            st.session_state.scroll_to_code = False
            st.session_state.readme = None
            st.session_state.commits = None

            st.rerun()

        except Exception as error:

            st.error(
                f"Something went wrong: {error}"
            )


# --------------------------------
# Repository Display
# --------------------------------

if st.session_state.repository_analyzed:

    summary = st.session_state.summary

    username = st.session_state.username
    repository = st.session_state.repository


    # ========================================
    # Repository Summary
    # ========================================

    st.success("Repository found!")

    st.subheader(
        summary["name"]
    )

    st.write(
        summary["description"]
        or "No description available."
    )


    # ========================================
    # Statistics
    # ========================================

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
            "🐛 Open Issues",
            summary["open_issues"]
        )

    with col4:

        st.metric(
            "👀 Watchers",
            summary["watchers"]
        )


    st.divider()


    # ========================================
    # Repository Information
    # ========================================

    st.subheader(
        "📊 Repository Information"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write("**💻 Language**")

        st.write(
            summary["language"]
            or "Not specified"
        )

    with col2:

        st.write("**📦 Size**")

        st.write(
            f'{summary["size"]} KB'
        )

    with col3:

        st.write("**📅 Created**")

        st.write(
            summary["created_at"][:10]
        )


    st.write("**🔄 Last Updated**")

    st.write(
        summary["updated_at"][:10]
    )


    st.markdown(
        f"[🔗 Open repository on GitHub]"
        f"({summary['html_url']})"
    )


    # ========================================
    # README
    # ========================================

    st.divider()

    st.subheader("📖 README")

    try:

        if st.session_state.readme is None:

            with st.spinner("Loading README..."):

                st.session_state.readme = get_readme(
                    username,
                    repository
                )


        if st.session_state.readme:

            st.markdown(
                st.session_state.readme
            )

        else:

            st.info(
                "No README.md file found in this repository."
            )

    except Exception as error:

        st.warning(
            f"Could not load README: {error}"
        )


    # ========================================
    # Recent Commits
    # ========================================

    st.divider()

    st.subheader(
        "📜 Recent Commits"
    )

    try:

        if st.session_state.commits is None:

            with st.spinner(
                "Loading recent commits..."
            ):

                st.session_state.commits = (
                    get_recent_commits(
                        username,
                        repository,
                        10
                    )
                )


        commits = st.session_state.commits


        if not commits:

            st.info(
                "No commits found."
            )

        else:

            for commit in commits:

                st.markdown(
                    f"### 📝 {commit['message']}"
                )

                st.write(
                    f"👤 **Author:** "
                    f"{commit['author']}"
                )

                if commit["date"]:

                    st.write(
                        f"📅 **Date:** "
                        f"{commit['date'][:10]}"
                    )

                st.write(
                    f"🔑 **Commit:** "
                    f"`{commit['sha']}`"
                )

                if commit["url"]:

                    st.markdown(
                        f"[🔗 View commit on GitHub]"
                        f"({commit['url']})"
                    )

                st.divider()


    except Exception as error:

        st.warning(
            f"Could not load commits: {error}"
        )


    # ========================================
    # Repository Files
    # ========================================

    st.subheader(
        "📁 Repository Files"
    )


    # --------------------------------
    # File Search
    # --------------------------------

    search_text = st.text_input(
        "🔎 Search files",
        placeholder="Search by file name..."
    )


    try:

        # ========================================
        # SEARCH MODE
        # ========================================

        if search_text:

            st.caption(
                "Searching all files and folders..."
            )

            all_files = get_all_repository_files(
                username,
                repository
            )

            search_lower = search_text.lower()

            matching_files = [
                file
                for file in all_files
                if (
                    search_lower in file["name"].lower()
                    or search_lower in file["path"].lower()
                )
            ]


            if not matching_files:

                st.info(
                    f'No files found matching "{search_text}".'
                )

            else:

                st.write(
                    f"**Found {len(matching_files)} file(s)**"
                )

                for file in matching_files:

                    if st.button(
                        f"📄 {file['path']}",
                        key=f"search_file_{file['path']}"
                    ):

                        source_code = get_source_code(
                            username,
                            repository,
                            file["path"]
                        )

                        st.session_state.selected_file = (
                            file["path"]
                        )

                        st.session_state.source_code = (
                            source_code
                        )

                        st.session_state.scroll_to_code = True

                        st.rerun()


        # ========================================
        # NORMAL FOLDER BROWSING
        # ========================================

        else:

            files = get_repository_files(
                username,
                repository
            )


            if not files:

                st.info(
                    "No files found."
                )


            for file in files:

                # --------------------------------
                # Folder
                # --------------------------------

                if file["type"] == "dir":

                    with st.expander(
                        f"📂 {file['name']}"
                    ):

                        folder_files = get_repository_files(
                            username,
                            repository,
                            file["path"]
                        )


                        for folder_file in folder_files:

                            if folder_file["type"] == "dir":

                                st.write(
                                    f"📂 {folder_file['name']}"
                                )

                            else:

                                if st.button(
                                    f"📄 {folder_file['name']}",
                                    key=f"file_{folder_file['path']}"
                                ):

                                    source_code = get_source_code(
                                        username,
                                        repository,
                                        folder_file["path"]
                                    )

                                    st.session_state.selected_file = (
                                        folder_file["path"]
                                    )

                                    st.session_state.source_code = (
                                        source_code
                                    )

                                    st.session_state.scroll_to_code = True

                                    st.rerun()


                # --------------------------------
                # Root File
                # --------------------------------

                else:

                    if st.button(
                        f"📄 {file['name']}",
                        key=f"file_{file['path']}"
                    ):

                        source_code = get_source_code(
                            username,
                            repository,
                            file["path"]
                        )

                        st.session_state.selected_file = (
                            file["path"]
                        )

                        st.session_state.source_code = (
                            source_code
                        )

                        st.session_state.scroll_to_code = True

                        st.rerun()


    except Exception as error:

        st.error(
            f"Could not load repository files: {error}"
        )


    # ========================================
    # Source Code Viewer
    # ========================================

    if st.session_state.source_code:

        st.divider()

        st.markdown(
            '<div id="source-code"></div>',
            unsafe_allow_html=True
        )

        st.subheader(
            "💻 Source Code"
        )

        st.write(
            f"File: `{st.session_state.selected_file}`"
        )


        # --------------------------------
        # Detect Language
        # --------------------------------

        language = get_language_from_file(
            st.session_state.selected_file
        )

        st.caption(
            f"Detected language: {language}"
        )


        # --------------------------------
        # Display Code
        # --------------------------------

        st.code(
            st.session_state.source_code,
            language=language
        )


        # --------------------------------
        # Automatic Scroll
        # --------------------------------

        if st.session_state.scroll_to_code:

            components.html(
                """
                <script>

                setTimeout(function() {

                    const parentDocument =
                        window.parent.document;

                    const sourceCode =
                        parentDocument.getElementById(
                            "source-code"
                        );

                    if (sourceCode) {

                        sourceCode.scrollIntoView({
                            behavior: "smooth",
                            block: "start"
                        });

                    } else {

                        window.parent.scrollTo({
                            top:
                                parentDocument.body.scrollHeight,
                            behavior: "smooth"
                        });

                    }

                }, 1000);

                </script>
                """,
                height=1
            )

            st.session_state.scroll_to_code = False
            