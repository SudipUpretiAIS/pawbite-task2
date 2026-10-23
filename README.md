# PawBite — Cloud-Based Pet Food Store

PawBite is a **Python Flask web application** for browsing and ordering pet food products. This repository is the cloud-ready version of the application used for the **SOFT807 Cloud Application** deployment exercise, with configurations for **Microsoft Azure App Service** and **Render**.

> **Project status:** Educational demonstration application. The code supports deployment to Azure and Render, but deploying it requires your own cloud accounts, PostgreSQL database, and environment variables. Cloud resources used for a demonstration may subsequently be deleted.

## Features

- Product catalogue with categories, product descriptions, prices, and images
- Customer registration, sign-in, and account-based access
- Shopping cart and order placement
- Order history and invoice PDF generation
- Administrator access for managing products and categories
- Demo product seeding and explicit administrator creation
- PostgreSQL support for cloud deployment
- `/healthz` endpoint for web-process health checks

**Demo limitations:** Live Khalti payments and email-based password recovery are disabled in this cloud copy. It is not intended for real customer transactions without further security review.

## Technology Stack

| Layer | Technology |
| --- | --- |
| Backend | Python 3.12, Flask |
| Database | PostgreSQL (cloud), SQLite (local development default) |
| ORM | Flask-SQLAlchemy / SQLAlchemy |
| Authentication | Flask-Login, Flask-Bcrypt |
| Production web server | Gunicorn |
| UI | HTML templates, CSS, Bootstrap, JavaScript |
| PDF invoices | ReportLab |
| Hosting | Microsoft Azure App Service and Render |

## Project Structure

```text
pawbite-task2-main/
├── application.py             # WSGI application entry point
├── run.py                     # Local Flask launcher
├── requirements.txt           # Python dependencies
├── render.yaml                # Render web-service configuration
├── .python-version            # Python version selection
├── .env.example               # Example environment settings
├── DEPLOYMENT_GUIDE.md        # Detailed Azure and Render instructions
├── shop/
│   ├── __init__.py            # Flask configuration and extensions
│   ├── cloud_commands.py      # Database and admin CLI commands
│   ├── admin/                 # Administration routes
│   ├── products/              # Product and order routes/models
│   ├── user/                  # Customer routes/models
│   ├── templates/             # HTML templates
│   └── static/                # Static assets and sample images
├── sql/
│   ├── 01_create_tables.sql
│   └── 02_insert_sample_data.sql
└── tests/
    └── smoke_test.py
```

## Local Setup (Windows / PowerShell)

Requirements: **Python 3.12** and a terminal in the project root.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit your local `.env` and replace the sample `SECRET_KEY` with a random secret at least 32 characters long. The default example uses a local SQLite database; do not set `APP_ENV=production` with SQLite.

Generate a secret for local use:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Use that output privately as the value of `SECRET_KEY` in `.env`. Do not commit `.env` or paste secrets into GitHub.

Initialize and populate the database:

```powershell
python -m flask --app application init-db
python -m flask --app application seed-demo
python -m flask --app application create-admin
python -m flask --app application check-db
```

The `create-admin` command prompts for an email, name, and password (minimum 12 characters). No default administrator password is supplied.

Start the local site:

```powershell
python run.py
```

Open `http://127.0.0.1:5000` in your browser.

## Deploying to Render

1. Create a PostgreSQL database on Render and note its region.
2. Create a **Python 3** Web Service connected to this repository, in the **same region** as the database if using the internal database URL.
3. Set build command to `pip install -r requirements.txt`.
4. Set start command to:

   ```bash
   gunicorn application:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
   ```

5. Configure `SECRET_KEY`, `DATABASE_URL`, `APP_ENV=production`, and `COOKIE_SECURE=true` as private environment variables.
6. Initialize and seed the new database **separately** using the documented Flask CLI commands from a trusted machine connected through Render's **External Database URL**; the free Web Service has no interactive shell.
7. Deploy and test `/healthz`, the catalogue, login, shopping cart, and administrator operations.

**Database URL:** Keep the credentials private. An internal Render database hostname works only where private networking is supported (typically same-region Render services). For access from a local machine or Azure, use the external database URL with TLS as described in `DEPLOYMENT_GUIDE.md`.

Render Free plans have availability, feature, and database-expiration limitations; consult current Render plan details before using them for long-term hosting.

## Deploying to Azure

Deploy this Python/Flask project to **Azure App Service (Linux, Python 3.12)**. Supply cloud application settings for `SECRET_KEY`, `DATABASE_URL`, `APP_ENV=production`, and `COOKIE_SECURE=true`; enable build during deployment where needed.

Production startup command:

```bash
gunicorn application:app --bind 0.0.0.0:8000 --workers 2 --timeout 120
```

The database must be reachable from Azure. Follow **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for resource creation, connection settings, verification, screenshots, limitations, and cleanup.

## Database Management

| Command | Purpose |
| --- | --- |
| `python -m flask --app application init-db` | Creates missing tables and initializes the invoice counter |
| `python -m flask --app application seed-demo` | Adds fictitious demo categories/products if absent |
| `python -m flask --app application create-admin` | Interactively creates an administrator |
| `python -m flask --app application check-db` | Checks database connectivity and product count |

`init-db` is **not a migration tool**. Do not assume it updates an existing schema. Run these commands only when `DATABASE_URL` points to the intended database; they should not be automatically run by Gunicorn workers.

## Testing

With dependencies installed and your test environment configured:

```powershell
python tests/smoke_test.py
```

Also perform browser-based checks for product browsing, authentication, cart changes, ordering, invoice PDFs, and admin product management. `/healthz` verifies the running process, not database correctness.

## Security and Cost Notes

- Never commit `.env`, real secrets, customer records, passwords, or database connection URLs.
- Rotate credentials promptly if they have been exposed.
- Use distinct, randomly generated secret keys for each cloud environment.
- Use TLS for external PostgreSQL connections and restrict database network access wherever possible.
- This demo needs additional production security hardening, including CSRF protection and safer handling of state-changing HTTP routes.
- Check cloud billing and **delete unused App Services, Render Web Services, databases, and other paid resources** after the assessment. Deleting a database destroys its data.

## Further Documentation

See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for the complete Azure/Render walkthrough and coursework-specific infrastructure limitations.
