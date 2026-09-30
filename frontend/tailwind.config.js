/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        family: {
          50: '#fdf8f6',
          100: '#f2e8e5',
          200: '#eaddd7',
          300: '#e0cec7',
          400: '#d2bab0',
          500: '#bfa094',
          600: '#a18072',
          700: '#846356',
          800: '#6d5146',
          900: '#5c443b',
          950: '#32231e',
        },
        sage: {
          50: '#f4f7f4',
          100: '#e5ece5',
          200: '#ceddce',
          300: '#a9c4aa',
          400: '#7fa481',
          500: '#608662',
          600: '#4b6b4d',
          700: '#3d553e',
          800: '#334534',
          900: '#2b392c',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Lora', 'Georgia', 'serif'],
      },
    },
  },
  plugins: [],
}
