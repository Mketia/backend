# BookHub API (FastAPI + MongoDB)

REST API for managing books with authentication, admin-protected CRUD, and insights.

## Setup

1. Create a virtual environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Update `.env` values (especially `JWT_SECRET_KEY` and `ADMIN_BOOTSTRAP_SECRET`).
3. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```

## Auth

- Register: `POST /auth/register`
- Login: `POST /auth/login`

To create an admin user, include `admin_secret` in register payload that matches `ADMIN_BOOTSTRAP_SECRET`.

## Books

- List: `GET /books`
- Detail: `GET /books/{id}` (increments `read_count`)
- Create: `POST /books` (admin)
- Update: `PUT /books/{id}` (admin)
- Delete: `DELETE /books/{id}` (admin)

## Insights (admin)

- Reads: `GET /admin/insights/reads`
- Recent: `GET /admin/insights/recent`
