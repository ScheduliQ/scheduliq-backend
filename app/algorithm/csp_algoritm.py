from ortools.sat.python import cp_model
from app.algorithm.format import format_schedule_output, format_schedule_input  # ייבוא הפונקציות
from models.manager_settings_model import get_manager_settings

def parse_json_to_constraints():
    manager_settings = get_manager_settings()
    fromDB = format_schedule_input()
    data = {
        "employee_skills": fromDB["employee_skills"],
        "employee_availability": fromDB["employee_availability"],
        "shifts_per_day": manager_settings["shifts_per_day"],
        "shift_length": 8,
        "shift_names": manager_settings["shift_names"],
        "work_days": manager_settings["work_days"],
        "min_max_employees_per_shift": manager_settings["min_max_employees_per_shift"],
        "roles_per_shift": manager_settings["roles_per_shift"],
        "max_consecutive_shifts": manager_settings["max_consecutive_shifts"],
        "role_importance": manager_settings["role_importance"]
    }
    print("data:", data)
    return data

def solve_schedule():
    model = cp_model.CpModel()
    
    # Reading data
    constraints = parse_json_to_constraints()
    employee_skills = constraints["employee_skills"]
    employees = list(employee_skills.keys())
    NUM_EMPLOYEES = len(employees)
    shifts_per_day = constraints["shifts_per_day"]
    work_days = constraints["work_days"]
    NUM_SHIFTS = shifts_per_day * len(work_days)
    min_employees = constraints["min_max_employees_per_shift"]["min"]
    max_employees = constraints["min_max_employees_per_shift"]["max"]
    roles_per_shift = constraints["roles_per_shift"]
    max_consecutive_shifts = constraints["max_consecutive_shifts"]
    employee_availability = constraints["employee_availability"]
    shift_names = constraints["shift_names"]
    role_importance = constraints["role_importance"]

    # Converting availability data into a convenient structure
    availability_dict = {}  # Mapping (employee, shift) -> priority
    for employee_name, shifts_data in employee_availability.items():
        for shift_id, priority in shifts_data:
            availability_dict[(employee_name, shift_id)] = priority

    # New variables: For each (employee, shift, role) marked as required
    assignments = {}
    for e in range(NUM_EMPLOYEES):
        employee = employees[e]
        for shift in range(NUM_SHIFTS):
            shift_name = shift_names[shift % shifts_per_day]
            # רק עבור התפקידים שמוגדרים למשמרת זו ועבורם העובד מוסמך
            for role in roles_per_shift[shift_name]:
                if role in employee_skills[employee]:
                    assignments[(e, shift, role)] = model.NewBoolVar(f'assign_{e}_{shift}_{role}')

    # Constraint 1: For each employee and shift, no more than one role
    shifts = {}  # Create a helper variable to indicate if the employee is assigned to this shift (to maintain the existing format)
    for e in range(NUM_EMPLOYEES):
        employee = employees[e]
        for shift in range(NUM_SHIFTS):
            shift_name = shift_names[shift % shifts_per_day]
            # Collect all variables for roles in which the employee can be assigned during this shift
            role_vars = [assignments[(e, shift, role)] for role in roles_per_shift[shift_name] if (e, shift, role) in assignments]
            if role_vars:
                # The employee can be assigned to the shift if at least one role is selected (and we limit it to 1)
                shifts[(e, shift)] = model.NewBoolVar(f'shift_{e}_{shift}')
                model.Add(sum(role_vars) == shifts[(e, shift)])
                model.Add(sum(role_vars) <= 1)  
            else:
                shifts[(e, shift)] = model.NewConstant(0)

    # Restrict employee availability – if the employee is not available for a shift, do not allow assignment
    for e in range(NUM_EMPLOYEES):
        employee = employees[e]
        for shift in range(NUM_SHIFTS):
            if not any(shift_data[0] == shift for shift_data in employee_availability[employee]):
                shift_name = shift_names[shift % shifts_per_day]
                for role in roles_per_shift[shift_name]:
                    if (e, shift, role) in assignments:
                        model.Add(assignments[(e, shift, role)] == 0)

    # Calculating preference cost – for each role assignment
    total_preference_cost = []
    for e in range(NUM_EMPLOYEES):
        employee = employees[e]
        for shift in range(NUM_SHIFTS):
            if any(shift_data[0] == shift for shift_data in employee_availability[employee]):
                priority = availability_dict.get((employee, shift), 0)
                shift_name = shift_names[shift % shifts_per_day]
                for role in roles_per_shift[shift_name]:
                    if (e, shift, role) in assignments:
                        total_preference_cost.append((10 - priority) * assignments[(e, shift, role)])

    # constraint 2: Role requirements, The sum of employees assigned to a role plus the shortage equals the requirement
    # Shortage variables for roles in each shift (as before)
    role_shortages = {}
    total_shortage_cost = []
    for shift in range(NUM_SHIFTS):
        shift_name = shift_names[shift % shifts_per_day]
        for role, required_count in roles_per_shift[shift_name].items():
            role_shortages[(shift, role)] = model.NewIntVar(0, required_count, f'shortage_{shift}_{role}')

    for shift in range(NUM_SHIFTS):
        shift_name = shift_names[shift % shifts_per_day]
        for role, required_count in roles_per_shift[shift_name].items():
            eligible_employees = []
            for e in range(NUM_EMPLOYEES):
                if (e, shift, role) in assignments:
                    eligible_employees.append(assignments[(e, shift, role)])

            model.Add(sum(eligible_employees) + role_shortages[(shift, role)] == required_count)
            model.Add(sum(eligible_employees) <= required_count)
            shortage_cost = role_shortages[(shift, role)] * role_importance[role]
            total_shortage_cost.append(shortage_cost)

    # Constraint 3: Limit the maximum number of employees per shift (using the variable shifts)
    for shift in range(NUM_SHIFTS):
        shift_employees = [shifts[(e, shift)] for e in range(NUM_EMPLOYEES) if any(shift_data[0] == shift for shift_data in employee_availability[employees[e]])]
        if shift_employees:
            model.Add(sum(shift_employees) <= max_employees)

    # Constraint 4: Limit the number of consecutive shifts for an employee
    for e in range(NUM_EMPLOYEES):
        for day in range(len(work_days)):
            for shift in range(shifts_per_day):
                start_shift = day * shifts_per_day + shift
                if start_shift + max_consecutive_shifts < NUM_SHIFTS:
                    model.Add(
                        sum(shifts[(e, s)] 
                            for s in range(start_shift, min(start_shift + max_consecutive_shifts + 1, NUM_SHIFTS)))
                        <= max_consecutive_shifts
                    )

    # Constraint 5: Balancing workload among employees
    shifts_per_employee = []
    for e in range(NUM_EMPLOYEES):
        employee_shifts = sum(shifts[(e, shift)] for shift in range(NUM_SHIFTS))
        shifts_per_employee.append(employee_shifts)
    
    min_shifts_per_employee = model.NewIntVar(0, NUM_SHIFTS, 'min_shifts')
    max_shifts_per_employee = model.NewIntVar(0, NUM_SHIFTS, 'max_shifts')
    model.AddMinEquality(min_shifts_per_employee, shifts_per_employee)
    model.AddMaxEquality(max_shifts_per_employee, shifts_per_employee)

    # Objective: Combining balance, shortage, and preference costs
    BALANCE_WEIGHT = 1000
    SHORTAGE_WEIGHT = 5000
    PREFERENCE_WEIGHT = 100
    balance_cost = max_shifts_per_employee - min_shifts_per_employee
    shortage_cost = sum(total_shortage_cost)
    preference_cost = sum(total_preference_cost)
    
    total_cost = (BALANCE_WEIGHT * balance_cost +
                  SHORTAGE_WEIGHT * shortage_cost +
                  PREFERENCE_WEIGHT * preference_cost)
    
    model.Minimize(total_cost)

    # Solving the model
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0
    status = solver.Solve(model)

    # Update display_schedule to also receive the new variables (assignments)
    textOutput = display_schedule(solver, shifts, assignments, availability_dict, role_shortages, constraints)
    # print("textOutput:", textOutput)
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        constraints["assignments"] = assignments

        formatted_json = format_schedule_output(
            solver, shifts, employees, work_days, shift_names, shifts_per_day, roles_per_shift, constraints
        )
        return formatted_json, textOutput

    return None  

def display_schedule(solver, shifts, assignments, availability_dict, role_shortages, constraints):
    """
    Displays a detailed summary of each shift, including assignments by role.
    """
    shift_summaries = []
    employees = list(constraints["employee_skills"].keys())
    shift_names = constraints["shift_names"]
    shifts_per_day = constraints["shifts_per_day"]
    work_days = constraints["work_days"]
    roles_per_shift = constraints["roles_per_shift"]
    NUM_SHIFTS = shifts_per_day * len(work_days)

    for shift in range(NUM_SHIFTS):
        lines = []
        day = work_days[shift // shifts_per_day]
        shift_name = shift_names[shift % shifts_per_day]
        
        lines.append(f"{day.upper()} - {shift_name.upper()}")
        lines.append("=" * 30)
        
        # 1. Role requirements
        shift_roles = roles_per_shift[shift_name]
        lines.append("Required Roles:")
        for role, count in shift_roles.items():
            lines.append(f"  • {role.capitalize()}: {count} needed")
        
        # 2. Employee assignments by role – using the assignments variables to determine which roles are filled
        lines.append("\nAssigned Employees by Role:")
        assigned_by_role = {role: [] for role in shift_roles.keys()}
        for e, employee in enumerate(employees):
            shift_name = shift_names[shift % shifts_per_day]
            for role in roles_per_shift[shift_name]:
                if (e, shift, role) in assignments and solver.Value(assignments[(e, shift, role)]) == 1:
                    priority = availability_dict.get((employee, shift), 0)
                    assigned_by_role[role].append((employee, priority))
        
        for role in shift_roles.keys():
            lines.append(f"  {role.capitalize()}:")
            if assigned_by_role[role]:
                for emp, priority in sorted(assigned_by_role[role], key=lambda x: x[0]):
                    lines.append(f"    ✓ {emp} (Priority: {priority}/10)")
            else:
                lines.append("    ⚠ No employees assigned")
        
        # 3. Shift Status
        lines.append("\nStaffing Status:")
        has_shortages = False
        shift_status = []
        for role in shift_roles.keys():
            required_count = shift_roles[role]
            # Number of employees assigned to this role
            assigned_count = len(assigned_by_role.get(role, []))
            shortage = required_count - assigned_count
            if shortage > 0:
                status_str = f"⚠ SHORTAGE: Missing {shortage}"
                has_shortages = True
            else:
                status_str = "✓ FULL"
            shift_status.append(f"  {role.capitalize()}: {status_str} ({assigned_count}/{required_count} filled)")
        shift_status.sort(key=lambda x: "SHORTAGE" not in x)
        lines.extend(shift_status)
        
        if has_shortages:
            lines.append("\n⚠ WARNING: This shift has staffing shortages!")
        else:
            lines.append("\n✓ All positions are properly filled for this shift")
        
        shift_summary = "<br>".join(lines)
        shift_summaries.append(shift_summary)
    
    return shift_summaries
