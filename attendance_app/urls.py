from django.urls import path
from .views import HomeView, QRScanView, FaceRecognitionView, verify_face, export_attendance

app_name = 'attendance_app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('qr-scan/', QRScanView.as_view(), name='qr_scan'),
    path('face-recognition/', FaceRecognitionView.as_view(), name='face_recognition'),
    path('verify-face/', verify_face, name='verify_face'),
    path('export/', export_attendance, name='export_attendance'),
]