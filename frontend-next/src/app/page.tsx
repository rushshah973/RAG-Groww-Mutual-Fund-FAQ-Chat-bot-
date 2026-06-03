"use client"

import React, { useRef, useEffect } from "react"
import Sidebar from "../components/Sidebar"
import Header from "../components/Header"
import EmptyState from "../components/EmptyState"
import ChatMessage from "../components/ChatMessage"
import LoadingState from "../components/LoadingState"
import ComplianceBanner from "../components/ComplianceBanner"
import InputBox from "../components/InputBox"
import { useChatStore } from "../store/useChatStore"

export default function Home() {
  const { messages, isLoading, isSidebarOpen, setSidebarOpen } = useChatStore()
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom whenever new messages arrive or loading status changes
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isLoading])

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 transition-colors duration-200">
      {/* 1. Left Sidebar (Fixed 280px on desktop) */}
      <Sidebar />

      {/* Backdrop overlay for mobile drawer */}
      {isSidebarOpen && (
        <div
          onClick={() => setSidebarOpen(false)}
          className="fixed inset-0 z-30 bg-black/30 backdrop-blur-sm md:hidden transition-opacity"
        />
      )}

      {/* 2. Main Content Container */}
      <div className="flex flex-col flex-1 h-full md:pl-[280px]">
        {/* Sticky Header */}
        <Header />

        {/* Chat Logs Window */}
        <main className="flex-1 overflow-y-auto px-4 md:px-8 py-6">
          {messages.length === 0 ? (
            <EmptyState />
          ) : (
            <div className="max-w-3xl mx-auto flex flex-col min-h-full justify-end pb-8">
              {messages.map((message) => (
                <ChatMessage key={message.id} message={message} />
              ))}
              
              {/* Render Animated Skeleton loader */}
              {isLoading && <LoadingState />}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </main>

        {/* Footer input elements */}
        <div className="flex flex-col mt-auto">
          <ComplianceBanner />
          <InputBox />
        </div>
      </div>
    </div>
  )
}
