# Migrant Connect

A Flask-based web application for managing migrant workers, employer registrations, welfare scheme enrollment, verification, and geo-location mapping.

## Key Features

- Admin panel for migrating approvals and status updates
- Migrant registration with Aadhaar + OTP verification
- Employer registration and login
- Welfare scheme management and scheme application tracking
- Migrant verification and job status updates
- QR code generation for approved migrant profiles
- Migrant location display using map coordinates
- Static site pages for information and contact templates

## Tech Stack

- Python 3
- Flask
- MySQL / MariaDB
- HTML / CSS / JavaScript
- PIL / qrcode for QR code generation
- FPDF for PDF functionality
- pandas / matplotlib for data handling (imported in app)

## Requirements

- Python 3.11+ (or 3.10+)
- MySQL server
- `mysql-connector-python`
- `Flask`
- `Pillow`
- `qrcode`
- `fpdf`
- `pandas`
- `matplotlib`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SSaiSurya2004/migrant-connect.git
   cd migrant-connect
   ```

2. Create and activate a Python virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install flask mysql-connector-python pillow qrcode fpdf pandas matplotlib
   ```

## Database Setup

1. Create a MySQL database called `migrant_connect`.
2. Import the SQL schema from `database/migrant_connect.sql`:

   ```bash
   mysql -u root -p migrant_connect < database/migrant_connect.sql
   ```

3. Update database connection values in `main.py` if your MySQL credentials are different:

   ```python
   def get_db_connection():
       return mysql.connector.connect(
           host="localhost",
           user="root",
           password="",
           charset="utf8",
           database="migrant_connect",
           autocommit=True
       )
   ```

## Running the App

Start the Flask application from the repository root:

```bash
python main.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## Default Credentials

- Admin: `admin` / `admin`

## Important Pages

- `/` — Landing page
- `/admin_login` — Admin login
- `/migrant_login` — Migrant login
- `/migrant_register` — Migrant registration
- `/employer_login` — Employer login
- `/employer_register` — Employer registration
- `/migrant_map` — Migrant map view
- `/view_schemes` — Welfare schemes listing

## Project Structure

- `main.py` — Flask application routes and logic
- `templates/` — HTML templates for app pages
- `static/` — Static assets, including CSS, JS, uploads, QR codes
- `database/migrant_connect.sql` — Database schema and sample data

## Notes

- This project uses file uploads for migrant documents and profile photos.
- The app currently stores passwords in plaintext in the database; consider adding hashing for production.
- Some routes depend on session values and user roles to function correctly.
- If you use the map feature, ensure location data is available in the database.

## License

This repository does not include an explicit license file. Add one if you want to permit reuse.
