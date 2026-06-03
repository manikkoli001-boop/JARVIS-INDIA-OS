import { Router } from 'express'
import { chat, memory } from '../controllers/aiController.js'
import { requireAuth } from '../middleware/authMiddleware.js'

const router = Router()

router.post('/chat', requireAuth, chat)
router.get('/memory', requireAuth, memory)

export default router
