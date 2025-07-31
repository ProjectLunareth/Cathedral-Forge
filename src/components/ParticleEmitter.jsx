// /src/components/ParticleEmitter.jsx
import React, { useRef, useState, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// A single, self-managing particle
const Particle = ({ initialPosition, velocity, lifespan, color }) => {
  const meshRef = useRef();
  const life = useRef(0);

  useFrame((_, delta) => {
    if (!meshRef.current) return;

    life.current += delta * 1000; // Track life in milliseconds
    
    // Move the particle
    meshRef.current.position.add(velocity.clone().multiplyScalar(delta));

    // Fade out as it nears the end of its life
    const remainingLife = 1.0 - (life.current / lifespan);
    meshRef.current.material.opacity = Math.max(0, remainingLife);

    // Hide the particle when its life is over
    if (life.current >= lifespan) {
      meshRef.current.visible = false;
    }
  });

  return (
    <mesh ref={meshRef} position={initialPosition}>
      <sphereGeometry args={[0.05, 8, 8]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={2} transparent />
    </mesh>
  );
};

// The Emitter, which manages creating and destroying particles
export const ParticleEmitter = ({ sourceGlyphName, emitterConfig }) => {
  const [particles, setParticles] = useState([]);
  const timeSinceLastEmit = useRef(0);

  const { rate = 50, lifespan = 2000, speed = 1, color = '#FFFFFF' } = emitterConfig;

  const emitInterval = 1000 / rate; // Time in ms between emits

  useFrame(({ scene }, delta) => {
    // Find the live 3D object for the source glyph in the scene
    const sourceObject = scene.getObjectByName(sourceGlyphName);
    if (!sourceObject) return;

    timeSinceLastEmit.current += delta * 1000;

    const newParticles = [];
    // Create new particles if enough time has passed
    while (timeSinceLastEmit.current > emitInterval) {
      newParticles.push({
        id: Math.random(), // Simple unique ID
        createdAt: Date.now(),
        position: sourceObject.position.clone(),
        velocity: new THREE.Vector3(
          (Math.random() - 0.5) * speed,
          (Math.random() - 0.5) * speed,
          (Math.random() - 0.5) * speed
        ),
        lifespan,
        color,
      });
      timeSinceLastEmit.current -= emitInterval;
    }
    
    // Add new particles and filter out old ones
    if (newParticles.length > 0) {
        setParticles(p => [...p.filter(particle => (Date.now() - particle.createdAt) < particle.lifespan), ...newParticles]);
    }
  });

  // A safety cleanup interval to remove any particles that might have been missed
  useEffect(() => {
    const interval = setInterval(() => {
      setParticles(p => p.filter(particle => (Date.now() - particle.createdAt) < particle.lifespan));
    }, 2000);
    return () => clearInterval(interval);
  }, [emitterConfig.lifespan]);

  return (
    <group>
      {particles.map(p => (
        <Particle
          key={p.id}
          initialPosition={p.position}
          velocity={p.velocity}
          lifespan={p.lifespan}
          color={p.color}
        />
      ))}
    </group>
  );
};
