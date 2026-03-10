from django.urls import path
from .views import StaffRegister, ManageBookViaStaff

urlpatterns = [
    path('staffs/', StaffRegister.as_view()),
    path('staff-books/', ManageBookViaStaff.as_view()),
]