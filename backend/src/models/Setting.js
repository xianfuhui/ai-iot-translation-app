const mongoose = require('mongoose');

// Cấu hình hệ thống dạng key-value (vd: key "ai" chứa API key Gemini).
// Giá trị nhạy cảm (apiKey) được mã hóa AES-256-GCM trước khi lưu — xem utils/crypto.js
const settingSchema = new mongoose.Schema(
  {
    key: { type: String, required: true, unique: true, trim: true },
    value: { type: mongoose.Schema.Types.Mixed, default: {} },
    updatedBy: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
  },
  { timestamps: true }
);

module.exports = mongoose.model('Setting', settingSchema);
