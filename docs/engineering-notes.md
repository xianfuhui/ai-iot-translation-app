# Engineering notes

Conventions and pitfalls worth knowing before changing the code.

## Database protection layers (keep when touching the backend)

- **Query-driven indexes** are declared in the Mongoose schemas (compound `{user, createdAt}`, `{user, updatedAt}`, …). When adding or changing a query, add the matching index and run `npm run db:sync`.
- **`$jsonSchema` validators** cover all 7 collections (`backend/scripts/sync-db.js`), including the polymorphic constraint on `translationhistories` (`conversation` requires `segments >= 1`; other types require `sourceText` and `translatedText`). Direct `mongosh` writes are validated too.
- **User deletion cascades** to vocabulary, history and conversations, in a transaction on a replica set and sequentially on standalone (the response carries `atomic`).
- **Language deletion is guarded**: HTTP 409 while the code is still referenced by models, vocabulary or history. Use `isActive` for soft-delete; the mobile app lists only active languages.
- **`messages[]` is bounded**: the app rejects at 200 messages (409 `CONVERSATION_FULL`), the DB validator hard-caps at 400. Never make an embedded array unbounded.
- Keep the JSON response shapes stable: the mobile app and admin web depend on them.

## Mobile platform pitfalls

1. **iOS simulator architecture.** `google_mlkit_translation` pins a GoogleMLKit pod without an arm64-simulator slice, so use an x86_64/Rosetta simulator. Real arm64 devices are fine.
2. **Vosk has no iOS implementation.** Every code path into Vosk must go through `VoskService.isSupported` (Android only); the microphone UI is hidden on iOS.
3. iOS deployment target is **15.5** (Podfile and project), required by ML Kit.
4. `baseUrl` in `mobile/lib/core/constants.dart` is platform-aware (Android `10.0.2.2`, iOS `localhost`, port 5000). Use the LAN IP on a physical device.
5. An ATS exception for `http://localhost` is set in `ios/Runner/Info.plist`.
6. Android: microphone permission and the JNA ProGuard rules for Vosk are already configured.

## Secrets

Never commit `.env` files or any key (`GEMINI_API_KEY`, `JWT_SECRET`, `SESSION_SECRET`). Use the provided `.env.example` files as templates.
