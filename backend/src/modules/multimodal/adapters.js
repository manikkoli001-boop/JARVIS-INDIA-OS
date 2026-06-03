function visionAdapter(payload) {
  return {
    mode: 'vision',
    accepted: Boolean(payload?.imageRef),
    summary: payload?.imageRef
      ? `Vision analysis queued for ${payload.imageRef}`
      : 'No image payload attached',
  }
}

function voiceAdapter(payload) {
  return {
    mode: 'voice',
    accepted: Boolean(payload?.voiceRef),
    summary: payload?.voiceRef
      ? `Voice processing queued for ${payload.voiceRef}`
      : 'No voice payload attached',
  }
}

module.exports = { visionAdapter, voiceAdapter }
