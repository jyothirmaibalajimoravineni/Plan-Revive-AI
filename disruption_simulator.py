import streamlit as st
import database
from custom_ui import show_page_header


def show_disruption_simulator(user_id):

    show_page_header(
        "Disruption Simulator",
        "Simulate unexpected project disruptions and analyze their impact."
    )
    st.write(
        "Simulate unexpected project disruptions and analyze their impact."
    )

    projects = database.get_user_projects(user_id)

    if not projects:
        st.warning("Please create a project first.")
        return

    project_options = {
        project["project_name"]: project
        for project in projects
    }

    selected_name = st.selectbox(
        "Select Project",
        list(project_options.keys())
    )

    selected_project = project_options[selected_name]
    project_id = selected_project["id"]

    tasks = database.get_project_tasks(project_id)

    if not tasks:
        st.warning("No tasks available in this project.")
        return

    task_names = [task["task_name"] for task in tasks]

    st.divider()
    st.subheader("Disruption Details")

    disruption_types = [
        "Unexpected Delay",
        "Team Member Unavailability",
        "Resource Shortage",
        "Task Failure",
        "Budget Reduction",
        "Equipment Failure",
        "Dependency Delay",
        "Deadline Change",
        "Scope Change",
        "Technical Issues",
        "Power Failure",
        "Communication Failure",
        "Material Shortage",
        "Quality Issue",
        "External Vendor Delay",
        "Other"
    ]

    with st.form("disruption_form"):

        disruption_type = st.selectbox(
            "Select Disruption Type",
            disruption_types
        )

        affected_task = st.selectbox(
            "Select Affected Task",
            task_names
        )

        delay_days = st.number_input(
            "Expected Delay (Days)",
            min_value=0,
            max_value=365,
            value=2
        )

        description = st.text_area(
            "Additional Details",
            placeholder="Describe what happened..."
        )

        submitted = st.form_submit_button(
            "Simulate Disruption",
            use_container_width=True
        )

    if submitted:

        try:
            connection = database.get_connection()

            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO disruptions
                (project_id, disruption_type, affected_task, delay_days)
                VALUES (?, ?, ?, ?)
                """,
                (
                    project_id,
                    disruption_type,
                    affected_task,
                    int(delay_days)
                )
            )

            connection.commit()
            connection.close()

            st.success("Disruption saved successfully!")

            st.subheader("Disruption Summary")

            col1, col2, col3 = st.columns(3)

            col1.metric("Project", selected_name)
            col2.metric("Affected Task", affected_task)
            col3.metric("Delay", f"{int(delay_days)} days")

            st.write("**Disruption Type:**", disruption_type)

            if description.strip():
                st.write("**Additional Details:**", description)

            st.info(
                "Disruption recorded. Recovery strategies can now be generated "
                "using this disruption."
            )

        except Exception as error:
            st.error(f"Unable to save disruption: {error}")