import { create } from "zustand"

export interface Message {
  id: string
  sender: "user" | "assistant"
  text: string
  status?: "success" | "violated" | "error"
  type?: string | null
  sourceUrl?: string | null
  lastUpdated?: string | null
}

interface ChatState {
  messages: Message[]
  isLoading: boolean
  loadingStage: string
  isSidebarOpen: boolean
  sendMessage: (query: string) => Promise<void>
  clearChat: () => void
  setSidebarOpen: (isOpen: boolean) => void
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || ""

export const useChatStore = create<ChatState>((set, get) => ({
  messages: [],
  isLoading: false,
  loadingStage: "",
  isSidebarOpen: false,

  sendMessage: async (query: string) => {
    const userMsgId = Math.random().toString(36).substring(7)
    const userMessage: Message = {
      id: userMsgId,
      sender: "user",
      text: query,
    }

    set((state) => ({
      messages: [...state.messages, userMessage],
      isLoading: true,
      loadingStage: "Searching official sources...",
    }))

    // Artificial delay to show smooth stage transitions
    const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))

    try {
      await delay(600)
      set({ loadingStage: "Verifying information safety..." })
      await delay(600)
      set({ loadingStage: "Compiling response from official docs..." })
      await delay(400)

      const response = await fetch(`${API_BASE}/api/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query }),
      })

      if (!response.ok) {
        throw new Error("Failed to contact the backend service.")
      }

      const data = await response.json()

      const assistantMessage: Message = {
        id: Math.random().toString(36).substring(7),
        sender: "assistant",
        text: data.answer || "An unexpected error occurred.",
        status: data.status, // "success", "violated", "error"
        type: data.type,     // "advisory", "pii"
        sourceUrl: data.source_url,
        lastUpdated: data.last_updated,
      }

      set((state) => ({
        messages: [...state.messages, assistantMessage],
        isLoading: false,
        loadingStage: "",
      }))
    } catch (error: any) {
      const errorMessage: Message = {
        id: Math.random().toString(36).substring(7),
        sender: "assistant",
        text: error.message || "Something went wrong. Please check your network connection.",
        status: "error",
        type: "system",
      }

      set((state) => ({
        messages: [...state.messages, errorMessage],
        isLoading: false,
        loadingStage: "",
      }))
    }
  },

  clearChat: () => set({ messages: [] }),
  setSidebarOpen: (isOpen) => set({ isSidebarOpen: isOpen }),
}))
