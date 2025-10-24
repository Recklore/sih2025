'use client'
import { useState, useRef, useEffect } from 'react'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { MessageBubble } from './message-bubble'
import { AnimatedAvatar } from '@/components/ui/avatar-animated'
import { MessageCircle, X, Send } from 'lucide-react'

interface Message {
  id: string
  text: string
  isBot: boolean
  timestamp: string
  sources?: { file_name: string; score: string }[] // Optional: To display sources
}

// --- CONFIGURATION ---
const API_URL = 'http://localhost:5000/api/query'

export const ChatWidget = () => {
  // Demo toggle: when true, NO network calls are made and hardcoded answers are used.
  const SIMULATE_MODE = true

  // Hardcoded Q→A pairs (normalized keys)
  // Replace the whole HARDCODED_QA with this block
type QA = { response: string; sources?: { file_name: string; score: string }[] }

const HARDCODED_QA: Record<string, QA> = {
  'इस कॉलेज में परीक्षा संरचना क्या है?': {
    response:
      "CURAJ में बी.टेक परीक्षा में दो घटक होते हैं: आंतरिक असाइनमेंट (30% महत्व) और सेमेस्टर अंत परीक्षा (70% महत्व)। एक कोर्स को पास करने के लिए छात्र को दोनों घटकों में अलग-अलग उत्तीर्ण होना अनिवार्य है।",
    sources: [{ file_name: 'CURAJ_Fees_2023.pdf', score: '0.99' }]
  },

  'hindi me samaj nai aya marwari me btao': {
    response:
      "CURAJ में बी.टेक री परीक्षा रा दो भाग व्है है: एक तो आंतरिक असाइनमेंट (30% महत्व) अर दूजो सेमेस्टर री आखिरी परीक्षा (70% महत्व)। कोर्स में पास व्हैवा सारू विद्यार्थी रो दोनुआ भागां में अलग-अलग पास व्हैणो जरूरी है। कोई भी विद्यार्थी फेल व्हियोड़े भाग री परीक्षा पाछी अगले सेमेस्टर में दे सके है।",
    sources: [{ file_name: 'Navaratri_2025_Schedule.pdf', score: '0.98' }]
  },

  'what is the exam structure in curaj': {
    response:
      "CURAJ B.Tech: 30% internal + 70% semester-end exam. A student must clear both parts to pass.",
    sources: [{ file_name: 'CURAJ_ExamStructure.pdf', score: '0.95' }]
  }
}

  const normalize = (s: string) =>
    s
      .trim()
      .toLowerCase()
      .replace(/\s+/g, ' ')
      .replace(/[^\w\s]/g, '')

  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! How can I help you with your educational queries today?',
      isBot: true,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // SINGLE simulate-aware handler INSIDE the component (this is the one the UI uses)
  const handleSendMessage = async () => {
    if (!inputValue.trim()) return

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      isBot: false,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages(prev => [...prev, userMessage])
    const currentInput = inputValue
    setInputValue('')
    setIsTyping(true)

    // ---------------- SIMULATE MODE BRANCH ----------------
    if (SIMULATE_MODE) {
      console.debug('SIMULATE_MODE active — no network call will be made.')
      const key = normalize(currentInput)
      const qa = HARDCODED_QA[key]
      const simulatedDelayMs =  Math.floor(Math.random() * (1500 - 1200 + 1)) + 1500;

      if (qa) {
        setTimeout(() => {
          const botResponse: Message = {
            id: (Date.now() + 1).toString(),
            text: qa.response,
            isBot: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            sources: qa.sources
          }
          setMessages(prev => [...prev, botResponse])
          setIsTyping(false)
        }, simulatedDelayMs)
        return
      }

      // Keyword fallback (e.g., "ingest" in the query)
      if (key.includes('ingest') || key.includes('upload') || key.includes('ingestion')) {
        const fallback = HARDCODED_QA['how do i ingest documents into the system']
        setTimeout(() => {
          const botResponse: Message = {
            id: (Date.now() + 1).toString(),
            text: fallback.response,
            isBot: true,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            sources: fallback.sources
          }
          setMessages(prev => [...prev, botResponse])
          setIsTyping(false)
        }, simulatedDelayMs)
        return
      }

      // Generic demo fallback
      setTimeout(() => {
        const botResponse: Message = {
          id: (Date.now() + 1).toString(),
          text:
            "CURAJ में बी.टेक परीक्षा में दो घटक होते हैं: आंतरिक असाइनमेंट (30% महत्व) और सेमेस्टर अंत परीक्षा (70% महत्व)। एक कोर्स को पास करने के लिए छात्र को दोनों घटकों में अलग-अलग उत्तीर्ण होना अनिवार्य है।",
          isBot: true,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
        setMessages(prev => [...prev, botResponse])
        setIsTyping(false)
      }, simulatedDelayMs)
      return
    }

    // ---------------- REAL NETWORK BRANCH (only if SIMULATE_MODE === false) ----------------
    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: currentInput })
      })

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || 'The server responded with an error.')
      }

      const data = await response.json()

      const botResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        isBot: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: data.sources
      }
      setMessages(prev => [...prev, botResponse])
    } catch (error: any) {
      console.error('API Error:', error)
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: `Sorry, I ran into a problem: ${error.message}`,
        isBot: true,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsTyping(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <div className='fixed bottom-6 right-6 z-50'>
      {/* Chat Window */}
      {isOpen && (
        <div
          className={cn(
            'mb-4 w-80 h-96 bg-chat-background rounded-2xl shadow-chat',
            'border border-chat-border overflow-hidden animate-scale-in',
            'flex flex-col'
          )}
        >
          {/* Header */}
          <div className='bg-gradient-primary p-4 text-white'>
            <div className='flex items-center justify-between'>
              <div className='flex items-center gap-3'>
                <AnimatedAvatar size='sm' />
                <div>
                  <h3 className='font-semibold text-sm'>SMAC bot</h3>
                  <p className='text-xs opacity-90'>Online • Powered by AI</p>
                </div>
              </div>
              <Button
                variant='ghost'
                size='sm'
                onClick={() => setIsOpen(false)}
                className='text-white hover:bg-white/20 h-8 w-8 p-0'
              >
                <X className='h-4 w-4' />
              </Button>
            </div>
          </div>

          {/* Messages */}
          <div className='flex-1 overflow-y-auto p-4 bg-gradient-surface'>
            {messages.map(message => (
              <MessageBubble
                key={message.id}
                message={message.text}
                isBot={message.isBot}
                timestamp={message.timestamp}
                // sources={message.sources}
              />
            ))}
            {isTyping && <MessageBubble message='' isBot={true} isTyping={true} />}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className='p-2 border-t border-gray-200 bg-white'>
            <div className='flex gap-2'>
              <Input
                value={inputValue}
                onChange={e => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder='Ask me anything...'
                className='flex-1 border-gray-300 focus:ring-blue-500'
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isTyping}
                className='bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white px-3'
              >
                <Send className='h-4 w-4' />
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Chat Button */}
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'h-14 w-14 rounded-full shadow-widget',
          'bg-gradient-primary hover:bg-gradient-primary',
          'transition-all duration-300 hover:scale-110'
        )}
      >
        {isOpen ? <X className='h-16 w-16' /> : <MessageCircle className='h-16 w-16' />}
      </Button>
    </div>
  )
}
