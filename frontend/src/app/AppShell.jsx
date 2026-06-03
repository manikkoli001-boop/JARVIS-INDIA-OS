import { RouterProvider } from 'react-router-dom'
import { appRouter } from './router'

function AppShell() {
  return <RouterProvider router={appRouter} />
}

export default AppShell
