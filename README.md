# Invoicr — Django SaaS Invoice Manager

A production-ready, multi-tenant invoice management system built with Django 5.2 LTS.
Live demo: https://web-production-45922.up.railway.app

**Demo account:** username `demo` / password `Demo1234!`

## Features

- **Multi-tenant architecture** — each user sees only their own data, enforced at the ORM level
- **Client management** — full CRUD with invoice history per client
- **Invoice lifecycle** — Draft → Sent → Paid → Overdue with one-click status transitions
- **PDF export** — professionally formatted invoices generated server-side
- **Stripe payments** — Stripe Checkout integration with webhook auto-status updates
- **Dashboard** — real-time revenue, unpaid, and overdue summaries
- **Production-ready** — deployed on Railway with PostgreSQL, Gunicorn, and WhiteNoise

## Tech Stack

| Layer      | Technology                        |
|------------|-----------------------------------|
| Backend    | Django 5.2 LTS, Python 3.12       |
| Database   | PostgreSQL (via psycopg2)          |
| Frontend   | Tailwind CSS (utility-first)       |
| PDF        | ReportLab (pure Python, no deps)  |
| Payments   | Stripe Checkout + Webhooks         |
| Deployment | Railway, Gunicorn, WhiteNoise      |
| Config     | python-decouple, dj-database-url   |

## Architecture Highlights

**Multi-tenancy** is enforced at the queryset level — every view filters by
`owner=request.user`. URL manipulation attacks are prevented via
`get_object_or_404(Invoice, pk=pk, owner=request.user)`.

**Settings are split** into `base.py`, `dev.py`, and `prod.py` — secrets managed
via environment variables, never committed to git.

**Database design** uses `on_delete=PROTECT` on Invoice→Client to prevent
accidental data loss, and `UniqueConstraint` scoped per owner so invoice
numbers are isolated between users.

## Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/invoicr.git
cd invoicr
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in your values
python manage.py migrate
python manage.py runserver
```

## Environment Variables

```
SECRET_KEY=
DATABASE_URL=
STRIPE_PUBLIC_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
ALLOWED_HOSTS=
```
