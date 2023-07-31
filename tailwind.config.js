/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        'synth-pink': '#F222FF'
      }
    },
  },
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  }
}
