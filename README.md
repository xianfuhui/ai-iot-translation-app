# Lingua: AI Translation & Language Learning App

An offline-first mobile app for translating and learning languages, backed by a MongoDB-centred API and an admin web console. Built as a team project for an **Advanced Database Systems** course (Master's program), using the app as a vehicle to study **NoSQL document modelling**.

## Overview

Lingua translates text and speech **on the device** (no network needed after a one-time model download), saves words for flashcard practice, and offers an AI assistant powered by Gemini. Administrators manage users, languages, offline model packs and the system vocabulary from a web console.

## Key features

- **On-device translation** with Google ML Kit, **speech-to-text** with Vosk (Android) and **text-to-speech** with the system engine
- **Offline-first with guest mode**: history and saved words are stored locally, queued, and synced when the backend is reachable
- **Vocabulary and flashcards**: personal word list, curated system word bank, pronunciation audio
- **AI assistant**: chat and conversation summaries through Gemini (proxied by the backend so the key stays server-side)
- **Admin console**: users, languages, model catalog (with file upload), system vocabulary, usage stats, Gemini key management
- **Database-focused design**: schema validation, query-driven indexes, transactions and bounded embedded arrays (see below)

## Tech stack

| Component | Stack |
|---|---|
| [`mobile/`](mobile) | Flutter 3 (Android, iOS), Provider, ML Kit Translation, Vosk, flutter_tts |
| [`backend/`](backend) | Node.js, Express, Mongoose, JWT, Gemini API |
| [`admin-web/`](admin-web) | Node.js, Express, EJS (server-rendered), express-session |
| Database | MongoDB 7, database `language_app`, 7 collections |

## Architecture

```
Flutter app ──┐
              ├──▶ REST API (backend :5000) ──▶ MongoDB
Admin web  ───┘         │
 (:4000)                └──▶ Gemini API (chat, summaries)
```

```
ai-iot-translation-app/
├── mobile/       # Flutter client
├── backend/      # REST API, seed scripts, DB validators
├── admin-web/    # Admin dashboard
└── docs/         # DB schema diagram, UI prototypes, engineering notes
```

## Database design

![Database schema](docs/db-schema.png)

*Generated with MongoDB Compass (Data Modeling) from the live database. Solid edges are `ObjectId` references; `languages` is referenced softly by code (`"en"`, `"vi"`, …).*

| Collection | Purpose | Key design decision |
|---|---|---|
| `users` | Accounts (user/admin) | bcrypt-hashed password, `select: false` |
| `translationhistories` | Translation history | **Polymorphic** by `type` (`text`, `speech`, `ai_chat`, `conversation`); voice sessions embed a `segments[]` array |
| `vocabularies` | Per-user saved words | Unique compound index `{user, word, targetLanguage}` |
| `systemvocabularies` | Admin-curated word bank | `createdBy` → `users` |
| `aiconversations` | Gemini chat sessions | `messages[]` embedded: one read returns the whole conversation |
| `languages` | Supported languages | Soft-referenced **by `code`**, not ObjectId |
| `models` | Vosk / ML Kit model catalog | Unique `{type, languageCode, identifier}` |

**Design decisions**

1. **Embed vs reference.** AI messages and voice segments are embedded because they are always read and written with their parent. Vocabulary and history are separate collections because they need pagination and their own indexes. Embedded arrays are bounded (app cap 200 messages, DB validator cap 400) to stay far from the 16 MB document limit.
2. **Soft references by language code.** Documents stay self-contained (no `populate`, cache-friendly). The lost referential integrity is enforced in the API: deleting a referenced language returns HTTP 409, and soft-delete (`isActive: false`) is used instead.
3. **No `ON DELETE CASCADE`.** Deleting a user cascades over their vocabulary, history and conversations in application code, inside a multi-document **transaction** on a replica set (sequential fallback on standalone; the response reports `atomic: true/false`).
4. **Two-layer validation.** Mongoose validates in the app; `$jsonSchema` validators on all 7 collections make MongoDB itself reject invalid writes, including the conditional shape of polymorphic history documents (`oneOf` on `type`).
5. **Query-driven indexes.** List screens filter by user and sort by time, so indexes are compound (`{user: 1, createdAt: -1}`, …). Verified with `explain()`: the "recents" query examines 20 of 2,563 documents via `IXSCAN` with no in-memory sort.

## Offline-first mobile app

| Feature | Guest | Signed in, backend down |
|---|---|---|
| Text translation (ML Kit, language pack downloaded once) | yes | yes |
| Speech to text (Vosk, Android) | yes | yes |
| Text to speech | yes | yes |
| History and saved words | local only | queued for sync |
| System word bank | no | cached copy |
| AI chat / summaries | no | no (needs Gemini via backend) |

Implementation lives in `mobile/lib/core/`: `session.dart` for guest/account identity, an `api_client.dart` with timeouts and a circuit breaker, a lock-protected `local_store.dart`, and an ordered, idempotent `sync_queue.dart` replayed on app start, login and pull-to-refresh. Model resolution order: installed on device → backend (cached) → built-in default.

## Getting started

### Prerequisites

Node.js 18+, MongoDB 7 (Docker is the easiest), Flutter SDK 3.3+.

### 1. MongoDB

```bash
docker run -d --name lingua-mongo -p 27017:27017 mongo:7
```

### 2. Backend (port 5000)

```bash
cd backend
cp .env.example .env        # set JWT_SECRET; GEMINI_API_KEY is optional
npm install
npm run seed:admin          # admin@example.com / Admin@123
npm run seed:data           # base sample data + user1@example.com / User@123
npm run db:sync             # attach $jsonSchema validators and sync indexes (idempotent)
npm run seed:rich           # optional: 15 learners and ~2.5k histories for demos
npm run dev
```

Without a Gemini key the AI tab shows a friendly error; everything else works. The admin can also set the key later in the admin console.

### 3. Admin web (port 4000)

```bash
cd admin-web
cp .env.example .env
npm install
npm start                   # http://localhost:4000
```

### 4. Mobile

```bash
cd mobile
flutter pub get
flutter run
```

The API address is set in `mobile/lib/core/constants.dart` (Android emulator `10.0.2.2:5000`, iOS simulator `localhost:5000`; use your LAN IP on a physical device).

### Demo accounts (local seed only)

| Account | Password | Role |
|---|---|---|
| `admin@example.com` | `Admin@123` | admin |
| `user1@example.com` | `User@123` | user |
| `learner1..15@example.com` | `User@123` | user (after `seed:rich`) |

## More documentation

- [Backend API reference](backend/README.md)
- [Admin console](admin-web/README.md)
- [Mobile app](mobile/README.md)
- [Engineering notes](docs/engineering-notes.md): DB protection rules and platform pitfalls
- [UI prototypes](docs/prototype/): clickable single-file HTML (open `prototype_v2.html` in a browser)
