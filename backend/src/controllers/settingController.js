const Setting = require('../models/Setting');
const { encrypt, decrypt, maskKey } = require('../utils/crypto');
const { callGemini, getAiConfig, invalidateAiConfig } = require('../utils/gemini');

const ALLOWED_MODELS_HINT = 'vd: gemini-2.0-flash, gemini-2.5-flash';

// @desc    Xem cấu hình AI hiện tại (API key luôn bị che)
// @route   GET /api/settings/ai
const getAiSettings = async (req, res, next) => {
  try {
    invalidateAiConfig();
    const cfg = await getAiConfig();
    res.json({
      hasKey: !!cfg.apiKey,
      apiKeyMasked: maskKey(cfg.apiKey),
      apiKeySource: cfg.apiKeySource, // database | env | none
      model: cfg.model,
      maxInputChars: cfg.maxInputChars,
      updatedAt: cfg.updatedAt,
    });
  } catch (error) {
    next(error);
  }
};

// @desc    Cập nhật cấu hình AI. apiKey để trống = giữ nguyên key cũ.
// @route   PUT /api/settings/ai
// body: { apiKey?, model?, maxInputChars?, clearKey? }
const updateAiSettings = async (req, res, next) => {
  try {
    const { apiKey, model, maxInputChars, clearKey } = req.body;

    const doc = (await Setting.findOne({ key: 'ai' })) || new Setting({ key: 'ai', value: {} });
    const value = { ...(doc.value || {}) };

    if (clearKey) {
      delete value.apiKeyEnc;
    } else if (typeof apiKey === 'string' && apiKey.trim()) {
      value.apiKeyEnc = encrypt(apiKey.trim());
    }

    if (typeof model === 'string' && model.trim()) {
      if (!/^[a-zA-Z0-9._-]+$/.test(model.trim())) {
        return res.status(400).json({ message: `Tên model không hợp lệ (${ALLOWED_MODELS_HINT})` });
      }
      value.model = model.trim();
    }

    if (maxInputChars !== undefined && maxInputChars !== '') {
      const n = parseInt(maxInputChars, 10);
      if (!Number.isInteger(n) || n < 500 || n > 100000) {
        return res.status(400).json({ message: 'Giới hạn ký tự phải từ 500 đến 100000' });
      }
      value.maxInputChars = n;
    }

    value.updatedAt = new Date();
    doc.value = value;
    doc.updatedBy = req.user._id;
    doc.markModified('value');
    await doc.save();

    invalidateAiConfig();
    res.json({ message: 'Đã lưu cấu hình AI' });
  } catch (error) {
    next(error);
  }
};

// @desc    Gọi thử Gemini bằng key/model (mới nhập hoặc đang lưu) để kiểm tra
// @route   POST /api/settings/ai/test
// body: { apiKey?, model? }
const testAiSettings = async (req, res) => {
  try {
    const { apiKey, model } = req.body;
    const reply = await callGemini([{ role: 'user', parts: [{ text: 'Reply with exactly: OK' }] }], {
      apiKey: apiKey?.trim() || undefined,
      model: model?.trim() || undefined,
    });
    res.json({ ok: true, message: 'Kết nối Gemini thành công', reply: reply.slice(0, 100) });
  } catch (error) {
    if (error.code === 'NO_API_KEY') {
      return res.status(400).json({ ok: false, message: error.message });
    }
    const detail = error.response?.data?.error?.message || error.message;
    res.status(502).json({ ok: false, message: `Gemini từ chối: ${detail}` });
  }
};

module.exports = { getAiSettings, updateAiSettings, testAiSettings };
