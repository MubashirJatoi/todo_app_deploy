'use client';

import { AuthProvider } from '@/lib/auth';
import { ToastProvider } from '@/components/ToastProvider';
import { ReactNode } from 'react';
import '@/app/globals.css';
import FloatingChatbot from "./components/FloatingChatbot"

export default function RootLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <ToastProvider>
            <div className="min-h-screen bg-gray-50">
              {children}
              {/* Floating Chatbot - This will always stay visible on all pages */}
              <FloatingChatbot />
            </div>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}