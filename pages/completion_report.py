import streamlit as st
import database
import plotly.express as px
from custom_ui import show_page_header


def show_completion_report(user_id):
    show_page_header(
        "Completion Report",
        "Review task progress and saved recovery results for a project."
    )

    projects = [
        dict(project)
        for project in database.get_user_projects(user_id)
    ]

    if not projects:
        st.info("No projects available. Please create a project first.")
        return

    project_names = [
        project["project_name"]
        for project in projects
    ]
    selected_name = st.selectbox(
        "Select Project",
        project_names,
        key="completion_report_project_name_v2"
    )
    selected_project = next(
        project
        for project in projects
        if project["project_name"] == selected_name
    )

    tasks = database.get_project_tasks(selected_project["id"])
    completed_tasks = [
        task for task in tasks
        if task["status"] == "Completed"
    ]
    total_tasks = len(tasks)

    st.subheader(selected_project["project_name"])
    st.write("Description:", selected_project["description"] or "Not provided")
    st.write("Deadline:", f"{selected_project['deadline']} days")
    st.write("Project Status:", selected_project["status"])

    st.subheader("Task Completion")
    st.progress(
        len(completed_tasks) / total_tasks if total_tasks else 0.0
    )
    st.write(f"Completed: {len(completed_tasks)} / {total_tasks} tasks")

    if tasks:
        status_counts = {
            "Pending": 0,
            "In Progress": 0,
            "Completed": 0,
            "Other": 0
        }
        for task in tasks:
            status = task["status"] or "Pending"
            if status not in status_counts:
                status = "Other"
            status_counts[status] += 1

        status_data = [
            {"Status": status, "Tasks": count}
            for status, count in status_counts.items()
            if count > 0
        ]
        status_chart = px.pie(
            status_data,
            names="Status",
            values="Tasks",
            hole=0.4,
            title="Task Status Breakdown"
        )
        status_chart.update_traces(
            textposition="inside",
            textinfo="label+percent"
        )
        st.plotly_chart(
            status_chart,
            use_container_width=True
        )

        st.dataframe(
            [
                {
                    "Task": task["task_name"],
                    "Duration (days)": task["duration"],
                    "Status": task["status"] or "Pending"
                }
                for task in tasks
            ],
            use_container_width=True
        )
    else:
        st.info("No tasks are recorded for this project.")

    connection = database.get_connection()
    recovery_history = connection.execute(
        """
        SELECT strategy_name, completion_days, feasibility, is_selected
        FROM recovery_history
        WHERE project_id = ?
        ORDER BY id DESC
        """,
        (selected_project["id"],)
    ).fetchall()
    connection.close()

    if recovery_history:
        st.subheader("Saved Recovery Results")
        st.dataframe(
            [
                {
                    "Strategy": result["strategy_name"],
                    "Completion (days)": result["completion_days"],
                    "Feasibility": result["feasibility"],
                    "Recommended": "Yes" if result["is_selected"] else "No"
                }
                for result in recovery_history
            ],
            use_container_width=True
        )
