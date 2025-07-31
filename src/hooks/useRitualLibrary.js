import { useState, useEffect } from 'react';
import { getFirestore, collection, query, onSnapshot, orderBy } from 'firebase/firestore';

const db = getFirestore();

/**
 * A custom hook to fetch and listen for real-time updates from the 'sacredLayouts' collection.
 * @returns {{layouts: Array<object>, loading: boolean}}
 */
export function useRitualLibrary() {
  const [layouts, setLayouts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const q = query(collection(db, 'sacredLayouts'), orderBy('createdAt', 'desc'));

    const unsubscribe = onSnapshot(q, (querySnapshot) => {
      const savedLayouts = [];
      querySnapshot.forEach((doc) => {
        savedLayouts.push({ id: doc.id, ...doc.data() });
      });
      setLayouts(savedLayouts);
      setLoading(false);
    }, (error) => {
      console.error("Error fetching sacred layouts:", error);
      setLoading(false);
    });

    // Cleanup the listener when the component unmounts
    return () => unsubscribe();
  }, []);

  return { layouts, loading };
}
