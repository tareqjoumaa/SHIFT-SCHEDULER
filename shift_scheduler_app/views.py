# views.py
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import *
import csv
from django.core.mail import send_mail
from .forms import ShiftSchedulerForm
from datetime import datetime, timedelta
from django.conf import settings
from celery.schedules import crontab
from celery import shared_task

def shift_scheduler(request):
    if request.method == 'POST':
        form = ShiftSchedulerForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            employees_count = form.cleaned_data['employees_count']
            from_time = form.cleaned_data['from_time']
            to_time = form.cleaned_data['to_time']

            employees_to_schedule = Employee.objects.all()[:employees_count]

            current_date = start_date
            while current_date <= end_date:
                for employee in employees_to_schedule:
                    EmployeeShift.objects.create(
                        employee=employee,
                        location_id=form.cleaned_data['location'].pk,
                        date=current_date,
                        from_time=from_time,
                        to_time=to_time,
                    )
                current_date += timedelta(days=1)

            return redirect('shift_scheduler')

    else:
        form = ShiftSchedulerForm()

    return render(request, 'shift_scheduler.html', {'form': form})


def schedule_report(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)

        shifts = EmployeeShift.objects.filter(date__range=(start_date, end_date))

        report_data = []
        for shift in shifts:
            report_data.append({
                'employee_id': shift.employee.id,
                'employee_name': shift.employee.full_name,
                'location': shift.location.name,
                'date': shift.date,
                'from_time': shift.from_time,
                'to_time': shift.to_time,
                'department': shift.employee.department,
            })

        csv_filename = 'schedule_report.csv'
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{csv_filename}"'
        
        csv_writer = csv.writer(response)
        csv_writer.writerow(['Employee ID', 'Employee Name', 'Location', 'Date', 'From Time', 'To Time', 'Department'])
        for data in report_data:
            csv_writer.writerow([data['employee_id'], data['employee_name'], data['location'], data['date'],
                                 data['from_time'], data['to_time'], data['department']])

        email_address = request.POST.get('email_address')
        subject = 'Schedule Report'
        message = 'Please find attached the schedule report.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email_address]

        send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=None, attachment=[('schedule_report.csv', response.content, 'text/csv')])

        return response

    return render(request, 'schedule_report_form.html')


@shared_task
def generate_daily_report():
    current_date = datetime.now().date()
    shifts = EmployeeShift.objects.filter(date=current_date)

    report_data = []
    for shift in shifts:
        report_data.append({
            'employee_id': shift.employee.id,
            'employee_name': shift.employee.full_name,
            'location': shift.location.name,
            'date': shift.date,
            'from_time': shift.from_time,
            'to_time': shift.to_time,
            'department': shift.employee.department,
        })

    csv_filename = f'daily_report_{current_date}.csv'
    csv_path = f'/tmp/{csv_filename}' 
    with open(csv_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Employee ID', 'Employee Name', 'Location', 'Date', 'From Time', 'To Time', 'Department'])
        for data in report_data:
            csv_writer.writerow([data['employee_id'], data['employee_name'], data['location'], data['date'],
                                data['from_time'], data['to_time'], data['department']])

    email_address = 'tareqjoumaa4@email.com'  
    subject = f'Daily Schedule Report - {current_date}'
    message = 'Please find attached the daily schedule report.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [email_address]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=None, attachment=[(csv_filename, open(csv_path).read(), 'text/csv')])


@periodic_task(run_every=(crontab(hour=0, minute=30)), name="generate_daily_report_task")
def generate_daily_report_task():
    generate_daily_report.delay()


