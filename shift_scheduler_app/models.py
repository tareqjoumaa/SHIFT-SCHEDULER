from django.db import models

# Create your models here.

class Location(models.Model):
    name = models.CharField(max_length=255, primary_key=True)

class Employee(models.Model):
    full_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE, default=1)

class EmployeeShift(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField()
    from_time = models.TimeField()
    to_time = models.TimeField()