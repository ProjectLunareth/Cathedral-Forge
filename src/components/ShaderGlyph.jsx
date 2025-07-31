// /src/components/ShaderGlyph.jsx
import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame, extend } from '@react-three/fiber';
import { shaderMaterial } from '@react-three/drei';
import * as THREE from 'three';

const HyperfractalMaterial = shaderMaterial(
  { u_time: 0, u_color: new THREE.Color('#7C3AED') },
  `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  `
    uniform float u_time;
    uniform vec3 u_color;
    varying vec2 vUv;
    void main() {
      float time = u_time * 0.5;
      vec2 p = vUv - 0.5;
      float r = length(p) * 2.0;
      float a = atan(p.y, p.x);
      float k = sin(10.0 * r - time * 2.0) * 0.5 + 0.5;
      k = pow(k, 3.0);
      float noise = (sin(a * 12.0 + time * 3.0) + 1.0) / 2.0;
      k *= noise;
      gl_FragColor = vec4(u_color * k, 1.0);
    }
  `
);

extend({ HyperfractalMaterial });

export function ShaderGlyph({ glyphData, allGlyphs, onInteraction }) {
  const meshRef = useRef();
  const materialRef = useRef();
  const velocity = useRef(new THREE.Vector3(0, 0, 0));
  const { name, position, animations, forces, color, scale = 1.0 } = glyphData;

  useEffect(() => {
    velocity.current.set(0, 0, 0);
    if(meshRef.current) {
        meshRef.current.position.copy(position);
    }
  }, [position]);

  const rotateAnimation = useMemo(() => animations.ROTATE, [animations]);

  useEffect(() => {
    if (materialRef.current) {
      materialRef.current.uniforms.u_color.value = new THREE.Color(color);
    }
  }, [color]);

  useFrame(({ clock }, delta) => {
    if (!meshRef.current) return;

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
    }

    if (materialRef.current) {
      materialRef.current.uniforms.u_time.value = clock.getElapsedTime();
    }
    if (rotateAnimation) {
        meshRef.current.rotation.y += rotateAnimation.speed * 0.01;
        meshRef.current.rotation.x += rotateAnimation.speed * 0.005;
    }
    meshRef.current.scale.set(scale, scale, scale);
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
      <sphereGeometry args={[1, 64, 64]} />
      <hyperfractalMaterial ref={materialRef} attach="material" />
    </mesh>
  );
}
