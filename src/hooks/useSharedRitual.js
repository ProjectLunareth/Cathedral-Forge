// /src/hooks/useSharedRitual.js
import { useState, useEffect, useCallback, useMemo } from 'react';
import { doc, onSnapshot, setDoc } from 'firebase/firestore';
import { db } from '../lib/firebase';

/**
 * A more robust hook for real-time synchronization of a ritual's DSL string.
 * It now correctly handles state updater functions to prevent saving functions to Firestore.
 */
export const useSharedRitual = (sessionId) => {
  const [dsl, setDsl] = useState(null);
  const [loading, setLoading] = useState(true);

  const sessionDocRef = useMemo(() => {
    if (!sessionId) return null;
    return doc(db, 'chorus_sessions', sessionId);
  }, [sessionId]);

  useEffect(() => {
    if (!sessionDocRef) {
        setLoading(false);
        setDsl(null); // Clear DSL when session ID is null
        return;
    };

    setLoading(true);
    const unsubscribe = onSnapshot(sessionDocRef, (docSnap) => {
      if (docSnap.exists()) {
        const data = docSnap.data();
        // Only update state if the incoming data is different
        setDsl(currentDsl => currentDsl !== data.dslString ? data.dslString : currentDsl);
      } else {
        console.log(`Session document '${sessionId}' does not exist. It will be created on the first update.`);
        setDsl(''); // Set to empty string if doc doesn't exist, ready for creation
      }
      setLoading(false);
    }, (error) => {
      console.error("Error listening to shared ritual:", error);
      setLoading(false);
    });

    return () => unsubscribe();
  }, [sessionDocRef, sessionId]);

  // This is the core of the fix.
  const updateDsl = useCallback(async (value) => {
    if (!sessionDocRef) return;

    // This function now mimics a React state setter. It can accept a value OR a function.
    if (typeof value === 'function') {
        // If it's a function, we must first resolve it to get the new string value.
        // We use our internal `setDsl` to safely get the current state.
        setDsl(currentDsl => {
            const newDslString = value(currentDsl);
            // Now that we have the final string, save IT to Firestore.
            setDoc(sessionDocRef, { dslString: newDslString }, { merge: true });
            return newDslString; // Return the new value for our local state
        });
    } else {
        // If it's just a value, we can save it directly.
        await setDoc(sessionDocRef, { dslString: value }, { merge: true });
        setDsl(value); // Also update local state immediately
    }
  }, [sessionDocRef]);

  return { dsl, updateDsl, loading };
};
