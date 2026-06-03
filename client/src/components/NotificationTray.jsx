import { useSystemStore } from '../store/systemStore'

export function NotificationTray() {
  const notifications = useSystemStore((state) => state.notifications)
  return (
    <div className="fixed bottom-3 right-3 z-50 space-y-2">
      {notifications.slice(-4).map((item) => (
        <div key={item.id} className="rounded-md border border-cyan-500/30 bg-black/70 px-3 py-2 text-xs">
          {item.message}
        </div>
      ))}
    </div>
  )
}
