# Post-Conversation Analysis

This is a **Django REST Framework** application built for the **Kipps.AI Internship Assignment**. It performs post-conversation analysis on chat messages, stores the results in a database, and provides API endpoints for uploading chats and retrieving reports.

The system includes **automated daily analysis**, configured to run using a custom management command and **Windows Task Scheduler**, as the suggested tools presented compatibility and complexity issues for this project's scope.

## Features

- **Chat Upload**: API endpoint to upload chat logs in JSON format
- **Conversation Analysis**: Performs analysis on **10+ parameters**, including **Sentiment**, **Resolution**, **Escalation Need**, and **Fallback Frequency**
- **Report Retrieval**: API endpoint to list all conversation analysis results
- **Automated Daily Job**: A custom Django management command (`run_analysis_job`) analyzes all new conversations
- **Database**: Uses **SQLite** for simplicity and rapid setup

## ScreenShots

![alt text](<Screenshot 2025-11-10 143539.png>)

![alt text](<Screenshot 2025-11-10 143727.png>)

## Project Structure

```
kipps-project/
├── analysis_api/
│   ├── management/
│   │   └── commands/
│   │       └── run_analysis_job.py    # Custom command for automation
│   ├── migrations/
│   ├── __init__.py
│   ├── admin.py
│   ├── analyzer.py                    # Core analysis logic
│   ├── apps.py
│   ├── models.py                      # Database models: Conversation, Message, Analysis
│   ├── serializers.py                 # DRF serializers
│   ├── tests.py
│   ├── urls.py                        # App-level API routes
│   └── views.py                       # API endpoint logic
├── kipps/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                    # Project settings
│   ├── urls.py                        # Project-level routes
│   └── wsgi.py
├── venv/
├── .gitignore
├── db.sqlite3                         # The database file
├── manage.py
├── README.md
└── requirements.txt                   # Python dependencies
```

## Setup and Run Instructions

### 1. Prerequisites

- **Python 3.10+**
- **Windows** (for Task Scheduler) or a Unix-like OS (for cron)

### 2. Local Setup

**Clone the repository:**

```bash
git clone <your-github-repo-url>
cd kipps-project
```

**Create and activate a virtual environment:**

```bash
# Create the environment
python -m venv venv

# Activate on Windows
.\venv\Scripts\activate
```

**Install dependencies:**

```bash
pip install -r requirements.txt
```

**Create the database:**

```bash
python manage.py makemigrations
python manage.py migrate
```

**Run the server:**

```bash
python manage.py runserver
```

The application will be running at `http://127.0.0.1:8000/`.

## API Documentation & Postman Testing

You can test all endpoints using an API client like Postman.

**Prerequisite:** Make sure your server is running: `python manage.py runserver`

### 1. Upload a Conversation

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/api/conversations/`

**Body:**
- Select the **Body** tab
- Select the **raw** option
- Choose **JSON** from the dropdown menu
- Paste in your chat JSON:

```json
{
  "messages": [
    {
      "sender": "user",
      "message": "My order is wrong."
    },
    {
      "sender": "ai",
      "message": "I'm not sure I can help with that."
    },
    {
      "sender": "user",
      "message": "This is useless. I want to talk to a human agent right now."
    }
  ]
}
```

**Success Response (201):**

```json
{
  "message": "Conversation uploaded successfully",
  "conversation_id": 1
}
```

### 2. List All Reports

**Method:** `GET`

**URL:** `http://127.0.0.1:8000/api/reports/`

**Body:** None

**Success Response (201):**

Click the "Pretty" tab in Postman to see a formatted list. The `analysis` field for the new conversation will be `null`.

```json
[
    {
        "id": 1,
        "title": "Chat on ...",
        "messages": [ ... ],
        "analysis": null
    }
]
```

### 3. Trigger Manual Analysis

**Method:** `POST`

**URL:** `http://127.0.0.1:8000/api/analyse/`

**Body:**
- Select **Body** → **raw** → **JSON**
- Paste in the ID of the conversation to analyze:

```json
{
  "conversation_id": 1
}
```

**Success Response (201):**

You will get the full analysis object back.

```json
{
    "id": 2,
    "clarity_score": 4.98,
    "relevance_score": 4.41,
    "accuracy_score": 4.5,
    "completeness_score": 4.28,
    "sentiment": "positive",
    "empathy_score": 4.2,
    "response_time_avg": 20.77,
    "resolution": true,
    "escalation_need": false,
    "fallback_frequency": 0,
    "overall_score": 4.62,
    "created_at": "2025-11-09T17:51:22.431122Z"
}
```

## Automation Setup

The project uses a custom management command for daily analysis.

### Tooling Choice (django-crontab vs. Celery vs. Management Command)

The assignment suggested `django-crontab` or Celery Beat. Here is the engineering decision for the chosen method:

**Why not django-crontab?**  
This tool is incompatible with Windows. It has a hard dependency on the `fcntl` Unix module, which does not exist on Windows. Attempting to use it results in a `ModuleNotFoundError`.

**Why not Celery Beat?**  
This is a heavy-duty, industrial-strength distributed task queue. For a 72-hour project, it's unnecessary "overkill." It would require installing, configuring, and running a separate message broker (like Redis or RabbitMQ) and at least two additional 24/7 processes (a Celery worker and a Celery Beat scheduler).

**Chosen Solution: Management Command + OS Scheduler**  
This is the simplest, most robust, and most professional solution for this task.

- `python manage.py run_analysis_job`: We created a custom command that isolates the analysis logic
- **Windows Task Scheduler**: This native Windows tool is used to run the command on the required daily schedule. It's lightweight, reliable, and requires zero external dependencies

### How to Set Up the Task (Windows)

1. Press the **Windows Key** and type "Task Scheduler" to open it

2. In the "Actions" pane, click **"Create Basic Task..."**

3. **Name:** `Kipps Analysis Job`

4. **Trigger:** Select "Daily"
   - **Daily:** Set the time to `12:00:00 AM`

5. **Action:** Select "Start a program"
   - **Program/script:**  
     Enter the full absolute path to the `python.exe` in your virtual environment.  
     Example: `C:\Users\YourUser\Desktop\kipps-project\venv\Scripts\python.exe`
   
   - **Add arguments (optional):**  
     Enter the full absolute path to your `manage.py` file, followed by the command name.  
     Example: `"C:\Users\YourUser\Desktop\kipps-project\manage.py" run_analysis_job`  
     (Use quotes if the path has spaces)
   
   - **Start in (optional):**  
     Set this to the directory containing `manage.py`.  
     Example: `C:\Users\YourUser\Desktop\kipps-project\`

6. Click **Finish**

This task will now run `python manage.py run_analysis_job` every day at midnight, analyzing all new chats.
