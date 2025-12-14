'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import { sendChatMessage, AgentUsed } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  metadata?: {
    agents_used: AgentUsed[];
    tools: { tool: string; count: number }[];
    execution_time: number;
  };
  timestamp: Date;
}

// Agent styling
const agentStyles: Record<string, { bg: string; text: string; border: string }> = {
  orchestrator: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/30' },
  spending: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/30' },
  budget: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/30' },
  travel: { bg: 'bg-teal-500/20', text: 'text-teal-400', border: 'border-teal-500/30' },
  insights: { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/30' },
  sms: { bg: 'bg-rose-500/20', text: 'text-rose-400', border: 'border-rose-500/30' },
  stock: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/30' },
};

interface ChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
  width: number;
  onWidthChange: (width: number) => void;
}

const MIN_WIDTH = 400;
const MAX_WIDTH = 800;
const DEFAULT_WIDTH = 520;

const STORAGE_KEY = 'spendwise_chat_messages';
const WIDTH_STORAGE_KEY = 'spendwise_chat_width';

export default function ChatPanel({ isOpen, onClose, width, onWidthChange }: ChatPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);
  const [isHydrated, setIsHydrated] = useState(false);

  // Load messages from localStorage on mount
  useEffect(() => {
    try {
      const savedMessages = localStorage.getItem(STORAGE_KEY);
      if (savedMessages) {
        const parsed = JSON.parse(savedMessages);
        // Convert timestamp strings back to Date objects
        const messagesWithDates = parsed.map((msg: Message) => ({
          ...msg,
          timestamp: new Date(msg.timestamp),
        }));
        setMessages(messagesWithDates);
      }
      
      // Load saved width
      const savedWidth = localStorage.getItem(WIDTH_STORAGE_KEY);
      if (savedWidth) {
        const parsedWidth = parseInt(savedWidth, 10);
        if (parsedWidth >= MIN_WIDTH && parsedWidth <= MAX_WIDTH) {
          onWidthChange(parsedWidth);
        }
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
    setIsHydrated(true);
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (isHydrated && messages.length > 0) {
      try {
        // Keep only last 50 messages to avoid localStorage limits
        const messagesToSave = messages.slice(-50);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messagesToSave));
      } catch (error) {
        console.error('Failed to save chat history:', error);
      }
    }
  }, [messages, isHydrated]);

  // Save width to localStorage
  useEffect(() => {
    if (isHydrated) {
      localStorage.setItem(WIDTH_STORAGE_KEY, width.toString());
    }
  }, [width, isHydrated]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Clear chat history function
  const clearHistory = () => {
    setMessages([]);
    localStorage.removeItem(STORAGE_KEY);
  };

  // Handle resize
  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    setIsResizing(true);
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      
      const newWidth = window.innerWidth - e.clientX;
      const clampedWidth = Math.min(MAX_WIDTH, Math.max(MIN_WIDTH, newWidth));
      onWidthChange(clampedWidth);
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, onWidthChange]);

  const exampleQuestions = [
    'Analyze NVDA - should I buy?',
    'Plan a weekend trip to Paris',
    'Any unusual spending this week?',
    'Show my stock portfolio',
    'What are my biggest expenses?',
  ];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sendChatMessage(userMessage.content);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        metadata: response.metadata || undefined,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, something went wrong. Make sure the API is running.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      {/* Overlay when open on mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Chat Panel */}
      <div 
        ref={panelRef}
        style={{ width: isOpen ? width : 0 }}
        className={`fixed right-0 top-0 h-full bg-[#0d0d0d] border-l border-[#1a1a1a] z-50 flex flex-col transition-all duration-300 ease-in-out ${
          isOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}
      >
        {/* Resize Handle */}
        <div
          onMouseDown={handleMouseDown}
          className={`absolute left-0 top-0 bottom-0 w-1 cursor-col-resize group hover:bg-blue-500/50 transition-colors ${
            isResizing ? 'bg-blue-500' : 'bg-transparent'
          }`}
        >
          {/* Visual indicator */}
          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-16 rounded-full bg-gray-600 group-hover:bg-blue-400 transition-colors" />
        </div>

        {/* Header */}
        <div className="p-5 border-b border-[#1a1a1a] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500/30 to-blue-500/30 rounded-xl flex items-center justify-center">
              <BrainIcon className="w-6 h-6 text-purple-400" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-white">SpendWise AI</h2>
              <p className="text-sm text-gray-500">Ask anything about your finances</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {messages.length > 0 && (
              <button
                onClick={clearHistory}
                className="p-2 hover:bg-[#1a1a1a] rounded-lg transition-colors text-gray-500 hover:text-red-400"
                title="Clear chat history"
              >
                <TrashIcon className="w-5 h-5" />
              </button>
            )}
            <button
              onClick={onClose}
              className="p-2 hover:bg-[#1a1a1a] rounded-lg transition-colors text-gray-400 hover:text-white"
            >
              <CloseIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-5">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center px-8">
              <div className="w-20 h-20 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-2xl flex items-center justify-center mb-6">
                <BrainIcon className="w-10 h-10 text-purple-400" />
              </div>
              <h3 className="text-xl font-medium text-white mb-3">How can I help you?</h3>
              <p className="text-base text-gray-500 mb-8 max-w-sm">
                I can analyze spending, manage budgets, plan trips, and help with stock investments.
              </p>
              <div className="space-y-3 w-full max-w-sm">
                {exampleQuestions.map((q, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(q)}
                    className="w-full px-5 py-4 bg-[#1a1a1a] hover:bg-[#252525] border border-[#333] rounded-xl text-base text-gray-300 text-left transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-2xl px-5 py-4 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white'
                      : 'bg-[#1a1a1a] border border-[#333]'
                  }`}
                >
                  <div className={`text-[15px] leading-relaxed ${message.role === 'assistant' ? 'text-gray-200' : ''}`}>
                    {message.role === 'assistant' ? (
                      <ReactMarkdown
                        components={{
                          p: ({ children }) => <p className="mb-3 last:mb-0">{children}</p>,
                          strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
                          em: ({ children }) => <em className="italic text-gray-300">{children}</em>,
                          ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                          ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                          li: ({ children }) => <li className="ml-2">{children}</li>,
                          code: ({ children }) => <code className="bg-[#252525] px-1.5 py-0.5 rounded text-sm font-mono text-purple-300">{children}</code>,
                          h1: ({ children }) => <h1 className="text-xl font-bold text-white mt-4 mb-3">{children}</h1>,
                          h2: ({ children }) => <h2 className="text-lg font-bold text-purple-300 mt-4 mb-2">{children}</h2>,
                          h3: ({ children }) => <h3 className="text-base font-semibold text-blue-300 mt-3 mb-2">{children}</h3>,
                          hr: () => <hr className="border-[#444] my-4" />,
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    ) : (
                      <span className="whitespace-pre-wrap">{message.content}</span>
                    )}
                  </div>

                  {/* Agent Metadata */}
                  {message.role === 'assistant' && message.metadata && (
                    <div className="mt-4 pt-3 border-t border-[#333]">
                      <div className="flex flex-wrap gap-2">
                        {/* Deduplicate agents by id */}
                        {Array.from(new Map(message.metadata.agents_used.map(a => [a.id, a])).values()).map((agent, idx) => {
                          const style = agentStyles[agent.id] || agentStyles.orchestrator;
                          return (
                            <span
                              key={`${agent.id}-${idx}`}
                              className={`px-3 py-1.5 rounded-lg text-sm border ${style.bg} ${style.text} ${style.border}`}
                            >
                              {agent.name}
                            </span>
                          );
                        })}
                      </div>
                      <div className="flex gap-4 mt-2 text-sm text-gray-500">
                        {message.metadata.tools.length > 0 && (
                          <span>
                            {message.metadata.tools.map(t => `${t.tool}:${t.count}`).join(', ')}
                          </span>
                        )}
                        {message.metadata.execution_time > 0 && (
                          <span>{message.metadata.execution_time}s</span>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}

          {/* Loading */}
          {loading && (
            <div className="flex justify-start">
              <div className="bg-[#1a1a1a] border border-[#333] rounded-2xl px-5 py-4">
                <div className="flex items-center gap-3 text-gray-400">
                  <div className="flex gap-1.5">
                    <span className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2.5 h-2.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                  <span className="text-base">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <form onSubmit={handleSubmit} className="p-5 border-t border-[#1a1a1a]">
          <div className="bg-[#1a1a1a] border border-[#333] rounded-xl flex items-center">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me anything..."
              className="flex-1 bg-transparent px-5 py-4 text-base text-white placeholder-gray-500 focus:outline-none"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="mr-3 p-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:from-gray-700 disabled:to-gray-700 rounded-xl transition-all"
            >
              <SendIcon className="w-5 h-5 text-white" />
            </button>
          </div>
        </form>
      </div>
    </>
  );
}

// Icons
function BrainIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
    </svg>
  );
}

function SendIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
    </svg>
  );
}

function CloseIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  );
}

function TrashIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
    </svg>
  );
}

export { DEFAULT_WIDTH, MIN_WIDTH, MAX_WIDTH };
