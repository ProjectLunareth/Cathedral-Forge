import React from 'react';
import { Toaster as HotToaster } from 'react-hot-toast';

/**
 * A styled wrapper for the react-hot-toast notification system.
 * This ensures all notifications in the Cathedral share a consistent, thematic appearance.
 */
export function Toaster() {
  return (
    <HotToaster
      position="bottom-center"
      toastOptions={{
        style: {
          background: '#1a1a2e',
          color: '#e6f3ff',
          border: '1px solid #4a044e',
          boxShadow: '0 0 20px rgba(192, 132, 252, 0.2)',
        },
        success: {
          iconTheme: {
            primary: '#a78bfa',
            secondary: '#1a1a2e',
          },
        },
        error: {
          iconTheme: {
            primary: '#f87171',
            secondary: '#1a1a2e',
          },
        },
      }}
    />
  );
}
