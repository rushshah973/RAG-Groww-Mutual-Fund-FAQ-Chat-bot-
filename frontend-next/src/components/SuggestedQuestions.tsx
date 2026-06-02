import React from "react"
import { useChatStore } from "../store/useChatStore"
import { ArrowRight, HelpCircle } from "lucide-react"

export default function SuggestedQuestions() {
  const sendMessage = useChatStore((state) => state.sendMessage)

  const sampleQuestions = [
    "What is the exit load of Axis Small Cap Fund?",
    "What is the minimum SIP amount for HDFC Top 100 Fund?",
    "Who is the fund manager of Nippon India Small Cap Fund?",
    "What is the exit load of SBI Small Cap Fund?",
    "What is the benchmark index of ICICI Prudential Bluechip Fund?"
  ]

  return (
    <div className="mt-8">
      <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">
        Suggested Inquiries
      </h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
        {sampleQuestions.map((q, i) => (
          <button
            key={i}
            onClick={() => sendMessage(q)}
            className="flex items-start justify-between gap-3 text-left p-4 bg-white hover:bg-groww-lightGreen/10 border border-gray-150 hover:border-groww-green/40 rounded-xl hover:shadow-cardHover transition-all duration-200 group"
          >
            <div className="flex gap-3">
              <HelpCircle className="w-5 h-5 text-gray-400 group-hover:text-groww-green shrink-0 mt-0.5" />
              <span className="text-sm font-medium text-gray-700 group-hover:text-gray-900 leading-snug">
                {q}
              </span>
            </div>
            <ArrowRight className="w-4 h-4 text-gray-300 group-hover:text-groww-green group-hover:translate-x-1 shrink-0 mt-1 transition-all duration-200" />
          </button>
        ))}
      </div>
    </div>
  )
}
