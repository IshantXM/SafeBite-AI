/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        doca: {
          navy: '#0f172a',
          blue: '#1e3a8a',
          accent: '#2563eb',
          gold: '#d97706',
          bg: '#f8fafc'
        }
      }
    },
  },
  plugins: [],
}
