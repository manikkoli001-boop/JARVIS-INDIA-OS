import { create } from 'zustand'

export const useSystemStore = create((set) => ({
  notifications: [],
  pushNotification: (message, type = 'info') =>
    set((state) => ({
      notifications: [...state.notifications, { id: Date.now(), message, type }],
    })),
  clearNotification: (id) =>
    set((state) => ({
      notifications: state.notifications.filter((item) => item.id !== id),
    })),
}))
