'use client';

import { useState } from 'react';
import Sidebar from './Sidebar';
import ChatPanel, { DEFAULT_WIDTH } from './ChatPanel';

interface AppLayoutProps {
  children: React.ReactNode;
}

export default function AppLayout({ children }: AppLayoutProps) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatWidth, setChatWidth] = useState(DEFAULT_WIDTH);

  return (
    <div className="flex min-h-screen">
      <Sidebar onChatToggle={() => setIsChatOpen(!isChatOpen)} isChatOpen={isChatOpen} />
      
      {/* Main content - adjusts when chat is open */}
      <main 
        className="flex-1 ml-64 p-8 transition-all duration-300"
        style={{ marginRight: isChatOpen ? chatWidth : 0 }}
      >
        {children}
      </main>
      
      {/* Floating Chat Button (visible when chat is closed) */}
      {!isChatOpen && (
        <button
          onClick={() => setIsChatOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 rounded-full shadow-lg shadow-purple-500/25 flex items-center justify-center transition-all hover:scale-105 z-40"
        >
          <ChatIcon className="w-6 h-6 text-white" />
        </button>
      )}
      
      {/* Chat Panel */}
      <ChatPanel 
        isOpen={isChatOpen} 
        onClose={() => setIsChatOpen(false)}
        width={chatWidth}
        onWidthChange={setChatWidth}
      />
    </div>
  );
}

function ChatIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
    </svg>
  );
}
