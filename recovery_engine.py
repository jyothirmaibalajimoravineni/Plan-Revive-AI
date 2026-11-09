from copy import deepcopy
from scheduler import calculate_schedule, validate_tasks


def apply_disruption(tasks, affected_task, delay_days):
    """Apply an additional delay to the affected task."""
    updated_tasks = deepcopy(tasks)

    if delay_days < 0:
        raise ValueError("Delay days cannot be negative.")

    found = False

    for task in updated_tasks:
        if task["task_name"] == affected_task:
            task["duration"] = int(task["duration"]) + int(delay_days)
            found = True
            break

    if not found:
        raise ValueError(
            f"Affected task '{affected_task}' was not found."
        )

    validate_tasks(updated_tasks)
    return updated_tasks


def make_strategy(name, description, tasks, deadline, action,
                  available=True):
    """Calculate and evaluate one recovery strategy."""

    if not available:
        return {
            "strategy_name": name,
            "description": description,
            "action": action,
            "available": False,
            "completion_days": None,
            "feasibility": "Unavailable",
            "schedule": []
        }

    result = calculate_schedule(tasks, deadline)

    return {
        "strategy_name": name,
        "description": description,
        "action": action,
        "available": True,
        "completion_days": result["total_duration"],
        "feasibility": result["deadline_status"],
        "schedule": result["schedule"]
    }


def generate_recovery_strategies(
    tasks,
    affected_task,
    delay_days,
    deadline,
    recovery_options=None
):
    """
    Generate five recovery scenarios.

    recovery_options must contain only actions the user permits:
      overtime_days: days saved using approved overtime
      extra_resource_days: days saved using approved extra resources
      scope_reduction_days: days saved using approved scope reduction
    """

    recovery_options = recovery_options or {}

    disrupted_tasks = apply_disruption(
        tasks, affected_task, delay_days
    )

    validate_tasks(disrupted_tasks)

    strategies = []

    # 1. Baseline: continue without recovery action.
    strategies.append(
        make_strategy(
            "Baseline Plan",
            "Continue with the disrupted project schedule.",
            disrupted_tasks,
            deadline,
            "No recovery action"
        )
    )

    def create_reduced_tasks(reduction_days):
        changed = deepcopy(disrupted_tasks)

        for task in changed:
            if task["task_name"] == affected_task:
                reduction = min(
                    max(0, int(reduction_days)),
                    max(0, int(task["duration"]) - 1)
                )
                task["duration"] -= reduction
                break

        return changed

    # 2. Overtime strategy.
    overtime_days = max(
        0, int(recovery_options.get("overtime_days", 0))
    )

    strategies.append(
        make_strategy(
            "Overtime Strategy",
            "Use approved overtime to recover affected task time.",
            create_reduced_tasks(overtime_days),
            deadline,
            f"Approved overtime: {overtime_days} days",
            available=overtime_days > 0
        )
    )

    # 3. Extra resource strategy.
    resource_days = max(
        0, int(recovery_options.get("extra_resource_days", 0))
    )

    strategies.append(
        make_strategy(
            "Resource Augmentation",
            "Use additional available resources for the affected task.",
            create_reduced_tasks(resource_days),
            deadline,
            f"Approved extra-resource benefit: {resource_days} days",
            available=resource_days > 0
        )
    )

    # 4. Scope adjustment strategy.
    scope_days = max(
        0, int(recovery_options.get("scope_reduction_days", 0))
    )

    strategies.append(
        make_strategy(
            "Scope Adjustment",
            "Reduce approved task scope to recover project time.",
            create_reduced_tasks(scope_days),
            deadline,
            f"Approved scope-adjustment benefit: {scope_days} days",
            available=scope_days > 0
        )
    )

    # 5. Resequencing strategy.
    # With unlimited resources and dependency-only scheduling,
    # changing the order of independent tasks does not reduce duration.
    resequenced_tasks = deepcopy(disrupted_tasks)
    resequenced_tasks.reverse()

    strategies.append(
        make_strategy(
            "Task Resequencing",
            "Explore a different order for independent tasks.",
            resequenced_tasks,
            deadline,
            "Explore an alternative valid task order"
        )
    )

    return strategies


def compare_strategies(strategies):
    """Compare available strategies by completion time."""

    available = [
        strategy for strategy in strategies
        if strategy["available"]
    ]

    if not available:
        return {
            "best_plan": None,
            "backup_plan": None,
            "comparison": []
        }

    feasible = [
        strategy for strategy in available
        if strategy["feasibility"] == "Feasible"
    ]

    # Prefer deadline-feasible strategies.
    candidates = feasible if feasible else available

    ranked = sorted(
        candidates,
        key=lambda item: item["completion_days"]
    )

    best_plan = ranked[0]
    backup_plan = ranked[1] if len(ranked) > 1 else None

    return {
        "best_plan": best_plan,
        "backup_plan": backup_plan,
        "comparison": ranked
    }