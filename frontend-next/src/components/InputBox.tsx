import React, { useState, useRef, useEffect } from "react"
import { useChatStore } from "../store/useChatStore"
import { Send, Paperclip, Mic } from "lucide-react"

export default function InputBox() {
  const { sendMessage, isLoading } = useChatStore()
  const [query, setQuery] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const trimmed = query.trim()
    if (trimmed && !isLoading) {
      sendMessage(trimmed)
      setQuery("")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  // Auto-resize textarea heights based on text rows
  useEffect(() => {
    const textarea = textareaRef.current
    if (textarea) {
      textarea.style.height = "auto"
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`
    }
  }, [query])

  return (
    <form onSubmit={handleSubmit} className="p-4 bg-white border-t border-gray-100 shadow-[0_-8px_30px_-6px_rgba(0,0,0,0.03)]">
      <div className="max-w-3xl mx-auto flex items-end gap-2 bg-gray-50 border border-gray-200 focus-within:border-groww-green/60 focus-within:ring-2 focus-within:ring-groww-green/10 rounded-2xl p-2 transition-all duration-150">
        
        {/* Attachment - Disabled by requirement */}
        <button
          type="button"
          disabled
          title="Attachments disabled"
          className="flex items-center justify-center p-2 text-gray-300 cursor-not-allowed rounded-lg shrink-0"
        >
          <Paperclip className="w-4 h-4" />
        </button>

        {/* Text Input area */}
        <textarea
          ref={textareaRef}
          rows={1}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a mutual fund question (e.g. exit load, expense ratio, manager)..."
          disabled={isLoading}
          className="flex-1 max-h-[120px] resize-none py-2 px-1 bg-transparent text-sm text-gray-800 focus:outline-none placeholder-gray-400 font-medium leading-relaxed"
        />

        {/* Optional Mic Icon - Styled as passive */}
        <button
          type="button"
          title="Voice input not active"
          className="flex items-center justify-center p-2 text-gray-400 hover:text-gray-600 rounded-lg shrink-0"
        >
          <Mic className="w-4 h-4" />
        </button>

        {/* Send Button */}
        <button
          type="submit"
          disabled={isLoading || !query.trim()}
          className="flex items-center justify-center p-2.5 bg-groww-green hover:bg-[#00b88a] disabled:bg-gray-200 text-white disabled:text-gray-400 rounded-xl hover:scale-105 active:scale-95 transition-all shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </form>
  )
}
