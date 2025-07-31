// /src/components/ConnectionLine.jsx
import React, { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Line } from '@react-three/drei';

/**
 * A component that draws a line between two moving objects in the scene.
 * It finds the objects by name on every frame to ensure the connection is live.
 */
export const ConnectionLine = ({ startGlyphName, endGlyphName }) => {
  const lineRef = useRef();

  useFrame(({ scene }) => {
    if (!lineRef.current) return;

    // Find the live 3D objects in the scene by their unique names
    const startObj = scene.getObjectByName(startGlyphName);
    const endObj = scene.getObjectByName(endGlyphName);

    // If both objects are found, update the line's geometry
    if (startObj && endObj) {
      lineRef.current.visible = true;
      const positions = lineRef.current.geometry.attributes.position.array;
      
      const startPos = startObj.position;
      const endPos = endObj.position;
      
      positions[0] = startPos.x;
      positions[1] = startPos.y;
      positions[2] = startPos.z;
      positions[3] = endPos.x;
      positions[4] = endPos.y;
      positions[5] = endPos.z;
      
      lineRef.current.geometry.attributes.position.needsUpdate = true;
      lineRef.current.geometry.computeBoundingSphere();
    } else {
        // Hide the line if one of the glyphs can't be found yet
        lineRef.current.visible = false;
    }
  });

  // Initialize the line with placeholder points.
  return <Line ref={lineRef} points={[[0,0,0], [0,0,0]]} color="#FFD700" lineWidth={2} />;
};
