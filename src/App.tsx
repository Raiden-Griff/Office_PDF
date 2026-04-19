import { useCallback, useState } from 'react'
import PDFImg from './assets/pdf.png'
import { useDropzone } from 'react-dropzone' 
import './App.css'

function App() {
  const [files, setFiles] = useState<File[]>([]);
  const [isMerging, setIsMerging] = useState(false);
  const [status, setStatus] = useState(''); // Added missing state
  const [preview, setPreview] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFiles((prev) => [...prev, ...acceptedFiles]);

      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }
  });

  const handleMerge = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    if (files.length < 2) return alert("Please add at least 2 PDFs!");

    setIsMerging(true);
    setStatus('Uploading and merging on server...');

    const formData = new FormData();
    files.forEach((file) => {
      formData.append('files', file); // 'files' must match Python argument name
    });

    try {
      const response = await fetch('http://localhost:8000/merge-pdfs', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Merge failed');

      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = "merged-office-doc.pdf";
      link.click();

      setStatus('Success! Merged via Python backend.');
    } catch (error) {
      console.error(error);
      setStatus('Error connecting to backend.');
    } finally {
      setIsMerging(false);
    }
  };
  
  return (
    <div className="container">
      <section id="center">
        <div className="hero">
          <img src={PDFImg} className="base" width="170" height="179" alt="PDF Icon" />
        </div>
        <div>
          <h1>Office PDF!</h1>
          <p>Drag and drop your PDFs below:</p>
          
          <div {...getRootProps()} className={`dropzone-box ${isDragActive ? 'active' : ''}`}>
            <input {...getInputProps()} />
            <span style={{ fontSize: '2rem' }}>📁</span>
            {isDragActive ? <p>Drop them!</p> : <p>Drag PDFs here or click</p>}
          </div>

          <div className="file-list">
            {files.map((f, i) => (
              <div key={i} className="file-item">📄 {f.name}</div>
            ))}
          </div>

          <button 
            onClick={handleMerge} 
            disabled={isMerging || files.length < 2}
            style={{ marginTop: '20px', padding: '10px 20px', cursor: 'pointer' }}
          >
            {isMerging ? 'Merging...' : 'Merge All PDFs'}
          </button>
          
          <p>{status}</p>
        </div>
      </section>

      {preview && (
        <div className="preview-section">
          <h2>Preview (First PDF):</h2>
          <iframe src={preview} width="100%" height="500px" title="Preview" />
        </div>
      )}
    </div>
  )
}

export default App;