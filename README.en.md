# 🚀 CRM System 🚀

[Русский](README.md) | [English](README.en.md)

A web-based CRM application designed for service centers to manage orders, customers, services, financial operations, documents, and inventory.

The project is built with Python and Django, uses PostgreSQL as its database, and relies on Docker, Gunicorn, and Nginx for deployment.

## 🧾 Project Overview 🧾

The main goal of the project is to bring the key operational processes of a service center into one centralized system.

The CRM provides tools for managing orders, tracking financial transactions, working with documents, managing services, and monitoring inventory.

## 🔑 Key Features 🔑

- **Order Management** - create orders, update statuses, calculate totals and discounts.
- **Customer Management** - search and work with customer information.
- **Service Management** - create and manage services and service categories.
- **Financial Operations** - record income and expenses, process payments, and view transaction history.
- **Document Management** - create, edit, and generate documents using HTML templates.
- **Inventory Management** - track incoming stock, write-offs, and inventory history.
- **User Profiles** - manage personal information and employee records.
- **Dynamic Forms** - create and configure forms for different business processes.

## 💼 Technology Stack 💼

| Technology | Purpose |
|---|---|
| Python 3.12 | Programming language |
| Django 5.2 | Backend framework |
| PostgreSQL | Relational database |
| HTML, CSS, JavaScript | Frontend |
| HTMX | Dynamic user interface interactions |
| TinyMCE | Rich text editor |
| django-autocomplete-light | Autocomplete fields |
| Gunicorn | WSGI application server |
| Nginx | Web server and reverse proxy |
| Docker Compose | Container orchestration |
| WhiteNoise | Static file handling |

## Project Structure

The project is organized into Django applications, each responsible for a specific area of functionality.

| Application | Responsibility |
|---|---|
| `auth_registration` | User registration and authentication |
| `profile_user` | User profiles, employee management, and documents |
| `orders` | Orders, statuses, payments, and document generation |
| `finance` | Financial operations and balance management |
| `services` | Service and service category management |
| `storage` | Inventory management and stock history |
| `crm_system` | Main Django project configuration |

## 📰 Application Architecture 📰

The application uses the following component structure:

```text
             Client Browser
                   |
                   v
                 Nginx
                   |
                   v
            Gunicorn / Django
                   |
                   v
              PostgreSQL
```

Docker Compose manages three main services:

- `web` - Django application served by Gunicorn.
- `db` - PostgreSQL database.
- `nginx` - reverse proxy handling HTTP and HTTPS requests.

## ▶️ Local Setup ▶️

### ❗ Requirements ❗

- Git
- Docker
- Docker Compose

### 1. Clone the repository

```bash
git clone https://github.com/SergeyBalatskiy/crm_system.git
cd crm_system
```

### 2. Configure environment variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key

POSTGRES_DB=crm_db
POSTGRES_USER=crm_user
POSTGRES_PASSWORD=your-secure-password

POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Replace the example values with your own. Never commit `.env` files, passwords, or secret keys to GitHub.

### 3. Build and start the application

To start the database and Django application locally, run:

```bash
docker compose up -d --build db web
```

When the `web` container starts, Django automatically applies database migrations before starting Gunicorn.

### 4. Create an administrator account

```bash
docker compose exec web python manage.py createsuperuser
```

### 5. Access the application

The application will be available at:

```text
http://localhost:8000
```

## 📌 Production Deployment 📌

The production environment uses Docker Compose, Gunicorn, Nginx, and PostgreSQL.

The Nginx configuration handles HTTP and HTTPS traffic. HTTPS requires a properly configured domain and SSL certificates stored in the Certbot configuration directory.

To update the application after pulling changes from GitHub:

```bash
git pull
docker compose up -d --build
```

Check the status of running containers:

```bash
docker compose ps
```

View Django application logs:

```bash
docker compose logs -f web
```

Before applying updates that affect the database, it is recommended to create a PostgreSQL backup.

## Current Limitations and Future Improvements

The project can be extended and improved further.

Potential areas for future development include:

- Addition of a new view handler for the "forgot password" button.
- Implementation of JWT-based authorization (access/refresh tokens).
- Development of a more flexible system for managing employee access rights.
- Expansion of automated testing.
- Further refinement of the application's deployment and maintenance configuration.
- Enhancement of the CRM system's UI/UX design.
  
## Author

Developer: [Sergey Balatskiy](https://github.com/SergeyBalatskiy)

GitHub: https://github.com/SergeyBalatskiy/crm_system
