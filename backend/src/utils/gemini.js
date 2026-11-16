const axios = require('axios');
const Setting = require('../models/Setting');
const { decrypt } = require('./crypto');

const GEMINI_API_URL = (model) =>
  `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;

// Mặc định cho giới hạn ký tự gửi tới LLM (tránh vượt quota/token, tránh phí cao).
// Admin có thể đổi trong trang Cài đặt; .env (GEMINI_MAX_INPUT_CHARS) là giá trị dự phòng.
const MAX_LLM_INPUT_CHARS = parseInt(process.env.GEMINI_MAX_INPUT_CHARS, 10) || 8000;

// ===== Cấu hình AI: ưu tiên DB (admin cài đặt), dự phòng .env =====
let cache = null;
let cacheAt = 0;
const CACHE_MS = 30 * 1000;

const invalidateAiConfig = () => {
  cache = null;
};

const getAiConfig = async () => {
  if (cache && Date.now() - cacheAt < CACHE_MS) return cache;

  let stored = {};
  try {
    const doc = await Setting.findOne({ key: 'ai' }).lean();
    stored = doc?.value || {};
  } catch (e) {
    // DB lỗi -> dùng .env
  }

  const dbKey = stored.apiKeyEnc ? decrypt(stored.apiKeyEnc) : '';
  cache = {
    apiKey: dbKey || process.env.GEMINI_API_KEY || '',
    apiKeySource: dbKey ? 'database' : process.env.GEMINI_API_KEY ? 'env' : 'none',
    model: stored.model || process.env.GEMINI_MODEL || 'gemini-2.0-flash',
    maxInputChars: stored.maxInputChars || MAX_LLM_INPUT_CHARS,
    updatedAt: stored.updatedAt || null,
  };
  cacheAt = Date.now();
  return cache;
};

/**
 * Cắt bớt văn bản nếu vượt quá giới hạn ký tự cho phép gửi tới LLM.
 * Giữ lại phần ĐẦU và phần CUỐI, lược bớt đoạn giữa nếu quá dài.
 */
const truncateForLlm = (text, maxChars = MAX_LLM_INPUT_CHARS) => {
  if (!text || text.length <= maxChars) return { text: text || '', truncated: false };

  const headChars = Math.floor(maxChars * 0.6);
  const tailChars = maxChars - headChars - 40;
  const head = text.slice(0, headChars);
  const tail = tailChars > 0 ? text.slice(-tailChars) : '';

  return {
    text: `${head}\n\n[... đã lược bớt một phần nội dung do vượt giới hạn ký tự ...]\n\n${tail}`,
    truncated: true,
  };
};

// Gọi Gemini API với danh sách nội dung (contents). `override` dùng để thử key/model trước khi lưu.
const callGemini = async (contents, override = {}) => {
  const cfg = await getAiConfig();
  const apiKey = override.apiKey || cfg.apiKey;
  const model = override.model || cfg.model;

  if (!apiKey) {
    const err = new Error('Chưa cấu hình Gemini API key. Vào Web Admin → Cài đặt để nhập.');
    err.code = 'NO_API_KEY';
    throw err;
  }

  const response = await axios.post(
    GEMINI_API_URL(model),
    { contents },
    {
      headers: { 'Content-Type': 'application/json', 'x-goog-api-key': apiKey },
      timeout: 30000,
    }
  );
  return response.data?.candidates?.[0]?.content?.parts?.[0]?.text || '';
};

module.exports = {
  callGemini,
  truncateForLlm,
  getAiConfig,
  invalidateAiConfig,
  MAX_LLM_INPUT_CHARS,
};
