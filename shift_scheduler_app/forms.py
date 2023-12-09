from django import forms
from .models import EmployeeShift , Location

class ShiftSchedulerForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
    employees_count = forms.IntegerField(min_value=1, max_value=100)
    from_time = forms.TimeField()
    to_time = forms.TimeField()
    location = forms.ModelChoiceField(queryset=Location.objects.all())
