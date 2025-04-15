# reports_calculations.py

from collections import defaultdict
import json
from models.weekly_schedule_model import WeeklyScheduleModel

def get_all_schedules_from_db():
    """
    Function that imports all schedules from the database.
    You can modify and add filtering by date range or limit the number of documents.
    """
    schedules = WeeklyScheduleModel.get_all_schedules()
    print("Number of schedules fetched:", len(schedules))
    return schedules

def calculate_employee_shift_count(schedules):
    """
    Calculates how many times each employee was assigned to a shift.
    
    :param schedules: A list of schedule documents, where each document contains the field 'days',
                      each day contains the field 'shifts', and each shift contains the field 'employees'.
    :return: A JSON dictionary where each key is an employee's name and the value is the number of times
             the employee appeared in the schedules.
    
    Example output:
    {
      "David Levi": 18,
      "Shira Cohen": 14,
      "Amit Azulay": 22
    }
    """
    employee_counts = defaultdict(int)

    for schedule in schedules:
        days = schedule.get("days", [])
        print("Processing schedule with", len(days), "days")
        for day in days:
            shifts = day.get("shifts", [])
            for shift in shifts:
                employees = shift.get("employees", [])
                for employee in employees:
                    # נניח שהשדה 'name' קיים לכל עובד, אחרת נשתמש בשם 'Unknown'
                    name = employee.get("name", "Unknown")
                    employee_counts[name] += 1

    result = dict(employee_counts)
    print("Employee shift counts:", result)
    return result


def calculate_role_required_vs_assigned(schedules):
    """
    Calculates the actual assignments and required count for each role based on multiple schedules.
    
    For each shift, for each role:
      - Count the actual number of employees assigned to that role.
      - Determine the shortage (if provided); if no shortage is provided, assume shortage is 0.
      - The total required count for that shift is (actual assignments + shortage).
    
    This function aggregates these numbers over all schedules.
    
    :param schedules: List of schedule documents (dictionaries), each containing a "days" field.
                      Each day contains "shifts", where each shift has "employees" (list of employee dicts with "role")
                      and an optional "shortages" dictionary.
    :return: A dictionary mapping each role to a dict with keys:
             - "actual": total count of assigned employees for that role
             - "required": total required count (actual + shortage)
             Example:
             {
               "Waiter": {"actual": 50, "required": 75},
               "Bartender": {"actual": 30, "required": 32},
               "Manager": {"actual": 18, "required": 18}
             }
    """
    actual_counts = defaultdict(int)
    required_counts = defaultdict(int)
    
    # Iterate over each schedule document.
    for schedule in schedules:
        for day in schedule.get("days", []):
            for shift in day.get("shifts", []):
                # Count assignments for each role in this shift.
                shift_role_actual = defaultdict(int)
                for employee in shift.get("employees", []):
                    role = employee.get("role")
                    if role:
                        shift_role_actual[role] += 1
                
                # Get shortages for this shift; if missing, assume empty dict.
                shortages = shift.get("shortages", {})
                
                # For each role that appears either in the assignments or in the shortages,
                # add the counts to the aggregated totals.
                roles_in_shift = set(list(shift_role_actual.keys()) + list(shortages.keys()))
                for role in roles_in_shift:
                    assigned = shift_role_actual.get(role, 0)
                    try:
                        shortage = int(shortages.get(role, 0))
                    except (ValueError, TypeError):
                        shortage = 0
                    actual_counts[role] += assigned
                    # Total required for this shift is the assigned plus the shortage.
                    required_counts[role] += assigned + shortage
                    
    # Prepare the final results dictionary.
    result = {}
    all_roles = set(list(actual_counts.keys()) + list(required_counts.keys()))
    for role in all_roles:
        result[role] = {
            "actual": actual_counts.get(role, 0),
            "required": required_counts.get(role, 0)
        }
    
    return dict(result)

    

def calculate_average_employees_per_shift(schedules):
    """
    Calculates the average number of employees assigned per shift over multiple schedules.
    
    :param schedules: A list of schedule documents, each containing a "days" field.
                      Each day has a "shifts" field with a list of shift dictionaries, where each shift 
                      includes an "employees" list.
    :return: A dictionary with the average number of employees per shift.
             Example: { "ממוצע עובדים למשמרת": 3.4 }
    """
    total_shifts = 0
    total_employees = 0

    # Loop over each schedule
    for schedule in schedules:
        days = schedule.get("days", [])
        # Loop over each day in the schedule
        for day in days:
            shifts = day.get("shifts", [])
            # Loop over each shift
            for shift in shifts:
                employees = shift.get("employees", [])
                total_employees += len(employees)
                total_shifts += 1

    # Calculate average; handle division by zero if no shifts are found
    average = (total_employees / total_shifts) if total_shifts > 0 else 0
    return {"average": round(average, 1)}



def calculate_shifts_by_type(schedules):
    """
    Calculates the count of shifts for each shift type (e.g., Morning, Evening, Night)
    across multiple schedules. The shift type is taken from the "time" field of each shift,
    normalized to lowercase.
    
    :param schedules: A list of schedule documents. Each document contains a "days" field,
                    and each day contains a "shifts" list with each shift having a "time" field.
    :return: A dictionary mapping each shift type to its count.
            Example: { "בוקר": 30, "ערב": 26, "לילה": 8 }
    """
    shift_type_counts = {}

    for schedule in schedules:
        days = schedule.get("days", [])
        for day in days:
            shifts = day.get("shifts", [])
            for shift in shifts:
                # Normalize the shift type to lowercase
                shift_type = shift.get("time", "").strip().lower()
                if shift_type:
                    shift_type_counts[shift_type] = shift_type_counts.get(shift_type, 0) + 1

    return shift_type_counts



