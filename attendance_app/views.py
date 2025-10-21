from django.shortcuts import render, redirect
from django.views import View
from .models import Student, Attendance
import cv2
from pyzbar.pyzbar import decode
import numpy as np
import json
import os
from django.http import JsonResponse, HttpResponse
from django.core.files.base import ContentFile
import base64
import time
import pandas as pd
import dlib

# Load dlib's shape predictor
shape_predictor_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.. ', 'easy_facial_recognition', 'pretrained_model', 'shape_predictor_68_face_landmarks.dat')
shape_predictor = dlib.shape_predictor(shape_predictor_path)


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
                    return JsonResponse({'status': 'error', 'message': 'Could not decode image.'})

                decoded_objects = decode(image)

                if decoded_objects:
                    student_id = decoded_objects[0].data.decode('utf-8')
                    return JsonResponse({'status': 'ok', 'student_id': student_id})
                else:
                    return JsonResponse({'status': 'no_qr', 'message': 'No QR Code found.'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)})

        return JsonResponse({'status': 'error', 'message': 'No image file found.'})



def verify_face(request):
    import face_recognition
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        image_data_url = request.POST.get('image')

        try:
            student = Student.objects.get(roll_number=student_id)
            stored_encoding = json.loads(student.face_encoding)
        except (Student.DoesNotExist, json.JSONDecodeError):
            return JsonResponse({'match': False, 'error': 'Invalid student data.'})

        format, imgstr = image_data_url.split(';base64,') 
        ext = format.split('/')[-1] 
        image_data = ContentFile(base64.b64decode(imgstr), name=f'{student_id}_{int(time.time())}.{ext}')

        # Convert to numpy array for face_recognition
        image_array = cv2.imdecode(np.frombuffer(image_data.read(), np.uint8), cv2.IMREAD_COLOR)

        # Find face locations and encodings
        face_locations = face_recognition.face_locations(image_array)
        print("Face locations:", face_locations)

        if not face_locations:
            print("No face detected.")
            return JsonResponse({'match': False, 'error': 'No face detected in the image.'})

        # Send face location and landmarks to frontend
        top, right, bottom, left = face_locations[0]
        face_location = {'top': top, 'right': right, 'bottom': bottom, 'left': left}
        print("Face location found:", face_location)

        # Get facial landmarks
        shape = shape_predictor(image_array, dlib.rectangle(left, top, right, bottom))
        landmarks = [(p.x, p.y) for p in shape.parts()]


        live_encoding = face_recognition.face_encodings(image_array, face_locations)[0]

        # Compare faces
        match = face_recognition.compare_faces([stored_encoding], live_encoding, tolerance=0.5)
        distance = face_recognition.face_distance([stored_encoding], live_encoding)[0]

        if match[0]:
            # Mark attendance
            Attendance.objects.create(
                student=student,
                status='PRESENT',
                snapshot=image_data,
                confidence=distance
            )
            response_data = {'match': True, 'confidence': distance, 'face_location': face_location, 'landmarks': landmarks}
            print("Response:", response_data)
            return JsonResponse(response_data)
        else:
            # Mark as failed match
            Attendance.objects.create(
                student=student,
                status='FAILED_MATCH',
                snapshot=image_data,
                confidence=distance
            )
            response_data = {'match': False, 'confidence': distance, 'face_location': face_location, 'landmarks': landmarks}
            print("Response:", response_data)
            return JsonResponse(response_data)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)

def export_attendance(request):
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    student_id = request.GET.get('student_id')

    attendance_records = Attendance.objects.all()

    if student_id:
        attendance_records = attendance_records.filter(student__student_id=student_id)
    if date_from:
        attendance_records = attendance_records.filter(timestamp__date__gte=date_from)
    if date_to:
        attendance_records = attendance_records.filter(timestamp__date__lte=date_to)

    df = pd.DataFrame(list(attendance_records.values(
        'student__student_id', 'student__full_name', 'timestamp', 'status', 'confidence'
    )))

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=attendance.xlsx'

    df.to_excel(response, index=False)

    return response
