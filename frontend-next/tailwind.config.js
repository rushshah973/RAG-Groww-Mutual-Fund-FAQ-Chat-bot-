/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        groww: {
          green: "#00D09C",
          lightGreen: "#EAFBF5",
          dark: "#111827",
          medium: "#374151",
          light: "#6B7280",
          bgLight: "#F8FAFC",
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
