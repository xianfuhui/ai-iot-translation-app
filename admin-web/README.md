# Admin Web

Server-rendered admin console (Express + EJS) for Lingua. It calls the [backend API](../backend) and keeps the admin's JWT in a server-side session, so the browser only holds a session cookie.

## Run

```bash
cp .env.example .env     # set BACKEND_API_URL and SESSION_SECRET
npm install
npm run dev              # or: npm start  (http://localhost:4000)
```

The backend must be running and at least one admin must exist (`npm run seed:admin` in `backend/`). Only accounts with `role: "admin"` can sign in.

## Pages

| Page | Route | What it does |
|---|---|---|
| Dashboard | `/dashboard` | User and vocabulary statistics, most-saved words |
| Users | `/users` | Search, change role, lock/unlock, delete |
| Vocabulary | `/vocabulary` | Manage the system word bank: add manually or import an Excel file, filter by topic |
| History | `/history` | View and delete system-wide translation history, filter by date |
| Languages and models | `/languages` | Enable/disable languages; per-language Vosk and ML Kit models with file upload or external link |

## Structure

```
admin-web/
├── server.js                 # entry point: session, routes
├── public/css/style.css
└── src/
    ├── middleware/           # requireAuth
    ├── services/             # axios client that forwards the session JWT, upload helper
    ├── routes/               # auth, dashboard, users, vocabulary, history, languages
    └── views/                # EJS templates and partials
```
