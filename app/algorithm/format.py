import json
from models.database import get_collection
from collections import defaultdict
from models.manager_settings_model import get_manager_settings


def format_schedule_output(solver, shifts, employees, work_days, shift_names, shifts_per_day, roles_per_shift, constraints):
    schedule = []
    
    for day_index, day_name in enumerate(work_days):
        day_shifts = []
        
        for shift_num in range(shifts_per_day):
            shift_index = day_index * shifts_per_day + shift_num
            assigned_employees = []
            
            # For each employee assigned to this shift...
            for emp_index, emp_name in enumerate(employees):
                if solver.Value(shifts[(emp_index, shift_index)]) == 1:
                    # Get the required roles for this shift (from your manager settings)
                    required_roles = roles_per_shift.get(shift_names[shift_num], {})
                    # Get the employee's skills
                    emp_skills = constraints["employee_skills"].get(emp_name, [])
                    # Choose the first matching role between the required roles and employee skills
                    assigned_role = None
                    for role in required_roles.keys():
                        if role in emp_skills:
                            assigned_role = role
                            break
                    if assigned_role is None:
                        assigned_role = "Unknown"
                    
                    assigned_employees.append({
                        "id": f"e{emp_index}_s{shift_index}",
                        "name": emp_name,
                        "role": assigned_role,
                        "hours": "8",
                    })
            
            # Compute shortages as before
            shortages_info = {}
            required_roles = roles_per_shift.get(shift_names[shift_num], {})
            for role, required_count in required_roles.items():
                # Count employees assigned to that role
                assigned_count = sum(
                    1 for emp in assigned_employees if emp["role"] == role
                )
                shortage = required_count - assigned_count
                if shortage > 0:
                    shortages_info[role] = shortage
            
            day_shifts.append({
                "id": f"s{shift_index}",
                "time": shift_names[shift_num],
                "employees": assigned_employees,
                "shortages": shortages_info,
            })
        
        schedule.append({
            "id": f"d{day_index}",
            "name": day_name,
            "shifts": day_shifts,
        })
    
    return json.dumps(schedule, indent=2)


def format_schedule_input():
    """
    Fetches constraints from the database and converts them into a format understood by the algorithm.
    """
    manager_settings= get_manager_settings()
    active_version = manager_settings["activeVersion"]
    constraintsDB = get_collection("constraints")
    shifts_per_day=manager_settings["shifts_per_day"]
    constraints = constraintsDB.find({"is_final": True,"version": active_version}) 

    employee_skills = {}
    employee_availability = defaultdict(list)

    for constraint in constraints:
        first_name = constraint.get("first_name", "").strip()
        last_name = constraint.get("last_name", "").strip()
        full_name = f"{first_name} {last_name}"  
        roles = constraint.get("roles", [])
        availability = constraint.get("availability", [])

        # Adding employee skills
        employee_skills[full_name] = roles

        # Convert availability to the algorithm's format
        for shift in availability:
            shift_id = shift["day"] * shifts_per_day + shift["shift"] 
            priority = shift["priority"]
            employee_availability[full_name].append([shift_id, priority])
    # print(f"employee_skills: {dict(employee_skills)}")
    # print(f"employee_availability: {dict(employee_availability)}")
    payload={
        "employee_skills": dict(employee_skills),
        "employee_availability": dict(employee_availability),
    }
    print(f"payload: {payload}")
    return payload
