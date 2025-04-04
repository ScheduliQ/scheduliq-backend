from ortools.sat.python import cp_model
from app.algorithm.format import format_schedule_output,format_schedule_input  # ייבוא הפונקציה
from models.manager_settings_model import get_manager_settings

"""
This script uses Google OR-Tools to generate an optimized employee shift schedule. 
It accounts for employee availability, skills, and preferences while enforcing various constraints and minimizing operational inefficiencies.

## Overview:
The scheduling algorithm assigns employees to shifts over a predefined period (e.g., a week) while considering:
- Employee availability and preference priorities.
- Required roles for each shift.
- Constraints on employee assignments, such as:
  - Maximum number of employees per shift.
  - Employees cannot work more than one role per shift.
  - Employees cannot work consecutive shifts beyond a specified limit.
- Balancing workload across employees to ensure fairness.

## Functions:
1. `parse_json_to_constraints()`: 
   - Parses predefined JSON-like data to extract shift requirements, employee skills, availability, and other constraints.
   - Returns structured data for the scheduling algorithm.

2. `solve_schedule()`:
   - Builds the optimization model using OR-Tools' `CpModel`.
   - Defines decision variables, including:
     - `shifts`: Binary variables representing whether an employee is assigned to a specific shift.
     - `role_shortages`: Integer variables tracking unmet role requirements per shift.
   - Implements constraints:
     - Employee availability: Employees can only be assigned to shifts they are available for.
     - Maximum employees per shift.
     - Role fulfillment: Ensures that required roles are filled for each shift, allowing for shortages with penalties.
     - Consecutive shift limits: Prevents employees from working beyond the maximum allowed consecutive shifts.
     - One role per employee per shift: An employee cannot occupy more than one role in the same shift.
     - Fair workload distribution: Balances the number of shifts assigned to each employee.
   - Defines a multi-objective cost function to:
     - Minimize workload imbalance.
     - Minimize role shortages based on role importance.
     - Minimize deviation from employee shift preferences.
   - Solves the model using OR-Tools' constraint programming solver.

3. `display_schedule()`:
   - Generates a human-readable schedule, showing:
     - Assigned employees for each role in every shift.
     - Priority scores of assigned employees.
     - Highlighted staffing shortages for roles.
   - Summarizes total shortages and role-specific shortages across all shifts.

4. `main()`:
   - Orchestrates the workflow by:
     - Parsing constraints.
     - Solving the scheduling problem.
     - Displaying the resulting schedule and shortage summary.

## Key Features:
- **Dynamic Employee Preferences**: Accounts for priority scores in employee availability, allowing preferences to influence the schedule.
- **Flexible Role Management**: Ensures all required roles are filled (or penalizes shortages) while respecting employee skills.
- **Load Balancing**: Distributes shifts fairly among employees, ensuring no single employee is overburdened.
- **Constraint Enforcement**: Prevents employees from taking on multiple roles in the same shift or working excessive consecutive shifts.

## Optimization Goal:
Minimize the total cost function, which is a weighted combination of:
1. Imbalance in the number of shifts per employee.
2. Role shortages, weighted by the importance of each role.
3. Deviations from employee preferences for shifts.

## Applications:
This script is designed for scheduling tasks in industries such as hospitality, retail, healthcare and more,
where shifts need to be assigned efficiently while considering complex constraints and employee preferences.

"""

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
    # data1 = {
    #     "employee_skills": {
    #         "Alice": ["manager", "waiter"],
    #         "Bob": ["bartender"],
    #         "Charlie": ["cleaner", "bartender"],
    #         "Diana": ["manager", "cleaner"],
    #         "Eve": ["waiter", "cleaner"],
    #         "Frank": ["manager", "bartender"],
    #         "Grace": ["waiter"],
    #     },
    #     "employee_availability": {
    #         "Alice": [[0, 8], [1, 7], [2, 10], [3, 6], [4, 9], [5, 8], [6, 10]],
    #         "Bob": [[7, 5], [8, 7], [9, 9], [10, 8], [11, 6], [12, 7], [13, 10]],
    #         "Charlie": [[14, 6], [15, 8], [16, 7], [17, 9], [18, 10], [19, 6], [20, 8]],
    #         "Diana": [[0, 10], [3, 7], [6, 9], [9, 6], [12, 8], [15, 7], [18, 10]],
    #         "Eve": [[1, 6], [4, 8], [7, 10], [10, 9], [13, 7], [16, 6], [19, 8]],
    #         "Frank": [[2, 8], [5, 9], [8, 7], [11, 10], [14, 8], [17, 6], [20, 9]],
    #         "Grace": [[0, 3], [6, 8], [7, 9], [12, 10], [14, 6], [18, 7], [20, 10]],
    #     },
    #     "shifts_per_day": 3,
    #     "shift_length": 8,
    #     "shift_names": ["Morning", "Evening", "Night"],
    #     "work_days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    #     "min_max_employees_per_shift": {"min": 2, "max": 4},
    #     "roles_per_shift": {
    #         "Morning": {"manager": 1, "waiter": 1},
    #         "Evening": {"manager": 1, "bartender": 1},
    #         "Night": {"manager": 1, "cleaner": 1},
    #     },
    #     "max_consecutive_shifts": 2,
    #     "role_importance": {
    #         "manager": 5,
    #         "waiter": 4,
    #         "bartender": 3,
    #         "cleaner": 2,
    #     }
    # }
    return data

def solve_schedule():
    # Create the model
    model = cp_model.CpModel()
    
    # Reading data
    constraints = parse_json_to_constraints()
    employee_skills = constraints["employee_skills"]
    print("employee_skills:", employee_skills)
    employees = list(employee_skills.keys())
    print("employees:", employees)
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

    # Convert availability data into a more convenient structure
    availability_dict = {}  # Mapping (employee, shift) -> priority
    for employee_name, shifts_data in constraints["employee_availability"].items():
        for shift_id, priority in shifts_data:
            availability_dict[(employee_name, shift_id)] = priority

    # Decision variables
    shifts = {}
    for employee in range(NUM_EMPLOYEES):
        for shift in range(NUM_SHIFTS):
            shifts[(employee, shift)] = model.NewBoolVar(f'shift_{employee}_{shift}')

    # Shortage variables for each role in each shift
    role_shortages = {}
    for shift in range(NUM_SHIFTS):
        shift_name = shift_names[shift % shifts_per_day]
        for role, required_count in roles_per_shift[shift_name].items():
            role_shortages[(shift, role)] = model.NewIntVar(
                0, required_count, f'shortage_{shift}_{role}'
            )

    # Constraint 1: Employee availability with consideration for priorities
    total_preference_cost = []
    for employee_index, employee_name in enumerate(employees):
        for shift in range(NUM_SHIFTS):
            # אם העובד לא זמין בכלל למשמרת זו
            if not any(shift_data[0] == shift for shift_data in employee_availability[employee_name]):
                model.Add(shifts[(employee_index, shift)] == 0)
            else:
                # מציאת העדיפות למשמרת זו
                priority = availability_dict.get((employee_name, shift), 0)
                # חישוב "עלות" השיבוץ (10 - עדיפות, כך שעדיפות גבוהה = עלות נמוכה)
                shift_cost = (10 - priority) * shifts[(employee_index, shift)]
                total_preference_cost.append(shift_cost)


# Constraint 2: Minimum and maximum number of employees per shift
    for shift in range(NUM_SHIFTS):
        shift_employees = []
        for employee in range(NUM_EMPLOYEES):
            if any(shift_data[0] == shift for shift_data in employee_availability[employees[employee]]):
                shift_employees.append(shifts[(employee, shift)])
        if shift_employees:
            # מאפשרים חריגה מהמינימום אבל עם עלות
            model.Add(sum(shift_employees) <= max_employees)


    # Constraint 3: Role requirements for each shift (with allowance for shortages)
    total_shortage_cost = []
    for shift in range(NUM_SHIFTS):
        shift_name = shift_names[shift % shifts_per_day]
        role_requirements = roles_per_shift[shift_name]
        
        for role, required_count in role_requirements.items():
            role_employees = []
            for employee_index, employee_name in enumerate(employees):
                if role in employee_skills[employee_name] and any(shift_data[0] == shift for shift_data in employee_availability[employee_name]):
                    role_employees.append(shifts[(employee_index, shift)])
            
            if role_employees:
                # מספר העובדים בפועל + החוסר = הדרישה
                model.Add(sum(role_employees) + role_shortages[(shift, role)] == required_count)
                
                # הוספת עלות לחוסר בתפקיד זה
                shortage_cost = role_shortages[(shift, role)] * role_importance[role]
                total_shortage_cost.append(shortage_cost)

    # Constraint 4: Maximum consecutive shifts
    for employee in range(NUM_EMPLOYEES):
        for day in range(len(work_days)):
            for shift in range(shifts_per_day):
                start_shift = day * shifts_per_day + shift
                if start_shift + max_consecutive_shifts < NUM_SHIFTS:
                    model.Add(
                        sum(shifts[(employee, s)] 
                            for s in range(start_shift, min(start_shift + max_consecutive_shifts + 1, NUM_SHIFTS)))
                        <= max_consecutive_shifts
                    )

    # Constraint 5: Balancing workload among employees
    min_shifts_per_employee = model.NewIntVar(0, NUM_SHIFTS, 'min_shifts')
    max_shifts_per_employee = model.NewIntVar(0, NUM_SHIFTS, 'max_shifts')
    
    shifts_per_employee = []
    for employee in range(NUM_EMPLOYEES):
        employee_shifts = sum(shifts[(employee, shift)] for shift in range(NUM_SHIFTS))
        shifts_per_employee.append(employee_shifts)
    
    model.AddMinEquality(min_shifts_per_employee, shifts_per_employee)
    model.AddMaxEquality(max_shifts_per_employee, shifts_per_employee)

    # Constraint 6: Employees cannot work in more than one role simultaneously in a shift
    for shift in range(NUM_SHIFTS):
        for employee_index, employee_name in enumerate(employees):
            roles_in_shift = []
            for role in roles_per_shift[shift_names[shift % shifts_per_day]].keys():
                if role in employee_skills[employee_name]:
                    roles_in_shift.append(shifts[(employee_index, shift)])
            if roles_in_shift:
                model.Add(sum(roles_in_shift) <= 1)


    # Combined objective function:
    balance_cost = max_shifts_per_employee - min_shifts_per_employee
    shortage_cost = sum(total_shortage_cost)
    preference_cost = sum(total_preference_cost)
    
    # Weights for each component in the objective
    BALANCE_WEIGHT = 1000  # High weight for workload balance
    SHORTAGE_WEIGHT = 500  # Medium weight for shortages
    PREFERENCE_WEIGHT = 100  # Lower weight for preferences
    
    total_cost = (BALANCE_WEIGHT * balance_cost + 
                 SHORTAGE_WEIGHT * shortage_cost + 
                 PREFERENCE_WEIGHT * preference_cost)
    
    model.Minimize(total_cost)

    # Solution
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 60.0
    status = solver.Solve(model)
    textOutput=display_schedule(solver, shifts, availability_dict, role_shortages, constraints)
    # splitted_output = textOutput.split("here")

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        formatted_json = format_schedule_output(
            solver, shifts, employees, work_days, shift_names, shifts_per_day, roles_per_shift,constraints
        )
        
        return formatted_json,textOutput  

    return None  
def display_schedule(solver, shifts, availability_dict, role_shortages, constraints):
    """
    Returns a list of strings, each representing one shift's summary.
    """
    shift_summaries = []
    employees = list(constraints["employee_skills"].keys())
    shift_names = constraints["shift_names"]
    shifts_per_day = constraints["shifts_per_day"]
    work_days = constraints["work_days"]
    roles_per_shift = constraints["roles_per_shift"]
    NUM_SHIFTS = shifts_per_day * len(work_days)

    for shift in range(NUM_SHIFTS):
        lines = []  # Hold the summary for the current shift.
        day = work_days[shift // shifts_per_day]
        shift_name = shift_names[shift % shifts_per_day]
        
        lines.append(f"{day.upper()} - {shift_name.upper()}")
        lines.append("=" * 30)
        
        # 1. Display required roles.
        shift_roles = roles_per_shift[shift_name]
        lines.append("Required Roles:")
        for role, count in shift_roles.items():
            lines.append(f"  • {role.capitalize()}: {count} needed")
        
        # 2. Display assigned employees by role.
        lines.append("\nAssigned Employees by Role:")
        assigned_by_role = {}
        for employee_index, employee_name in enumerate(employees):
            if solver.Value(shifts[(employee_index, shift)]) == 1:
                employee_roles = constraints["employee_skills"][employee_name]
                for role in employee_roles:
                    if role not in assigned_by_role:
                        assigned_by_role[role] = []
                    assigned_by_role[role].append(employee_name)
        for role in shift_roles.keys():
            lines.append(f"  {role.capitalize()}:")
            if role in assigned_by_role and assigned_by_role[role]:
                for emp in sorted(assigned_by_role[role]):
                    priority = availability_dict.get((emp, shift), 0)
                    lines.append(f"    ✓ {emp} (Priority: {priority}/10)")
            else:
                lines.append("    ⚠ No employees assigned")
        
        # 3. Display staffing status.
        lines.append("\nStaffing Status:")
        has_shortages = False
        shift_status = []
        for role in shift_roles.keys():
            required_count = shift_roles[role]
            assigned_count = len(assigned_by_role.get(role, []))
            shortage = required_count - assigned_count
            if shortage > 0:
                status_str = f"⚠ SHORTAGE: Missing {shortage}"
                has_shortages = True
            else:
                status_str = "✓ FULL"
            shift_status.append(f"  {role.capitalize()}: {status_str} ({assigned_count}/{required_count} filled)")
        # Sort status so that shortages appear first.
        shift_status.sort(key=lambda x: "SHORTAGE" not in x)
        lines.extend(shift_status)
        
        if has_shortages:
            lines.append("\n⚠ WARNING: This shift has staffing shortages!")
        else:
            lines.append("\n✓ All positions are properly filled for this shift")
        
        # Join the lines for the current shift summary and add it to the list.
        shift_summary = "<br>".join(lines)
        shift_summaries.append(shift_summary)
    
    return shift_summaries
        # print("\n" + "-" * 50)

# def main():
#     constraints = parse_json_to_constraints()
#     solver, shifts,availability_dict, role_shortages, found_solution = solve_schedule()
    
#     if found_solution:
#         print("\nSolution found!")
        
#         # חישוב סך כל החוסרים
#         total_shortages = 0
#         shortages_by_role = {}
        
#         for shift in range(len(constraints["work_days"]) * constraints["shifts_per_day"]):
#             shift_name = constraints["shift_names"][shift % constraints["shifts_per_day"]]
#             for role, required_count in constraints["roles_per_shift"][shift_name].items():
#                 if solver is not None and role_shortages is not None:
#                     current_shortage = solver.Value(role_shortages[(shift, role)])
#                     total_shortages += current_shortage
                    
#                     if current_shortage > 0:
#                         if role not in shortages_by_role:
#                             shortages_by_role[role] = 0
#                         shortages_by_role[role] += current_shortage
        
#         if total_shortages > 0:
#             print("\n⚠ Staffing Shortages Summary:")
#             print(f"Total shortages across all shifts: {total_shortages}")
#             print("\nBreakdown by role:")
#             for role, count in sorted(shortages_by_role.items()):
#                 print(f"  • {role.capitalize()}: {count} missing positions")
#         else:
#             print("\n✓ Perfect solution found with no staffing shortages!")
            
#         display_schedule(solver, shifts,availability_dict, role_shortages, constraints)
#     else:
#         print("No solution found.")

# if __name__ == "__main__":
#     main()