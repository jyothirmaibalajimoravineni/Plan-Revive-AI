import streamlit as st
import plotly.express as px
import database
from pages.create_project import show_create_project
from pages.disruption_simulator import show_disruption_simulator
from pages.recovery_simulator import show_recovery_simulator
from pages.backup_failure_sim import show_backup_failure_sim
from pages.what_if_sandbox import show_what_if_sandbox
from pages.task_tracking import show_task_tracking
from pages.completion_report import show_completion_report
from custom_ui import apply_custom_design, show_page_header, show_sidebar_branding
# Page configuration
st.set_page_config(
    page_title="PlanRevive AI",
    page_icon="📊",
    layout="wide"
)
apply_custom_design()

NAVIGATION_LABELS = {
    "Dashboard": "📊 Dashboard",
    "Create Project": "➕ Create Project",
    "Project Overview": "📋 Project Overview",
    "Disruption Simulator": "⚠️ Disruption Simulator",
    "Recovery Simulator": "🛠️ Recovery Simulator",
    "Backup & Failure Sim": "🛡️ Backup & Failure Sim",
    "What-If Sandbox": "🧪 What-If Sandbox",
    "Task Tracking": "✅ Task Tracking",
    "Completion Report": "📈 Completion Report"
}
PAGE_BY_NAVIGATION_LABEL = {
    label: page
    for page, label in NAVIGATION_LABELS.items()
}

# Initialize database
database.initialize_database()

# Session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "username" not in st.session_state:
    st.session_state.username = None

if "main_navigation" not in st.session_state:
    st.session_state.main_navigation = NAVIGATION_LABELS["Dashboard"]


def _open_project(project_id):
    st.session_state.selected_project_id = project_id
    st.session_state.main_navigation = NAVIGATION_LABELS["Project Overview"]


def _navigate_to(page):
    st.session_state.main_navigation = NAVIGATION_LABELS[page]


# ---------------- LOGIN PAGE ----------------

def login_page():

    show_sidebar_branding()
    show_page_header(
        "PlanRevive AI",
        "Intelligent Planning and Recovery Strategy Simulator"
    )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:

        st.markdown("### Welcome Back")

        username = st.text_input(
            "Username",
            key="login_username"
        )

        password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button("Login", use_container_width=True):

            user_id = database.login_user(
                username,
                password
            )

            if user_id is not None:
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with register_tab:

        st.markdown("### Create Account")

        new_username = st.text_input(
            "Choose Username",
            key="register_username"
        )

        new_password = st.text_input(
            "Choose Password",
            type="password",
            key="register_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button("Register", use_container_width=True):

            if not new_username.strip() or not new_password:
                st.warning("Please enter username and password.")

            elif new_password != confirm_password:
                st.error("Passwords do not match.")

            elif len(new_password) < 8:
                st.warning(
                    "Password must contain at least 8 characters."
                )

            else:
                success = database.register_user(
                    new_username.strip(),
                    new_password
                )

                if success:
                    st.success(
                        "Account created! Please login."
                    )
                else:
                    st.error("Username already exists.")


# ---------------- DASHBOARD ----------------

def show_dashboard():

    show_page_header(
        "Dashboard",
        f"Welcome back, {st.session_state.username}."
    )

    projects = database.get_user_projects(
        st.session_state.user_id
    )
    projects = [dict(project) for project in projects]

    total_projects = len(projects)

    active_projects = sum(
        1 for project in projects
        if project["status"] == "Active"
    )

    completed_projects = sum(
        1 for project in projects
        if project["status"] == "Completed"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("📁 Total Projects", total_projects)
    col2.metric("🟢 Active Projects", active_projects)
    col3.metric("🏁 Completed Projects", completed_projects)

    project_progress = []
    task_status_totals = {
        "Pending": 0,
        "In Progress": 0,
        "Completed": 0
    }

    for project in projects:
        tasks = database.get_project_tasks(project["id"])
        completed_count = sum(
            1 for task in tasks if task["status"] == "Completed"
        )
        if tasks:
            project_progress.extend([
                {
                    "Project": project["project_name"],
                    "Progress": "Completed",
                    "Tasks": completed_count
                },
                {
                    "Project": project["project_name"],
                    "Progress": "Remaining",
                    "Tasks": len(tasks) - completed_count
                }
            ])

        for task in tasks:
            status = task["status"] or "Pending"
            if status not in task_status_totals:
                status = "Pending"
            task_status_totals[status] += 1

    if project_progress:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            progress_chart = px.bar(
                project_progress,
                x="Tasks",
                y="Project",
                color="Progress",
                orientation="h",
                barmode="stack",
                title="Task Progress by Project",
                labels={"Tasks": "Number of tasks"}
            )
            st.plotly_chart(progress_chart, use_container_width=True)

        with chart_col2:
            status_data = [
                {"Status": status, "Tasks": count}
                for status, count in task_status_totals.items()
                if count
            ]
            status_chart = px.pie(
                status_data,
                names="Status",
                values="Tasks",
                hole=0.45,
                title="Overall Task Status"
            )
            status_chart.update_traces(
                textposition="inside",
                textinfo="label+percent"
            )
            st.plotly_chart(status_chart, use_container_width=True)

    st.subheader("Your Projects")

    if projects:

        for project in projects:

            with st.container(border=True):

                st.markdown(f"### 📁 {project['project_name']}")

                st.write(
                    f"Deadline: {project['deadline']} days"
                )

                st.write(
                    f"Status: {project['status']}"
                )
                st.button(
                    "Open project →",
                    key=f"open_project_{project['id']}",
                    on_click=_open_project,
                    args=(project["id"],),
                    use_container_width=True
                )

    else:

        st.info(
            "No projects yet. Open Create Project to add your first project."
        )


# ---------------- PROJECT OVERVIEW ----------------

def show_project_overview():

    show_page_header(
        "Project Overview",
        "Review project details, tasks, and current status."
    )

    projects = database.get_user_projects(
        st.session_state.user_id
    )

    if not projects:
        st.info("No projects available. Please create a project first.")
        return

    project_options = {
        f"{project['project_name']} · #{project['id']}": dict(project)
        for project in projects
    }
    project_labels = list(project_options)
    selected_project_id = st.session_state.get("selected_project_id")
    default_index = next(
        (
            index
            for index, project in enumerate(project_options.values())
            if project["id"] == selected_project_id
        ),
        0
    )
    selected_label = st.selectbox(
        "Select Your Project",
        project_labels,
        index=default_index,
        key="overview_project_select"
    )
    selected_project = project_options[selected_label]
    st.session_state.selected_project_id = selected_project["id"]

    st.subheader(selected_project["project_name"])

    st.write(
        "Description:",
        selected_project["description"]
    )

    st.write(
        "Deadline:",
        selected_project["deadline"],
        "days"
    )

    st.write(
        "Status:",
        selected_project["status"]
    )

    tasks = database.get_project_tasks(
        selected_project["id"]
    )

    st.subheader("Project Tasks")

    if tasks:
        status_counts = {
            "Pending": 0,
            "In Progress": 0,
            "Completed": 0
        }
        for task in tasks:
            status = task["status"] or "Pending"
            if status not in status_counts:
                status = "Pending"
            status_counts[status] += 1

        status_col, task_count_col = st.columns([2, 1])
        status_data = [
            {"Status": status, "Tasks": count}
            for status, count in status_counts.items()
            if count
        ]
        with status_col:
            status_chart = px.pie(
                status_data,
                names="Status",
                values="Tasks",
                hole=0.45,
                title="Task Status"
            )
            status_chart.update_traces(
                textposition="inside",
                textinfo="label+percent"
            )
            st.plotly_chart(status_chart, use_container_width=True)
        with task_count_col:
            st.metric("✅ Completed", status_counts["Completed"])
            st.metric("🔄 In Progress", status_counts["In Progress"])
            st.metric("⏳ Pending", status_counts["Pending"])

        task_data = []

        for task in tasks:

            task_data.append({
                "Task Name": task["task_name"],
                "Duration": task["duration"],
                "Dependencies": task["dependencies"] or "None",
                "Assigned Member": task["assigned_member"] or "Not Assigned",
                "Status": task["status"]
            })

        st.dataframe(
            task_data,
            use_container_width=True
        )

        st.metric(
            "Total Tasks",
            len(tasks)
        )

    else:

        st.info("No tasks found for this project.")

    st.subheader("Continue project workflow")
    next_step_columns = st.columns(3)
    workflow_steps = [
        ("⚠️ Record disruption", "Disruption Simulator"),
        ("✅ Update task progress", "Task Tracking"),
        ("📈 View completion report", "Completion Report")
    ]
    for column, (button_label, page_name) in zip(
        next_step_columns,
        workflow_steps
    ):
        column.button(
            button_label,
            key=f"project_next_{selected_project['id']}_{page_name}",
            on_click=_navigate_to,
            args=(page_name,),
            use_container_width=True
        )

# ---------------- MAIN DASHBOARD NAVIGATION ----------------

def dashboard():

    show_sidebar_branding()
    selected_navigation = st.sidebar.radio(
        "Navigation",
        list(PAGE_BY_NAVIGATION_LABEL),
        key="main_navigation"
    )
    page = PAGE_BY_NAVIGATION_LABEL[selected_navigation]

    if page == "Dashboard":

        show_dashboard()

    elif page == "Create Project":

        show_create_project(
            st.session_state.user_id
        )

    elif page == "Project Overview":

        show_project_overview()

    elif page == "Disruption Simulator":

        show_disruption_simulator(
            st.session_state.user_id
        )

    elif page == "Recovery Simulator":

        show_recovery_simulator(
            st.session_state.user_id
        )


    elif page == "Backup & Failure Sim":

        show_backup_failure_sim(
            st.session_state.user_id
        )

    elif page == "What-If Sandbox":

        show_what_if_sandbox(
            st.session_state.user_id
        )

    elif page == "Task Tracking":
        show_task_tracking(
            st.session_state.user_id
            )

    elif page == "Completion Report":
         show_completion_report(
        st.session_state.user_id
        )
    else:

        show_page_header(page, "Project planning and recovery workspace.")

        st.info(
            "This module will be connected in the next development steps."
        )


# ---------------- APPLICATION ENTRY ----------------

if st.session_state.user_id is None:

    login_page()

else:

    dashboard()
