import React, { useState } from 'react';
import axios from 'axios';

const Upload = ({ onUploadSuccess }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setError(null);
    setLoading(true);
    
    const formData = new FormData();
    formData.append("file", file);

    try {
      const previewUrl = URL.createObjectURL(file);
      const response = await axios.post("http://localhost:8000/extract/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      
      // Use backend provided URL if available (important for PDFs -> PNGs), otherwise fallback to local preview
      const finalImageSrc = response.data.processed_image_url 
          ? `http://localhost:8000${response.data.processed_image_url}` 
          : previewUrl;
          
      onUploadSuccess(response.data, finalImageSrc);
    } catch (err) {
      console.error(err);
      setError("Analysis failed. Backend might be offline.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      height: '100%',
      backgroundColor: '#f8f9fa',
      fontFamily: '"Segoe UI", sans-serif'
    }}>
      <div style={{
        background: 'white',
        padding: '50px',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.05)',
        textAlign: 'center',
        width: '500px'
      }}>
        <h1 style={{ fontWeight: '800', margin: '0 0 10px', fontSize: '32px', letterSpacing: '-1px' }}>WERK<span style={{color: '#5d5fef'}}>24</span></h1>
        
        <div style={{ margin: '30px 0 20px', border: '2px dashed #e0e0e0', padding: '40px', borderRadius: '8px' }}>
             <p style={{ color: '#666', marginBottom: '20px' }}>Drag & drop your engineering drawing here<br/>or</p>
             <label htmlFor="file-upload" style={{
                backgroundColor: '#5d5fef',
                color: 'white',
                padding: '12px 24px',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: '600',
                display: 'inline-block',
                transition: 'background 0.2s'
             }}>
                {loading ? "Analyzing..." : "Upload your own"}
             </label>
             <input 
                id="file-upload" 
                type="file" 
                onChange={handleFileChange} 
                accept="image/*,application/pdf" 
                style={{ display: 'none' }} 
                disabled={loading}
             />
        </div>
        
        {error && <p style={{ color: '#e74c3c', fontSize: '14px', marginTop: '10px' }}>{error}</p>}
      </div>
    </div>
  );
};

export default Upload;
