import React from "react"
import { useChatStore } from "../store/useChatStore"
import { Menu, ShieldCheck } from "lucide-react"

export default function Header() {
  const { isSidebarOpen, setSidebarOpen } = useChatStore()

  return (
    <header className="sticky top-0 z-30 flex items-center justify-between w-full h-16 px-4 md:px-8 bg-white/80 backdrop-blur-md border-b border-gray-100">
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

      {/* Verified Badge */}
      <div className="flex items-center gap-1.5 py-1.5 px-3 rounded-full bg-groww-lightGreen border border-groww-green/20">
        <ShieldCheck className="w-4 h-4 text-groww-green" />
        <span className="text-xs font-semibold text-groww-green whitespace-nowrap">
          Official Sources Only (AMC | AMFI | SEBI)
        </span>
      </div>
    </header>
  )
}
