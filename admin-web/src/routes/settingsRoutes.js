const express = require('express');
const router = express.Router();
const apiClient = require('../services/apiClient');
const { requireAuth } = require('../middleware/requireAuth');

router.use(requireAuth);

// Lấy & xóa thông báo flash lưu trong session (hiện 1 lần sau redirect)
const takeFlash = (req) => {
  const flash = req.session.flash || null;
  delete req.session.flash;
  return flash;
};
const setFlash = (req, type, message) => {
  req.session.flash = { type, message };
};
const apiMessage = (err, fallback) => err.response?.data?.message || fallback;

// Trang Cài đặt: cấu hình AI + đổi mật khẩu
router.get('/settings', async (req, res, next) => {
  try {
    const { data } = await apiClient(req).get('/settings/ai');
    res.render('settings/index', { ai: data, flash: takeFlash(req) });
  } catch (err) {
    next(err);
  }
});

// Lưu cấu hình AI (API key để trống = giữ key cũ)
router.post('/settings/ai', async (req, res, next) => {
  try {
    const { apiKey, model, maxInputChars, clearKey } = req.body;
    await apiClient(req).put('/settings/ai', {
      apiKey,
      model,
      maxInputChars,
      clearKey: clearKey === 'on',
    });
    setFlash(req, 'success', 'Đã lưu cấu hình AI');
    res.redirect('/settings');
  } catch (err) {
    if (err.response?.status === 401) return next(err);
    setFlash(req, 'error', apiMessage(err, 'Không lưu được cấu hình AI'));
    res.redirect('/settings');
  }
});

// Gọi thử Gemini (dùng key mới nhập nếu có, không thì key đang lưu)
router.post('/settings/ai/test', async (req, res, next) => {
  try {
    const { apiKey, model } = req.body;
    const { data } = await apiClient(req).post('/settings/ai/test', { apiKey, model });
    setFlash(req, 'success', data.message);
  } catch (err) {
    if (err.response?.status === 401) return next(err);
    setFlash(req, 'error', apiMessage(err, 'Không kết nối được tới backend'));
  }
  res.redirect('/settings');
});

// Đổi mật khẩu admin đang đăng nhập
router.post('/settings/password', async (req, res, next) => {
  const { oldPassword, newPassword, confirmPassword } = req.body;
  if (!oldPassword || !newPassword) {
    setFlash(req, 'error', 'Vui lòng nhập đầy đủ mật khẩu cũ và mật khẩu mới');
    return res.redirect('/settings#password');
  }
  if (newPassword !== confirmPassword) {
    setFlash(req, 'error', 'Mật khẩu xác nhận không khớp');
    return res.redirect('/settings#password');
  }
  if (newPassword === oldPassword) {
    setFlash(req, 'error', 'Mật khẩu mới phải khác mật khẩu cũ');
    return res.redirect('/settings#password');
  }
  try {
    await apiClient(req).put('/auth/change-password', { oldPassword, newPassword });
    setFlash(req, 'success', 'Đổi mật khẩu thành công');
  } catch (err) {
    // 401 do sai mật khẩu cũ KHÔNG phải token hết hạn -> không đá về login
    setFlash(req, 'error', apiMessage(err, 'Đổi mật khẩu thất bại'));
  }
  res.redirect('/settings#password');
});

module.exports = router;
