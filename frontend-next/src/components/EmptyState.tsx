import React from "react"
import WelcomeCard from "./WelcomeCard"
import SuggestedQuestions from "./SuggestedQuestions"
import { Compass } from "lucide-react"

export default function EmptyState() {
  return (
    <div className="max-w-3xl mx-auto py-6 md:py-12 px-4 flex flex-col justify-center min-h-[70vh]">
      {/* Welcome Hero Container */}
      <WelcomeCard />

      {/* Quick Suggestion List */}
      <SuggestedQuestions />

      {/* Suggested Topics List */}
      <div className="mt-8 pt-6 border-t border-gray-150 flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2 text-xs font-bold text-gray-400 uppercase tracking-wider">
          <Compass className="w-4 h-4 text-gray-400" />
          <span>Factual Parameters Indexed</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {["Expense Ratios", "Exit Loads", "SIP Minimums", "Fund Managers", "Riskometers", "Account Statements"].map((tag, idx) => (
            <span
              key={idx}
              className="text-[10px] md:text-xs font-semibold text-gray-500 bg-gray-100/80 border border-gray-200/60 px-2.5 py-1 rounded-full"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
