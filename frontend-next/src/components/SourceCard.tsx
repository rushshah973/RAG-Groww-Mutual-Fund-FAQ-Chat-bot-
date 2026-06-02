import React from "react"
import { ExternalLink, CheckCircle } from "lucide-react"

interface SourceCardProps {
  url: string
}

export default function SourceCard({ url }: SourceCardProps) {
  // Extract a clean display name from the URL
  const getSourceLabel = (link: string) => {
    try {
      const parsed = new URL(link)
      if (parsed.hostname.includes("groww")) return "Official Groww AMC factsheet"
      if (parsed.hostname.includes("sebi")) return "SEBI Investor Portal"
      if (parsed.hostname.includes("amfi")) return "AMFI Official Portal"
      return `${parsed.hostname} document`
    } catch {
      return "Official Fund Factsheet"
    }
  }

  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="flex items-center justify-between gap-3 p-3.5 mt-3 bg-groww-lightGreen/20 hover:bg-groww-lightGreen/40 border border-groww-green/20 hover:border-groww-green/40 rounded-xl transition-all duration-200 group"
    >
      <div className="flex items-center gap-2">
        <CheckCircle className="w-4 h-4 text-groww-green shrink-0" />
        <div>
          <span className="text-[10px] font-bold text-groww-green uppercase tracking-wider block">
            Verified Source
          </span>
          <span className="text-xs font-semibold text-gray-700 group-hover:text-gray-900 transition-colors">
            {getSourceLabel(url)}
          </span>
        </div>
      </div>
      <div className="flex items-center gap-1 text-xs font-bold text-groww-green">
        <span>View Source</span>
        <ExternalLink className="w-3.5 h-3.5 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
      </div>
    </a>
  )
}
