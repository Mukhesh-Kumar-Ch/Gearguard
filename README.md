# GearGuard – Maintenance Management System

GearGuard is a full-stack **maintenance tracking and workflow management system** built using **Django, SQL (SQLite), JavaScript, and Bootstrap**.  
It helps organizations track equipment, assign maintenance teams, and manage repair requests through an automated workflow.

This project was developed as part of a hackathon to simulate an **Odoo-like enterprise maintenance module**.

---

## 🚀 Problem Statement

In many organizations, equipment failures are tracked informally, leading to:
- Poor visibility of asset health
- Manual technician assignment
- No structured repair workflow
- Missed preventive maintenance

**GearGuard solves this by connecting:**
- **Equipment** → what needs maintenance  
- **Maintenance Teams** → who fixes it  
- **Maintenance Requests** → the work lifecycle  

---

## 🧩 Core Features

### 1️⃣ Equipment Management
- Central registry of all company assets
- Track equipment by:
  - Department
  - Assigned employee
  - Physical location
- Each equipment is mapped to:
  - A **maintenance team**
  - A **default technician**
- Automatically shows count of open requests per equipment

### 2️⃣ Maintenance Teams
- Create multiple specialized teams (IT, Electrical, Mechanical, etc.)
- Assign users (technicians) to teams
- Technicians are auto-filtered based on equipment responsibility

### 3️⃣ Maintenance Requests (Workflow Engine)
Each request follows a structured lifecycle:

**New → In Progress → Repaired → Scrap**

- Request types:
  - **Corrective** (unplanned breakdown)
  - **Preventive** (scheduled maintenance)
- Smart automation:
  - Auto-assigns default technician
  - If unavailable, assigns **least-loaded technician**
- Scrap logic:
  - Marking a request as *Scrap* automatically flags equipment as unusable

### 4️⃣ Kanban Board (Technician Workspace)
- Drag & drop requests between stages
- Visual indicators:
  - Assigned technician badge
  - Overdue requests highlighted
- Real-time state updates using JavaScript + AJAX

### 5️⃣ Preventive Maintenance Calendar
- Calendar view for all preventive requests
- Overdue tasks highlighted
- Click on date to schedule maintenance
- Built using **FullCalendar.js**

---

## 🛠️ Tech Stack

**Backend**
- Python  
- Django  
- Django ORM  

**Database**
- SQLite (SQL-based relational database)

**Frontend**
- HTML  
- CSS  
- Bootstrap  
- JavaScript (AJAX, drag & drop)

**Architecture**
- MVC (Model–View–Template)  
- Relational data modeling  
- Server-side validation & business rules  

---

## 🗄️ Data Model Overview

### MaintenanceTeam
- Contains **Users (Technicians)**

### Equipment
- Linked to a **MaintenanceTeam**
- Has a **Default Technician**

### MaintenanceRequest
- Associated with **Equipment**
- Assigned to a **Technician**
- Tracks **Workflow State**


---

## ⚙️ Smart Automations Implemented
- Auto technician assignment on request creation
- Least-loaded technician selection logic
- Preventive requests appear in calendar automatically
- Equipment becomes unusable when scrapped
- Scrapped equipment cannot receive new requests

---

## 📌 Future Enhancements 
- Analytics dashboard (requests per team / equipment)  
- REST API integration  

---

## 👤 Author
**Ch. Mukhesh Kumar**   
