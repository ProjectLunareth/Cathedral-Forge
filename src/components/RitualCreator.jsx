import React, { useState } from 'react';
import { getFirestore, collection, addDoc, serverTimestamp } from 'firebase/firestore';
import { useKarmaAccess } from '../hooks/useKarmaAccess';
import toast from 'react-hot-toast';

const db = getFirestore();

/**
 * A form component for creating new rituals.
 * Only visible and usable by authenticated, non-anonymous users.
 */
export function RitualCreator() {
  const { user } = useKarmaAccess();
  const [ritualName, setRitualName] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!ritualName.trim() || !user || user.isAnonymous) {
      toast.error('You must be signed in to inscribe a ritual.');
      return;
    }

    setIsSubmitting(true);
    const loadingToast = toast.loading('Inscribing to the Codex...');

    try {
      // Create a new document in the 'rituals' collection
      await addDoc(collection(db, 'rituals'), {
        name: ritualName,
        authorId: user.uid,
        authorName: user.displayName || 'Anonymous Seeker',
        createdAt: serverTimestamp(),
      });
      
      toast.success('Ritual inscribed successfully!', { id: loadingToast });
      setRitualName(''); // Clear the input field on success
    } catch (err) {
      console.error("Error inscribing ritual:", err);
      toast.error('Failed to inscribe the ritual.', { id: loadingToast });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Do not render the form for guests or logged-out users
  if (!user || user.isAnonymous) {
    return null; 
  }

  return (
    <div className="w-full max-w-md mx-auto mt-8">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <h2 className="text-xl font-semibold text-amber-300">Inscribe a New Ritual</h2>
        <input
          type="text"
          value={ritualName}
          onChange={(e) => setRitualName(e.target.value)}
          placeholder="Whisper the name of your ritual..."
          className="w-full px-4 py-2 bg-gray-800 border border-purple-500/50 rounded-lg focus:ring-2 focus:ring-purple-400 focus:outline-none transition-all"
          disabled={isSubmitting}
        />
        <button
          type="submit"
          disabled={isSubmitting || !ritualName.trim()}
          className="px-6 py-2 font-bold text-lg bg-purple-700 hover:bg-purple-600 rounded-lg disabled:bg-gray-600 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting ? 'Inscribing...' : 'Commit to the Codex'}
        </button>
      </form>
    </div>
  );
}
