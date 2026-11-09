import streamlit as st
import database
from custom_ui import show_page_header

from recovery_engine import (
    generate_recovery_strategies,
    compare_strategies
)


def show_recovery_simulator(user_id):

    show_page_header(
        "Recovery Strategy Simulator",
        "Generate and compare strategies to recover your disrupted project."
    )

    st.write(
        "Generate and compare five recovery strategies "
        "to recover your disrupted project."
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

    # Get the latest disruption
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
        st.info(
            "Please simulate and save a disruption before generating "
            "recovery strategies."
        )
        return

    st.divider()
    st.subheader("Latest Disruption")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Disruption",
        disruption["disruption_type"]
    )

    col2.metric(
        "Affected Task",
        disruption["affected_task"]
    )

    col3.metric(
        "Delay",
        f"{disruption['delay_days']} days"
    )

    deadline = project["deadline"]

    st.subheader("Recovery Options")

    st.write(
        "Enter the recovery improvements that are available "
        "to your project."
    )

    with st.form("recovery_options_form"):

        overtime_days = st.number_input(
            "Days saved through overtime",
            min_value=0,
            max_value=365,
            value=1
        )

        extra_resource_days = st.number_input(
            "Days saved through additional resources",
            min_value=0,
            max_value=365,
            value=2
        )

        scope_reduction_days = st.number_input(
            "Days saved through approved scope reduction",
            min_value=0,
            max_value=365,
            value=1
        )

        generate = st.form_submit_button(
            "Generate Recovery Strategies",
            use_container_width=True
        )

    if generate:

        try:
            task_inputs = []

            for task in tasks:

                task_inputs.append({
                    "task_name": task["task_name"],
                    "duration": task["duration"],
                    "dependencies": task["dependencies"],
                    "assigned_member": task["assigned_member"]
                })

            strategies = generate_recovery_strategies(
                tasks=task_inputs,
                affected_task=disruption["affected_task"],
                delay_days=disruption["delay_days"],
                deadline=deadline,
                recovery_options={
                    "overtime_days": int(overtime_days),
                    "extra_resource_days": int(extra_resource_days),
                    "scope_reduction_days": int(scope_reduction_days)
                }
            )

            comparison = compare_strategies(strategies)

            if len(strategies) != 5:
                st.error(
                    "The recovery engine did not generate five strategies."
                )
                return

            st.session_state["recovery_strategies"] = strategies
            st.session_state["recovery_comparison"] = comparison
            st.session_state["recovery_project_id"] = project_id

        except (ValueError, KeyError) as error:
            st.error(f"Unable to generate strategies: {error}")
            return

    # Display generated strategies
    strategies = st.session_state.get("recovery_strategies")

    if (
        strategies
        and st.session_state.get("recovery_project_id") == project_id
    ):

        comparison = st.session_state["recovery_comparison"]

        st.divider()
        st.subheader("Five Recovery Strategies")

        strategy_data = []

        for strategy in strategies:

            strategy_data.append({
                "Strategy": strategy["strategy_name"],
                "Action": strategy["action"],
                "Completion Days": strategy["completion_days"],
                "Feasibility": strategy["feasibility"]
            })

        st.dataframe(
            strategy_data,
            use_container_width=True
        )

        st.subheader("Recovery Plan Selection")

        best_plan = comparison["best_plan"]
        backup_plan = comparison["backup_plan"]

        if best_plan:

            st.success(
                f"Recommended Plan: {best_plan['strategy_name']}"
            )

            st.metric(
                "Expected Completion",
                f"{best_plan['completion_days']} days"
            )

            st.write(
                "Feasibility:",
                best_plan["feasibility"]
            )

        else:
            st.warning(
                "No valid recovery plan was found."
            )

        if backup_plan:

            st.info(
                f"Backup Plan: {backup_plan['strategy_name']}"
            )

            st.write(
                "Backup Completion:",
                f"{backup_plan['completion_days']} days"
            )

        else:
            st.warning(
                "No alternative backup plan is available."
            )

        # Save recovery results
        if st.button("Save Recovery Results"):

            connection = database.get_connection()

            cursor = connection.cursor()

            cursor.execute(
                "DELETE FROM recovery_history WHERE project_id = ?",
                (project_id,)
            )

            for strategy in strategies:

                is_selected = (
                    1 if best_plan and
                    strategy["strategy_name"] == best_plan["strategy_name"]
                    else 0
                )

                cursor.execute(
                    """
                    INSERT INTO recovery_history
                    (
                        project_id,
                        strategy_name,
                        completion_days,
                        feasibility,
                        is_selected
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        project_id,
                        strategy["strategy_name"],
                        strategy["completion_days"],
                        str(strategy["feasibility"]),
                        is_selected
                    )
                )

            connection.commit()
            connection.close()

            st.success("Recovery results saved successfully!")