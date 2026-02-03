import React from 'react';

const AnnotationLayer = ({ dimensions, scale = 1 }) => {
  if (!dimensions) return null;

  return (
    <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', pointerEvents: 'none' }}>
      {dimensions.map((dim, idx) => {
        if (!dim.bbox) return null;
        
        // dim.bbox = [x1, y1, x2, y2]
        // We want to place the bubble roughly at the top-left or center of the bbox
        const [x1, y1, x2, y2] = dim.bbox;
        
        // Simple positioning logic: Place bubble at top-left corner of the bbox
        // Depending on scale, we might need to multiply x1, y1 by scale.
        // Assuming bbox is in image coordinates and parent container matches image size exactly for now.
        // If image is scaled via CSS (max-width: 100%), we need robust scaling logic in parent. 
        // For POC, we rely on parent ensuring coordinate space alignment.
        
        const bubbleSize = 24; 
        
        // Adjust position slightly so it doesn't obscure the text too much, or places it near
        const left = x1 * scale - (bubbleSize / 2);
        const top = y1 * scale - (bubbleSize / 2);

        return (
          <div
            key={idx}
            style={{
              position: 'absolute',
              left: `${left}px`,
              top: `${top}px`,
              width: `${bubbleSize}px`,
              height: `${bubbleSize}px`,
              backgroundColor: '#eb3b5a',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              fontSize: '11px',
              fontWeight: 'bold',
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
              zIndex: 10
            }}
          >
            {idx + 1}
          </div>
        );
      })}
    </div>
  );
};

export default AnnotationLayer;
