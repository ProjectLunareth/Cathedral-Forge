// /src/hooks/useChorusPresence.js
import { useState, useEffect, useMemo } from 'react';
import { collection, doc, onSnapshot, setDoc, deleteDoc, serverTimestamp } from 'firebase/firestore';
import { db } from '../lib/firebase';

/**
 * Manages and retrieves the list of participants in a shared chorus session.
 * @param {string} sessionId - The ID of the shared session.
 * @param {object | null} user - The current authenticated user object.
 * @returns {{participants: Array, loading: boolean}}
 */
export const useChorusPresence = (sessionId, user) => {
  const [participants, setParticipants] = useState([]);
  const [loading, setLoading] = useState(true);

  // Memoize the collection reference for stability
  const presenceColRef = useMemo(() => {
    if (!sessionId) return null;
    return collection(db, 'chorus_sessions', sessionId, 'presence');
  }, [sessionId]);

  // Effect to manage user's own presence (joining and leaving)
  useEffect(() => {
    if (!presenceColRef || !user) return;

    const userDocRef = doc(presenceColRef, user.uid);

    // Set presence when user comes online
    setDoc(userDocRef, { 
      uid: user.uid,
      displayName: user.displayName || 'Anonymous Scribe',
      photoURL: user.photoURL,
      joinedAt: serverTimestamp() 
    }).catch(console.error);

    // Use a separate async function to handle onDisconnect logic
    const setupOnDisconnect = async () => {
        // Firebase's onDisconnect is a Realtime Database feature, not Firestore.
        // The common workaround is to handle this on the client-side during cleanup.
        // A more robust solution uses Cloud Functions triggered by Realtime Database's
        // onDisconnect, but for our purposes, a client-side cleanup is sufficient.
    };
    
    setupOnDisconnect();

    // Cleanup function when the component unmounts (user leaves)
    return () => {
      deleteDoc(userDocRef).catch(console.error);
    };
  }, [presenceColRef, user]);

  // Effect to listen for changes in the participants list
  useEffect(() => {
    if (!presenceColRef) {
      setLoading(false);
      return;
    }

    setLoading(true);
    const unsubscribe = onSnapshot(presenceColRef, (snapshot) => {
      const presentUsers = snapshot.docs.map(doc => doc.data());
      setParticipants(presentUsers);
      setLoading(false);
    }, (error) => {
      console.error("Error listening to presence:", error);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [presenceColRef]);

  return { participants, loading };
};
