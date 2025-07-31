// /src/components/ChorusParticipants.jsx
import React from 'react';
import { Users } from 'lucide-react';

/**
 * Displays a list of participants currently in the Chorus session.
 * @param {{participants: Array, loading: boolean}} props
 */
export const ChorusParticipants = ({ participants, loading }) => {
  return (
    <div className="bg-gray-900 bg-opacity-50 p-4 rounded-lg h-full">
      <h3 className="text-lg font-semibold text-cyan-200 mb-3 flex items-center gap-2">
        <Users size={20} />
        Chorus Participants ({participants.length})
      </h3>
      {loading ? (
        <p className="text-gray-400">Loading scribes...</p>
      ) : (
        <ul className="space-y-2 overflow-y-auto max-h-32">
          {participants.map((p) => (
            <li key={p.uid} className="flex items-center gap-3 bg-gray-800/50 p-2 rounded">
              <img 
                src={p.photoURL || `https://api.dicebear.com/8.x/bottts-neutral/svg?seed=${p.uid}`} 
                alt={p.displayName} 
                className="w-8 h-8 rounded-full border-2 border-purple-400"
              />
              <span className="text-gray-200 font-medium">{p.displayName}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};
