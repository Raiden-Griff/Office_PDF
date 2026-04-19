import { useCallback, useState } from 'react'
import heroImg from './assets/hero.png'
import { useDropzone } from 'react-dropzone'
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
  const [file, setFile] = useState<File | undefined>()
  const [state, setState] = useState<'idle' | 'processing' | 'building' | 'done' | 'error'>('idle')
  const [processResult, setProcessResult] = useState<ProcessResult | null>(null)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [expandedPapers, setExpandedPapers] = useState<Set<number>>(new Set())

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) setFile(acceptedFiles[0])
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }
  })

  function toggleExpand(idx: number) {
    setExpandedPapers(prev => {
      const next = new Set(prev)
      next.has(idx) ? next.delete(idx) : next.add(idx)
      return next
    })
  }

  async function handleSubmit(e: React.SyntheticEvent) {
    e.preventDefault()
    if (!file) return

    try {
      setState('processing')
      setProcessResult(null)
      setPdfUrl(null)
      setError(null)
      setExpandedPapers(new Set())

      const formData = new FormData()
      formData.append('file', file)

      const res1 = await fetch('http://localhost:8000/process', {
        method: 'POST',
        body: formData
      })
      if (!res1.ok) throw new Error(await res1.text())
      const data1: ProcessResult = await res1.json()
      setProcessResult(data1)

      setState('building')
      const res2 = await fetch('http://localhost:8000/build', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ papers: data1.papers, groups: data1.groups })
      })
      if (!res2.ok) throw new Error(await res2.text())
      const data2 = await res2.json()
      setPdfUrl(`http://localhost:8000${data2.pdf_url}`)
      setState('done')

    } catch (err: any) {
      setError(err.message)
      setState('error')
    }
  }

  const paperLookup = processResult
    ? Object.fromEntries(processResult.papers.map(p => [p.index, p]))
    : {}

  return (
    <section id="center">
      <div className="hero">
        <img src={heroImg} className="base" width="170" height="179" alt="" />
      </div>

      <h1>Office PDF!</h1>
      <p>Drag and drop your paper below to find and compile related work.</p>

      <div {...getRootProps()} className={`dropzone-box ${isDragActive ? 'dropzone-active' : ''}`}>
        <input {...getInputProps()} />
        <span style={{ fontSize: '2rem', marginBottom: '10px' }}>📁</span>
        {isDragActive ? (
          <p style={{ color: '#2e7d32' }}>Release to drop the PDF</p>
        ) : (
          <p>Drag 'n' drop your <b>PDF</b> here, or click to select</p>
        )}
        {file && (
          <div style={{ marginTop: '15px', color: '#646cff', fontWeight: 'bold' }}>
            Selected: {file.name}
          </div>
        )}
      </div>

      <button
        className="upload-btn"
        onClick={handleSubmit}
        disabled={!file || state === 'processing' || state === 'building'}
      >
        {state === 'processing' ? 'Finding papers...' :
         state === 'building'   ? 'Building PDF...' :
         'Upload PDF'}
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {(processResult || state === 'building' || pdfUrl) && (
        <div className="results-layout">

          <div className="groups-section">
            <h2>Paper Groups</h2>
            <div className="groups-scroll"></div>
            {processResult?.groups.groups.map((group, i) => (
              <div key={i} className="group-card">
                <div className="group-header">
                  <h3>{group.label}</h3>
                  <p className="rationale">{group.rationale}</p>
                </div>
                <div className="papers-list">
                  {group.paper_indices.map(idx => {
                    const paper = paperLookup[idx]
                    const isExpanded = expandedPapers.has(idx)
                    return paper ? (
                      <div key={idx} className="paper-card">
                        <a href={paper.link} target="_blank" rel="noreferrer">{paper.title}</a>
                        <p className="authors">
                          {paper.authors.slice(0, 3).join(', ')}
                          {paper.authors.length > 3 ? ' et al.' : ''} · {paper.published}
                        </p>
                        <p className={`abstract ${isExpanded ? 'expanded' : ''}`}>
                          {paper.abstract}
                        </p>
                        <button className="expand-btn" onClick={() => toggleExpand(idx)}>
                          {isExpanded ? 'Show less ↑' : 'Read more ↓'}
                        </button>
                      </div>
                    ) : null
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="pdf-section">
            <h2>Compiled PDF</h2>
            {pdfUrl ? (
              <>
                <iframe src={pdfUrl} />
                <a href={pdfUrl} download="compiled.pdf">
                  <button className="upload-btn">Download PDF</button>
                </a>
              </>
            ) : (
              <div className="pdf-placeholder">
                {state === 'building' ? 'Building your PDF...' : 'PDF will appear here'}
              </div>
            )}
          </div>

        </div>
      )}
    </section>
  )
}

export default App