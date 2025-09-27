import os
import qrcode
from django.core.management.base import BaseCommand
from django.conf import settings
from attendance_app.models import Student

class Command(BaseCommand):
    help = 'Generate QR code for a student'

    def add_arguments(self, parser):
        parser.add_argument('--student', type=str, help='The student_id of the student')

    def handle(self, *args, **options):
        student_id = options['student']
        if not student_id:
            self.stdout.write(self.style.ERROR('Please provide a student_id using --student argument.'))
            return

        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Student with student_id "{student_id}" does not exist.'))
            return

        qr_data = student.student_id
        qr_code_image = qrcode.make(qr_data)

        # Ensure the media directory exists
        qr_code_dir = os.path.join(settings.MEDIA_ROOT, 'qrcodes')
        os.makedirs(qr_code_dir, exist_ok=True)

        # Save the QR code image
        qr_code_filename = f'{student.student_id}.png'
        qr_code_path = os.path.join(qr_code_dir, qr_code_filename)
        qr_code_image.save(qr_code_path)

        # Update the student's qr_data field
        student.qr_data = os.path.join('qrcodes', qr_code_filename)
        student.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully generated QR code for {student.full_name} ({student.student_id})'))