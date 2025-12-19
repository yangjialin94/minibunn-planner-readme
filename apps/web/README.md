# Minibunn Planner (Web)

**Status:** Discontinued (December 2025)  
**Active period:** July 2025 – December 2025

Minibunn Planner (Web) was the frontend application for the Minibunn Planner product. It provided the user interface for task management, notes, journaling, calendar views, and subscription-aware features.

This repository is preserved **for technical review and documentation purposes only**.  
All production deployments and services have been shut down.

---

## Overview

The web application supported:

- Task and backlog management
- Rich-text notes and daily journaling
- Calendar-based planning views
- User account and subscription management
- Responsive layouts for desktop and mobile

It was built as a modern React/Next.js application with a strong focus on state management, UX, and maintainability.

---

## Tech Stack

- **Language**: TypeScript  
- **Framework**: Next.js (React)  
- **Styling**: SCSS  
- **State Management**: Zustand, React Query, Context API  
- **Authentication**: Firebase Authentication  
- **Rich Text Editor**: Tiptap  
- **Drag & Drop**: Dnd-kit  
- **Animations**: Motion  
- **Icons**: Lucide-react  
- **Notifications**: React-toastify  
- **Linting**: ESLint  

---

## Project Structure

```text
src/
├── api/          # API client and request helpers
├── app/          # Next.js routes, layouts, and pages
├── components/   # Reusable UI components
├── context/      # Global context providers
├── hooks/        # Custom React hooks
├── lib/          # Shared libraries and helpers
├── styles/       # SCSS stylesheets
├── types/        # TypeScript type definitions
└── utils/        # Utility functions
```

---

## Architectural Notes

- Component-driven UI design
- Server and client concerns separated via API abstraction
- Centralized state with lightweight stores
- Subscription and auth state enforced at page and component level

---

## Shutdown Notes

As part of the product sunset:

- Production frontend deployments were disabled
- Firebase authentication was decommissioned
- All subscription-related UI flows were shut down
- Environment variables and secrets were revoked

The application is no longer accessible to end users.

---

## Related Project

This API was part of the broader Minibunn Planner project.

- Main project overview: <https://github.com/yangjialin94/minibunn-planner>
- Backend (API): <https://github.com/yangjialin94/minibunn-planner/apps/api>

---

## ⚖️ License

- Code is **not open source** and cannot be copied, modified, or redistributed.  
- This repository is for **review purposes only**.  
