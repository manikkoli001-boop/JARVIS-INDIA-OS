const test = require('node:test')
const assert = require('node:assert/strict')
const request = require('supertest')

const { createApp } = require('../src/app')

test('health endpoint should return ok', async () => {
  const app = createApp()
  const response = await request(app).get('/api/v1/health')
  assert.equal(response.status, 200)
  assert.equal(response.body.status, 'ok')
})

test('assistant endpoint should return workflow and inference', async () => {
  const app = createApp()
  const response = await request(app)
    .post('/api/v1/core/assistant')
    .send({ command: 'Build deployment package' })

  assert.equal(response.status, 200)
  assert.equal(response.body.accepted, true)
  assert.equal(Array.isArray(response.body.workflow), true)
  assert.equal(typeof response.body.inference.selectedProvider, 'string')
})
