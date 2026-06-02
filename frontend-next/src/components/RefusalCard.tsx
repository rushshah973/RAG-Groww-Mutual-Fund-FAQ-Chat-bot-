import React from "react"
import { AlertTriangle, ArrowRight } from "lucide-react"

interface RefusalCardProps {
  text: string
  sourceUrl?: string | null
}

export default function RefusalCard({ text, sourceUrl }: RefusalCardProps) {
  const amfiUrl = sourceUrl || "https://www.amfiindia.com/investor-corner/knowledge-center/tax-benefits.html"

  return (
    <div className="p-5 bg-amber-50/70 border border-amber-200 rounded-2xl shadow-sm max-w-xl">
      <div className="flex gap-3">
        <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
        <div>
          <h4 className="text-sm font-bold text-amber-850">Facts-Only Assistant</h4>
          <p className="text-sm text-amber-700 font-medium mt-1 leading-relaxed">
            {text}
          </p>
          
          <div className="mt-4">
            <a
              href={amfiUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs font-bold text-amber-600 hover:text-amber-800 hover:underline transition-colors"
            >
              Learn More at AMFI
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>
    </div>
  )
}
