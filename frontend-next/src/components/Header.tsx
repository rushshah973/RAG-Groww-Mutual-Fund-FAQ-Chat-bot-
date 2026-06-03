import React, { useState, useEffect } from "react"
import { useChatStore } from "../store/useChatStore"
import { Menu, ShieldCheck, Sun, Moon } from "lucide-react"

export default function Header() {
  const { isSidebarOpen, setSidebarOpen } = useChatStore()
  const [theme, setTheme] = useState<"light" | "dark" | null>(null)

  // Initialize theme from storage or system
  useEffect(() => {
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light")
    
    setTheme(initialTheme)
    if (initialTheme === "dark") {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }, [])

  const toggleTheme = () => {
    const nextTheme = theme === "light" ? "dark" : "light"
    setTheme(nextTheme)
    localStorage.setItem("theme", nextTheme)
    
    if (nextTheme === "dark") {
      document.documentElement.classList.add("dark")
    } else {
      document.documentElement.classList.remove("dark")
    }
  }

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between w-full h-16 px-4 md:px-8 bg-white/80 backdrop-blur-md border-b border-gray-100 transition-colors duration-200">
      {/* Mobile Toggle */}
      <button
        onClick={() => setSidebarOpen(!isSidebarOpen)}
        className="flex items-center justify-center p-2 rounded-lg text-gray-500 hover:text-gray-900 hover:bg-gray-50 md:hidden transition-colors"
        aria-label="Toggle Sidebar"
      >
        <Menu className="w-5 h-5" />
      </button>

      {/* Center Branding / Navigation Title */}
      <div className="flex items-center gap-2">
        <span className="font-semibold text-gray-900 text-base md:text-lg">
          Groww Mutual Fund Assistant
        </span>
      </div>

      {/* Header Actions (Badge + Theme Toggle Button) */}
      <div className="flex items-center gap-2.5">
        <div className="flex items-center gap-1.5 py-1.5 px-3 rounded-full bg-groww-lightGreen border border-groww-green/20">
          <ShieldCheck className="w-4 h-4 text-groww-green" />
          <span className="text-xs font-semibold text-groww-green whitespace-nowrap hidden sm:inline">
            Official Sources Only
          </span>
          <span className="text-xs font-semibold text-groww-green whitespace-nowrap sm:hidden">
            Official Sources
          </span>
        </div>

        {theme && (
          <button
            onClick={toggleTheme}
            className="flex items-center justify-center w-8 h-8 rounded-full bg-groww-lightGreen border border-groww-green/20 text-groww-green hover:bg-groww-green/20 active:scale-95 transition-all"
            aria-label="Toggle Theme"
          >
            {theme === "light" ? (
              <Moon className="w-4 h-4" />
            ) : (
              <Sun className="w-4 h-4" />
            )}
          </button>
        )}
      </div>
    </header>
  )
}
