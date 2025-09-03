from django.shortcuts import render, redirect
from integration_utils.bitrix24.bitrix_user_auth.main_auth import main_auth
from datetime import datetime, timedelta


# Create your views here.
@main_auth(on_cookies=True)
def list_employees(request):
    but = request.bitrix_user_token
    departments = but.call_api_method('department.get', {}).get('result', {})
    department_ids = [x.get('ID') for x in departments]

    employees = but.call_api_method('im.department.employees.get', {
        'ID': department_ids,
        'USER_DATA': 'Y',
    }).get('result', {})

    managers = but.call_api_method('im.department.managers.get', {
        'ID': department_ids,
        'USER_DATA': 'Y'
    }).get('result', {})

    since = (datetime.now() - timedelta(hours=24)).isoformat()

    calls = but.call_api_method('voximplant.statistic.get', {
        'FILTER': {
            ">=CALL_DURATION": 60,
            "CALL_TYPE": 1,
            ">CALL_START_DATE": since
        },
    }).get('result', {})

    calls_count = {}
    for call in calls:
        user_id = call.get('PORTAL_USER_ID')
        if user_id:
            calls_count[user_id] = calls_count.get(user_id, 0) + 1

    tree = build_tree(employees, managers, departments, calls_count)

    unique_employees = []
    for dep in tree:
        for emp in dep['employees']:
            temp_emp = {'id': emp['id'], 'name': emp['name']}
            if temp_emp not in unique_employees:
                unique_employees.append(temp_emp)

    return render(request, 'employees/index.html', {'tree': tree, 'unique_employees': unique_employees})


def build_tree(employees, managers, departments, calls_count):
    emp_map = {}
    for dep, emps in employees.items():
        for e in emps:
            emp_map[e["id"]] = e

    def get_manager_chain(emp):
        chain = []
        visited = set()
        visited.add(emp['id'])

        def climb(e):
            for dep_id in e.get("departments", []):
                for mgr in managers.get(str(dep_id), []):
                    if mgr["id"] not in visited:
                        visited.add(mgr["id"])
                        chain.append(mgr["name"])
                        climb(mgr)

        climb(emp)
        return chain

    result = []
    for dep in departments:
        dep_id = dep['ID']
        dep_name = dep['NAME']

        emps_data = []
        for emp in employees.get(dep_id, []):
            chain = get_manager_chain(emp)
            emps_data.append({
                'id': emp['id'],
                'name': emp['name'],
                'work_position': emp.get('work_position', ''),
                'departments': emp.get('departments', ''),
                'managers': chain,
                'calls_count': calls_count.get(str(emp['id']), 0)
            })

        if emps_data:
            result.append({
                'department': dep_name,
                'employees': emps_data
            })

    return result


@main_auth(on_cookies=True)
def add_call(request):
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        duration = int(request.POST.get("minutes"))*60+int(request.POST.get("seconds"))

        but = request.bitrix_user_token

        call_start = datetime.now().isoformat()

        call = but.call_api_method('telephony.externalcall.register', {
            "USER_ID": user_id,
            "PHONE_NUMBER": "+79995553535",
            "CALL_START_DATE": call_start,
            "CRM_CREATE": 0,
            "TYPE": 1,
            "SHOW": 0
        })

        call_id = call.get("result", {}).get("CALL_ID")

        but.call_api_method('telephony.externalcall.finish', {
            "CALL_ID": call_id,
            "USER_ID": user_id,
            "DURATION": duration,
        })

    return redirect('employees_index')

