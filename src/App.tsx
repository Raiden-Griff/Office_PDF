import { useCallback, useState } from 'react'
import PDFImg from './assets/pdf.png'
import { useDropzone } from 'react-dropzone' // Fixed lowercase 'z'
import { PDFDocument } from 'pdf-lib'
import './App.css'

type Paper = {
  index: number
  title: string
  abstract: string
  authors: string[]
  published: string
  link: string
  pdf_link: string
}

type Group = {
  label: string
  rationale: string
  paper_indices: number[]
}

type ProcessResult = {
  meaning: object
  papers: Paper[]
  groups: { groups: Group[], reading_order: number[] }
}

function App() {
  const [state, setState] = useState('');
  const [files, setFiles] = useState<File[]>([]);
  const [isMerging, setIsMerging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null); // Fixed null type

const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
     setFiles((prev) => [...prev, ...acceptedFiles]); // Append new files to existing state

      const reader = new FileReader();

      reader.onload = () => setPreview(reader.result as string);
      reader.readAsDataURL(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] } // Optional: force PDF only
  });

  const handleMerge = async () => {
    if (files.length < 2) return alert("Please upload at least 2 PDFs to merge!");

    setIsMerging(true);
    setStatus('Merging...');
    
    try {
      const mergedPdf = await PDFDocument.create();
      
      for (const f of files) {
        const bytes = await f.arrayBuffer();
        const pdf = await PDFDocument.load(bytes);
        const pages = await mergedPdf.copyPages(pdf, pdf.getPageIndices());
        pages.forEach((page) => mergedPdf.addPage(page));
      }

      const mergedBytes = await mergedPdf.save();
      const blob = new Blob([mergedBytes], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = "Merged_Office_Doc.pdf";
      link.click();
      
      setStatus('Success! Merged PDF downloaded.');
    } catch (err) {
      console.error(err);
      setStatus('Error merging files.');
    } finally {
      setIsMerging(false);
    }
  };
  
  return (
    <>
      <section id="center">
        <div className="hero">
          <img src={PDFImg} className="base" width="170" height="179" alt="" />
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
        </div>
      </section>

      <div>
        {state === 'Submitting...' && <h1>Submitting...</h1>}
        {state === 'Submitted!' && <h1>Submitted!</h1>}
      </div>
      {
        preview && (
          <div style={{ marginTop: '20px' }}>
            <h2>PDF Preview:</h2>
            <iframe 
              src={preview as string}
              title="PDF Preview"
              width="100%"
              height="500px"
              style={{ border: '1px solid #ccc' }}
            />
          </div>
        )
      }
    </>
  )
}

export default App