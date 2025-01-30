import json

def format_schedule(solver, shifts, employees, work_days, shift_names, shifts_per_day):
    schedule = []
    
    for day_index, day_name in enumerate(work_days):
        day_shifts = []
        
        for shift_num in range(shifts_per_day):
            shift_index = day_index * shifts_per_day + shift_num
            assigned_employees = []

            for emp_index, emp_name in enumerate(employees):
                if solver.Value(shifts[(emp_index, shift_index)]) == 1:
                    assigned_employees.append({
                        "id": f"e{emp_index}_s{shift_index}",  # מזהה ייחודי לכל מופע של עובד
                        "name": emp_name,
                        "role": "Unknown",
                        "hours": "8",
                    })

            day_shifts.append({
                "id": f"s{shift_index}",
                "time": shift_names[shift_num],
                "employees": assigned_employees
            })

        schedule.append({
            "id": f"d{day_index}",
            "name": day_name,
            "shifts": day_shifts
        })

    return json.dumps(schedule, indent=2)