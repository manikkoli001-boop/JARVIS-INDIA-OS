import { createBrowserRouter } from 'react-router-dom'
import DashboardPage from '../pages/DashboardPage'
import AssistantPage from '../pages/AssistantPage'
import AutomationsPage from '../pages/AutomationsPage'
import SystemCorePage from '../pages/SystemCorePage'

export const appRouter = createBrowserRouter([
  { path: '/', element: <DashboardPage /> },
  { path: '/assistant', element: <AssistantPage /> },
  { path: '/automations', element: <AutomationsPage /> },
  { path: '/system-core', element: <SystemCorePage /> },
])
