import React, { useState, useMemo } from 'react';
import { SacredGeometryCompiler } from '../core/SacredGeometryCompiler';

/**
 * A UI component for writing, compiling, and inspecting
 * Sacred Geometry DSL code.
 */
export function CathedralDSLEditor() {
  const [dslCode, setDslCode] = useState('PLACE "SUN_STONE" AT 0 0 0;\nPULSE "SUN_STONE" INTERVAL 2000;');
  const [compiledOutput, setCompiledOutput] = useState(null);
  const [error, setError] = useState('');

  // We use useMemo to ensure the compiler is only instantiated once per component lifecycle.
  const compiler = useMemo(() => new SacredGeometryCompiler(), []);

  const handleCompile = () => {
    try {
      setError('');
      const output = compiler.compile(dslCode);
      setCompiledOutput(output);
    } catch (err) {
      console.error("Compilation Error:", err);
      setError(err.message);
      setCompiledOutput(null);
    }
  };

  return (
    <div className="w-full p-4 space-y-4">
      <h2 className="text-2xl font-semibold text-amber-300 text-center">Architect's Table</h2>
      
      <div className="flex flex-col">
        <label htmlFor="dsl-input" className="text-lg text-purple-300 mb-2">Sacred Geometry DSL</label>
        <textarea
          id="dsl-input"
          value={dslCode}
          onChange={(e) => setDslCode(e.target.value)}
          className="w-full h-48 p-3 font-mono text-base bg-gray-900 border-2 border-purple-500/50 rounded-lg focus:ring-2 focus:ring-purple-400 focus:outline-none transition-all text-gray-100"
          placeholder="BEGIN SEQUENCE..."
        />
      </div>

      <div className="text-center">
        <button
          onClick={handleCompile}
          className="px-8 py-3 font-bold text-xl bg-purple-700 hover:bg-purple-600 rounded-lg transition-colors shadow-lg shadow-purple-500/20"
        >
          Compile Glyphs
        </button>
      </div>

      {error && (
        <div className="p-4 mt-4 text-red-400 bg-red-900/50 border border-red-500/50 rounded-lg">
          <p className="font-bold">Compilation Failed:</p>
          <p>{error}</p>
        </div>
      )}
      {compiledOutput && (
        <div className="p-4 mt-4 bg-gray-800/50 border border-gray-700 rounded-lg">
          <h3 className="text-lg font-semibold text-green-400">Compiled Blueprint</h3>
          <pre className="mt-2 p-3 text-sm text-left bg-black rounded-md overflow-x-auto">
            {JSON.stringify(compiledOutput, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
}
