from django.core.management.base import BaseCommand
from attendance_app.models import Student
import json

class Command(BaseCommand):
    help = 'Generate face encodings for students who have a photo but no encoding.'

    def handle(self, *args, **options):
        import sys
        import os
        # Add the site-packages directory to sys.path to ensure face_recognition_models is found
        site_packages_path = '/home/sujjalbtw/Projects/Smart-Attendance-System/venv/lib/python3.13/site-packages'
        if site_packages_path not in sys.path:
            sys.path.insert(0, site_packages_path)

        import face_recognition
        import numpy as np

        students_to_process = Student.objects.filter(photo__isnull=False).filter(face_encoding__isnull=True)
        self.stdout.write(self.style.SUCCESS(f'Found {len(students_to_process)} students to process.'))

        for student in students_to_process:
            self.stdout.write(f'Processing {student.roll_number}...')
            try:
                image = face_recognition.load_image_file(student.photo.path)
                encodings = face_recognition.face_encodings(image)
                if encodings:
                    student.face_encoding = json.dumps(encodings[0].tolist())
                    student.save()
                    self.stdout.write(self.style.SUCCESS(f'  Successfully generated encoding for {student.roll_number}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  Could not find a face in the photo for {student.roll_number}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  An error occurred for {student.roll_number}: {e}'))
