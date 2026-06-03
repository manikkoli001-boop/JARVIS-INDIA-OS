import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { authService } from '../services/authService'
import { useAuthStore } from '../store/authStore'

export function SignupPage() {
  const navigate = useNavigate()
  const setAuth = useAuthStore((s) => s.setAuth)
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')

  const submit = async (e) => {
    e.preventDefault()
    try {
      const { data } = await authService.signup(form)
      setAuth(data)
      navigate('/')
    } catch {
      setError('Signup failed')
    }
  }

  return (
    <div className="auth-shell">
      <form className="jarvis-panel w-full max-w-md space-y-3" onSubmit={submit}>
        <h2 className="text-2xl text-jarvisNeon">Signup</h2>
        <input className="jarvis-input" placeholder="Name" onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <input className="jarvis-input" placeholder="Email" onChange={(e) => setForm({ ...form, email: e.target.value })} />
        <input className="jarvis-input" placeholder="Password" type="password" onChange={(e) => setForm({ ...form, password: e.target.value })} />
        {error ? <p className="text-xs text-red-300">{error}</p> : null}
        <button className="jarvis-button w-full">Create Operator Profile</button>
        <Link className="text-xs text-cyan-200 underline" to="/login">
          Back to login
        </Link>
      </form>
    </div>
  )
}
