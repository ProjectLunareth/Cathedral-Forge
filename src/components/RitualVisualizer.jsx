// /src/components/RitualVisualizer.jsx
import React, { useMemo, forwardRef } from 'react';
import * as THREE from 'three';
import { AnimatedGlyph } from './AnimatedGlyph';
import { ShaderGlyph } from './ShaderGlyph';
import { Line } from '@react-three/drei';
import { ParticleEmitter } from './ParticleEmitter';

const getGlyphProperties = (glyphName, layout) => {
    const props = { name: glyphName, position: new THREE.Vector3(0,0,0), animations: {}, forces: [], material: 'default', color: '#DB2777', scale: 1.0 };
    if (!layout || !layout.steps) return props;
    layout.steps.forEach(step => {
        const stepGlyphName = step.arguments[1]?.replace(/"/g, '');
        if (stepGlyphName !== glyphName) return;
        switch(step.command) {
            case 'PLACE':
                props.position = new THREE.Vector3(parseFloat(step.arguments[3]||0), parseFloat(step.arguments[4]||0), parseFloat(step.arguments[5]||0));
                const materialIndex = step.arguments.indexOf('MATERIAL');
                if (materialIndex !== -1 && step.arguments[materialIndex + 1]) { props.material = step.arguments[materialIndex + 1].replace(/"/g, ''); }
                break;
            case 'PULSE': props.animations.PULSE = { interval: parseFloat(step.arguments[3] || 2000), amplitude: 1.5 }; break;
            case 'ORBIT': props.animations.ORBIT = { center: step.arguments[3].replace(/"/g, ''), speed: parseFloat(step.arguments[5] || 1.0) }; break;
            case 'ROTATE': props.animations.ROTATE = { speed: parseFloat(step.arguments[3] || 1.0) }; break;
            case 'SCALE': props.scale = parseFloat(step.arguments[3] || 1.0); break;
            case 'COLOR': props.color = step.arguments[3]; break;
            case 'ATTRACT': props.forces.push({ type: 'ATTRACT', target: step.arguments[3].replace(/"/g, ''), strength: parseFloat(step.arguments[5] || 1.0) }); break;
            case 'REPEL': props.forces.push({ type: 'REPEL', target: step.arguments[3].replace(/"/g, ''), strength: parseFloat(step.arguments[5] || 1.0) }); break;
            default: break;
        }
    });
    return props;
};

export const RitualVisualizer = forwardRef(({ layout, onGlyphInteraction }, ref) => {
  
  const allGlyphs = useMemo(() => {
    if (!layout || !layout.steps) return {};
    const placedGlyphNames = [...new Set(layout.steps.filter(s => s.command === 'PLACE').map(s => s.arguments[1]?.replace(/"/g, '')).filter(Boolean))];
    return placedGlyphNames.reduce((acc, name) => {
        acc[name] = getGlyphProperties(name, layout);
        return acc;
    }, {});
  }, [layout]);

  const emitters = useMemo(() => {
    if (!layout || !layout.steps) return [];
    return layout.steps
      .filter(step => step.command === 'EMIT')
      .map((step, index) => {
        const from = step.arguments[2].replace(/"/g, '');
        const rateArg = step.arguments.indexOf('RATE');
        const lifeArg = step.arguments.indexOf('LIFESPAN');
        const speedArg = step.arguments.indexOf('SPEED');
        const colorArg = step.arguments.indexOf('COLOR');

        return {
          id: `${from}-${index}`,
          sourceGlyphName: from,
          config: {
            rate: rateArg !== -1 ? parseFloat(step.arguments[rateArg + 1]) : 50,
            lifespan: lifeArg !== -1 ? parseFloat(step.arguments[lifeArg + 1]) : 2000,
            speed: speedArg !== -1 ? parseFloat(step.arguments[speedArg + 1]) : 1,
            color: colorArg !== -1 ? step.arguments[colorArg + 1] : '#FFFFFF',
          }
        };
      });
  }, [layout]);

  if (!layout) return null;

  return (
    <group ref={ref}>
      {Object.values(allGlyphs).map((glyphData) => {
        const GlyphComponent = glyphData.material === 'HYPERFRACTAL' ? ShaderGlyph : AnimatedGlyph;
        return (
          <GlyphComponent
            key={glyphData.name}
            glyphData={glyphData}
            allGlyphs={allGlyphs}
            onInteraction={onGlyphInteraction}
          />
        );
      })}
        
      {layout.connections?.map((conn, index) => {
        const startGlyph = allGlyphs[conn.from];
        const endGlyph = allGlyphs[conn.to];
        if (startGlyph && endGlyph) {
            return <Line key={`conn-${index}`} points={[startGlyph.position, endGlyph.position]} color="#FFD700" lineWidth={2} />;
        }
        return null;
      })}

      {emitters.map((emitter) => (
        <ParticleEmitter 
            key={emitter.id}
            sourceGlyphName={emitter.sourceGlyphName}
            emitterConfig={emitter.config}
        />
      ))}
    </group>
  );
});
