# Mobile App (Flutter)

Offline-first client for Lingua: on-device translation and speech, flashcards, history, and an AI assistant.

## Run

```bash
flutter pub get
flutter run
```

Requires Flutter SDK 3.3+ and the [backend](../backend) running. Set the API address in `lib/core/constants.dart` (Android emulator `10.0.2.2:5000`, iOS simulator `localhost:5000`, physical device: your LAN IP).

## Features

| Area | Implementation |
|---|---|
| Translation | Google ML Kit on device; language packs download once |
| Speech to text | Vosk on device (Android only); models resolved from device, then backend, then built-in defaults |
| Text to speech | System TTS engine via `flutter_tts` |
| Vocabulary and flashcards | Save words from translations, system word bank, pronunciation audio |
| History | Text, speech and conversation entries; voice sessions show turns, timings and an AI summary |
| AI assistant | Chat and summaries through the backend (needs network) |
| Offline packs | Profile → offline packs: pre-download or delete ML Kit and Vosk models |
| Guest mode | Full local use without an account; data is adopted by the account on sign-in |

## Structure

```
lib/
├── main.dart
├── core/          # api client, session, local store, sync queue, backend status, built-in models, theme
├── models/        # User, Language, Vocabulary, History, AIConversation, ModelConfig
├── services/      # one service per backend module + translation, Vosk, offline packs
├── providers/     # auth state (Provider)
└── screens/       # splash, home, auth, translate, ai, vocabulary, history, profile, models
```

Platform notes (iOS simulator architecture, Vosk on iOS, permissions) are in [`../docs/engineering-notes.md`](../docs/engineering-notes.md).
