import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'
import { useAuthStore } from '../store/authStore'

export function LoginPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    try {
      const { data } = await authService.login(form)
      setAuth(data)
      navigate('/')
    } catch {
      setError('Invalid credentials')
    }
  }

  return (
    <div className="auth-shell">
      <form className="jarvis-panel w-full max-w-md space-y-3" onSubmit={submit}>
        <h2 className="text-2xl text-jarvisNeon">Login</h2>
        <input className="jarvis-input" placeholder="Email" onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="jarvis-input" placeholder="Password" type="password" onChange={(e) => setForm({ ...form, password: e.target.value })} />
        {error ? <p className="text-xs text-red-300">{error}</p> : null}
        <button className="jarvis-button w-full">Access Command Center</button>
        <Link className="text-xs text-cyan-200 underline" to="/signup">
          Create account
        </Link>
      </form>
    </div>
  )
}
