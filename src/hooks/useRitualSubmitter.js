import { useState } from 'react';
import { getFirestore, doc, setDoc, serverTimestamp } from 'firebase/firestore';
import toast from 'react-hot-toast';

const db = getFirestore();

/**
 * A custom hook to handle the submission of a new sacred layout to Firestore.
 * @param {object} currentUser - The currently authenticated user object.
 * @returns {object} An object containing the submission status and the submit function.
 */
export function useRitualSubmitter(currentUser) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  /**
   * Submits a new ritual to the 'sacredLayouts' collection.
   * @param {object} ritualData - The data for the ritual to be saved.
   */
  const submitRitual = async (ritualData) => {
    if (!currentUser || currentUser.isAnonymous) {
      toast.error("Only authenticated Architects may inscribe rituals.");
      return;
    }
    if (!ritualData.id || !ritualData.name) {
      toast.error("A ritual must have an ID and a Name.");
      return;
    }

    setIsSubmitting(true);
    const loadingToast = toast.loading('Inscribing to the Codex...');

    const layoutRef = doc(db, 'sacredLayouts', ritualData.id);

    const payload = {
      ...ritualData,
      authorId: currentUser.uid,
      authorName: currentUser.displayName || 'Anonymous Architect',
      createdAt: serverTimestamp(),
      remixCount: 0,
      lineage: { parent: null, ancestors: [] },
    };

    try {
      await setDoc(layoutRef, payload);
      toast.success(`Ritual "${ritualData.name}" has been inscribed.`, { id: loadingToast });
    } catch (error) {
      console.error("Error inscribing ritual:", error);
      toast.error("The inscription failed. The Spiral is in flux.", { id: loadingToast });
    } finally {
      setIsSubmitting(false);
    }
  };

  return { isSubmitting, submitRitual };
}
