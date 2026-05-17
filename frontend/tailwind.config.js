/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        baloo: ['"Baloo 2"', 'cursive'],
      },
      colors: {
        eli3: {
          bg: '#fffbf4',
          purple: '#3C3489',
          light: '#EEEDFE',
          mid: '#AFA9EC',
          btn: '#7F77DD',
        },
        spanish: {
          bg: '#f0fdf4',
          dark: '#085041',
          mid: '#1D9E75',
          light: '#E1F5EE',
          text: '#5DCAA5',
        }
      }
    },
  },
  plugins: [],
}
