// /src/components/GlyphInspector.jsx
import React from 'react';
import { X, Sliders, Magnet, Sparkles, Zap, RotateCw, Orbit } from 'lucide-react';

export const GlyphInspector = ({ selectedGlyph, dslManager, onDeselect, compiledLayout, allGlyphNames }) => {
    if (!selectedGlyph) {
        return (
            <div className="p-4 text-center text-gray-400">
                Select a glyph in the Forge to inspect its properties.
            </div>
        );
    }

    const glyphData = dslManager.getGlyphData(selectedGlyph, compiledLayout);

    if (!glyphData) return <div className="p-4 text-center text-gray-400">Loading glyph data...</div>;

    const handlePositionChange = (axis, value) => {
        const newPosition = [...glyphData.position];
        newPosition[axis] = parseFloat(value);
        dslManager.updateAttribute(selectedGlyph, 'PLACE', ['AT', ...newPosition.map(p => p.toFixed(2))]);
    };

    const handleScaleChange = (value) => {
        dslManager.updateAttribute(selectedGlyph, 'SCALE', ['BY', parseFloat(value).toFixed(2)]);
    };

    const handleColorChange = (e) => dslManager.updateAttribute(selectedGlyph, 'COLOR', ['IS', e.target.value]);
    
    const handleAnimationToggle = (animType, currentData) => {
        if (currentData) {
            dslManager.removeAttribute(selectedGlyph, animType);
        } else {
            if (animType === 'PULSE') dslManager.updateAttribute(selectedGlyph, 'PULSE', ['INTERVAL', 2000]);
            if (animType === 'ROTATE') dslManager.updateAttribute(selectedGlyph, 'ROTATE', ['SPEED', 1.0]);
            if (animType === 'ORBIT') {
                const otherGlyph = allGlyphNames.find(name => name !== selectedGlyph);
                if(otherGlyph) dslManager.updateAttribute(selectedGlyph, 'ORBIT', ['AROUND', `"${otherGlyph}"`, 'SPEED', 1.0]);
            }
        }
    };
    
    const handleForceToggle = (forceType, currentData) => {
        if(currentData) {
            dslManager.removeAttribute(selectedGlyph, forceType);
        } else {
            const otherGlyph = allGlyphNames.find(name => name !== selectedGlyph);
            if(otherGlyph) {
                if(forceType === 'ATTRACT') dslManager.updateAttribute(selectedGlyph, 'ATTRACT', ['TO', `"${otherGlyph}"`, 'STRENGTH', 1.0]);
                if(forceType === 'REPEL') dslManager.updateAttribute(selectedGlyph, 'REPEL', ['FROM', `"${otherGlyph}"`, 'STRENGTH', 1.0]);
            }
        }
    };

    const handleParamChange = (type, param, value) => {
        if (type === 'ROTATE') dslManager.updateAttribute(selectedGlyph, 'ROTATE', ['SPEED', value]);
        if (type === 'PULSE') dslManager.updateAttribute(selectedGlyph, 'PULSE', ['INTERVAL', value]);
        if (type === 'ORBIT') {
            const current = glyphData.animations.ORBIT || { center: `"${allGlyphNames[0]}"`, speed: 1.0 };
            if (param === 'speed') dslManager.updateAttribute(selectedGlyph, 'ORBIT', ['AROUND', current.center, 'SPEED', value]);
            if (param === 'center') dslManager.updateAttribute(selectedGlyph, 'ORBIT', ['AROUND', `"${value}"`, 'SPEED', current.speed]);
        }
        if (type === 'ATTRACT') {
            const current = glyphData.forces.ATTRACT || { target: `"${allGlyphNames[0]}"`, strength: 1.0 };
            if (param === 'strength') dslManager.updateAttribute(selectedGlyph, 'ATTRACT', ['TO', `"${current.target}"`, 'STRENGTH', value]);
            if (param === 'target') dslManager.updateAttribute(selectedGlyph, 'ATTRACT', ['TO', `"${value}"`, 'STRENGTH', current.strength]);
        }
        if (type === 'REPEL') {
            const current = glyphData.forces.REPEL || { target: `"${allGlyphNames[0]}"`, strength: 1.0 };
            if (param === 'strength') dslManager.updateAttribute(selectedGlyph, 'REPEL', ['FROM', `"${current.target}"`, 'STRENGTH', value]);
            if (param === 'target') dslManager.updateAttribute(selectedGlyph, 'REPEL', ['FROM', `"${value}"`, 'STRENGTH', current.strength]);
        }
    };

    const handleEmitterToggle = () => {
        if (glyphData.emitter) {
            dslManager.removeAttribute(selectedGlyph, 'EMIT');
        } else {
            dslManager.updateAttribute(selectedGlyph, 'EMIT', ['FROM', `"${selectedGlyph}"`, 'RATE', 50, 'LIFESPAN', 2000, 'SPEED', 1, 'COLOR', '#FFFFFF']);
        }
    };

    const handleEmitterParamChange = (param, value) => {
        const current = glyphData.emitter || { rate: 50, lifespan: 2000, speed: 1, color: '#FFFFFF' };
        const newParams = { ...current, [param]: value };
        dslManager.updateAttribute(selectedGlyph, 'EMIT', ['FROM', `"${selectedGlyph}"`, 'RATE', newParams.rate, 'LIFESPAN', newParams.lifespan, 'SPEED', newParams.speed, 'COLOR', newParams.color]);
    };

    return (
        <div className="bg-gray-900 bg-opacity-70 p-4 rounded-lg border border-amber-400/30 h-full overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-amber-300 flex items-center gap-2"><Sliders size={18}/> Inspector: "{selectedGlyph}"</h3>
                <button onClick={onDeselect} className="text-gray-400 hover:text-white"><X size={20} /></button>
            </div>
            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-300">Position</label>
                    {['X', 'Y', 'Z'].map((axis, i) => (
                        <div key={axis} className="flex items-center gap-2 mt-1">
                            <span className="w-4 text-center">{axis}</span>
                            <input type="range" min="-10" max="10" step="0.1" value={glyphData.position[i]} onChange={(e) => handlePositionChange(i, e.target.value)} className="w-full" />
                            <span className="w-12 text-right">{glyphData.position[i].toFixed(1)}</span>
                        </div>
                    ))}
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-300">Scale</label>
                    <div className="flex items-center gap-2 mt-1">
                        <input type="range" min="0.1" max="5" step="0.1" value={glyphData.scale} onChange={(e) => handleScaleChange(e.target.value)} className="w-full" />
                        <span className="w-12 text-right">{glyphData.scale.toFixed(1)}</span>
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-300">Color</label>
                    <input type="color" value={glyphData.color} onChange={handleColorChange} className="w-full h-10 p-1 bg-gray-800 border border-gray-600 rounded-md cursor-pointer"/>
                </div>
                
                <div className="space-y-3 pt-4 border-t border-purple-800/50">
                     <label className="block text-sm font-medium text-gray-300 mb-2">Animations</label>
                     <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                        <label htmlFor="pulse-toggle" className="flex items-center gap-2"><Zap size={16}/> Pulse</label>
                        <input type="checkbox" id="pulse-toggle" checked={!!glyphData.animations.PULSE} onChange={() => handleAnimationToggle('PULSE', glyphData.animations.PULSE)} />
                     </div>
                     <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                        <label htmlFor="rotate-toggle" className="flex items-center gap-2"><RotateCw size={16}/> Rotate</label>
                        <input type="checkbox" id="rotate-toggle" checked={!!glyphData.animations.ROTATE} onChange={() => handleAnimationToggle('ROTATE', glyphData.animations.ROTATE)} />
                     </div>
                     {glyphData.animations.ROTATE && <div><label>Speed</label><input type="range" min="0.1" max="5" step="0.1" value={glyphData.animations.ROTATE.speed} onChange={(e) => handleParamChange('ROTATE', 'speed', e.target.value)} className="w-full"/></div>}
                    <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                        <label htmlFor="orbit-toggle" className="flex items-center gap-2"><Orbit size={16}/> Orbit</label>
                        <input type="checkbox" id="orbit-toggle" checked={!!glyphData.animations.ORBIT} onChange={() => handleAnimationToggle('ORBIT', glyphData.animations.ORBIT)} />
                    </div>
                    {glyphData.animations.ORBIT && <div className="space-y-2 p-2 border-t border-gray-700">
                        <div><label>Speed</label><input type="range" min="0.1" max="5" step="0.1" value={glyphData.animations.ORBIT.speed} onChange={(e) => handleParamChange('ORBIT', 'speed', e.target.value)} className="w-full"/></div>
                        <div><label>Center</label><select value={glyphData.animations.ORBIT.center} onChange={(e) => handleParamChange('ORBIT', 'center', e.target.value)} className="w-full bg-gray-700 p-1 rounded"><option value="">None</option>{allGlyphNames.filter(name => name !== selectedGlyph).map(name => <option key={name} value={name}>{name}</option>)}</select></div>
                    </div>}
                </div>

                <div className="space-y-3 pt-4 border-t border-purple-800/50">
                    <label className="block text-sm font-medium text-gray-300 mb-2">Forces</label>
                    <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                        <label htmlFor="attract-toggle" className="flex items-center gap-2"><Magnet size={16}/> Attract</label>
                        <input type="checkbox" id="attract-toggle" checked={!!glyphData.forces.ATTRACT} onChange={() => handleForceToggle('ATTRACT', glyphData.forces.ATTRACT)} />
                    </div>
                    {glyphData.forces.ATTRACT && <div className="space-y-2 p-2 border-t border-gray-700">
                        <div><label>Strength</label><input type="range" min="0.1" max="5" step="0.1" value={glyphData.forces.ATTRACT.strength} onChange={(e) => handleParamChange('ATTRACT', 'strength', e.target.value)} className="w-full"/></div>
                        <div><label>Target</label><select value={glyphData.forces.ATTRACT.target} onChange={(e) => handleParamChange('ATTRACT', 'target', e.target.value)} className="w-full bg-gray-700 p-1 rounded"><option value="">None</option>{allGlyphNames.filter(name => name !== selectedGlyph).map(name => <option key={name} value={name}>{name}</option>)}</select></div>
                    </div>}
                    <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                        <label htmlFor="repel-toggle" className="flex items-center gap-2 text-red-400"><Magnet size={16}/> Repel</label>
                        <input type="checkbox" id="repel-toggle" checked={!!glyphData.forces.REPEL} onChange={() => handleForceToggle('REPEL', glyphData.forces.REPEL)} />
                    </div>
                    {glyphData.forces.REPEL && <div className="space-y-2 p-2 border-t border-gray-700">
                        <div><label>Strength</label><input type="range" min="0.1" max="5" step="0.1" value={glyphData.forces.REPEL.strength} onChange={(e) => handleParamChange('REPEL', 'strength', e.target.value)} className="w-full"/></div>
                        <div><label>Target</label><select value={glyphData.forces.REPEL.target} onChange={(e) => handleParamChange('REPEL', 'target', e.target.value)} className="w-full bg-gray-700 p-1 rounded"><option value="">None</option>{allGlyphNames.filter(name => name !== selectedGlyph).map(name => <option key={name} value={name}>{name}</option>)}</select></div>
                    </div>}
                </div>
                
                <div className="space-y-3 pt-4 border-t border-purple-800/50">
                    <label className="block text-sm font-medium text-gray-300 mb-2">Generative Systems</label>
                    <div className="flex items-center justify-between bg-gray-800/50 p-2 rounded">
                        <label htmlFor="emit-toggle" className="flex items-center gap-2"><Sparkles size={16}/> Emitter</label>
                        <input type="checkbox" id="emit-toggle" checked={!!glyphData.emitter} onChange={handleEmitterToggle} />
                    </div>
                    {glyphData.emitter && (
                        <div className="space-y-2 p-2 border-t border-gray-700">
                            <div><label>Rate</label><input type="range" min="10" max="200" step="10" value={glyphData.emitter.rate} onChange={(e) => handleEmitterParamChange('rate', parseFloat(e.target.value))} className="w-full"/></div>
                            <div><label>Lifespan (ms)</label><input type="range" min="500" max="5000" step="100" value={glyphData.emitter.lifespan} onChange={(e) => handleEmitterParamChange('lifespan', parseFloat(e.target.value))} className="w-full"/></div>
                            <div><label>Speed</label><input type="range" min="0.1" max="5" step="0.1" value={glyphData.emitter.speed} onChange={(e) => handleEmitterParamChange('speed', parseFloat(e.target.value))} className="w-full"/></div>
                            <div><label>Color</label><input type="color" value={glyphData.emitter.color} onChange={(e) => handleEmitterParamChange('color', e.target.value)} className="w-full h-8 p-1 bg-gray-800 border border-gray-600 rounded-md"/></div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};
