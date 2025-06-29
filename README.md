## 🏥 Medical Recovery Planner

**An AI-powered system to analyze medical reports and generate personalized recovery plans**  
*Automated deficiency detection • Smart calendar generation • Real-time progress tracking*
---
<img width="1440" alt="Screenshot 2025-06-29 at 11 32 34 AM" src="https://github.com/user-attachments/assets/7fccb323-e12a-4699-ac38-3e1ab0494ed1" />

## ✨ Features

- **Medical Report Analysis**  
  Upload lab reports to detect deficiencies and borderline values using NLP and Gemini AI

- **Personalized Recovery Plans**  
  Generates tailored daily schedules with:
  - Exercises 🏋️‍♂️  
  - Diet plans 🥗  
  - Medication schedules 💊  

- **Dynamic Calendar**  
  - Adjusts schedules automatically if activities are missed  
  - Tracks progress with completion metrics  

- **Smart Notifications**  
  Real-time alerts for scheduled activities  

---

## 🛠️ Tech Stack

| Component          | Technology                          |
|--------------------|-------------------------------------|
| Backend            | Python (Flask)                      |
| AI/NLP             | Google Gemini, LangChain            |
| Database           | Firebase Firestore                  |
| Frontend           | HTML5, Bootstrap 5, Jinja2          |
| Notifications      | Plyer                               |

---

## 🚀 Quick Setup

### Prerequisites
- Python 3.10+
- Firebase project with Firestore enabled
- Google Gemini API key

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/Naman-jain020/ReGenAI.git
   cd ReGenAI
   
2. Create and activate virtual environment:
   ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   
6. Configure environment variables:
   cp .env.example .env

   Edit .env with your:
    Firebase credentials
    Gemini API key
    Flask secret key
   
8. Run the application:
   ```bash
   python app.py

<img width="402" alt="Screenshot 2025-06-29 at 11 36 55 AM" src="https://github.com/user-attachments/assets/afa074e9-e47f-44be-a265-f51acb57d05f" />
