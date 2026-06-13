/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'accent-blue': '#00F0FF',
        'accent-amber': '#FFB800',
        'accent-crimson': '#FF3366',
        'bg-dark': '#0B1021',
        'glass-bg': 'rgba(16, 24, 48, 0.65)',
        'glass-border': 'rgba(0, 240, 255, 0.15)',
      }
    },
  },
  plugins: [],
}
