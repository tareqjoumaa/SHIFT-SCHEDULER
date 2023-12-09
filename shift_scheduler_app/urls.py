from django.urls import path, include
from . import views
from .views import *


urlpatterns = [
    path('shift_scheduler/', shift_scheduler, name='shift_scheduler'),
    path('schedule_report/', schedule_report, name='schedule_report'),

]