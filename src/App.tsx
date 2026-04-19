import { useCallback, useState } from 'react'
import PDFImg from './assets/pdf.png'
import { useDropzone } from 'react-dropzone' 
import { PDFDocument } from 'pdf-lib'
import './App.css'

function App() {
  // --- States ---
  const [files, setFiles] = useState<File[]>([]); 
  const [preview, setPreview] = useState<string | null>(null);
  const [status, setStatus] = useState('');
  const [isMerging, setIsMerging] = useState(false);

  // --- Dropzone Logic ---
  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      // Append new files to the list (Colby's multiple file approach)
      setFiles((prev) => [...prev, ...acceptedFiles]);

      // Preview the first file dropped in this batch
      const reader = new FileReader();
      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ 
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }
  });

  // --- Merge Logic (Creating "PDF C") ---
  const handleMerge = async (e: React.SyntheticEvent) => {
    e.preventDefault();
    if (files.length < 2) return alert("Please add at least 2 PDFs!");

    setIsMerging(true);
    setStatus('Merging documents...');

    try {
      const mergedPdf = await PDFDocument.create();
      
      for (const file of files) {
        const bytes = await file.arrayBuffer();
        const pdf = await PDFDocument.load(bytes);
        const copiedPages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
        copiedPages.forEach((page) => mergedPdf.addPage(page));
      }

      const mergedPdfBytes = await mergedPdf.save();
      const blob = new Blob([mergedPdfBytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      // Creating a download link
      const link = document.createElement('a');
      link.href = url;
      link.download = "merged-office-doc.pdf";
      link.click();

      setStatus('Success! Your merged PDF has downloaded.');
    } catch (error) {
      console.error(error);
      setStatus('Error merging files.');
    } finally {
      setIsMerging(false);
    }
  };

  return (
    <div className="App">
      <section id="center">
        <div className="hero">
          <img src={PDFImg} width="170" alt="PDF Icon" />
        </div>

        <h1>Office PDF!</h1>
        <p>Drop PDF A and PDF B to create PDF C.</p>

        {/* Dropzone Area */}
        <div {...getRootProps()} className={`dropzone-box ${isDragActive ? 'active' : ''}`}>
          <input {...getInputProps()} />
          <span style={{ fontSize: '2rem' }}>📁</span>
          <p>{isDragActive ? "Drop them!" : "Drag 'n' drop your PDFs here"}</p>
        </div>

        {/* File List & Submit */}
        {files.length > 0 && (
          <div className="file-list">
            <h3>Queue ({files.length} files):</h3>
            <ul>
              {files.map((f, i) => <li key={i}>📄 {f.name}</li>)}
            </ul>
            <button onClick={handleMerge} disabled={isMerging} className="merge-btn">
              {isMerging ? 'Processing...' : 'Merge & Download'}
            </button>
            <button onClick={() => {setFiles([]); setPreview(null);}} className="clear-btn">
              Clear
            </button>
          </div>
        )}

        {status && <p className="status-msg">{status}</p>}

        {/* Preview Frame */}
        {preview && (
          <div className="preview-wrap">
            <hr />
            <h3>Latest Upload Preview:</h3>
            <iframe src={preview} width="100%" height="500px" title="Preview" />
          </div>
        )}
      </section>
    </div>
  )
}

export default App;