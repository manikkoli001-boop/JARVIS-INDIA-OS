import bcrypt from 'bcryptjs'
import { User } from '../models/User.js'
import { signToken } from '../services/tokenService.js'

export async function signup(req, res) {
  const { name, email, password } = req.body
  const existing = await User.findOne({ email })
  if (existing) return res.status(409).json({ message: 'Email already exists' })

  const passwordHash = await bcrypt.hash(password, 10)
  const user = await User.create({ name, email, passwordHash })
  const token = signToken({ id: user._id, email: user.email, name: user.name })
  return res.status(201).json({ token, user: { id: user._id, name: user.name, email: user.email } })
}

export async function login(req, res) {
  const { email, password } = req.body
  const user = await User.findOne({ email })
  if (!user) return res.status(401).json({ message: 'Invalid credentials' })

  const valid = await bcrypt.compare(password, user.passwordHash)
  if (!valid) return res.status(401).json({ message: 'Invalid credentials' })

  const token = signToken({ id: user._id, email: user.email, name: user.name })
  return res.json({ token, user: { id: user._id, name: user.name, email: user.email } })
}

export async function me(req, res) {
  const user = await User.findById(req.user.id).select('-passwordHash')
  return res.json({ user })
}
