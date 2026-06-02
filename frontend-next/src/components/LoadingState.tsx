import React from "react"
import { useChatStore } from "../store/useChatStore"
import { Loader2 } from "lucide-react"

export default function LoadingState() {
  const loadingStage = useChatStore((state) => state.loadingStage)

  return (
    <div className="flex flex-col gap-4 max-w-xl w-full p-5 bg-white border border-gray-100 rounded-2xl shadow-premium mb-5 animate-pulse">
      {/* Top Badge Loader */}
      <div className="flex items-center gap-2">
        <div className="w-5 h-5 rounded-full bg-gray-200" />
        <div className="w-24 h-4 bg-gray-200 rounded" />
      </div>

      {/* Main Text Skeleton Lines */}
      <div className="space-y-2 mt-2">
        <div className="h-4 bg-gray-200 rounded w-full" />
        <div className="h-4 bg-gray-200 rounded w-[90%]" />
        <div className="h-4 bg-gray-200 rounded w-[60%]" />
      </div>

      {/* Status indicator footer */}
      <div className="flex items-center gap-2.5 mt-4 pt-3 border-t border-gray-50">
        <Loader2 className="w-4 h-4 text-groww-green animate-spin" />
        <span className="text-xs font-bold text-groww-green tracking-wide">
          {loadingStage || "Verifying source credentials..."}
        </span>
      </div>
    </div>
  )
}
