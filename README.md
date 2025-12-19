# Minibunn Planner

**Status:** Discontinued (2025)

Minibunn Planner was a **full-stack productivity web application** designed to help users organize **tasks, notes, journals, and calendars** in a single, cohesive workspace. The project was built end-to-end as a personal SaaS to explore product design, system architecture, and subscription-based monetization.

This repository is preserved **for review and documentation purposes** and reflects the final state of the project prior to shutdown.

---

## ✨ Features

- **Task Management** – Create, edit, reorder, and complete tasks  
- **Notes & Journals** – Rich-text editor (Tiptap) for notes and journaling  
- **Calendar** – Event scheduling with multiple date views  
- **Backlogs** – Organize long-term goals alongside daily tasks  
- **User Accounts** – Google Sign-In authentication  
- **Subscriptions** – Monthly and yearly plans via Stripe  
- **Responsive Design** – Optimized for desktop and mobile  

---

## 🛠 Tech Stack

### Frontend (Web)

- **Framework**: Next.js (React, TypeScript)
- **Styling**: SCSS
- **State Management**: Zustand, React Query, Context API
- **UI / UX**: Dnd-kit, Motion, React-toastify, Lucide-react
- **Deployment**: Vercel (inactive)

### Backend (API)

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (SQLAlchemy, Alembic)
- **Authentication**: Firebase Authentication
- **Payments**: Stripe (subscriptions, webhooks)
- **Background Jobs**: APScheduler
- **Deployment**: Render (inactive)
- **Testing**: Pytest

---

## 🚀 Architecture Overview

- Frontend communicates with the backend via REST APIs
- Backend handles business logic, persistence, and subscription state
- Firebase provides secure authentication
- Stripe manages billing and customer subscriptions

All production services have been **shut down** as part of the project sunset.

---

## 📸 Screenshots

### Calendar

![Calendar](/screenshots/calendar-071825.png)

### Tasks

![Tasks](/screenshots/task-071825.png)

### Notes

![Notes](/screenshots/note-071825.png)

### Backlogs

![Backlogs](/screenshots/backlog-071825.png)

### User Profile

![User Profile](/screenshots/user-071825.png)

---

## 🗂 Repo Structure

```text
minibunn-planner/
├── README.md
├── ARCHIVED.md
├── screenshots/
└── apps/
    ├── api/        # backend (archived)
    └── web/        # frontend (archived)
```

---

## ⚖️ License

- Code is **not open source** and cannot be copied, modified, or redistributed.  
- This repository is for **review purposes only**.  
