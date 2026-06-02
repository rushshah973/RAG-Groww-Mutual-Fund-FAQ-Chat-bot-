import React from "react"
import { ShieldCheck, Calendar } from "lucide-react"
import SourceCard from "./SourceCard"

interface AnswerCardProps {
  text: string
  sourceUrl?: string | null
  lastUpdated?: string | null
}

export default function AnswerCard({ text, sourceUrl, lastUpdated }: AnswerCardProps) {
  return (
    <div className="bg-white border border-gray-150 rounded-2xl shadow-premium p-5 md:p-6 max-w-2xl relative overflow-hidden">
      {/* Visual Accent */}
      <div className="absolute left-0 top-0 bottom-0 w-1.5 bg-groww-green" />

      <div className="flex items-center gap-2 mb-3.5">
        <ShieldCheck className="w-5 h-5 text-groww-green shrink-0" />
        <span className="text-xs font-bold text-gray-900 tracking-wide uppercase">
          Verified Information
        </span>
      </div>

      {/* Answer content */}
      <p className="text-sm md:text-base text-gray-800 leading-relaxed font-medium">
        {text}
      </p>

      {/* Divider */}
      {(sourceUrl || lastUpdated) && (
        <div className="mt-5 pt-4 border-t border-gray-100 flex flex-col gap-2">
          {/* Last Updated Timestamp */}
          {lastUpdated && (
            <div className="flex items-center gap-1.5 text-xs text-gray-400 font-semibold">
              <Calendar className="w-3.5 h-3.5 text-gray-300" />
              <span>Last updated: {lastUpdated}</span>
            </div>
          )}

          {/* Render Source Link */}
          {sourceUrl && <SourceCard url={sourceUrl} />}
        </div>
      )}
    </div>
  )
}
