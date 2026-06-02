import React from "react"
import { Message } from "../store/useChatStore"
import AnswerCard from "./AnswerCard"
import RefusalCard from "./RefusalCard"
import { ShieldAlert, AlertCircle } from "lucide-react"

interface ChatMessageProps {
  message: Message
}

export default function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.sender === "user"

  if (isUser) {
    return (
      <div className="flex justify-end w-full mb-5">
        <div className="max-w-[80%] bg-groww-green text-white text-sm font-semibold py-3 px-4.5 rounded-2xl rounded-tr-none shadow-sm leading-relaxed">
          {message.text}
        </div>
      </div>
    )
  }

  // Assistant responses
  const { status, type, text, sourceUrl, lastUpdated } = message

  // 1. Advisory Violation Refusal
  if (status === "violated" && type === "advisory") {
    return (
      <div className="flex justify-start w-full mb-5">
        <RefusalCard text={text} sourceUrl={sourceUrl} />
      </div>
    )
  }

  // 2. PII scanner blockage warning
  if (status === "violated" && type === "pii") {
    return (
      <div className="flex justify-start w-full mb-5 max-w-xl">
        <div className="flex gap-3 p-4 bg-red-50/70 border border-red-200 rounded-2xl shadow-sm text-red-800">
          <ShieldAlert className="w-5 h-5 text-red-500 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-red-900">Privacy Intercepted</h4>
            <p className="text-sm text-red-700 font-medium mt-1 leading-relaxed">
              {text}
            </p>
          </div>
        </div>
      </div>
    )
  }

  // 3. System errors
  if (status === "error") {
    return (
      <div className="flex justify-start w-full mb-5 max-w-xl">
        <div className="flex gap-3 p-4 bg-gray-50 border border-gray-200 rounded-2xl shadow-sm text-gray-800">
          <AlertCircle className="w-5 h-5 text-gray-500 shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-gray-900">System Notification</h4>
            <p className="text-sm text-gray-600 font-medium mt-1 leading-relaxed">
              {text}
            </p>
          </div>
        </div>
      </div>
    )
  }

  // 4. Successful context-bound response
  return (
    <div className="flex justify-start w-full mb-5">
      <AnswerCard text={text} sourceUrl={sourceUrl} lastUpdated={lastUpdated} />
    </div>
  )
}
