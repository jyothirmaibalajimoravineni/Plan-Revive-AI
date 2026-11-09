import streamlit as st
import database
from custom_ui import show_page_header

from recovery_engine import (
    generate_recovery_strategies,
    compare_strategies
)


def show_what_if_sandbox(user_id):

    show_page_header(
        "What-If Sandbox",
        "Experiment with recovery improvements and compare project outcomes."
    )

    st.write(
        "Experiment with different recovery improvements "
        "and compare their effect on project completion time."
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

    project = project_options[selected_name]
    project_id = project["id"]

    tasks = database.get_project_tasks(project_id)

    if not tasks:
        st.warning("No tasks found in this project.")
        return

    connection = database.get_connection()

    disruption = connection.execute(
        """
        SELECT *
        FROM disruptions
        WHERE project_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (project_id,)
    ).fetchone()

    connection.close()

    if disruption is None:
        st.warning(
            "Please save a disruption before using What-If Sandbox."
        )
        return

    st.subheader("Current Disruption")

    st.write("Disruption:", disruption["disruption_type"])
    st.write("Affected Task:", disruption["affected_task"])
    st.write("Delay:", disruption["delay_days"], "days")

    st.divider()
    st.subheader("Experiment with Recovery Options")

    with st.form("what_if_form"):

        overtime_days = st.slider(
            "Overtime Benefit (Days)",
            0, 10, 1
        )

        resource_days = st.slider(
            "Additional Resource Benefit (Days)",
            0, 10, 2
        )

        scope_days = st.slider(
            "Scope Adjustment Benefit (Days)",
            0, 10, 1
        )

        simulate = st.form_submit_button(
            "Run What-If Simulation",
            use_container_width=True
        )

    if simulate:

        task_inputs = []

        for task in tasks:
            task_inputs.append({
                "task_name": task["task_name"],
                "duration": task["duration"],
                "dependencies": task["dependencies"],
                "assigned_member": task["assigned_member"]
            })

        try:
            strategies = generate_recovery_strategies(
                tasks=task_inputs,
                affected_task=disruption["affected_task"],
                delay_days=disruption["delay_days"],
                deadline=project["deadline"],
                recovery_options={
                    "overtime_days": overtime_days,
                    "extra_resource_days": resource_days,
                    "scope_reduction_days": scope_days
                }
            )

            comparison = compare_strategies(strategies)

            st.session_state["what_if_result"] = {
                "project_id": project_id,
                "strategies": strategies,
                "comparison": comparison
            }

        except (ValueError, KeyError) as error:
            st.error(f"Simulation error: {error}")

    result = st.session_state.get("what_if_result")

    if result and result["project_id"] == project_id:

        st.divider()
        st.subheader("What-If Simulation Results")

        strategies = result["strategies"]

        st.dataframe(
            [
                {
                    "Strategy": item["strategy_name"],
                    "Completion Days": item["completion_days"],
                    "Feasibility": item["feasibility"]
                }
                for item in strategies
            ],
            use_container_width=True
        )

        best_plan = result["comparison"]["best_plan"]

        if best_plan:

            st.success(
                "Best Scenario: " + best_plan["strategy_name"]
            )

            st.metric(
                "Expected Completion",
                f"{best_plan['completion_days']} days"
            )

            st.write(
                "Deadline Status:",
                best_plan["feasibility"]
            )

        st.info(
            "This experiment uses the recovery benefits entered above. "
            "It does not change your original saved project tasks."
        )