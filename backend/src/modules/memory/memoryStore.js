const conversationLog = []

function remember(entry) {
  const record = {
    id: conversationLog.length + 1,
    timestamp: new Date().toISOString(),
    ...entry,
  }
  conversationLog.push(record)
  return record
}

function recent(limit = 10) {
  return conversationLog.slice(-limit)
}

module.exports = { remember, recent }
