import React, { useState } from 'react';

const Sidebar = ({ data }) => {
  const [activeTab, setActiveTab] = useState('features');

  const tabs = [
    { id: 'metadata', label: 'Meta Data' },
    { id: 'features', label: 'Features' },
    { id: 'redaction', label: 'Redaction' },
  ];

  return (
    <div style={{ 
      width: '350px', 
      borderLeft: '1px solid #e0e0e0', 
      display: 'flex', 
      flexDirection: 'column', 
      backgroundColor: '#fff',
      height: '100%',
      fontFamily: '"Segoe UI", Roboto, Helvetica, Arial, sans-serif'
    }}>
      {/* Tabs Header */}
      <div style={{ display: 'flex', borderBottom: '1px solid #e0e0e0' }}>
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              flex: 1,
              padding: '12px 0',
              border: 'none',
              background: 'none',
              borderBottom: activeTab === tab.id ? '2px solid #5d5fef' : 'none',
              color: activeTab === tab.id ? '#5d5fef' : '#666',
              fontWeight: activeTab === tab.id ? '600' : '400',
              cursor: 'pointer',
              fontSize: '14px'
            }}
          >
             {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px' }}>
        
        {activeTab === 'metadata' && (
          <div>
            <h3 style={{ fontSize: '14px', color: '#5d5fef', marginBottom: '10px' }}>Identification & Documentation</h3>
            <div style={{ marginBottom: '20px' }}>
               <label style={{ display: 'block', fontSize: '11px', color: '#999' }}>Designation</label>
               <div style={{ fontWeight: '500', fontSize: '14px' }}>{data.part_name || "N/A"}</div>
            </div>

            <h3 style={{ fontSize: '14px', color: '#5d5fef', marginBottom: '10px' }}>Material & Manufacturing</h3>
            <div style={{ marginBottom: '20px' }}>
               <label style={{ display: 'block', fontSize: '11px', color: '#999' }}>Material</label>
               <div style={{ fontWeight: '500', fontSize: '14px' }}>{data.material || "N/A"}</div>
            </div>
             <div style={{ marginBottom: '20px' }}>
               <label style={{ display: 'block', fontSize: '11px', color: '#999' }}>Original File</label>
               <div style={{ fontWeight: '500', fontSize: '14px' }}>{data.original_file || "N/A"}</div>
            </div>
          </div>
        )}

        {activeTab === 'features' && (
            <div>
                 {(() => {
                    if (!data.dimensions || data.dimensions.length === 0) {
                        return <p style={{color: '#999', fontSize: '13px'}}>No dimensions detected.</p>;
                    }

                    // Group by type
                    const groups = data.dimensions.reduce((acc, dim, idx) => {
                        const type = dim.type || 'other';
                        if (!acc[type]) acc[type] = [];
                        acc[type].push({ ...dim, originalIndex: idx });
                        return acc;
                    }, {});

                    return Object.keys(groups).map(type => (
                        <div key={type} style={{ marginBottom: '20px' }}>
                            <h3 style={{ 
                                fontSize: '13px', 
                                color: '#666', 
                                textTransform: 'uppercase', 
                                letterSpacing: '0.5px', 
                                borderBottom: '1px solid #eee',
                                paddingBottom: '4px',
                                marginBottom: '12px'
                            }}>
                                {type === 'linear' ? 'Linear Dimensions' : 
                                 type === 'diameter' ? 'Bores / Diameters' :
                                 type === 'radius' ? 'Radii' : 
                                 type === 'chamfer' ? 'Chamfers' : type}
                            </h3>
                            <ul style={{ listStyle: 'none', padding: 0 }}>
                                {groups[type].map((dim) => (
                                    <li key={dim.originalIndex} style={{ display: 'flex', alignItems: 'center', marginBottom: '12px' }}>
                                        {/* Red Bubble ID */}
                                        <div style={{
                                            width: '24px',
                                            height: '24px',
                                            borderRadius: '50%',
                                            backgroundColor: '#eb3b5a', 
                                            color: 'white',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontSize: '12px',
                                            fontWeight: 'bold',
                                            marginRight: '12px',
                                            flexShrink: 0
                                        }}>
                                            {dim.originalIndex + 1}
                                        </div>
                                        
                                        {/* Value */}
                                        <div style={{ flex: 1 }}>
                                            <div style={{ fontSize: '15px', color: '#333', fontWeight: '500' }}>
                                                {dim.type === 'diameter' ? '⌀' : (dim.type === 'radius' ? 'R' : '')} {dim.value}
                                            </div>
                                            <div style={{ fontSize: '12px', color: '#888' }}>
                                                {dim.tolerance ? dim.tolerance : 'General Tol.'}
                                            </div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ));
                 })()}
            </div>
        )}

        {activeTab === 'redaction' && (
            <div style={{ textAlign: 'center', color: '#999', marginTop: '40px' }}>
                <p>No redacted areas.</p>
            </div>
        )}

      </div>
    </div>
  );
};

export default Sidebar;
