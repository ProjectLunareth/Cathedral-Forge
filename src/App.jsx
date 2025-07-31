import React, { useState, useMemo, useCallback, useEffect } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { Auth } from './components/Auth';
import { useKarmaAccess } from './hooks/useKarmaAccess';
import { SacredGeometryCompiler } from './core/SacredGeometryCompiler';
import { useRitualSubmitter } from './hooks/useRitualSubmitter';
import { RitualLibraryBrowser } from './components/RitualLibraryBrowser';
import { RitualCanvas } from './components/RitualCanvas';
import { Save, Beaker, Zap, Wand2, BookOpen, Sliders, ArrowLeft, CircleDot } from 'lucide-react';
import { useSharedRitual } from './hooks/useSharedRitual';
import { useChorusPresence } from './hooks/useChorusPresence';
import { ChorusParticipants } from './components/ChorusParticipants';
import { useDslManager } from './hooks/useDslManager';
import { GlyphInspector } from './components/GlyphInspector';
import { MemoryNexus } from './components/MemoryNexus';
import { PatternTools } from './components/PatternTools';

function ArchitectTools({ sharedDsl, setSharedDsl, compiledLayout, onCompile, onSave, user, selectedGlyph, onSelectGlyph, sessionId, dslLoading, symmetry, onSymmetryChange, onAddGlyph }) {
    const dslManager = useDslManager(sharedDsl, setSharedDsl);
    const { participants, loading: participantsLoading } = useChorusPresence(sessionId, user);
    
    const [activeTab, setActiveTab] = useState('inspector');
    const [ritualId, setRitualId] = useState('GenerativeRitual');
    const [ritualName, setRitualName] = useState("The Fountain of Souls");
  
    const allGlyphNames = useMemo(() => {
      return compiledLayout?.steps
          .filter(s => s.command === 'PLACE')
          .map(s => s.arguments[1].replace(/"/g, '')) || [];
    }, [compiledLayout]);
  
    useEffect(() => {
      if (selectedGlyph) setActiveTab('inspector');
    }, [selectedGlyph]);
    
    const handleLoadRitual = (ritual) => {
      setSharedDsl(ritual.dslString);
      setRitualId(ritual.id || `ritual_${Date.now()}`);
      setRitualName(ritual.name || "Untitled Ritual");
      toast.success(`Broadcasted "${ritual.name}" to the Chorus.`);
    };
  
    const handleSaveClick = () => {
      if (!compiledLayout) { toast.error('You must compile before saving.'); return; }
      onSave({ id: ritualId, name: ritualName, dslString: sharedDsl });
    };
  
    return (
      <div className="w-full h-full p-4 flex flex-col bg-black/30 rounded-2xl shadow-lg border border-purple-500/30">
          <div className="text-center">
              <h2 className="text-xl font-semibold text-amber-300">Architect's Table</h2>
              <p className="text-sm text-cyan-300 flex items-center justify-center gap-2"><Zap size={14} /> {sessionId}</p>
          </div>
          <div className="my-2"><ChorusParticipants participants={participants} loading={participantsLoading} /></div>
          
          <div className="flex-shrink-0 p-2 my-2 bg-gray-900/50 rounded-lg border border-purple-700/50">
              <h4 className="text-sm font-bold text-center text-gray-300 mb-2">Symmetry Mode</h4>
              <div className="flex justify-around">
                  {['X', 'Y', 'Z'].map(axis => (
                      <label key={axis} className="flex items-center gap-2 text-lg font-mono">
                          <input type="checkbox" checked={symmetry[axis.toLowerCase()]} onChange={() => onSymmetryChange(axis.toLowerCase())} />
                          {axis}
                      </label>
                  ))}
              </div>
          </div>
  
          <div className="flex-shrink-0 flex border-b border-purple-800">
              <button onClick={() => setActiveTab('inspector')} className={`px-4 py-2 flex items-center gap-2 ${activeTab === 'inspector' ? 'text-amber-300 border-b-2 border-amber-300' : 'text-gray-400'}`}><Sliders size={16}/> Inspector</button>
              <button onClick={() => setActiveTab('patterns')} className={`px-4 py-2 flex items-center gap-2 ${activeTab === 'patterns' ? 'text-amber-300 border-b-2 border-amber-300' : 'text-gray-400'}`}><CircleDot size={16}/> Patterns</button>
              <button onClick={() => setActiveTab('codex')} className={`px-4 py-2 flex items-center gap-2 ${activeTab === 'codex' ? 'text-amber-300 border-b-2 border-amber-300' : 'text-gray-400'}`}><BookOpen size={16}/> Codex</button>
          </div>
  
          <div className="flex-grow py-4 min-h-0">
              {activeTab === 'inspector' && ( <GlyphInspector selectedGlyph={selectedGlyph} dslManager={dslManager} onDeselect={() => onSelectGlyph(null)} compiledLayout={compiledLayout} allGlyphNames={allGlyphNames} /> )}
              {activeTab === 'patterns' && ( <PatternTools allGlyphNames={allGlyphNames} compiledLayout={compiledLayout} sharedDsl={sharedDsl} setSharedDsl={setSharedDsl} /> )}
              {activeTab === 'codex' && ( <RitualLibraryBrowser onLoadRitual={handleLoadRitual} /> )}
          </div>
  
          <div className="flex-shrink-0 flex justify-between items-center gap-4">
             <button onClick={onAddGlyph} className="flex items-center gap-2 px-4 py-2 font-bold bg-green-700 hover:bg-green-600 rounded-lg transition-colors"><Wand2 size={20}/>Add Glyph</button>
             <div className="flex gap-4">
              <button onClick={() => onCompile(sharedDsl)} className="flex items-center gap-2 px-4 py-2 font-bold bg-indigo-700 hover:bg-indigo-600 rounded-lg transition-colors"><Beaker size={20}/>Compile</button>
              <button onClick={handleSaveClick} className="flex items-center gap-2 px-4 py-2 font-bold bg-purple-700 hover:bg-purple-600 rounded-lg transition-colors"><Save size={20}/>Save</button>
             </div>
          </div>
      </div>
    );
}

function App() {
  const { user } = useKarmaAccess();
  const { submitRitual } = useRitualSubmitter(user);
  const [activeSessionId, setActiveSessionId] = useState(null);
  
  const { dsl: sharedDsl, updateDsl: setSharedDsl, loading: dslLoading } = useSharedRitual(activeSessionId);
  const dslManager = useDslManager(sharedDsl, setSharedDsl);

  const [selectedGlyph, setSelectedGlyph] = useState(null);
  const [connectionStartGlyph, setConnectionStartGlyph] = useState(null);
  const [symmetry, setSymmetry] = useState({ x: false, y: false, z: false });
  const [isCtrlPressed, setIsCtrlPressed] = useState(false);

  const compiler = useMemo(() => new SacredGeometryCompiler(), []);
  const [compiledLayout, setCompiledLayout] = useState(null);

  useEffect(() => {
    const handleKeyDown = (e) => { if (e.key === 'Control') setIsCtrlPressed(true); };
    const handleKeyUp = (e) => { if (e.key === 'Control') setIsCtrlPressed(false); };
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  const handleCompile = useCallback((dsl) => {
    if (dsl === null || dsl === undefined) { setCompiledLayout(null); return; }
    try {
      const output = compiler.compile(dsl);
      setCompiledLayout(output);
    } catch (e) { console.error(`Compilation failed: ${e.message}`); }
  }, [compiler]);
  
  useEffect(() => {
    if(sharedDsl !== null && !dslLoading) handleCompile(sharedDsl);
  }, [sharedDsl, dslLoading, handleCompile]);

  const handleSymmetryChange = (axis) => {
      setSymmetry(prev => ({ ...prev, [axis]: !prev[axis] }));
  };

  const handleAddGlyph = () => {
    const baseName = `Glyph_${Date.now().toString().slice(-6)}`;
    dslManager.addGlyph(baseName, [2, 0, 0], symmetry);
    setSelectedGlyph(baseName);
  };

  const handleGlyphInteraction = useCallback((glyphName, event, type) => {
    if (!glyphName) { setSelectedGlyph(null); setConnectionStartGlyph(null); return; }
    
    if (type === 'wheel') {
        event.stopPropagation();
        const glyphData = dslManager.getGlyphData(glyphName, compiledLayout);
        if (!glyphData) return;
        const scaleAmount = event.deltaY > 0 ? -0.1 : 0.1;
        const newScale = Math.max(0.1, (glyphData.scale || 1.0) + scaleAmount);
        dslManager.updateAttribute(glyphName, 'SCALE', ['BY', newScale.toFixed(2)], symmetry);
        return;
    }

    if (type === 'pointerdown') {
        event.stopPropagation();
        if (event.ctrlKey) {
            if (!connectionStartGlyph) {
                setConnectionStartGlyph(glyphName);
                toast(`Connecting from "${glyphName}"...`);
            } else {
                if (connectionStartGlyph !== glyphName) {
                    setSharedDsl(currentDsl => `${currentDsl || ''}\nCONNECT "${connectionStartGlyph}" TO "${glyphName}";`.trim());
                    toast.success(`Connected "${connectionStartGlyph}" to "${glyphName}"!`);
                }
                setConnectionStartGlyph(null);
            }
        } else {
            setSelectedGlyph(glyphName);
            setConnectionStartGlyph(null);
        }
    }
  }, [connectionStartGlyph, setSharedDsl, dslManager, compiledLayout, symmetry]);

  const handleGlyphDrag = useCallback((glyphName, newPosition) => {
    dslManager.updateAttribute(glyphName, 'PLACE', ['AT', ...newPosition.map(p => p.toFixed(2))], symmetry);
  }, [dslManager, symmetry]);
  
  const handleSelectPath = (action) => {
      if (action === 'join_chorus') {
          const initialDsl = 'PLACE "HEART_STONE" AT 0 0 0 MATERIAL "HYPERFRACTAL";\nSCALE "HEART_STONE" BY 1.5;\nEMIT FROM "HEART_STONE" RATE 100 LIFESPAN 3000 SPEED 2 COLOR #A78BFA;\nPLACE "SATELLITE" AT 6 0 0;\nATTRACT "SATELLITE" TO "HEART_STONE" STRENGTH 1.0;';
          setSharedDsl(initialDsl);
          setActiveSessionId('main_chorus');
      }
      if (action === 'new_ritual') {
          const newSessionId = `ritual_${user.uid}_${Date.now()}`;
          setSharedDsl('PLACE "origin" AT 0 0 0;');
          setActiveSessionId(newSessionId);
      }
  };

  const renderWorkspace = () => (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 w-full max-w-7xl mx-auto flex-grow h-[calc(100vh-150px)]">
        <button onClick={() => setActiveSessionId(null)} className="absolute top-24 left-8 z-10 flex items-center gap-2 px-3 py-1 bg-purple-800/50 hover:bg-purple-700/50 rounded-lg"><ArrowLeft size={16}/> Back to Nexus</button>
        <ArchitectTools
            sessionId={activeSessionId}
            sharedDsl={sharedDsl}
            setSharedDsl={setSharedDsl}
            user={user}
            compiledLayout={compiledLayout}
            onCompile={handleCompile}
            onSave={submitRitual}
            selectedGlyph={selectedGlyph}
            onSelectGlyph={setSelectedGlyph}
            dslLoading={dslLoading}
            symmetry={symmetry}
            onSymmetryChange={handleSymmetryChange}
            onAddGlyph={handleAddGlyph}
        />
        <div className="bg-black/30 rounded-2xl shadow-lg border border-purple-500/30">
            <RitualCanvas 
                layout={compiledLayout} 
                onGlyphInteraction={handleGlyphInteraction}
                onGlyphDrag={handleGlyphDrag}
                isCtrlPressed={isCtrlPressed}
            />
        </div>
    </div>
  );

  return (
    <main className="relative flex flex-col items-center h-screen p-4 bg-gray-900 text-gray-100">
      <Toaster position="bottom-right" />
      <Auth />
      <header className="text-center py-4 shrink-0">
        <h1 className="text-4xl md:text-5xl font-bold text-purple-300 tracking-wider drop-shadow-[0_0_20px_rgba(192,132,252,0.5)]">The Cathedral of Glyphs</h1>
      </header>
      {user ? (
          activeSessionId ? renderWorkspace() : <MemoryNexus onSelectPath={handleSelectPath} />
      ) : (
        <div className="flex-grow flex items-center justify-center">
            <p className="text-center text-amber-300 mt-8 text-xl">The gates are open. Announce yourself to the Spiral to begin your work.</p>
        </div>
      )}
    </main>
  );
}

export default App;
