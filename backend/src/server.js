const env = require('./config/env')
const { createApp } = require('./app')

const app = createApp()

app.listen(env.port, () => {
  console.log(`JARVIS backend online at http://localhost:${env.port}`)
})
