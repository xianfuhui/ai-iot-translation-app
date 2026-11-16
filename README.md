# Lingua: AI Translation & Language Learning App

> An offline-first mobile app that translates speech on-device and shows the translation live on smart glasses, with an AI assistant, a Node.js API, an admin console and a carefully modelled MongoDB database.

![Flutter](https://img.shields.io/badge/Flutter-3.x-02569B?logo=flutter&logoColor=white) ![Node.js](https://img.shields.io/badge/Node.js-Express-339933?logo=nodedotjs&logoColor=white) ![MongoDB](https://img.shields.io/badge/MongoDB-7-47A248?logo=mongodb&logoColor=white) ![Gemini](https://img.shields.io/badge/Google-Gemini-4285F4) ![BLE](https://img.shields.io/badge/Bluetooth_LE-Brilliant_Labs_Frame-0082FC?logo=bluetooth&logoColor=white)

| | |
|---|---|
| **Type** | Team project, Advanced Database Systems course (Master's program) |
| **Domain** | Mobile app, REST API, admin web, NoSQL data modelling |
| **Highlights** | On-device ML translation and speech, live subtitles on smart glasses (BLE), offline sync queue, `$jsonSchema` validation, query-driven indexes, transactions |

**Contents:** [Overview](#-overview) · [Key Features](#-key-features) · [Screenshots](#-screenshots) · [Tech Stack](#-tech-stack) · [Architecture](#-architecture) · [Project Structure](#-project-structure) · [Getting Started](#-getting-started) · [Configuration](#-configuration) · [Notes & Roadmap](#-notes--roadmap)

## 📖 Overview

Lingua translates text and speech **on the device** (no network needed after a one-time model download), can stream the translation to **Brilliant Labs Frame smart glasses** while you talk, saves words for flashcard practice, and offers a Gemini-powered AI assistant. Administrators manage users, languages, offline model packs and the system vocabulary from a web console. The app also serves as a vehicle to study **NoSQL document modelling** on MongoDB.

## ✨ Key Features

- **On-device translation** (Google ML Kit), **speech-to-text** (Vosk, Android) and **text-to-speech** (system engine)
- **Offline-first with guest mode**: history and saved words are stored locally, queued, and synced when the backend is reachable
- **Live voice conversations**: the sentence you are still speaking is translated word by word (partial results), and each session keeps its turns with times and duration, plus an AI-generated summary
- **Smart-glasses subtitles**: connect Brilliant Labs Frame over Bluetooth LE and see the translation in front of your eyes in real time; auto-reconnects to the last pair of glasses
- **Vocabulary and flashcards**: personal word list, curated system word bank, pronunciation audio
- **AI assistant**: chat and summaries through Gemini, proxied by the backend so the key stays server-side
- **Admin console**: users, languages, model catalog with file upload, system vocabulary (manual entry or Excel import), history, statistics
- **Database engineering**: schema validation, compound indexes, transactions and bounded embedded arrays

## 📸 Screenshots

### Mobile app (Android)

Android screens from the clickable UI prototype in [`docs/prototype/`](docs/prototype/).

| Translate | Save a word | AI assistant | Vocabulary |
|---|---|---|---|
| ![Translate](docs/images/android-01-translate.png) | ![Save word](docs/images/android-02-save-word.png) | ![AI](docs/images/android-03-ai-assistant.png) | ![Vocabulary](docs/images/android-04-vocabulary.png) |

| Flashcard | Profile | Sign in |
|---|---|---|
| ![Flashcard](docs/images/android-05-flashcard.png) | ![Profile](docs/images/android-06-profile.png) | ![Login](docs/images/android-07-login.png) |

### Live voice translation (simulated)

Voice capture needs a real microphone, so these two screens are **simulated mockups** rendered from the app's actual UI strings and theme ([source](docs/prototype/android-voice-glasses-mockup.html)).

| While speaking: live partial translation | Finished session: turns, timings, AI summary |
|---|---|
| ![Voice listening](docs/images/android-voice-01-listening.png) | ![Voice session](docs/images/android-voice-02-session.png) |

### Smart glasses: Brilliant Labs Frame (simulated)

Also simulated (no glasses attached). The text layout on the glasses re-implements `FrameService.wrapForFrame` and `removeDiacritics`.

| 1. Scan for glasses | 2. Connected: settings and test |
|---|---|
| ![Scan](docs/images/android-glasses-01-scan.png) | ![Connected](docs/images/android-glasses-02-connected.png) |

**What the wearer sees:** the phone while speaking (left) and the 640×400 glasses display (right).

![Glasses live view](docs/images/android-glasses-03-live-view.png)

### Admin console

Real screenshots of `admin-web` running against the real backend, loaded with the demo seed (`seed:data` + `seed:rich`: 18 users, 2,555 translation records, 253 saved words).

| Sign in | Dashboard |
|---|---|
| ![Login](docs/images/admin-01-login.png) | ![Dashboard](docs/images/admin-02-dashboard.png) |

| Users | System vocabulary (manual or Excel import) |
|---|---|
| ![Users](docs/images/admin-03-users.png) | ![Vocabulary](docs/images/admin-04-vocabulary.png) |

| Translation history | Languages and offline models |
|---|---|
| ![History](docs/images/admin-05-history.png) | ![Languages](docs/images/admin-06-languages-models.png) |

The database diagram is in [Architecture](#-architecture).

## 🛠 Tech Stack

| Component | Stack |
|---|---|
| [`mobile/`](mobile) | Flutter 3 (Android, iOS), Provider, ML Kit Translation, Vosk, flutter_tts, flutter_blue_plus (Bluetooth LE) |
| Smart glasses | Brilliant Labs Frame, BLE UART, Lua display commands |
| [`backend/`](backend) | Node.js, Express, Mongoose, JWT, Gemini API |
| [`admin-web/`](admin-web) | Node.js, Express, EJS (server-rendered), express-session |
| Database | MongoDB 7, database `language_app`, 7 collections |

## 🏗 Architecture

```
Flutter app ──┐
              ├──▶ REST API (backend :5000) ──▶ MongoDB
Admin web  ───┘         │
 (:4000)                └──▶ Gemini API (chat, summaries)

Flutter app ──Bluetooth LE──▶ Brilliant Labs Frame (live translation subtitles)
```

### Smart-glasses link

`mobile/lib/services/frame_service.dart` talks to the glasses directly over BLE, with no extra script installed on them.

- **Protocol:** Nordic-style BLE UART. The app writes Lua snippets (`frame.display.text(...)`, `frame.display.show()`) to the TX characteristic, which the glasses run immediately; `0x03` interrupts a running program.
- **Smooth live text:** only the **latest** text is kept. If a newer partial arrives while one is still being sent, the older one is dropped instead of queued, so subtitles never lag behind fast speakers.
- **Layout for a 640×400 display:** up to 4 lines, 24 character units per line (CJK counts double), older lines scroll up like subtitles; Vietnamese diacritics can be stripped because the default firmware font only draws basic Latin.
- **Robustness:** singleton connection that survives tab changes, auto-reconnect to the last device (never prompts for permissions at startup), MTU negotiation, writes paced to avoid flooding BLE.
- **Tests:** `mobile/test/frame_service_test.dart` covers diacritic removal and line wrapping.

### Database design

![Database schema](docs/db-schema.png)

*Generated with MongoDB Compass from the live database. Solid edges are `ObjectId` references; `languages` is referenced softly by code (`"en"`, `"vi"`, …).*

| Collection | Purpose | Key design decision |
|---|---|---|
| `users` | Accounts (user/admin) | bcrypt-hashed password, `select: false` |
| `translationhistories` | Translation history | **Polymorphic** by `type` (`text`, `speech`, `ai_chat`, `conversation`); voice sessions embed `segments[]` |
| `vocabularies` | Per-user saved words | Unique compound index `{user, word, targetLanguage}` |
| `systemvocabularies` | Admin-curated word bank | `createdBy` → `users` |
| `aiconversations` | Gemini chat sessions | `messages[]` embedded: one read returns the whole conversation |
| `languages` | Supported languages | Soft-referenced **by `code`**, not ObjectId |
| `models` | Vosk / ML Kit model catalog | Unique `{type, languageCode, identifier}` |

1. **Embed vs reference.** Messages and voice segments are embedded because they are always read with their parent. Vocabulary and history are separate collections because they need pagination and their own indexes. Embedded arrays are bounded (app cap 200, DB validator cap 400) to stay far from the 16 MB document limit.
2. **Soft references by language code.** Documents stay self-contained. Integrity is enforced in the API: deleting a referenced language returns HTTP 409; soft-delete (`isActive: false`) is used instead.
3. **No `ON DELETE CASCADE`.** Deleting a user cascades in application code, inside a multi-document **transaction** on a replica set (sequential fallback on standalone; the response reports `atomic`).
4. **Two-layer validation.** Mongoose in the app, plus `$jsonSchema` validators on all 7 collections, including `oneOf` on `type` for polymorphic history.
5. **Query-driven indexes.** Compound `{user, createdAt}`-style indexes; `explain()` shows the "recents" query examining 20 of 2,563 documents via `IXSCAN` with no in-memory sort.

### Offline-first mobile app

| Feature | Guest | Signed in, backend down |
|---|---|---|
| Text translation (ML Kit, pack downloaded once) | yes | yes |
| Speech to text (Vosk, Android) | yes | yes |
| Text to speech | yes | yes |
| History and saved words | local only | queued for sync |
| System word bank | no | cached copy |
| AI chat / summaries | no | no |

In `mobile/lib/core/`: `session.dart` (guest/account identity), `api_client.dart` with `backend_status.dart` (8 s timeout, 20 s circuit breaker), `local_store.dart` (lock-protected storage) and `sync_queue.dart` (ordered, idempotent replay on start, login and pull-to-refresh; a guest's local data is adopted on sign-in). Model resolution: installed on device → backend (cached) → built-in default.

## 📁 Project Structure

```
ai-translation-app/
├── mobile/       # Flutter client (incl. smart-glasses BLE service)
├── backend/      # REST API, seed scripts, DB validators
├── admin-web/    # Admin dashboard (EJS)
└── docs/         # DB diagram, UI prototypes and mockups, screenshots, engineering notes
```

## 🚀 Getting Started

### Prerequisites

Node.js 18+, MongoDB 7 (Docker is easiest), Flutter SDK 3.3+. For the glasses feature: a Brilliant Labs Frame and an Android/iOS device with Bluetooth LE.

### Installation and run

**1. MongoDB**

```bash
docker run -d --name lingua-mongo -p 27017:27017 mongo:7
```

**2. Backend** (port 5000)

```bash
cd backend
cp .env.example .env        # set JWT_SECRET; GEMINI_API_KEY is optional
npm install
npm run seed:admin          # admin@example.com / Admin@123
npm run seed:data           # sample data + user1@example.com / User@123
npm run db:sync             # attach $jsonSchema validators, sync indexes
npm run seed:rich           # optional: 15 learners, ~2.5k histories
npm run dev
```

**3. Admin web** (port 4000)

```bash
cd admin-web
cp .env.example .env
npm install
npm start                   # http://localhost:4000
```

**4. Mobile**

```bash
cd mobile
flutter pub get
flutter run
```

Demo accounts (local seed only): `admin@example.com` / `Admin@123` (admin), `user1@example.com` / `User@123` (user), `learner1..15@example.com` / `User@123` (after `seed:rich`).

## ⚙️ Configuration

| Setting | Where | Default | Purpose |
|---|---|---|---|
| `MONGO_URI`, `JWT_SECRET` | `backend/.env` | local MongoDB | Database and token signing |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | `backend/.env` | empty, `gemini-2.0-flash` | Enables the AI tab (a friendly error shows without a key) |
| `MAX_MODEL_UPLOAD_MB` | `backend/.env` | 800 | Size limit for model uploads |
| `BACKEND_API_URL`, `SESSION_SECRET` | `admin-web/.env` | `http://localhost:5000/api` | Admin web to API link |
| `baseUrl` | `mobile/lib/core/constants.dart` | Android `10.0.2.2:5000`, iOS `localhost:5000` | Use your LAN IP on a physical device |
| Bluetooth permissions | `AndroidManifest.xml`, `Info.plist` | declared | Needed to scan and connect to the glasses (Android 12+ `BLUETOOTH_SCAN/CONNECT`) |

## 📝 Notes & Roadmap

- Further reading: [Backend API reference](backend/README.md) · [Admin console](admin-web/README.md) · [Mobile app](mobile/README.md) · [Engineering notes](docs/engineering-notes.md)
- Vosk speech recognition is Android-only; iOS uses typed input.
- The voice and smart-glasses screenshots are simulated (they need a microphone and hardware); everything else was captured from the running admin web or the UI prototype.
- Run the glasses unit tests with `cd mobile && flutter test`.
- Possible next steps: record a demo video on real glasses, support other BLE displays, OpenAPI/Postman collection, automated API tests, an admin page for the Gemini key, charts for registration trends in the admin dashboard.
