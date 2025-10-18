import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.conf import settings
from attendance_app.models import Student

class Command(BaseCommand):
    help = 'Generate QR code for a student (stores image in student.qr_code)'

    def add_arguments(self, parser):
        parser.add_argument('--roll', type=str, help='The roll_number of the student')

    def handle(self, *args, **options):
        roll = options['roll']
        if not roll:
            self.stdout.write(self.style.ERROR('Please provide a roll_number using --roll argument.'))
            return

        try:
            student = Student.objects.get(roll_number=roll)
        except Student.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Student with roll_number "{roll}" does not exist.'))
            return

        # Payload stored in QR: use roll_number (keep minimal)
        qr_payload = student.roll_number
        qr_img = qrcode.make(qr_payload)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)

        # Save to the ImageField
        filename = f'{student.roll_number}_qr.png'
        student.qr_code.save(filename, ContentFile(buffer.read()), save=True)

        self.stdout.write(self.style.SUCCESS(f'Successfully generated QR code for {student.name} ({student.roll_number})'))
