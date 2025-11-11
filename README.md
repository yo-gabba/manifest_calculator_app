# Logistics Manifest Calculator & Reporting Tool

A full-stack web application designed for logistics and trucking companies to track, calculate, and analyze delivery manifests.
Built with Flask, SQLite, and JavaScript, this tool streamlines driver management, automates rate calculations, and provides data-driven insights through visual dashboards and printable reports.

# Features

Driver & Manifest Management:

>Add and manage multiple drivers, manifests, and delivery stops.

>Automatically calculates miles, pallets, and daily totals.

Automated Calculations:

>Built-in logic for zone-based pricing and pallet/stop/accessorial rates.

Dashboard Overview:

>Displays total miles, stops, pallets, and earnings for the day, week, or month.

>Includes Chart.js bar charts for easy visual insights.

Reports Page:

>Filter and print reports by driver or date range (daily, weekly, monthly).

Database Integration:

>Uses SQLite with SQLAlchemy ORM for relational data between drivers, manifests, stops, and zones.

Future-Ready Architecture:
>Designed to scale with user authentication and individual driver logins.

# Tech Stack

```python
Category	        Tools

Backend 	        Python, Flask, SQLAlchemy

Frontend	        HTML, CSS, JavaScript, Chart.js

Database	        SQLite

Deployment	        Render

Version Control	    Git & GitHub

```

# Installation & Setup
1. Clone the repository

        git clone https://github.com/yo-gabba/manifest_calculator_app.git
        cd manifest_calculator_app

2. Create a virtual environment

        python3 -m venv venv
        source venv/bin/activate   # Mac/Linux
        venv\Scripts\activate      # Windows

3. Install dependencies

        pip install -r requirements.txt

4. Initialize the database

        python init_db.py

5. Run the app

        flask run

The app will be available at http://127.0.0.1:5000/

# Usage

Access the dashboard to view daily, weekly, or monthly metrics.

Navigate to the Reports page to filter manifests by driver or date range.

Export or print reports as needed.

Admins can later add new drivers and manage rate structures directly through the interface.

# Future Enhancements
Driver authentication and personal dashboards

PDF/CSV export functionality for reports

Integration with GPS or mileage tracking systems

Cloud database migration (PostgreSQL)

# Author
Gabriela Alcala
Software Engineer | Developer | Web Designer

📧 gabby9295@gmail.com
🔗 https://yo-gabba.github.io/portfolio/
