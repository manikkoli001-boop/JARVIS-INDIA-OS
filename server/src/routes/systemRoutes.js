import { Router } from 'express'
import { dashboardMetrics, systemStatus } from '../controllers/systemController.js'
import { requireAuth } from '../middleware/authMiddleware.js'

const router = Router()

router.get('/metrics', requireAuth, dashboardMetrics)
router.get('/status', requireAuth, systemStatus)

export default router
