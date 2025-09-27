from django.shortcuts import render, redirect
from django.views import View
from .models import Student, Attendance
import cv2
from pyzbar.pyzbar import decode
import numpy as np

class HomeView(View):
    def get(self, request):
        return render(request, 'attendance_app/home.html')

class QRScanView(View):
    def get(self, request):
        return render(request, 'attendance_app/qr_scan.html')
    
    def post(self, request):
        image_file = request.FILES.get('image')
        if image_file:
            try:
                image_data = np.frombuffer(image_file.read(), np.uint8)
                image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

                if image is None:
                    return render(request, 'attendance_app/qr_scan.html', {'error': 'Could not decode image.'})

                decoded_objects = decode(image)

                if decoded_objects:
                    roll_number = decoded_objects[0].data.decode('utf-8')
                    try:
                        student = Student.objects.get(roll_number=roll_number)
                        Attendance.objects.create(student=student, verification_method='QR')
                        return render(request, 'attendance_app/qr_scan.html', {'success': f'Attendance marked for {student.name}'})
                    except Student.DoesNotExist:
                        return render(request, 'attendance_app/qr_scan.html', {'error': f'Student with roll number {roll_number} not found.'})
                else:
                    return render(request, 'attendance_app/qr_scan.html', {'error': 'No QR Code found.'})
            except Exception as e:
                return render(request, 'attendance_app/qr_scan.html', {'error': str(e)})

        return render(request, 'attendance_app/qr_scan.html', {'error': 'No image file found.'})

class FaceRecognitionView(View):
    def get(self, request):
        return render(request, 'attendance_app/face_recognition.html')
    
    def post(self, request):
        # Face recognition logic here
        pass
