import React, { useState, useRef, useEffect } from 'react';
import Sidebar from './Sidebar';
import AnnotationLayer from './AnnotationLayer';

const Viewer = ({ data, imageSrc }) => {
  const [scale, setScale] = useState(1);
  const imgRef = useRef(null);
  const containerRef = useRef(null);

  // Simple resize handler to keep annotations aligned
  // For POC, we re-calculate scale when image loads or window resizes
  const updateScale = () => {
    if (imgRef.current) {
        // Assuming the bbox coordinates are roughly 1:1 with natural image size
        // If the backend returns normalized coords (0-1), logic changes. 
        // Assuming pixel coords here based on YOLO output.
        
        const currentWidth = imgRef.current.width;
        const naturalWidth = imgRef.current.naturalWidth;
        
        if (naturalWidth > 0) {
            setScale(currentWidth / naturalWidth);
        }
    }
  };

  useEffect(() => {
    window.addEventListener('resize', updateScale);
    return () => window.removeEventListener('resize', updateScale);
  }, []);

  return (
    <div style={{ display: 'flex', flex: 1, overflow: 'hidden', height: 'calc(100vh - 60px)' }}> {/* Subtract header height */}
      
      {/* Left: Canvas / Image Area */}
      <div 
        ref={containerRef}
        style={{ 
          flex: 1, 
          backgroundColor: '#f5f5f5', 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center', 
          position: 'relative',
          overflow: 'auto',
          padding: '20px'
        }}
      >
        <div style={{ position: 'relative', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', background: 'white' }}>
            <img 
                ref={imgRef}
                src={imageSrc} 
                alt="Drawing" 
                onLoad={updateScale}
                style={{ maxWidth: '100%', maxHeight: '85vh', display: 'block' }} 
            />
            <AnnotationLayer dimensions={data.dimensions} scale={scale} />
        </div>
      </div>

      {/* Right: Sidebar */}
      <Sidebar data={data} />
      
    </div>
  );
};

export default Viewer;
