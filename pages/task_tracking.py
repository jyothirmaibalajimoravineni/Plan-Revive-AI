import streamlit as st
import database
from custom_ui import show_page_header


def show_task_tracking(user_id):

    show_page_header(
        "Task Tracking",
        "Track project tasks and update their completion status."
    )
    st.write("Track project tasks and update their completion status.")

    projects = database.get_user_projects(user_id)

    if not projects:
        st.warning("Please create a project first.")
        return

    project_options = {
        f"{p['project_name']} (ID: {p['id']})": p
        for p in projects
    }

    selected_name = st.selectbox(
        "Select Project",
        list(project_options.keys())
    )

    project = project_options[selected_name]
    tasks = database.get_project_tasks(project["id"])

    if not tasks:
        st.info("No tasks available.")
        return

    total_count = len(tasks)
    completed_count = sum(
        1 for task in tasks if task["status"] == "Completed"
    )
    in_progress_count = sum(
        1 for task in tasks if task["status"] == "In Progress"
    )
    pending_count = total_count - completed_count - in_progress_count

    st.subheader("Project Task Status")

    st.progress(completed_count / total_count)

    col1, col2, col3 = st.columns(3)
    col1.metric("Completed", completed_count)
    col2.metric("In Progress", in_progress_count)
    col3.metric("Pending", pending_count)

    st.write(f"Overall completion: {completed_count / total_count * 100:.1f}%")

    st.divider()

    for task in tasks:

        with st.container(border=True):

            st.subheader(task["task_name"])

            st.write("Assigned Member:", task["assigned_member"] or "Not Assigned")
            st.write("Duration:", f"{task['duration']} days")

            status_options = ["Pending", "In Progress", "Completed"]
            current_status = task["status"] or "Pending"

            selected_status = st.selectbox(
                "Task Status",
                status_options,
                index=status_options.index(current_status),
                key=f"status_{task['id']}"
            )

            if st.button("Update Status", key=f"update_{task['id']}"):

                database.update_task_status(
                    task["id"],
                    selected_status
                )

                st.success("Task status saved successfully!")
                st.rerun()

    if completed_count == total_count:
        st.success("All project tasks are completed!")