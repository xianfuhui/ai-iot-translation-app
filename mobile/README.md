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
| Live voice translation | Partial (still-being-spoken) sentences are translated as you talk; the final sentence usually hits an in-memory cache |
| Smart glasses | Connect Brilliant Labs Frame over Bluetooth LE (top-bar glasses button); every translation, spoken or typed, is pushed to the glasses display |
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
├── services/      # one service per backend module + translation, Vosk, offline packs, frame_service (smart glasses over BLE)
├── providers/     # auth state (Provider)
├── screens/       # splash, home, auth, translate, ai, vocabulary, history, profile, models
└── widgets/       # brand mark, connection banner, word tools, frame_connect_sheet (glasses pairing UI)
```

## Tests

```bash
flutter test     # diacritic removal and line wrapping for the glasses display
```

Platform notes (iOS simulator architecture, Vosk on iOS, smart-glasses BLE) are in [`../docs/engineering-notes.md`](../docs/engineering-notes.md).
