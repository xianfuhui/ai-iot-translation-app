const crypto = require('crypto');

// Khóa mã hóa: ưu tiên SETTINGS_ENCRYPTION_KEY, nếu không có thì dẫn xuất từ JWT_SECRET.
// Lưu ý: đổi khóa này sẽ làm API key đã lưu không giải mã được (admin chỉ cần nhập lại).
const getKey = () =>
  crypto
    .createHash('sha256')
    .update(process.env.SETTINGS_ENCRYPTION_KEY || process.env.JWT_SECRET || 'dev_secret')
    .digest();

const encrypt = (plain) => {
  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv('aes-256-gcm', getKey(), iv);
  const enc = Buffer.concat([cipher.update(plain, 'utf8'), cipher.final()]);
  const tag = cipher.getAuthTag();
  return [iv, tag, enc].map((b) => b.toString('base64')).join('.');
};

const decrypt = (payload) => {
  try {
    const [iv, tag, enc] = payload.split('.').map((s) => Buffer.from(s, 'base64'));
    const decipher = crypto.createDecipheriv('aes-256-gcm', getKey(), iv);
    decipher.setAuthTag(tag);
    return Buffer.concat([decipher.update(enc), decipher.final()]).toString('utf8');
  } catch (e) {
    return '';
  }
};

// "AIzaSy...abcd" -> "AIza••••••abcd"
const maskKey = (key) => {
  if (!key) return '';
  if (key.length <= 8) return '••••••••';
  return `${key.slice(0, 4)}••••••••${key.slice(-4)}`;
};

module.exports = { encrypt, decrypt, maskKey };
