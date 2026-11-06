from django.shortcuts import render

def home(request):
    context = {
        'system_name': 'Hostel Management System',
        'student_name': 'Bhavesh',
        'total_rooms': 50,
    }
    return render(request, 'core/home.html')

def student_dashboard(request):
    context = {
        'student_name': 'Rahul',
        'room_number': 205,
        'hostel_name': 'Xavier Hostel',
        'is_active': True,
        'subjects': [
            'Python',
            'DBMS',
            'Java',
            'Web Development'
        ]
    }
    return render(request, 'core/student_dashboard.html', context)