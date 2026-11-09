from recovery_engine import (
    generate_recovery_strategies,
    compare_strategies
)

# Sample project input for testing
tasks = [
    {
        "task_name": "Analysis",
        "duration": 3,
        "dependencies": []
    },
    {
        "task_name": "Design",
        "duration": 4,
        "dependencies": ["Analysis"]
    },
    {
        "task_name": "Development",
        "duration": 7,
        "dependencies": ["Analysis"]
    },
    {
        "task_name": "Integration",
        "duration": 3,
        "dependencies": ["Design", "Development"]
    },
    {
        "task_name": "Testing",
        "duration": 4,
        "dependencies": ["Integration"]
    }
]

# Disruption details
affected_task = "Development"
delay_days = 3
deadline = 20

# Generate five recovery strategies
strategies = generate_recovery_strategies(
    tasks=tasks,
    affected_task=affected_task,
    delay_days=delay_days,
    deadline=deadline,
    recovery_options={
        "overtime_days": 1,
        "extra_resource_days": 2,
        "scope_reduction_days": 1
    }
)

# Display all strategies
print("\n========== PLANREVIVE AI ==========")
print("Project: Website Development")
print("Affected Task:", affected_task)
print("Delay:", delay_days, "days")
print("Deadline:", deadline, "days")

print("\n========== RECOVERY STRATEGIES ==========")

for number, strategy in enumerate(strategies, start=1):
    print("\nStrategy", number)
    print("Name:", strategy["strategy_name"])
    print("Action:", strategy["action"])
    print("Completion Days:", strategy["completion_days"])
    print("Feasibility:", strategy["feasibility"])

# Compare strategies
comparison = compare_strategies(strategies)

print("\n========== FINAL RESULT ==========")

if comparison["best_plan"]:
    print(
        "Best Recovery Plan:",
        comparison["best_plan"]["strategy_name"]
    )

if comparison["backup_plan"]:
    print(
        "Backup Recovery Plan:",
        comparison["backup_plan"]["strategy_name"]
    )
else:
    print("Backup Recovery Plan: Not available")

print("\n========== TEST COMPLETED ==========")