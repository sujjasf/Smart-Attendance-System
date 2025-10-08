# Smart Attendance System

A Django-based attendance system using QR codes and facial recognition.

## Setup

source venv/bin/activate
echo $VIRTUAL_ENV
1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure environment:**
    - Copy `.env.example` to `.env`
    - Fill in the database credentials and a secret key in the `.env` file.

3.  **Run migrations:**
    ```bash
    python manage.py migrate
    ```

4.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```