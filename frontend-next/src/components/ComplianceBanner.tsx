import React from "react"
import { ShieldCheck } from "lucide-react"

export default function ComplianceBanner() {
  return (
    <div className="flex items-center justify-center gap-2 py-2 px-4 bg-gray-50 border-t border-b border-gray-100 w-full text-center">
      <ShieldCheck className="w-4 h-4 text-groww-green shrink-0" />
      <span className="text-[11px] md:text-xs text-gray-500 font-semibold leading-none">
        Information provided is factual and sourced directly from official AMC, AMFI, and SEBI documents.
      </span>
    </div>
  )
}
