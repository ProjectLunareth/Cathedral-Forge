import React from 'react';
import { useRitualLibrary } from '../hooks/useRitualLibrary';
import { formatDistanceToNow } from 'date-fns';
import { LoaderCircle, BookOpen, Download } from 'lucide-react';

/**
 * A UI component to browse, search, and load rituals from the Firestore archive.
 * @param {object} props - Component props.
 * @param {function(object): void} props.onLoadRitual - Callback to load a ritual into the editor.
 */
export function RitualLibraryBrowser({ onLoadRitual }) {
  const { layouts, loading } = useRitualLibrary();

  return (
    <div className="w-full h-full p-4 bg-black/20 rounded-lg border border-purple-500/20 flex flex-col">
      <h2 className="text-xl font-semibold text-amber-300 mb-4 flex items-center gap-2">
        <BookOpen size={24} />
        The Codex Archive
      </h2>
      {loading ? (
        <div className="flex-grow flex items-center justify-center text-purple-400">
          <LoaderCircle size={32} className="animate-spin" />
        </div>
      ) : layouts.length === 0 ? (
        <div className="flex-grow flex items-center justify-center text-gray-500">
          <p>The Codex is silent. No rituals have been inscribed.</p>
        </div>
      ) : (
        <ul className="space-y-3 overflow-y-auto flex-grow pr-2">
          {layouts.map((layout) => (
            <li key={layout.id} className="p-3 bg-gray-800/50 border border-purple-500/30 rounded-lg text-left shadow-md transition-colors group hover:bg-gray-700/50">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-purple-300">{layout.name}</h3>
                  <p className="text-xs text-gray-400 mt-1">Scribed by: {layout.authorName}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {layout.createdAt ? formatDistanceToNow(layout.createdAt.toDate()) : 'Recently'} ago
                  </p>
                </div>
                <button 
                  onClick={() => onLoadRitual(layout)}
                  className="p-2 bg-indigo-800/50 rounded-md opacity-0 group-hover:opacity-100 transition-opacity hover:bg-indigo-700"
                  title="Load this ritual into the editor"
                >
                  <Download size={16} />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
