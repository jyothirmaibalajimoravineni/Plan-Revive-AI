import streamlit as st
import database
from scheduler import validate_tasks, calculate_schedule
from custom_ui import show_page_header


def show_create_project(user_id):

    show_page_header(
        "Create New Project",
        "Enter your project details and task information."
    )

    project_name = st.text_input("Project Name")
    description = st.text_area("Project Description")
    deadline = st.number_input(
        "Project Deadline (Days)",
        min_value=1,
        value=20
    )

    st.divider()
    st.subheader("Task Details")

    task_count = st.number_input(
        "How many tasks does your project have?",
        min_value=1,
        max_value=20,
        value=3,
        step=1
    )

    with st.form("project_form"):

        tasks = []

        for i in range(int(task_count)):

            st.markdown(f"**Task {i + 1}**")

            task_name = st.text_input(
                "Task Name",
                key=f"task_name_{i}"
            )

            duration = st.number_input(
                "Duration (Days)",
                min_value=1,
                value=2,
                key=f"duration_{i}"
            )

            dependencies = st.text_input(
                "Dependencies (Enter task names separated by commas)",
                placeholder="Example: Requirement Analysis",
                key=f"dependencies_{i}"
            )

            assigned_member = st.text_input(
                "Assigned Team Member",
                key=f"member_{i}"
            )

            tasks.append({
                "task_name": task_name.strip(),
                "duration": int(duration),
                "dependencies": [
                    item.strip()
                    for item in dependencies.split(",")
                    if item.strip()
                ],
                "assigned_member": assigned_member.strip()
            })

            st.divider()

        submitted = st.form_submit_button(
            "Save Project",
            use_container_width=True
        )

    if submitted:

        if not project_name.strip():
            st.error("Please enter a project name.")

        elif database.project_name_exists(user_id, project_name.strip()):
            st.error(
                "A project with this name already exists. "
                "Choose a different name."
            )

        elif any(not task["task_name"] for task in tasks):
            st.error("Please enter names for all tasks.")

        else:
            try:
                validate_tasks(tasks)

                schedule_result = calculate_schedule(
                    tasks,
                    int(deadline)
                )

                project_id = database.create_project(
                    user_id,
                    project_name.strip(),
                    description.strip(),
                    int(deadline)
                )

                for task in tasks:
                    database.add_task(
                        project_id,
                        task["task_name"],
                        task["duration"],
                        ",".join(task["dependencies"]),
                        task["assigned_member"]
                    )

                st.success("Project created successfully!")

                st.subheader("Initial Project Schedule")

                st.dataframe(
                    schedule_result["schedule"],
                    use_container_width=True
                )

                st.metric(
                    "Estimated Project Duration",
                    f"{schedule_result['total_duration']} days"
                )

                st.write(
                    "Deadline Status:",
                    schedule_result["deadline_status"]
                )

            except ValueError as error:
                st.error(str(error))
