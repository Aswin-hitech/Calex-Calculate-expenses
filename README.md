# Calex- A Personal Expense Tracking system

A full-stack Business Intelligence solution for personal expense tracking, management, and analytics using **Flask**, **PostgreSQL (Neon)**, and **Power BI**.

The project enables users to manage expense records through a web application while leveraging Power BI for advanced analytics, KPI monitoring, and interactive reporting.

---

## Project Overview

This project was initially developed as a CSV-based Power BI dashboard and later upgraded into a complete data analytics platform with:

* Flask-based Expense Management Portal
* PostgreSQL Database hosted on Neon
* Full CRUD Operations
* Search and Filtering Capabilities
* Interactive Power BI Dashboards
* Business Intelligence Reporting

The application follows a modern data-driven architecture where transaction data is stored in PostgreSQL, managed through Flask, and analyzed through Power BI.

---

## System Architecture

```text
┌─────────────┐
│ End User    │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│ Flask Web Application       │
│ • Expense Management        │
│ • CRUD Operations           │
│ • Search & Filters          │
│ • Data Validation           │
└─────────────┬───────────────┘
              │ SQL Queries
              ▼
┌─────────────────────────────┐
│ PostgreSQL Database (Neon)  │
│ • Expense Data              │
│ • Categories                │
│ • Payment Modes             │
│ • User Records              │
└─────────────┬───────────────┘
              │ Live Connection
              ▼
┌─────────────────────────────┐
│ Power BI Analytics Layer    │
│ • Data Transformation       │
│ • DAX Calculations          │
│ • KPI Metrics               │
│ • Visual Reports            │
└─────────────┬───────────────┘
              ▼
┌─────────────────────────────┐
│ Business Intelligence       │
│ • Expense Trends            │
│ • Category Analysis         │
│ • Spending Insights         │
│ • Interactive Dashboards    │
└─────────────────────────────┘
```

---

## Features

### Expense Management

* View All Expenses
* Add New Expenses
* Update Existing Records
* Delete Individual Records
* Delete All Records
* Search Expenses
* Filter Expenses
* Expense History Management

### Database Management

* PostgreSQL Integration
* Secure Database Connectivity
* Parameterized SQL Queries
* Data Validation
* Error Handling

### Business Intelligence

* KPI Monitoring
* Budget Utilization Tracking
* Savings Opportunity Analysis
* Category-wise Expense Analysis
* College vs Hometown Spending Analysis
* Payment Mode Analysis
* Expense Trend Visualization

---

## Technology Stack

### Backend

* Flask
* Python
* PostgreSQL (Neon)

### Frontend

* HTML5
* CSS3
* Bootstrap 5
* JavaScript

### Analytics

* Power BI
* DAX
* Power Query

### Database

* PostgreSQL
* SQL

---

## Project Structure

```text
Personal_Expense_Analytics_System/
│
├── app.py
├── config.py
├── requirements.txt
├── .env
│
├── Database/
│   ├── db_connection.py
│   └── expense_queries.py
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── add_expense.html
│   ├── edit_expense.html
│   └── search_results.html
│
├── static/
│   ├── css/
│   │   └── styles.css
│   │
│   └── js/
│       └── scripts.js
│
├── sql/
│   └── create_tables.sql
│
└── PowerBI/
    └── Personal_Expense_Analytics.pbix
```

---

## Database Schema

Main Table:

```sql
expense_records
```

Contains:

* Entry Date
* Category
* Description
* Amount
* Location
* Balance
* Payment Mode
* Priority
* Necessity
* Expense Level
* Running Expense
* Daily Expense
* Savings Opportunity
* Remaining Budget
* Budget Utilization Percentage
* Food Type
* Expense Group

---

## Dashboard Highlights

The Power BI dashboard includes:

### KPI Cards

* Total Expense
* College Expense
* Hometown Expense
* Savings Opportunity
* Average Daily Spend
* Remaining Budget

### Visualizations

* Expense Trend Analysis
* Category Distribution
* College vs Hometown Spending
* Payment Mode Analysis
* Priority Analysis
* Expense Group Analysis
* Budget Monitoring
* Interactive Filters and Slicers

---

## Setup Instructions

### Clone Repository

```bash
git clone <repository-url>
cd Personal_Expense_Analytics_System
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key

DATABASE_URL=postgresql://username:password@host/database?sslmode=require
```

### Run Application

```bash
python app.py
```

Application:

```text
http://localhost:5000
```

---

## Learning Outcomes

Through this project, I gained practical experience in:

* Full-Stack Development
* Flask Application Development
* PostgreSQL Database Design
* SQL Query Optimization
* CRUD Operations
* Data Modeling
* Business Intelligence
* Power BI Dashboard Development
* DAX Calculations
* Data Visualization

---

## Future Enhancements

* User Authentication
* Expense Forecasting using Machine Learning
* Budget Prediction Models
* Email Reports
* Expense Alerts
* REST API Integration
* Mobile Responsive Dashboard
* Cloud Deployment

---

## Author

**Aswin**

Artificial Intelligence & Machine Learning Student

Focused on AI, Data Analytics, Business Intelligence, Full Stack Development, and Machine Learning Projects.

---

## License

This project is developed for educational and open source contribution purpose.
