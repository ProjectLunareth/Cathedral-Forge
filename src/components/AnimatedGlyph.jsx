// /src/components/AnimatedGlyph.jsx
import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// Reverted to a simple component without forwardRef
export function AnimatedGlyph({ glyphData, allGlyphs, onInteraction }) {
  const meshRef = useRef();
  const velocity = useRef(new THREE.Vector3(0, 0, 0));
  const { name, position, animations, forces, color, scale = 1.0 } = glyphData;

  // Reset physics state if the glyph's core position changes
  useEffect(() => {
    velocity.current.set(0, 0, 0);
    if(meshRef.current) {
        meshRef.current.position.copy(position);
    }
  }, [position]);

  const pulseAnimation = useMemo(() => animations.PULSE, [animations]);
  const orbitAnimation = useMemo(() => animations.ORBIT, [animations]);
  const rotateAnimation = useMemo(() => animations.ROTATE, [animations]);

  const orbitRadiusOffset = useMemo(() => {
    if (!orbitAnimation) return null;
    const centerGlyph = allGlyphs[orbitAnimation.center];
    if (!centerGlyph) return null;
    return new THREE.Vector3().subVectors(position, centerGlyph.position);
  }, [orbitAnimation, allGlyphs, position]);


  useFrame(({ clock }, delta) => {
    if (!meshRef.current) return;
    const time = clock.getElapsedTime();

    if (forces && forces.length > 0) {
        const acceleration = new THREE.Vector3(0, 0, 0);
        forces.forEach(force => {
            if (force.type === 'ATTRACT') {
                const targetGlyph = allGlyphs[force.target];
                if (targetGlyph) {
                    const direction = new THREE.Vector3().subVectors(targetGlyph.position, meshRef.current.position);
                    const distanceSq = direction.lengthSq();
                    if (distanceSq > 0.1) {
                        const forceMagnitude = (force.strength * 10) / distanceSq;
                        direction.normalize().multiplyScalar(forceMagnitude);
                        acceleration.add(direction);
                    }
                }
            } else if (force.type === 'REPEL') {
                const targetGlyph = allGlyphs[force.target];
                if (targetGlyph) {
                    const direction = new THREE.Vector3().subVectors(targetGlyph.position, meshRef.current.position);
                    const distanceSq = direction.lengthSq();
                    if (distanceSq > 0.1) {
                        const forceMagnitude = (force.strength * 10) / distanceSq;
                        direction.normalize().multiplyScalar(forceMagnitude);
                        acceleration.sub(direction);
                    }
                }
            }
        });
        velocity.current.add(acceleration.multiplyScalar(delta));
        velocity.current.multiplyScalar(0.95);
        meshRef.current.position.add(velocity.current.clone().multiplyScalar(delta));
    } else if (orbitAnimation && orbitRadiusOffset) {
        const centerGlyph = allGlyphs[orbitAnimation.center];
        if (centerGlyph) {
            const angle = time * orbitAnimation.speed;
            const newPos = new THREE.Vector3().copy(centerGlyph.position);
            newPos.x += Math.cos(angle) * orbitRadiusOffset.x - Math.sin(angle) * orbitRadiusOffset.z;
            newPos.z += Math.sin(angle) * orbitRadiusOffset.x + Math.cos(angle) * orbitRadiusOffset.z;
            newPos.y += orbitRadiusOffset.y;
            meshRef.current.position.copy(newPos);
        }
    }

    let baseScale = scale;
    if (pulseAnimation) {
      const pulseFactor = (Math.sin(time * (Math.PI * 2 / (pulseAnimation.interval / 1000))) + 1) / 2;
      baseScale = scale + pulseFactor * 0.5;
    }
    meshRef.current.scale.set(baseScale, baseScale, baseScale);

    if (rotateAnimation) {
        meshRef.current.rotation.y += rotateAnimation.speed * 0.01;
        meshRef.current.rotation.x += rotateAnimation.speed * 0.005;
    }
  });
  
  const handleInteraction = (e, type) => {
      e.stopPropagation();
      onInteraction(name, e, type);
  };

  return (
    <mesh 
      ref={meshRef} 
      name={name} 
      position={position} 
      onPointerDown={(e) => handleInteraction(e, 'pointerdown')}
      onWheel={(e) => handleInteraction(e, 'wheel')}
    >
      <sphereGeometry args={[0.5, 32, 32]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.7} />
    </mesh>
  );
}
