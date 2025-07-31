import React, { useState, useEffect } from 'react';
import { getFirestore, collection, query, where, onSnapshot, orderBy } from 'firebase/firestore';
import { useKarmaAccess } from '../hooks/useKarmaAccess';
import { formatDistanceToNow } from 'date-fns';

const db = getFirestore();

/**
 * Displays a real-time list of rituals created by the current user.
 */
export function RitualList() {
  const { user } = useKarmaAccess();
  const [rituals, setRituals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user || user.isAnonymous) {
      setLoading(false);
      setRituals([]);
      return; // Do nothing if user is not signed in or is a guest
    }

    setLoading(true);
    // Create a query to get rituals created by the current user, ordered by creation date
    const q = query(
      collection(db, 'rituals'),
      where('authorId', '==', user.uid),
      orderBy('createdAt', 'desc')
    );

    // onSnapshot listens for real-time updates from Firestore
    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const userRituals = [];
      querySnapshot.forEach((doc) => {
        userRituals.push({ id: doc.id, ...doc.data() });
      });
      setRituals(userRituals);
      setLoading(false);
    }, (error) => {
      console.error("Error fetching rituals:", error);
      setLoading(false);
    });

    // Cleanup the listener when the component unmounts to prevent memory leaks
    return () => unsubscribe();
  }, [user]); // Rerun this effect if the user object changes

  if (!user || user.isAnonymous) {
    return (
        <div className="text-center text-gray-500 mt-8">
            Sign in to view and create your personal rituals.
        </div>
    );
  }

  if (loading) {
    return <div className="text-purple-400 animate-pulse mt-8">Summoning your echoes...</div>;
  }

  return (
    <div className="w-full max-w-md mx-auto mt-8">
      <h2 className="text-xl font-semibold text-amber-300 mb-4">Your Ritual Archive</h2>
      {rituals.length > 0 ? (
        <ul className="space-y-3">
          {rituals.map((ritual) => (
            <li key={ritual.id} className="p-4 bg-gray-800/50 border border-purple-500/30 rounded-lg text-left shadow-md">
              <p className="font-semibold text-purple-300">{ritual.name}</p>
              <p className="text-xs text-gray-500 mt-1">
                Inscribed {ritual.createdAt ? formatDistanceToNow(ritual.createdAt.toDate()) : 'recently'} ago
              </p>
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500">Your archive is empty. Inscribe a ritual to begin your codex.</p>
      )}
    </div>
  );
}
