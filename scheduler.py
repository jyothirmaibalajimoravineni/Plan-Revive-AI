from collections import defaultdict, deque


def prepare_tasks(tasks):
    """Convert task inputs into a consistent format."""

    prepared = []

    no_dependency_values = [
        "", "none", "no dependency",
        "no dependencies", "nil", "n/a", "na", "-"
    ]

    for task in tasks:
        task = dict(task)

        task_name = str(task.get("task_name", "")).strip()
        raw_dependencies = task.get("dependencies", [])

        if raw_dependencies is None:
            raw_dependencies = []

        if isinstance(raw_dependencies, str):
            raw_dependencies = raw_dependencies.split(",")

        dependencies = []

        for item in raw_dependencies:
            item = str(item).strip()

            if item.casefold() not in no_dependency_values:
                dependencies.append(item)

        prepared.append({
            "task_name": task_name,
            "duration": int(task["duration"]),
            "dependencies": dependencies,
            "release_delay": int(task.get("release_delay", 0))
        })

    # Match dependency names without case sensitivity
    name_map = {
        task["task_name"].casefold(): task["task_name"]
        for task in prepared
    }

    for task in prepared:
        task["dependencies"] = [
            name_map.get(dep.casefold(), dep)
            for dep in task["dependencies"]
        ]

    return prepared


def validate_tasks(tasks):
    """Validate task names, durations and dependencies."""

    tasks = prepare_tasks(tasks)

    if not tasks:
        raise ValueError("Please add at least one task.")

    names = [task["task_name"] for task in tasks]

    if any(not name for name in names):
        raise ValueError("Task names cannot be empty.")

    if len(names) != len(set(names)):
        raise ValueError("Duplicate task names are not allowed.")

    task_names = set(names)

    for task in tasks:

        if task["duration"] <= 0:
            raise ValueError(
                f"Duration must be positive: {task['task_name']}"
            )

        if task["release_delay"] < 0:
            raise ValueError(
                f"Release delay cannot be negative: {task['task_name']}"
            )

        for dependency in task["dependencies"]:

            if dependency not in task_names:
                raise ValueError(
                    f"Unknown dependency '{dependency}' "
                    f"for task '{task['task_name']}'."
                )

            if dependency == task["task_name"]:
                raise ValueError(
                    f"A task cannot depend on itself: {dependency}"
                )

    return True


def calculate_schedule(tasks, deadline=None):
    """
    Calculate an earliest-start schedule using dependencies.
    Day numbering starts from Day 1.
    Independent tasks can run in parallel.
    """

    tasks = prepare_tasks(tasks)

    validate_tasks(tasks)

    task_map = {
        task["task_name"]: task
        for task in tasks
    }

    indegree = {
        task["task_name"]: len(task["dependencies"])
        for task in tasks
    }

    dependents = defaultdict(list)

    for task in tasks:
        for dependency in task["dependencies"]:
            dependents[dependency].append(task["task_name"])

    queue = deque(
        task["task_name"]
        for task in tasks
        if indegree[task["task_name"]] == 0
    )

    start_times = {}
    end_times = {}
    schedule = []

    while queue:

        current_name = queue.popleft()
        current_task = task_map[current_name]

        dependency_end = max(
            (
                end_times[dependency]
                for dependency in current_task["dependencies"]
            ),
            default=0
        )

        start = max(
            dependency_end,
            current_task["release_delay"]
        )

        end = start + current_task["duration"]

        start_times[current_name] = start
        end_times[current_name] = end

        schedule.append({
            "task_name": current_name,
            "start_day": start + 1,
            "end_day": end,
            "duration": current_task["duration"],
            "dependencies": current_task["dependencies"]
        })

        for next_task in dependents[current_name]:

            indegree[next_task] -= 1

            if indegree[next_task] == 0:
                queue.append(next_task)

    if len(schedule) != len(tasks):
        raise ValueError(
            "Circular dependency detected. "
            "Please check the task dependencies."
        )

    total_duration = max(end_times.values(), default=0)

    if deadline is not None:
        deadline = int(deadline)

        deadline_status = (
            "Feasible"
            if total_duration <= deadline
            else "Not Feasible"
        )
    else:
        deadline_status = "Not Checked"

    return {
        "schedule": schedule,
        "total_duration": total_duration,
        "deadline": deadline,
        "deadline_status": deadline_status
    }


def calculate_project_duration(tasks):
    result = calculate_schedule(tasks)
    return result["total_duration"]
