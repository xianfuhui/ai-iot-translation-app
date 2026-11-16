const express = require('express');
const router = express.Router();
const {
  getAiSettings,
  updateAiSettings,
  testAiSettings,
} = require('../controllers/settingController');
const { protect, adminOnly } = require('../middleware/auth');

router.use(protect, adminOnly);

router.get('/ai', getAiSettings);
router.put('/ai', updateAiSettings);
router.post('/ai/test', testAiSettings);

module.exports = router;
