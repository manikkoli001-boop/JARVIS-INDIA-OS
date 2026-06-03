import mongoose from 'mongoose'

const memorySchema = new mongoose.Schema(
  {
    userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
    role: { type: String, required: true },
    content: { type: String, required: true },
  },
  { timestamps: true },
)

export const MemoryEntry = mongoose.model('MemoryEntry', memorySchema)
