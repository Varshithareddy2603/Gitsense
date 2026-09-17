import streamlit as st

from app.repository_service import (
    get_repository_summary,
    get_repository_files
)


st.title("🔍 GitSense")

st.write(
    "Analyze a GitHub repository and explore its key statistics."
)


username = st.text_input(
    "GitHub Username",
    placeholder="e.g. Varshithareddy2603"
)


repository = st.text_input(
    "Repository Name",
    placeholder="e.g. GitSense"
)


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

            # --------------------------------
            # Repository Summary
            # --------------------------------

            summary = get_repository_summary(
                username,
                repository
            )

            st.success("Repository found!")

            st.subheader(summary["name"])

            if summary["description"]:
                st.write(summary["description"])
            else:
                st.write("No description available.")


            # --------------------------------
            # Repository Statistics
            # --------------------------------

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


            # --------------------------------
            # Additional Information
            # --------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                st.write("**💻 Language**")

                st.write(
                    summary["language"]
                    or "Not specified"
                )

            with col2:

                st.write("**📦 Repository Size**")

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


            # --------------------------------
            # GitHub Repository Link
            # --------------------------------

            st.divider()

            st.write("### 🔗 Repository")

            st.markdown(
                f"[Open {summary['name']} on GitHub]"
                f"({summary['html_url']})"
            )


            # --------------------------------
            # Repository Files
            # --------------------------------

            st.divider()

            st.subheader("📁 Repository Files")

            files = get_repository_files(
                username,
                repository
            )


            if not files:

                st.info(
                    "No files found in this repository."
                )

            else:

                for file in files:

                    if file["type"] == "dir":

                        with st.expander(
                            f"📂 {file['name']}"
                        ):

                            folder_files = get_repository_files(
                                username,
                                repository,
                                file["path"]
                            )


                            if not folder_files:

                                st.write(
                                    "This folder is empty."
                                )

                            else:

                                for folder_file in folder_files:

                                    if folder_file["type"] == "dir":

                                        st.write(
                                            f"📂 {folder_file['name']}"
                                        )

                                    else:

                                        st.write(
                                            f"📄 {folder_file['name']}"
                                        )

                    else:

                        st.write(
                            f"📄 {file['name']}"
                        )


        except ValueError as error:

            st.error(
                str(error)
            )


        except Exception as error:

            st.error(
                f"Something went wrong: {error}"
            )