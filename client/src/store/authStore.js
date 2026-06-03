import { create } from 'zustand'

const token = localStorage.getItem('jarvis-token')

export const useAuthStore = create((set) => ({
  token,
  user: null,
  setAuth: ({ token: nextToken, user }) => {
    localStorage.setItem('jarvis-token', nextToken)
    set({ token: nextToken, user })
  },
  clearAuth: () => {
    localStorage.removeItem('jarvis-token')
    set({ token: null, user: null })
  },
}))
