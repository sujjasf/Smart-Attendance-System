from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'roll_number', 'email', 'created_at']
    search_fields = ['name', 'roll_number', 'email']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'date', 'time', 'verification_method']
    list_filter = ['date', 'verification_method']
    search_fields = ['student__name', 'student__roll_number']