import { useCallback, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import { useDropzone } from 'react-dropzone' // Fixed lowercase 'z'
import './App.css'

function App() {
  const [state, setState] = useState('');
  const [file, setFile] = useState<File | undefined>();
  const [preview, setPreview] = useState<string | ArrayBuffer | null>(null); // Fixed null type
  const [uploadedPath, setUploadedPath] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles && acceptedFiles.length > 0) {
      const selectedFile = acceptedFiles[0];
      setFile(selectedFile);

      const reader = new FileReader();
      reader.onload = function () {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  }, [])

  // Fixed hook name to useDropzone
  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: { 'application/pdf': ['.pdf'] } // Optional: force PDF only
  })

  async function handleOnSubmit(e: React.SyntheticEvent) {
    e.preventDefault();
    if (typeof file === 'undefined') return;

    const formData = new FormData();
    formData.append('pdf', file);

    setState('Submitting...');
    const res = await fetch('http://localhost:8000/upload', {
      method: 'POST',
      body: formData
    });
    const data = await res.json();
    setUploadedPath(data.path); // SAVE THE PATH HERE
    setState('Submitted!');
  }

  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={heroImg} className="base" width="170" height="179" alt="" />
          <img src={reactLogo} className="framework" alt="React logo" />
          <img src={viteLogo} className="vite" alt="Vite logo" />
        </div>
        <div>
          <h1>Office PDF!</h1>
          <p>
            Please drag and drop your pdf's into the correct spaces below:
          </p>
       <div 
  {...getRootProps()} 
  className={`dropzone-box ${isDragActive ? 'dropzone-active' : ''}`}
>
  <input {...getInputProps()} />
  
  {/* Add a little emoji or icon to make it obvious! */}
  <span style={{ fontSize: '2rem', marginBottom: '10px' }}>📁</span>
  
  {isDragActive ? (
    <p style={{ color: '#2e7d32' }}>Release to drop the PDF</p>
  ) : (
    <p>Drag 'n' drop your <b>PDF</b> here, or click to select</p>
  )}

  {/* This shows the file name ONLY after you pick one */}
  {file && (
    <div style={{ marginTop: '15px', color: '#646cff', fontWeight: 'bold' }}>
      Selected: {file.name}
    </div>
  )}
</div>
    <button 
      className="upload-btn"
      onClick={handleOnSubmit} 
      disabled={!file || state === 'Submitting...'}
    >
      Upload PDF
    </button>
        </div>

      <div>
        {state && <p className="status-text">{state}</p>}
      </div>
          </section>

    </>
  )
}

export default App
