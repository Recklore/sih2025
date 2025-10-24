"use client"; // <-- Add this at the very top of the file

import React from 'react';
import { ChatWidget } from '@/components/chat/chat-widget';

export default function HomePage() {
  return (
    <>
     
      {/* styled-jsx now works because this is a Client Component */}
      <style jsx global>{`
        body {
          margin: 0;
          padding: 0;
          overflow: hidden; // Hides scrollbars from the main page
        }
      `}</style>

      <iframe
        src="/legacy.html"
        style={{
          width: '100vw',    // 100% of viewport width
          height: '100vh',   // 100% of viewport height
          border: 'none'     // No ugly border
        }}
        title="Legacy Homepage"
      />

      <ChatWidget />
    </>
  );
}