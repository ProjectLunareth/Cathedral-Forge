// /src/components/PatternTools.jsx
import React, { useState, useMemo } from 'react';
import { CircleDot, Zap, Orbit } from 'lucide-react';
import toast from 'react-hot-toast';

export const PatternTools = ({ allGlyphNames, compiledLayout, sharedDsl, setSharedDsl }) => {
  const [centerGlyph, setCenterGlyph] = useState('');
  const [sourceGlyph, setSourceGlyph] = useState('');
  const [count, setCount] = useState(8);
  const [radius, setRadius] = useState(5);
  const [plane, setPlane] = useState('xz');
  const [scale, setScale] = useState(1.0);
  const [addPulse, setAddPulse] = useState(false);
  const [addOrbit, setAddOrbit] = useState(false);
  const [orbitSpeed, setOrbitSpeed] = useState(1.0);
  const [orbitDirection, setOrbitDirection] = useState(1);

  const glyphDataMap = useMemo(() => {
    const map = new Map();
    if (!compiledLayout || !compiledLayout.steps) return map;
    compiledLayout.steps.forEach(step => {
      if (step.command === 'PLACE') {
        const name = step.arguments[1].replace(/"/g, '');
        map.set(name, {
          position: [
            parseFloat(step.arguments[3] || 0),
            parseFloat(step.arguments[4] || 0),
            parseFloat(step.arguments[5] || 0)
          ]
        });
      }
    });
    return map;
  }, [compiledLayout]);

  const handleGenerate = () => {
    if (!centerGlyph || !sourceGlyph) {
      toast.error('Please select a center and source glyph.');
      return;
    }

    const centerData = glyphDataMap.get(centerGlyph);
    if (!centerData) {
      toast.error('Center glyph position not found.');
      return;
    }
    
    const [cx, cy, cz] = centerData.position;
    let newCommands = '';
    const angleStep = (2 * Math.PI) / count;
    
    const generationId = Date.now().toString().slice(-5);

    for (let i = 0; i < count; i++) {
      const angle = i * angleStep;
      let x, y, z;

      switch (plane) {
        case 'xy':
          x = cx + radius * Math.cos(angle);
          y = cy + radius * Math.sin(angle);
          z = cz;
          break;
        case 'yz':
          x = cx;
          y = cy + radius * Math.cos(angle);
          z = cz + radius * Math.sin(angle);
          break;
        case 'xz':
        default:
          x = cx + radius * Math.cos(angle);
          y = cy;
          z = cz + radius * Math.sin(angle);
          break;
      }
      
      const newGlyphName = `${sourceGlyph}_${generationId}_${i}`;
      
      newCommands += `\nPLACE "${newGlyphName}" AT ${x.toFixed(2)} ${y.toFixed(2)} ${z.toFixed(2)};`;
      newCommands += `\nSCALE "${newGlyphName}" BY ${scale.toFixed(2)};`;
      newCommands += `\nCONNECT "${centerGlyph}" TO "${newGlyphName}";`;

      if (addPulse) {
          newCommands += `\nPULSE "${newGlyphName}" INTERVAL 2000;`;
      }
      if (addOrbit) {
          const finalSpeed = orbitSpeed * orbitDirection;
          newCommands += `\nORBIT "${newGlyphName}" AROUND "${centerGlyph}" SPEED ${finalSpeed.toFixed(2)};`;
      }
    }

    setSharedDsl((currentDsl) => (currentDsl || '') + newCommands);
    toast.success(`Generated a ${count}-point mandala.`);
  };

  return (
    <div className="bg-gray-900 bg-opacity-70 p-4 rounded-lg border border-amber-400/30 h-full overflow-y-auto">
        <h3 className="text-lg font-semibold text-amber-300 flex items-center gap-2 mb-4">
            <CircleDot size={18}/>
            Radial Array Tool
        </h3>
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-gray-300">Center Glyph</label>
                <select value={centerGlyph} onChange={(e) => setCenterGlyph(e.target.value)} className="w-full mt-1 bg-gray-800 border border-gray-600 rounded-md p-2">
                    <option value="">Select Center...</option>
                    {allGlyphNames.map(name => <option key={name} value={name}>{name}</option>)}
                </select>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-300">Source Glyph (to copy)</label>
                <select value={sourceGlyph} onChange={(e) => setSourceGlyph(e.target.value)} className="w-full mt-1 bg-gray-800 border border-gray-600 rounded-md p-2">
                    <option value="">Select Source...</option>
                    {allGlyphNames.map(name => <option key={name} value={name}>{name}</option>)}
                </select>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-300">Generation Plane</label>
                <div className="flex justify-around mt-1 bg-gray-800/50 p-1 rounded-md">
                    {['XY', 'XZ', 'YZ'].map(p => (
                        <button key={p} onClick={() => setPlane(p.toLowerCase())} className={`px-3 py-1 rounded w-full ${plane === p.toLowerCase() ? 'bg-purple-600 text-white' : 'bg-transparent text-gray-300'}`}>
                            {p}
                        </button>
                    ))}
                </div>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-300">Count: {count}</label>
                <input type="range" min="3" max="32" step="1" value={count} onChange={(e) => setCount(parseInt(e.target.value))} className="w-full"/>
            </div>
            <div>
                <label className="block text-sm font-medium text-gray-300">Radius: {radius}</label>
                <input type="range" min="1" max="15" step="0.5" value={radius} onChange={(e) => setRadius(parseFloat(e.target.value))} className="w-full"/>
            </div>
             <div>
                <label className="block text-sm font-medium text-gray-300">Scale: {scale.toFixed(1)}</label>
                <input type="range" min="0.1" max="3" step="0.1" value={scale} onChange={(e) => setScale(parseFloat(e.target.value))} className="w-full"/>
            </div>
            <div className="space-y-3 pt-4 border-t border-purple-800/50">
                <label className="block text-sm font-medium text-gray-300 mb-2">Animation Settings</label>
                <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                    <label htmlFor="pulse-toggle" className="flex items-center gap-2"><Zap size={16}/> Add Pulse</label>
                    <input type="checkbox" id="pulse-toggle" checked={addPulse} onChange={(e) => setAddPulse(e.target.checked)} />
                </div>
                <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                    <label htmlFor="orbit-toggle" className="flex items-center gap-2"><Orbit size={16}/> Add Orbit</label>
                    <input type="checkbox" id="orbit-toggle" checked={addOrbit} onChange={(e) => setAddOrbit(e.target.checked)} />
                </div>
                {addOrbit && (
                    <div className="pl-2 space-y-3">
                        <div>
                            <label className="block text-sm font-medium text-gray-300">Orbit Speed: {orbitSpeed.toFixed(1)}</label>
                            <input type="range" min="0.1" max="5" step="0.1" value={orbitSpeed} onChange={(e) => setOrbitSpeed(parseFloat(e.target.value))} className="w-full"/>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-300">Direction</label>
                            <div className="flex justify-around mt-1 bg-gray-800/50 p-1 rounded-md">
                                <button onClick={() => setOrbitDirection(1)} className={`px-3 py-1 rounded w-full ${orbitDirection === 1 ? 'bg-purple-600 text-white' : 'bg-transparent text-gray-300'}`}>
                                    Clockwise
                                </button>
                                <button onClick={() => setOrbitDirection(-1)} className={`px-3 py-1 rounded w-full ${orbitDirection === -1 ? 'bg-purple-600 text-white' : 'bg-transparent text-gray-300'}`}>
                                    Counter-CW
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>

            <button onClick={handleGenerate} className="w-full px-4 py-2 font-bold bg-amber-600 hover:bg-amber-500 rounded-lg transition-colors text-white">
                Generate Mandala
            </button>
        </div>
    </div>
  );
};
