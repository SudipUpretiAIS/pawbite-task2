# PawBite on Azure and Render

This package is a cloud-adapted copy of your Flask application. No cloud account was accessed and no deployment or paid resource has been created. Follow these steps in your accounts. The same code runs on both platforms.

## Architecture and assessment limitation

- Azure App Service on Linux hosts deployment A.
- Render Free Python Web Service hosts deployment B.
- One Render Free PostgreSQL database stores the shared catalogue, customers, carts and orders. Render uses its Internal Database URL; Azure and your local setup use its External Database URL with TLS. Using one database avoids paying for a second database, but creates a shared dependency and cross-cloud network traffic. This is a student demonstration, not a production architecture.
- The Free Render database expires after 30 days. Record its expiry date and export evidence/data before expiry. Free web services sleep after 15 minutes idle; wake the site before the demo.
- Render Free is fixed at one instance: it cannot demonstrate manual horizontal scaling or autoscaling. Render autoscaling requires an eligible paid service and Pro workspace or above. Azure Free F1 also cannot scale out; Azure Monitor rule-based autoscale requires Standard or above. Do not describe free-plan limitation screenshots as successful scaling. Task 2's two-platform scaling requirement remains incomplete with this free-only setup; discuss that limitation with your lecturer before relying on it for the final submission.

## What changed

Added environment-based database configuration, PostgreSQL driver, pinned dependencies, Gunicorn entry point, Render blueprint, schema/seed SQL and database/admin commands. Increased email and image column capacity for PostgreSQL; retained images in the database so instance filesystems do not need persistent disks. Replaced Windows-only PDF generation with ReportLab. Added basic server validation and removed Flask debug mode.

This cloud copy disables email password recovery and live Khalti payments. The former used an unsafe reset flow and SMTP ports blocked on Render Free; the latter included a hardcoded key. No live payment credentials are included. Required Task 2 customer/admin login, registration, product CRUD and cart functions remain. Rotate the original payment key if active. The original SQLite DB and environment file are excluded; the cloud database starts with fictitious sample products, not a copy of your existing users/orders. Keep your original ZIP as a backup. This is deployment preparation, not a complete security audit; add CSRF protection and replace state-changing GET routes before real customer use.

## 1 Prepare the code in VS Code

1. Extract this ZIP into a new folder, not over your working original. Open the folder in VS Code. `application.py`, `requirements.txt`, `.python-version`, `render.yaml` and the `shop` folder must be at its top level.
2. In a PowerShell terminal create a Python 3.12 virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If activation is blocked, run `.\.venv\Scripts\python.exe` instead of `python`; you do not need to change the system execution policy. You may use your existing Python 3.12 environment.

3. Create a private GitHub repository and upload the project contents. Include the hidden `.python-version` file. Do not upload `.env`, `info.env`, your local database, `.venv` or `__pycache__`. If uploading through GitHub's web interface, check that hidden files were included; otherwise set a fully qualified Python 3.12 patch version via Render's PYTHON_VERSION setting. Never upload database URLs or passwords.

## 2 Create the free cloud database first

1. Sign in at https://dashboard.render.com and choose New > Postgres.
2. Name it `pawbite-db`, select the Free compute option, and choose a region. Use the same region for the Render web service. Verify the displayed plan is Free before creating it.
3. Wait for the database to become available. Record its expiry date.
4. Privately copy its External Database URL for local setup and Azure. Keep its Internal Database URL for Render. Neither belongs in screenshots or GitHub.
5. In the database network access settings, allow your current public IP for local setup. After Azure is created, allow the web app's outbound IP addresses as required. Keep access as narrow as practical. These restrictions affect external connectivity; the Render service should use the internal URL.

## 3 Initialise tables and sample products from VS Code

Render Free has no interactive service shell. Run the setup from your own computer against the external database instead. These commands create the schema and sample catalogue; they do not start a local SQLite database.

```powershell
$env:SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
$env:DATABASE_URL = Read-Host "Paste the Render External Database URL privately"
# External PostgreSQL connections must use TLS. Do not add sslmode twice.
if ($env:DATABASE_URL -notmatch 'sslmode=') {
  if ($env:DATABASE_URL.Contains('?')) { $env:DATABASE_URL += '&sslmode=require' }
  else { $env:DATABASE_URL += '?sslmode=require' }
}
$env:APP_ENV = 'production'
$env:COOKIE_SECURE = 'false'
python -m flask --app application init-db
python -m flask --app application seed-demo
python -m flask --app application create-admin
python -m flask --app application check-db
```

Enter a new admin email, name and strong password at the prompts. Password entry is hidden. No default administrator is included. Save your admin details privately. The commands do not overwrite an existing account.

Alternatively, run `sql/01_create_tables.sql` and `sql/02_insert_sample_data.sql` with a PostgreSQL client against the existing Render database, then run `create-admin`. These are the SQL submission artefacts. Choose one schema/seed method, not both during a demo. The scripts do not migrate an old SQLite schema or original records.

To check the app locally against the cloud database, run `python run.py` and open http://127.0.0.1:5000. COOKIE_SECURE must remain false for local HTTP; it will be true on cloud HTTPS. Do not display the environment or URL in a recording.

## 4 Deploy to Render Free

1. Choose New > Web Service, connect GitHub, and select your private PawBite repository.
2. Choose Python runtime and the same region as the database. The `.python-version` file selects Python 3.12.
3. Set Build Command: `pip install -r requirements.txt`
4. Set Start Command: `gunicorn application:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
5. Choose Free compute. Two Gunicorn worker processes are not two cloud instances and are not an autoscaling demonstration.
6. Add environment variables:

| Key | Value |
| --- | --- |
| SECRET_KEY | A new random 64-character secret; generate locally with `python -c "import secrets; print(secrets.token_hex(32))"` |
| DATABASE_URL | Render's Internal Database URL |
| APP_ENV | production |
| COOKIE_SECURE | true |

7. Deploy. Read the build/runtime logs if it fails. Open the onrender.com address and test `/healthz`, then the homepage and login. `/healthz` only confirms the web process; it does not prove database connectivity. Confirm database access through catalogue and login/CRUD.
8. As an alternative to manual settings, create a Blueprint from `render.yaml`; it creates only a Free web service and asks for DATABASE_URL. The database is still created manually in section 2.

## 5 Deploy to Azure App Service

1. In https://portal.azure.com create a new Web App. Use a dedicated Task 2 resource group such as `rg-pawbite-task2`; do not reuse a Node.js Task 1 app without changing its runtime.
2. Select Publish: Code, Runtime: Python 3.12, OS: Linux, and an available region allowed by your subscription.
3. Inspect the App Service plan before creation. F1 can be used for initial hosting if available. B1 is paid and allows manual scale out; Standard S1 or above is needed for Azure Monitor autoscale. Select paid capacity only when you deliberately choose to perform that demonstration. This package does not create or upgrade plans.
4. In the web app's Environment variables / Application settings, add:

| Key | Value |
| --- | --- |
| SECRET_KEY | A separately generated random secret |
| DATABASE_URL | Render's External Database URL with `sslmode=require` |
| APP_ENV | production |
| COOKIE_SECURE | true |
| SCM_DO_BUILD_DURING_DEPLOYMENT | true |

5. Save the settings. Find the app's outbound IP addresses in Properties and allow the required addresses in the Render database external network rules. Outbound IPs can change when hosting configuration changes. If all outbound traffic is routed through another network, use its actual egress addresses.
6. Set Startup Command under Configuration / General settings or Stack settings:

```text
gunicorn application:app --bind 0.0.0.0:8000 --workers 2 --timeout 120
```

7. In VS Code install Microsoft's Azure App Service extension, sign into your Azure account, locate the existing web app, and choose Deploy to Web App for this project folder. Keep build automation enabled. The deployment can replace that web app's existing files, so confirm you selected the new PawBite app.
8. Alternatively, use Azure CLI to upload the provided root-level ZIP:

```powershell
az login
az webapp deploy --resource-group rg-pawbite-task2 --name YOUR_UNIQUE_APP_NAME --src-path "C:\path\PawBite_Azure_Render.zip" --type zip
```

9. Open the HTTPS azurewebsites.net URL. Check Log stream if the app fails, then test the same customer/admin flows as Render. Because the apps share a database, a product created on one should appear on the other.

## 6 Capture assessment evidence

For each platform record: live URL, deploy success/logs, database connection without secrets, registration and invalid input, customer login/logout, catalogue/product selection, add/edit/remove cart items, admin login/logout, and add/read/edit/delete products with before/after database results. Use fictitious accounts. Never show SECRET_KEY, database URLs, payment keys or account credentials.

For Azure scaling, if you choose an eligible paid tier, capture the actual before/after tier or instance counts, CPU-based rules, and a triggered scale event. Record real metric duration, cooldown, limits and test outcome. Reduce resources when finished. For Render Free, capture the actual limitation and describe the requirement gap accurately. Sleep/wake and Git-triggered redeploys are not autoscaling. A written explanation alone does not fulfil the practical scaling requirement.

Keep the App Intro (1–2 pages), implementation/evaluation report and demonstration video separate from this deployment guide. They should describe only the work you actually complete. The report needs hands-on evaluation of infrastructure, platform services and scalability on each platform.

## Troubleshooting and costs

- Missing table: run init-db against the exact same database configured in the service.
- Database timeout: check internal vs external URL, TLS, hostname, firewall and database availability/expiry.
- Blank catalogue: seed-demo must target the same database; /healthz is not a DB test.
- Import/build failure: confirm requirements.txt and application.py are at the repository/ZIP root and Python is 3.12.
- Unable to log in locally: COOKIE_SECURE must be false over local HTTP.
- Image uploads: capped at 5 MB per request. Images are stored in the cloud database, which uses some of the free database quota.
- Original data is not migrated. Export it separately before replacing any working environment.
- Render Free is subject to included usage limits; monitor usage. Paid workspace features and paid compute are separate. Stopping an Azure app does not necessarily stop App Service plan charges. Review and remove unneeded plans/resources after collecting evidence; keep required demo URLs available for marking.

## Verification performed

Tested on Python 3.12 with the pinned packages, using a disposable in-memory SQLite database: source imports, explicit schema setup, repeatable seeding, public pages, registration/login, admin access restrictions, cart updates, ordering, PDF output, disabled reset/payment endpoints, admin product CRUD and logout. PostgreSQL schema SQL was generated from the models using SQLAlchemy's PostgreSQL dialect. No live PostgreSQL server or hosted Azure/Render endpoint was available in this session, so PostgreSQL runtime behaviour, network connectivity and platform deployment still need validation in your accounts. These are not completed cloud deployments.

## Official instructions checked 18 October 2026

- https://render.com/docs/deploy-flask
- https://render.com/docs/free
- https://render.com/docs/scaling
- https://render.com/docs/postgresql-creating-connecting
- https://render.com/docs/python-version
- https://learn.microsoft.com/en-us/azure/app-service/quickstart-python
- https://learn.microsoft.com/en-us/azure/app-service/deploy-zip
- https://learn.microsoft.com/en-us/azure/app-service/manage-automatic-scaling
