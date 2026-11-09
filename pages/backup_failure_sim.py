import streamlit as st
from custom_ui import show_page_header


def show_backup_failure_sim(user_id):

    show_page_header(
        "Backup & Failure Simulator",
        "Test what happens when the selected recovery strategy fails."
    )

    st.write(
        "Test what happens when the selected recovery strategy fails."
    )

    strategies = st.session_state.get("recovery_strategies")
    comparison = st.session_state.get("recovery_comparison")

    if not strategies or not comparison:
        st.warning(
            "Please generate recovery strategies first."
        )
        return

    best_plan = comparison.get("best_plan")
    backup_plan = comparison.get("backup_plan")

    if not best_plan:
        st.warning("No recommended recovery plan is available.")
        return

    st.subheader("Current Recovery Plans")

    col1, col2 = st.columns(2)

    with col1:
        st.success("Recommended Plan")
        st.write(best_plan["strategy_name"])
        st.metric(
            "Completion",
            f"{best_plan['completion_days']} days"
        )

    with col2:
        st.info("Backup Plan")
        if backup_plan:
            st.write(backup_plan["strategy_name"])
            st.metric(
                "Completion",
                f"{backup_plan['completion_days']} days"
            )
        else:
            st.write("No backup plan available")

    st.divider()
    st.subheader("Simulate Recovery Plan Failure")

    failure = st.radio(
        "What happened to the recommended plan?",
        [
            "Recommended plan failed",
            "Recommended plan succeeded"
        ]
    )

    if st.button(
        "Run Failure Simulation",
        use_container_width=True
    ):

        if failure == "Recommended plan failed":

            st.error(
                f"Failure detected: {best_plan['strategy_name']}"
            )

            if backup_plan:

                st.success("Backup plan activated!")

                st.subheader("Activated Backup Plan")

                st.write(
                    "**Strategy:**",
                    backup_plan["strategy_name"]
                )

                st.metric(
                    "Expected Completion",
                    f"{backup_plan['completion_days']} days"
                )

                st.write(
                    "**Feasibility:**",
                    backup_plan["feasibility"]
                )

                st.session_state["active_recovery_plan"] = (
                    backup_plan
                )

            else:
                st.warning(
                    "No backup plan is available. "
                    "Please generate alternative recovery strategies."
                )

        else:

            st.success(
                "Recommended recovery plan completed successfully!"
            )

            st.write(
                "Active Plan:",
                best_plan["strategy_name"]
            )

            st.session_state["active_recovery_plan"] = best_plan
