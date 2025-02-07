import json
from models.database import get_collection
from collections import defaultdict



def format_schedule_output(solver, shifts, employees, work_days, shift_names, shifts_per_day):
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



def format_schedule_input():
    """ 
    שואבת את האילוצים מהדאטהבייס וממירה אותם לפורמט שהאלגוריתם מבין.
    """
    constraintsDB = get_collection("constraints")
    shifts_per_day=3 #needs to be taken from the database
    constraints = constraintsDB.find({"status": "active"})  # מביא את כל האילוצים הפעילים

    employee_skills = {}
    employee_availability = defaultdict(list)

    for constraint in constraints:
        first_name = constraint.get("first_name", "").strip()
        last_name = constraint.get("last_name", "").strip()
        full_name = f"{first_name} {last_name}"  
        roles = constraint.get("roles", [])
        availability = constraint.get("availability", [])

        # הוספת כישורים של העובד
        employee_skills[full_name] = roles

        # המרת זמינות לפורמט של האלגוריתם
        for shift in availability:
            shift_id = shift["day"] * shifts_per_day + shift["shift"] 
            priority = shift["priority"]
            employee_availability[full_name].append([shift_id, priority])

    return {
        "employee_skills": dict(employee_skills),
        "employee_availability": dict(employee_availability),
    }
