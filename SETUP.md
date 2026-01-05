# SAYHITOFIT - Contact Form with FastAPI Backend

This project now includes a FastAPI backend for handling contact form submissions securely and storing responses in a JSON file.

## Setup Instructions

### 1. Install Python Dependencies

Make sure you have Python 3.7+ installed. Then install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Run the FastAPI Backend

Start the FastAPI server:

```bash
python main.py
```

The server will run on `http://localhost:8000`

You can verify it's running by visiting: `http://localhost:8000/docs` (Swagger UI for API documentation)

### 3. Open the Website

Open your browser and navigate to the website's `index.html` file in the `src` folder.

## How It Works

### Contact Form Flow

1. **User submits the contact form** with their name, email, and message
2. **JavaScript sends the data** to the FastAPI backend via a POST request to `/api/contact`
3. **FastAPI validates the input** (checks for valid email format)
4. **Data is stored** in a `contacts.json` file in the project root directory
5. **Success message** is displayed to the user with a smooth animation
6. **Form is cleared** automatically after submission

### Response Format

When a contact form is submitted successfully, the response looks like:

```json
{
  "success": true,
  "message": "Your message has been recorded successfully!",
  "contact_id": 1
}
```

### Stored Data Format

Contact submissions are saved in `contacts.json`:

```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Great program!",
    "timestamp": "2025-12-17T10:30:00.123456"
  }
]
```

## API Endpoints

### POST /api/contact
Submit a contact form

**Request Body:**
```json
{
  "name": "string",
  "email": "string (valid email format)",
  "message": "string"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Your message has been recorded successfully!",
  "contact_id": 1
}
```

### GET /api/contacts
Retrieve all contact submissions (for admin purposes)

**Response:**
```json
{
  "success": true,
  "count": 2,
  "contacts": [...]
}
```

## Features

✅ FastAPI backend with CORS support
✅ Email validation using Pydantic
✅ JSON file storage for contact responses
✅ Automatic timestamp for each submission
✅ Smooth success message animation using GSAP
✅ Error handling with user-friendly messages
✅ Form auto-reset after successful submission
✅ Responsive design with Font Awesome icons

## Troubleshooting

### "Could not connect to server" Error

Make sure:
1. The FastAPI backend is running on `http://localhost:8000`
2. No other application is using port 8000
3. Open the browser console (F12) to see detailed error messages

### CORS Issues

The FastAPI backend is configured to allow requests from any origin. If you need to restrict this for production, modify the `allow_origins` parameter in `main.py`.

## File Structure

```
Sayhitofir/
├── main.py                 # FastAPI backend application
├── requirements.txt        # Python dependencies
├── contacts.json          # Stored contact submissions (auto-created)
└── src/
    ├── index.html
    ├── assets/
    │   ├── css/
    │   │   ├── main.css
    │   │   └── styles.css
    │   └── js/
    │       └── main.js
    └── components/
```

## Production Deployment

For production deployment:

1. Change `allow_origins` in `main.py` to your actual domain
2. Use a production ASGI server like Gunicorn
3. Set up a reverse proxy (Nginx) in front of the FastAPI server
4. Use environment variables for configuration
5. Implement proper error logging and monitoring

Example production run:
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Support

For issues or questions, check the console logs and the FastAPI documentation at `http://localhost:8000/docs`

---

**Created**: December 17, 2025
