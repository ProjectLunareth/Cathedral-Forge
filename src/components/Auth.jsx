// FILE: src/components/Auth.jsx

import React from 'react';
import { useKarmaAccess } from '../hooks/useKarmaAccess';
import toast from 'react-hot-toast';

/**
 * A UI component for handling user authentication.
 * UPDATED: Now uses react-hot-toast to display sign-in errors.
 */
export function Auth() {
  const { user, karmaRole, loading, signInWithGoogle, signInAsGuest, signOut } = useKarmaAccess();

  const handleSignInGoogle = async () => {
    const result = await signInWithGoogle();
    if (!result.success) {
      // Provide a user-friendly error message
      toast.error(result.error.code === 'auth/popup-closed-by-user' 
        ? 'Sign-in cancelled.' 
        : 'Sign-in failed. Please try again.'
      );
    }
  };
  
  const handleSignInGuest = async () => {
    const result = await signInAsGuest();
    if (!result.success) {
      toast.error('Could not sign in as guest.');
    }
  };

  if (loading) {
    return (
        <div className="absolute top-4 right-4 p-4 bg-black/50 border border-purple-500/30 rounded-lg text-sm text-gray-300 shadow-lg">
            <div className="text-purple-400 animate-pulse">Awakening...</div>
        </div>
    );
  }

  return (
    <div className="absolute top-4 right-4 p-4 bg-black/50 border border-purple-500/30 rounded-lg text-sm text-gray-300 shadow-lg backdrop-blur-sm">
      {user ? (
        <div className="flex items-center space-x-4">
          <div>
            <p className="font-semibold">{user.displayName || 'Anonymous Seeker'}</p>
            <p className="text-purple-400 capitalize">Role: {karmaRole}</p>
          </div>
          <button
            onClick={signOut}
            className="px-4 py-2 bg-purple-800 hover:bg-purple-700 rounded-md transition-colors duration-300"
          >
            Sign Out
          </button>
        </div>
      ) : (
        <div className="flex items-center space-x-2">
           <button
            onClick={handleSignInGuest}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 rounded-md transition-colors duration-300"
          >
            Enter as Guest
          </button>
          <button
            onClick={handleSignInGoogle}
            className="px-4 py-2 bg-indigo-700 hover:bg-indigo-600 rounded-md transition-colors duration-300"
          >
            Sign In with Google
          </button>
        </div>
      )}
    </div>
  );
}
