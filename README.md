# LibraTrack — Community Library Management System

A full-stack web application for managing a community library's book catalogue,
authors, categories, and borrowing records. Built with Django and Bootstrap 5.

---

## Purpose and Value

LibraTrack allows library staff and members to:

- Browse the full book catalogue with search and filtering
- Add, edit, and remove books, authors, and categories
- Borrow and return books with due-date tracking
- View personal borrowing history and overdue alerts
- Manage records via the Django admin back-end

---

## Technology Stack

| Layer       | Technology              |
|-------------|-------------------------|
| Backend     | Python 3.11, Django 4.2 |
| Frontend    | Bootstrap 5, custom CSS |
| Database    | SQLite (dev) / PostgreSQL (prod) |
| Deployment  | Heroku (Gunicorn + WhiteNoise) |
| Forms       | django-crispy-forms + crispy-bootstrap5 |
| Auth        | Django built-in auth    |

---

## Data Model

The application uses four related models:

```
Category ──< Book >── Author
              │
              └──< BorrowRecord >── User
```

- **Author**: stores first/last name, bio, and birth year
- **Category**: genre/topic labels for books
- **Book**: central entity linked to authors and categories via many-to-many relationships;
  tracks title, ISBN, published year, status, and who added it
- **BorrowRecord**: links a User to a Book with borrow date, due date, and return date

---

## Local Development Setup

### Prerequisites

- Python 3.11+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/libratrack.git
cd libratrack

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment variables file
cp .env.example .env
# Edit .env and set a strong SECRET_KEY

# Run database migrations
python manage.py migrate

# Seed sample data (creates admin / adminpassword123)
python manage.py seed_data

# Collect static files
python manage.py collectstatic --noinput

# Start the development server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` to view the application.
Admin panel: `http://127.0.0.1:8000/admin` — user: `admin`, password: `adminpassword123`

---

## Running Tests

```bash
# Run all tests
python manage.py test books

# Run with coverage report
coverage run manage.py test books
coverage report
coverage html     # generates htmlcov/index.html
```

The test suite covers models, form validation, views (CRUD), and the borrow/return workflow — 33 tests in total.

---

## Deployment to Heroku

### Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- A Heroku account

### Steps

```bash
# Log in to Heroku
heroku login

# Create a new Heroku app
heroku create your-app-name

# Set required environment variables (never commit these)
heroku config:set SECRET_KEY="your-very-long-random-secret-key"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS="your-app-name.herokuapp.com"

# Push code to Heroku
git push heroku main

# Run migrations on Heroku
heroku run python manage.py migrate

# Seed initial data (optional)
heroku run python manage.py seed_data

# Open the deployed app
heroku open
```

### Environment Variables

| Variable        | Required | Description                              |
|-----------------|----------|------------------------------------------|
| `SECRET_KEY`    | Yes      | Django secret key — long random string   |
| `DEBUG`         | Yes      | Set to `False` in production             |
| `ALLOWED_HOSTS` | Yes      | Comma-separated list of allowed hostnames|
| `DATABASE_URL`  | Auto     | Set automatically by Heroku Postgres add-on |

**Security**: Environment variables are loaded from `.env` locally (which is in `.gitignore`)
and set via `heroku config:set` in production. Secret keys are never committed to the repository.

---

## File Structure

```
libratrack/
├── books/                      # Main Django app
│   ├── management/
│   │   └── commands/
│   │       └── seed_data.py    # Database seeding command
│   ├── migrations/             # Auto-generated database migrations
│   ├── admin.py                # Django admin configuration
│   ├── forms.py                # Form classes with validation
│   ├── models.py               # Data models (Book, Author, Category, BorrowRecord)
│   ├── tests.py                # Automated test suite (33 tests)
│   ├── urls.py                 # URL routing for books app
│   └── views.py                # View functions and class-based views
├── library_project/
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Root URL configuration
│   └── wsgi.py                 # WSGI entry point
├── static/
│   ├── css/style.css           # Custom styles
│   └── js/main.js              # Progressive enhancement JS
├── templates/
│   ├── base.html               # Base layout with nav and footer
│   ├── books/                  # Book, author, category templates
│   └── registration/           # Login template
├── .env                        # Local environment variables (not in git)
├── .gitignore                  # Files excluded from version control
├── manage.py                   # Django management utility
├── Procfile                    # Heroku process definition
├── README.md                   # This file
├── requirements.txt            # Python dependencies
└── runtime.txt                 # Python version for Heroku
```

---

## Accessibility

The application follows WCAG 2.1 AA guidelines:

- Semantic HTML with ARIA roles and labels throughout
- Skip-navigation link for keyboard users
- Visible focus indicators on all interactive elements
- Sufficient colour contrast (Bootstrap 5 defaults)
- `aria-live` region for dynamic flash messages
- All form fields have associated `<label>` elements
- Tables include `scope` attributes on header cells

---

## Credits

Built as a full-stack portfolio project using Django, Bootstrap 5, and crispy-forms.
