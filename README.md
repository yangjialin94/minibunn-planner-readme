# Minibunn Planner

Minibunn Planner is a **full-stack productivity web application** designed to help users organize their **tasks, notes, journals, and calendars** in one seamless experience. It combines a clean and modern interface with a robust backend to support authentication, subscriptions, and reliable data storage.

👉 This repository is **public for recruiters and collaborators to review the project’s scope and technology choices**. The source code remains private.

---

## ✨ Features

- **Task Management** – Create, edit, reorder, and complete tasks.  
- **Notes & Journals** – Rich-text editor (Tiptap) for notes and daily journaling.  
- **Calendar** – Manage events with date views and filtering.  
- **Backlogs** – Organize larger goals alongside daily tasks.  
- **User Accounts** – Authentication with Google Sign-In via Firebase.  
- **Subscriptions** – Stripe integration for monthly & yearly plans.  
- **Responsive Design** – Built for both desktop and mobile use.  

---

## 🛠 Tech Stack

**Frontend (Web)**  
- **Framework**: Next.js (React, TypeScript)  
- **Styling**: SCSS  
- **State Management**: Zustand + React Query + Context API  
- **UI Enhancements**: Dnd-kit (drag-and-drop), Motion (animations), React-toastify (notifications), Lucide-react (icons)  
- **Hosting**: Vercel  

**Backend (API)**  
- **Framework**: FastAPI (Python)  
- **Database**: PostgreSQL (SQLAlchemy ORM, Alembic for migrations)  
- **Auth**: Firebase Authentication  
- **Payments**: Stripe (checkout, subscription status, webhooks)  
- **Scheduling**: APScheduler (background tasks)  
- **Hosting**: Render  
- **Testing**: Pytest with 97% coverage  

---

## 🚀 Architecture Overview

- **Frontend** consumes REST APIs from the FastAPI backend.  
- **Backend** handles business logic, subscriptions, and persistence.  
- **Firebase** ensures secure authentication across both layers.  
- **Stripe** manages subscription billing and customer portal.  

---

## 📸 Screenshots

### Calendar
![Home Page](/screenshots/calendar-071825.png)

### Tasks
![Calendar Page](/screenshots/task-071825.png)

### Notes
![Notes Page](/screenshots/note-071825.png)

### Backlogs
![Tasks Page](/screenshots/backlog-071825.png)

### User Profile
![User Profile Page](/screenshots/user-071825.png)

---

## 📬 Contact

Interested in learning more about Minibunn Planner?  
- **Portfolio**: [jialinyang.com](https://www.jialinyang.com)
- **LinkedIn**: [[linkedin.com/in/jialinyang](https://www.linkedin.com/in/jialinyang)](https://www.linkedin.com/in/jialin-yang-jy/)
- **Email**: work@jialinyang.com

---

## ⚖️ License

This project is released under a **Proprietary License**.  
- Code is **not open source** and cannot be copied, modified, or redistributed.  
- This repository is for **review purposes only**.  
