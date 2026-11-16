# Backend API

REST API shared by the Flutter app and the admin console. Node.js, Express, Mongoose, JWT.

## Structure

```
backend/
├── server.js            # entry point
├── .env.example         # copy to .env
├── scripts/sync-db.js   # $jsonSchema validators + index sync
├── seed/                # createAdmin, seedData, seedRich
└── src/
    ├── config/          # MongoDB connection
    ├── models/          # User, Language, Vocabulary, SystemVocabulary, TranslationHistory, AIConversation, Model
    ├── middleware/      # auth (JWT + roles), error handler, upload
    ├── controllers/     # business logic per module
    ├── routes/          # endpoint definitions
    └── utils/           # Gemini client, token helper
```

## Run

```bash
cp .env.example .env     # MONGO_URI, JWT_SECRET, optional GEMINI_API_KEY
npm install
npm run seed:admin
npm run seed:data
npm run db:sync
npm run dev              # or: npm start  (http://localhost:5000, health: /api/health)
```

Requires Node.js 18+ and MongoDB (local or Atlas).

## Scripts

| Script | What it does |
|---|---|
| `npm run seed:admin` | Create the admin account (`SEED_ADMIN_*` in `.env`) |
| `npm run seed:data` | Base sample data: languages, users, system words, history, an AI conversation, models |
| `npm run seed:rich` | Bulk demo data: 15 learners, ~250 vocabulary entries, ~2,500 histories, AI conversations |
| `npm run db:sync` | Attach `$jsonSchema` validators to all 7 collections and sync indexes (idempotent) |

## Authentication

Send `Authorization: Bearer <token>` (token from `/api/auth/login` or `/api/auth/register`). Roles are `user` (mobile) and `admin` (console); admin-only routes return 403 otherwise.

## Endpoints

**Accounts**

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST | `/api/auth/register` | public | Register (mobile) |
| POST | `/api/auth/login` | public | Log in |
| POST | `/api/auth/logout` | any | Log out |
| PUT | `/api/auth/change-password` | any | Change password |
| GET | `/api/auth/me` | any | Current account |
| GET, POST, PUT, DELETE | `/api/users`, `/api/users/:id` | admin | Manage users |

**Languages and models**

| Method | Endpoint | Role | Description |
|---|---|---|---|
| GET | `/api/languages` | any | Supported languages |
| POST, PUT, DELETE | `/api/languages`, `/api/languages/:id` | admin | Manage languages (delete is guarded: 409 if referenced) |
| GET | `/api/models` | any | Vosk (speech-to-text) and ML Kit (translation) model catalog |
| POST, PUT, DELETE | `/api/models`, `/api/models/:id` | admin | Manage models, with optional file upload |

**AI assistant (Gemini)**

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/ai/chat` | Send a message |
| POST | `/api/ai/summarize/:conversationId` | Summarise a conversation |
| GET | `/api/ai/conversations` | List saved conversations |
| GET | `/api/ai/conversations/:id` | Conversation detail |

**Vocabulary**

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST, GET | `/api/vocabulary` | user | Save / list own words |
| PUT, DELETE | `/api/vocabulary/:id/flashcard` | user | Add to / remove from flashcards |
| DELETE | `/api/vocabulary/:id` | user | Delete a word |
| GET | `/api/vocabulary/system`, `/api/vocabulary/system/categories` | any | System word bank and its topics |
| POST, PUT, DELETE | `/api/vocabulary/system`, `/api/vocabulary/system/:id` | admin | Manage the word bank |
| POST | `/api/vocabulary/system/import` | admin | Import from an Excel file (`.xlsx`/`.xls`; required columns `word`, `meaning`; row-level errors are reported) |

**History and statistics**

| Method | Endpoint | Role | Description |
|---|---|---|---|
| POST, GET | `/api/history` | user | Record / list own history |
| POST | `/api/history/:id/summarize` | user | AI summary of a voice session |
| DELETE | `/api/history/:id`, `/api/history/:id/segments` | user | Delete a record / a segment of a session |
| GET, DELETE | `/api/history/admin/all`, `/api/history/admin/:id` | admin | System-wide history |
| GET | `/api/stats/users`, `/api/stats/vocabulary` | admin | Statistics |

## Model file upload

`POST/PUT /api/models` accepts `multipart/form-data` with an optional `modelFile` field plus the text fields (`type`, `name`, `languageCode`, `identifier`, …). Files are stored in `uploads/models/` and served at `/uploads/models/<file>`. The default size limit is 800 MB (`MAX_MODEL_UPLOAD_MB`).

ML Kit does not accept custom models: files uploaded for type `mlkit` are for reference only, while `vosk` files are downloaded by the app.

## Sample data

`npm run seed:data` creates three active languages (en, vi, ja) and one inactive (ko), two users, system words in several topics, saved words and flashcards, history records, an AI conversation with a summary, and Vosk plus ML Kit models. `seed:rich` adds the bulk demo data on top.
