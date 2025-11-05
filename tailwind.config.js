/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./app/index.html', './app/src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        background: '#0f172a',
        canvas: '#111827',
      },
    },
  },
  plugins: [],
};
