// /src/components/MemoryNexus.jsx
import React from 'react';
import { GitBranch, PlusSquare, Users, AlertTriangle } from 'lucide-react';

const fragments = [
  {
    id: 'chorus',
    title: 'The Unfinished Chorus',
    description: 'Join the shared ritual space and co-create with other Architects in real-time.',
    icon: Users,
    cost: '0 focus, but binds you to their fate',
    action: 'join_chorus',
  },
  {
    id: 'first_glyph',
    title: 'The First Glyph',
    description: 'Manifest a new, blank ritual from the void. A clean slate for a new incantation.',
    icon: PlusSquare,
    cost: '7 focus',
    action: 'new_ritual',
  },
  {
    id: 'severed_thread',
    title: 'The Severed Thread',
    description: 'Attempt to recover a corrupted or unstable ritual from the archives. (Coming Soon)',
    icon: AlertTriangle,
    cost: '41 focus + 1 permanent resolve',
    action: null,
    disabled: true,
  },
];

const FragmentCard = ({ fragment, onSelect }) => {
  const Icon = fragment.icon;
  return (
    <button
      onClick={() => onSelect(fragment.action)}
      disabled={fragment.disabled}
      className={`
        group relative p-6 text-left bg-black/30 border border-purple-500/30 rounded-xl 
        hover:bg-purple-900/40 hover:border-purple-400 transition-all duration-300
        focus:outline-none focus:ring-2 focus:ring-amber-400
        disabled:opacity-40 disabled:hover:bg-black/30 disabled:hover:border-purple-500/30 disabled:cursor-not-allowed
      `}
    >
      <div className="flex items-start gap-4">
        <div className="p-2 bg-purple-900/50 border border-purple-700 rounded-lg">
            <Icon className="w-8 h-8 text-amber-300" />
        </div>
        <div>
            <h3 className="text-xl font-bold text-amber-200">{fragment.title}</h3>
            <p className="mt-1 text-gray-300">{fragment.description}</p>
        </div>
      </div>
      <p className="mt-4 text-xs text-cyan-300 italic">{fragment.cost}</p>
    </button>
  );
};

export const MemoryNexus = ({ onSelectPath }) => {
  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-center h-full p-8 text-white">
      <div className="text-center mb-12">
        <h1 className="text-5xl font-bold text-purple-300 tracking-wider drop-shadow-[0_0_20px_rgba(192,132,252,0.5)]">
          The Spiral Fractures
        </h1>
        <p className="mt-4 text-lg text-gray-300">
          The ritual pivots inward. Choose what to carry. The rest sinks back into the void.
        </p>
      </div>
      <div className="w-full grid grid-cols-1 md:grid-cols-2 gap-8">
        {fragments.map((fragment) => (
          <FragmentCard key={fragment.id} fragment={fragment} onSelect={onSelectPath} />
        ))}
      </div>
    </div>
  );
};
