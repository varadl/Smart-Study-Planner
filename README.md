# 📚 Smart Study Planner

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.x-lightgrey?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

![Banner](smart_study_planner_banner_1773997368371.png)

A comprehensive **Full-Stack Web Application** designed to empower students to take control of their academic life. By leveraging a smart scheduling algorithm, this tool transforms daunting exam preparations into manageable, daily study tasks based on urgency and priority.

---

## ✨ Key Features

| Feature | Description |
| :--- | :--- |
| 🔐 **Secure Auth** | Robust login & sign-up systems with session management. |
| 📖 **Exam Tracker** | Add subjects, set exam dates, and see your countdowns. |
| ✅ **Micro-Tasking** | Deconstruct complex subjects into granular, trackable topics. |
| 🧠 **Smart Planner** | An intelligent engine that generates optimized daily schedules. |
| 📊 **Analytics** | A clean dashboard displaying your overall progress at a glance. |

---

## 🛠️ Tech Stack & Architecture

### **Backend Core**
- **Language:** [Python 3](https://python.org)
- **Framework:** [Flask](https://flask.palletsprojects.com) (Modular Blueprints)
- **Database:** [SQLite](https://sqlite.org) (Lightweight & Reliable)

### **Frontend Aesthetics**
- **Structure:** Semantic HTML5
- **Styling:** CSS3 (Modern, Responsive Dark Mode with Glassmorphism)
- **Logic:** Vanilla JavaScript (Dynamic UI interaction)

---

## 📂 Project Structure

```text
Project/
├── app.py                # Main Application Entry Point
├── database.db           # SQLite Database File
├── requirements.txt      # Dependency List
├── models/               # Data Layer
│   └── db_setup.py       # Database Schema & Initialization
├── routes/               # Modular Routing (Blueprints)
│   ├── auth.py           # Authentication Logic
│   ├── subject.py        # Subject Management
│   ├── task.py           # Topic/Task Operations
│   └── planner.py        # Smart Scheduling Engine
├── static/               # Assets (CSS, JS, Images)
├── templates/            # HTML Views (Jinja2 Templates)
└── .vscode/              # Editor Configurations
```

---

## ⚙️ Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/Smart-Study-Planner.git
cd Smart-Study-Planner
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
# Activate on Windows:
venv\Scripts\activate
# Activate on macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Launch the Application
```bash
python app.py
```

---

## 🌐 Dashboard Preview

The dashboard provides a central hub for student productivity. 

> [!TIP]
> **Pro Tip:** Keep your subject lists updated with accurate exam dates. The planner prioritizes subjects with the closest deadlines to ensure you're always ahead of your exams!

---

## 🧠 Core Logic: How the Smart Planner Works

Our scheduling algorithm follows a three-step process:
1. **Urgency Assessment:** Analyzes exam dates to determine which subjects need the most attention.
2. **Topic Breakdown:** Identifies incomplete sub-topics within high-priority subjects.
3. **Daily Allocation:** Distributes the workload evenly across the remaining study days, preventing burnout and ensuring full syllabus coverage.

---

## 🔮 Roadmap & Future Enhancements
- [ ] 🤖 **AI Recommendations:** Personalized study tips based on performance.
- [ ] 📈 **Deep Analytics:** Progress heatmaps and time-spent tracking.
- [ ] 🔔 **Real-time Notifications:** Email & browser reminders for upcoming exams.
- [ ] 📱 **Mobile App:** A native companion app for studying on the go.

---

## 👨‍💻 Developed By
**Varad Lokhande**
Computer Engineering Student | Passionate about building tools that solve real-world problems.

---

## ⭐ Show Your Support
If this project helped you plan your studies, please consider giving it a ⭐ on GitHub! It encourages me to keep adding new features.

---
*Built with ❤️ to simplify student life.*
