import { useEffect, useState, useCallback } from 'react';
import { getAuth, onAuthStateChanged, signInWithPopup, GoogleAuthProvider, signOut as firebaseSignOut, signInAnonymously } from 'firebase/auth';
import { getFirestore, doc, getDoc, setDoc, serverTimestamp } from 'firebase/firestore';

// Get the initialized services from the central firebase.js file
import { app } from '../lib/firebase'; 

const auth = getAuth(app);
const db = getFirestore(app);

/**
 * A custom React hook to manage user authentication and their "karmaRole".
 * It handles user state, sign-in/out, and fetches role from Firestore.
 * UPDATED: Now includes error state management.
 */
export function useKarmaAccess() {
  const [user, setUser] = useState(null);
  const [karmaRole, setKarmaRole] = useState('viewer');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // New state for errors

  const handleUser = useCallback(async (firebaseUser) => {
    setLoading(true);
    setError(null); // Clear previous errors on auth change
    if (firebaseUser) {
      const userRef = doc(db, `users/${firebaseUser.uid}`);
      const userSnap = await getDoc(userRef);

      if (userSnap.exists()) {
        const userData = userSnap.data();
        setKarmaRole(userData.karmaRole || 'seeker');
        setUser(firebaseUser);
      } else {
        const newUserProfile = {
          uid: firebaseUser.uid,
          email: firebaseUser.email,
          displayName: firebaseUser.displayName,
          karmaRole: 'seeker',
          createdAt: serverTimestamp(),
        };
        await setDoc(userRef, newUserProfile);
        setKarmaRole('seeker');
        setUser(firebaseUser);
      }
    } else {
      setUser(null);
      setKarmaRole('viewer');
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, handleUser);
    return () => unsubscribe();
  }, [handleUser]);

  const signInWithGoogle = async () => {
    setLoading(true);
    setError(null);
    try {
      const provider = new GoogleAuthProvider();
      await signInWithPopup(auth, provider);
      return { success: true };
    } catch (error) {
      console.error("Error signing in with Google:", error);
      setError(error);
      setLoading(false);
      return { success: false, error };
    }
  };

  const signOut = async () => {
    setLoading(true);
    setError(null);
    try {
      await firebaseSignOut(auth);
      return { success: true };
    } catch (error) {
      console.error("Error signing out:", error);
      setError(error);
      setLoading(false);
      return { success: false, error };
    }
  };
  
  const signInAsGuest = async () => {
    setLoading(true);
    setError(null);
    try {
        await signInAnonymously(auth);
        return { success: true };
    } catch (error) {
        console.error("Error signing in as guest:", error);
        setError(error);
        setLoading(false);
        return { success: false, error };
    }
  }

  return { user, karmaRole, loading, error, signInWithGoogle, signInAsGuest, signOut };
}
