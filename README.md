# 🛍️ Django Products Store

> A portfolio e-commerce backend designed for local containerized deployment.

A containerized e-commerce backend built with **Django 5**, **PostgreSQL**, and **Docker**.

The project combines traditional Django server-rendered templates with a REST API for product management. It uses
separate configurations for development and production, JWT authentication through Djoser, and Gunicorn for serving the
production application locally via Docker.

---

## 🚀 Key Features & Tech Stack

* **Architecture:** Hybrid setup supporting traditional Django Templates (Server-Side Rendered) and a Django REST
  Framework (DRF) API.
* **Backend & Database:** Python, Django 5, PostgreSQL 18, Gunicorn, Whitenoise, Nginx.
* **Authentication:** Djoser (JWT tokens for API) alongside standard session authentication for templates.
* **DevOps:** Split settings (Dev/Prod), Django Debug Toolbar, and fully containerized via Docker & Docker Compose.

---

## 📂 Project Structure

```text
OnlineStore/
│
├── core/                # Core configurations & base views
├── store/               # Products app (models, views, serializers)
├── OnlineStore/         # Project settings package
│   ├── settings/
│   │   ├── base.py      # Shared settings
│   │   ├── development.py
│   │   └── production.py
│   │
├── dev/                 # Local Development Docker files & env template
├── prod/                # Production Docker files & env template
├── manage.py
└── README.md
```

---

## ⚙️ Getting Started & Installation

To run this project locally, make sure you have **Docker** and **Docker Compose** installed on your machine.

### Clone the Repository

```bash
git clone https://github.com/ViKTor833/django-docker-ecommerce-store.git
cd django-docker-ecommerce-store
```

## Running the Development Server

The development environment is located inside the dev/ directory.

### 1. Enter the development directory

```
cd dev/
``` 

### 2. Create the environment file

```bash
cp .env.example .env
```

Open .env and replace the example values with your own configuration.

### 3.Start the development containers:

```bash
docker compose up --build
```

### 4. Apply database migrations:

(Migrations do not auto-apply in dev by default). Open a shell inside the Django container:

```bash
docker compose exec web python manage.py migrate
```

- The application will be available at: `http://localhost:8000/`
- To stop the environment: `docker compose down`

## Running the Production Server

The production environment is located inside the prod/ directory.

### 1. Enter the production directory

```bash
cd prod/
```

### 2. Create the production environment file

```bash
cp .env.example .env
```

Open .env and provide the required production secrets.

### 3. Start the production containers

```bash
docker compose up --build
```

The production setup automatically handles database health-check, migrations, static file collection, and boots
Gunicorn (2 workers).

- The application will be available at: `http://localhost:8001/`
- To stop the environment: `docker compose down`

## Creating an admin user

To create a Django superuser, run the following commands while your containers are running:

```bash
docker compose exec web python manage.py createsuperuser
```

> **Note:**
> The application uses a custom *user_type* field for user_roles, administrator users should have:
`user_type = A`

The Django admin interface can then be accessed at: `http://localhost:8001/admin/`

---

# 🔐 Environment Variables

Development and production use separate environment files.

Each environment contains an .env.example file showing which variables are required.

Create your local environment file and replace the example values with your own configuration:

```bash
cp .env.example .env
```

Example configuration variables include:

```env
POSTGRES_DB=your_database
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
DJANGO_SETTINGS_MODULE=OnlineStore.settings.development
SECRET_KEY='your_django_secure_key'
ALLOWED_HOSTS=your_allowed_hosts
```

# 🔑 Authentication

The project supports different authentication mechanisms depending on how the application is accessed.

- WEB UI: Uses Django's standard session-based authentication.
- REST API: Uses JWT authentication via Djoser (/api/auth/ endpoints).

# 🗄️ Database

The application uses **PostgreSQL** running inside a Docker container.

PostgreSQL data is stored in a Docker volume so that the database data persists when the containers are stopped or
recreated.

The development and production environments use separate database volumes.

## 📄 License

This project is licensed under the [MIT License](LICENSE).