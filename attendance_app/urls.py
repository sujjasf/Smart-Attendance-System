from django.urls import path
from .views import HomeView, QRScanView, verify_face, export_attendance

app_name = 'attendance_app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('qr-scan/', QRScanView.as_view(), name='qr_scan'),
    path('verify-face/', verify_face, name='verify_face'),
    path('export/', export_attendance, name='export_attendance'),
]