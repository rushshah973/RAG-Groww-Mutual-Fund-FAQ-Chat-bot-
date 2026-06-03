/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        white: "var(--bg-card)",
        gray: {
          50: "var(--bg-light)",
          100: "var(--border-color)",
          150: "var(--border-color)",
          200: "var(--border-card)",
          300: "var(--text-muted)",
          400: "var(--text-muted)",
          500: "var(--text-muted)",
          600: "var(--text-secondary)",
          700: "var(--text-secondary)",
          800: "var(--text-primary)",
          900: "var(--text-primary)",
        },
        slate: {
          50: "var(--bg-light)",
          900: "var(--bg-sidebar)",
          950: "var(--bg-light)",
        },
        groww: {
          green: "#00D09C",
          lightGreen: "var(--light-green-themed)",
          dark: "var(--text-primary)",
          medium: "var(--text-secondary)",
          light: "var(--text-muted)",
          bgLight: "var(--bg-light)",
        },
        warning: "#F59E0B",
        error: "#EF4444",
      },
      fontFamily: {
        sans: ["Inter", "Outfit", "sans-serif"],
      },
      boxShadow: {
        premium: "0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 8px -1px rgba(0, 0, 0, 0.03)",
        cardHover: "0 12px 30px -4px rgba(0, 208, 156, 0.1), 0 4px 12px -2px rgba(0, 0, 0, 0.04)",
      },
    },
  },
  plugins: [],
}
