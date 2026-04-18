import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import heroImg from './assets/hero.png'
import './App.css'

function App() {
  const [state, setState] = useState('');
  const [file, setFile] = useState<File | undefined>();

  async function handleOnSubmit(e: React.SyntheticEvent) {
    e.preventDefault();
    if( typeof file === 'undefined' ) return;

    console.log('file', file)
    const formData = new FormData();
    formData.append('file', file);

    setState('Submitting...');
    await new Promise((resolve) => setTimeout(resolve, 2000));
    setState('Submitted!');
  }

  function handleOnFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target as HTMLInputElement & {
      files: FileList;
    };
    setFile(files.files[0]);
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
        </div>
        <form onSubmit={handleOnSubmit}>
          <input type="file" name="pdf" onChange={handleOnFileChange} multiple />
          <button type="submit"> Submit </button>
        </form>
      </section>

      <div>
        {state === 'Submitting...' && <h1>Submitting...</h1>}
        {state === 'Submitted!' && <h1>Submitted!</h1>}
      </div>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#documentation-icon"></use>
          </svg>
          <h2>Documentation</h2>
          <p>Your questions, answered</p>
          <ul>
            <li>
              <a href="https://vite.dev/" target="_blank">
                <img className="logo" src={viteLogo} alt="" />
                Explore Vite
              </a>
            </li>
            <li>
              <a href="https://react.dev/" target="_blank">
                <img className="button-icon" src={reactLogo} alt="" />
                Learn more
              </a>
            </li>
          </ul>
        </div>
        <div id="social">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#social-icon"></use>
          </svg>
          <h2>Connect with us</h2>
          <p>Join the Vite community</p>
          <ul>
            <li>
              <a href="https://chat.vite.dev/" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#discord-icon"></use>
                </svg>
                Discord
              </a>
            </li>
            <li>
              <a href="https://x.com/vite_js" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#x-icon"></use>
                </svg>
                X.com
              </a>
            </li>
            <li>
              <a href="https://bsky.app/profile/vite.dev" target="_blank">
                <svg
                  className="button-icon"
                  role="presentation"
                  aria-hidden="true"
                >
                  <use href="/icons.svg#bluesky-icon"></use>
                </svg>
                Bluesky
              </a>
            </li>
          </ul>
        </div>
      </section>
      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  )
}

export default App
