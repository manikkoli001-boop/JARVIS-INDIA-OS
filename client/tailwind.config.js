/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        jarvisBg: '#050816',
        jarvisPanel: '#0B1120',
        jarvisNeon: '#00F5FF',
        jarvisGlow: '#00E5FF',
      },
    },
  },
  plugins: [],
}
