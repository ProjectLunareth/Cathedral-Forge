import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

/**
 * A single, animatable glyph that responds to PULSE commands.
 * @param {object} props - Component props.
 * @param {THREE.Vector3} props.position - The initial position of the glyph.
 * @param {object} props.animation - The animation data from the compiled layout.
 */
export function PulsingGlyph({ position, animation }) {
  const meshRef = useRef();

  // useFrame is a hook that runs on every rendered frame, the heart of our animation
  useFrame(({ clock }) => {
    if (!meshRef.current || !animation) return;

    // Handle PULSE animation logic
    if (animation.type === 'PULSE') {
      const { interval, amplitude } = animation;
      // Create a smooth wave function (sine wave) based on the current time and the specified interval
      const time = clock.getElapsedTime();
      const pulse = (Math.sin((time * Math.PI * 2) / (interval / 1000)) + 1) / 2; // Oscillates between 0 and 1
      
      // Apply the pulse to the scale and emissive intensity of the glyph's material
      const scale = 1 + pulse * (amplitude - 1);
      meshRef.current.scale.set(scale, scale, scale);
      meshRef.current.material.emissiveIntensity = 0.5 + pulse * 1.5;
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <icosahedronGeometry args={[0.4, 1]} />
      <meshStandardMaterial 
        color="#f472b6" 
        emissive="#a855f7" 
        emissiveIntensity={0.5} 
        roughness={0.1} 
        metalness={0.9} 
      />
    </mesh>
  );
}
