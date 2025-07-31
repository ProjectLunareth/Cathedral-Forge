// /src/components/RitualCanvas.jsx
import React, { Suspense, useState, useRef, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, Text, DragControls } from '@react-three/drei';
import { RitualVisualizer } from './RitualVisualizer';

const FallbackText = () => (
  <Text color="white" anchorX="center" anchorY="middle" fontSize={0.5}>
    Compile a Ritual to Begin...
  </Text>
);

export const RitualCanvas = ({ layout, onGlyphInteraction, onGlyphDrag, isCtrlPressed }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [draggableObjects, setDraggableObjects] = useState([]);
  const visualizerRef = useRef();
  const activeObject = useRef();

  useEffect(() => {
    if (visualizerRef.current) {
      setDraggableObjects(visualizerRef.current.children.filter(c => c.isMesh));
    }
  }, [layout]);

  const handleDragStart = (event) => {
    setIsDragging(true);
    activeObject.current = event.object;
  };

  const handleDragEnd = () => {
    setIsDragging(false);
    if (activeObject.current) {
      const object = activeObject.current;
      onGlyphDrag(object.name, [object.position.x, object.position.y, object.position.z]);
    }
  };

  return (
    <Canvas camera={{ position: [0, 0, 15], fov: 75 }}>
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={1.5} />
      <DragControls objects={draggableObjects} onDragStart={handleDragStart} onDragEnd={handleDragEnd} />
      <Suspense fallback={null}>
        {layout && layout.steps && layout.steps.length > 0 ? (
          <RitualVisualizer 
            ref={visualizerRef}
            layout={layout} 
            onGlyphInteraction={onGlyphInteraction}
          />
        ) : (
          <FallbackText />
        )}
      </Suspense>
      <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade />
      <OrbitControls enabled={!isDragging && !isCtrlPressed} />
    </Canvas>
  );
};
