import React from "react"
import { ShieldCheck, Info } from "lucide-react"

export default function WelcomeCard() {
  return (
    <div className="relative p-6 md:p-8 bg-gradient-to-br from-white to-groww-lightGreen/20 rounded-2xl border border-gray-100 shadow-premium overflow-hidden">
      <div className="absolute right-0 top-0 -mr-6 -mt-6 w-32 h-32 bg-groww-green/5 rounded-full blur-2xl pointer-events-none" />
      
      <div className="flex items-center gap-2.5 mb-4">
        <span className="flex h-2.5 w-2.5 relative">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-groww-green opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-groww-green"></span>
        </span>
        <span className="text-xs font-bold text-groww-green bg-groww-lightGreen border border-groww-green/20 px-2 py-0.5 rounded">
          ACTIVE REGULATORY COMPLIANCE
        </span>
      </div>

      <h1 className="text-2xl md:text-3xl font-extrabold text-gray-900 tracking-tight leading-tight">
        Get Verified Mutual Fund Information
      </h1>
      
      <p className="mt-2 text-sm md:text-base text-gray-600 font-medium">
        Ask factual questions sourced from official Asset Management Company (AMC), AMFI, and SEBI regulatory filings.
      </p>

      <div className="flex items-start gap-2 mt-5 p-3 rounded-lg bg-gray-50 border border-gray-100 max-w-xl">
        <Info className="w-4 h-4 text-groww-light shrink-0 mt-0.5" />
        <span className="text-[11px] md:text-xs text-gray-500 leading-relaxed font-medium">
          <strong>Compliance Disclaimer:</strong> This portal serves only factual details (such as expense ratios, scheme holdings, load timings, and managers). It strictly rejects subjective investment opinions, advisory ratings, comparison tables, and buying suggestions.
        </span>
      </div>
    </div>
  )
}
