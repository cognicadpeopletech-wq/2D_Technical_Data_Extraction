import { useState } from 'react'
import Upload from './pages/Upload'
import Viewer from './components/Viewer'
import './App.css'

function App() {
  const [data, setData] = useState(null)
  const [imageSrc, setImageSrc] = useState(null)

  const handleSuccess = (resultData, previewUrl) => {
    setData(resultData)
    setImageSrc(previewUrl)
  }

  const handleReset = () => {
    setData(null)
    setImageSrc(null)
  }

  return (
    <div className="App" style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <header style={{ 
        height: '60px', 
        backgroundColor: '#fff', 
        borderBottom: '1px solid #e0e0e0', 
        display: 'flex', 
        alignItems: 'center', 
        padding: '0 20px',
        justifyContent: 'space-between',
        zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '40px' }}>
          {/* Logo Area */}
          <div style={{ fontSize: '24px', fontWeight: '800', letterSpacing: '-1px' }}>
            WERK<span style={{color: '#5d5fef'}}>24</span>
          </div>

          {/* Nav Tabs (Mock) */}
          <nav style={{ display: 'flex', gap: '20px' }}>
             <span style={{ fontSize: '14px', color: '#666', cursor: 'pointer', borderBottom: '2px solid transparent', paddingBottom: '18px', paddingTop: '18px' }}>Example 1: Turning</span>
             <span style={{ fontSize: '14px', color: '#666', cursor: 'pointer' }}>Example 2: Milling</span>
          </nav>
        </div>

        {/* Action Button */}
        <div>
           <button 
             onClick={handleReset}
             style={{
               backgroundColor: '#5d5fef',
               color: 'white',
               border: 'none',
               padding: '8px 16px',
               borderRadius: '4px',
               fontWeight: '600',
               fontSize: '13px',
               cursor: 'pointer'
             }}
           >
             Upload your own
           </button>
        </div>
      </header>
      
      {/* Main Content */}
      <main style={{ flex: 1, overflow: 'hidden' }}>
        {!data ? (
           <Upload onUploadSuccess={handleSuccess} />
        ) : (
           <Viewer data={data} imageSrc={imageSrc} />
        )}
      </main>
    </div>
  )
}

export default App
