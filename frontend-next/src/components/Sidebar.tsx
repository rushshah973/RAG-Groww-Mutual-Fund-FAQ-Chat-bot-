import React from "react"
import { useChatStore } from "../store/useChatStore"
import { MessageSquarePlus, ShieldAlert, Sparkles, TrendingUp, HelpCircle } from "lucide-react"

export default function Sidebar() {
  const { clearChat, isSidebarOpen, setSidebarOpen, sendMessage } = useChatStore()

  const recentTopics = [
    { label: "Expense Ratio Details", query: "What is the expense ratio of Axis Small Cap Fund?" },
    { label: "Exit Load Charges", query: "What is the exit load of SBI Small Cap Fund?" },
    { label: "Minimum SIP Amount", query: "What is the minimum SIP amount for HDFC Top 100 Fund?" },
    { label: "Fund Manager Tenure", query: "Who is the fund manager of Nippon India Small Cap Fund?" },
    { label: "Riskometer Classifications", query: "What is the benchmark index of ICICI Prudential Bluechip Fund?" }
  ]

  return (
    <aside
      className={`fixed top-0 bottom-0 left-0 z-40 flex flex-col w-[280px] bg-white border-r border-gray-100 transition-transform duration-300 ease-in-out md:translate-x-0 ${
        isSidebarOpen ? "translate-x-0" : "-translate-x-full"
      }`}
    >
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-6 h-16 border-b border-gray-50">
        <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-groww-lightGreen">
          <svg
            className="w-5 h-5 text-groww-green"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="3"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-gray-900 tracking-tight text-lg">Groww</span>
            <span className="text-[10px] font-semibold text-groww-green bg-groww-lightGreen px-1.5 py-0.5 rounded-full">
              SECURE
            </span>
          </div>
          <p className="text-xs text-gray-500 font-medium -mt-0.5">MF FAQ Assistant</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="p-4">
        <button
          onClick={() => {
            clearChat()
            setSidebarOpen(false)
          }}
          className="flex items-center justify-center gap-2 w-full py-2.5 px-4 bg-groww-green hover:bg-[#00b88a] text-white font-semibold rounded-lg shadow-sm hover:scale-[1.02] active:scale-[0.98] transition-all duration-200"
        >
          <MessageSquarePlus className="w-4 h-4" />
          New Chat
        </button>
      </div>

      {/* Suggested Topics List */}
      <div className="flex-1 overflow-y-auto px-4 py-2">
        <div className="mb-2 px-2 text-[11px] font-bold text-gray-400 uppercase tracking-wider">
          Suggested Topics
        </div>
        <nav className="space-y-1">
          {recentTopics.map((topic, i) => (
            <button
              key={i}
              onClick={() => {
                sendMessage(topic.query)
                setSidebarOpen(false)
              }}
              className="flex items-center gap-2.5 w-full text-left py-2 px-3 text-sm font-medium text-gray-600 hover:text-groww-green hover:bg-groww-lightGreen rounded-lg transition-colors duration-150 group"
            >
              <TrendingUp className="w-3.5 h-3.5 text-gray-400 group-hover:text-groww-green" />
              <span className="truncate">{topic.label}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Sidebar Footer Disclaimer */}
      <div className="p-4 border-t border-gray-50 bg-gray-50/50">
        <div className="flex gap-2.5 p-3 rounded-lg border border-gray-200 bg-white">
          <ShieldAlert className="w-5 h-5 text-groww-green shrink-0 mt-0.5" />
          <div>
            <h4 className="text-xs font-semibold text-gray-900">Facts-Only Engine</h4>
            <p className="text-[11px] text-gray-500 mt-0.5 leading-relaxed">
              Strictly non-advisory. Offers official details only from AMC, AMFI and SEBI sources.
            </p>
          </div>
        </div>
      </div>
    </aside>
  )
}
