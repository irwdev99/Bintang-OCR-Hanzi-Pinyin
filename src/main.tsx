import {StrictMode} from 'react';
import {createRoot} from 'react-dom/client';
import './index.css';

// Simply injecting the HTML from /web/index.html to give a preview in the browser environment
const HTML_CONTENT = `
  <div id="loading-screen" class="fixed inset-0 bg-[#0a0a0b] flex flex-col items-center justify-center z-[9999] transition-opacity duration-500">
    <svg viewBox="0 0 24 24" fill="none" stroke="#00f3ff" stroke-width="1.5" style="width: 100px; filter: drop-shadow(0 0 10px #00f3ff); margin-bottom: 24px;">
      <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
    </svg>
    <h1 style="color: white; font-size: 2rem; font-family: sans-serif; margin-bottom: 8px;">Bintang OCR Hanzi Pinyin</h1>
    <p style="color: #64748b; font-size: 1rem; font-family: monospace;">made by irwan (irw.dev99@gmail.com)</p>
  </div>

  <div class="flex flex-col h-screen w-full bg-[#0a0a0b] text-slate-300 font-sans overflow-hidden hidden" id="app-container">
    <header class="h-16 border-b border-white/10 flex items-center justify-between px-6 bg-[#0d0d0f]">
      <div class="flex items-center gap-3">
        <div class="p-1.5 rounded bg-cyan-500/10 border border-cyan-500/30">
          <svg viewBox="0 0 24 24" fill="none" stroke="#00f3ff" stroke-width="2" class="w-6 h-6" style="filter: drop-shadow(0 0 5px #00f3ff);">
            <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
          </svg>
        </div>
        <div>
          <h1 class="text-lg font-bold tracking-tight text-white uppercase">Bintang OCR <span class="text-cyan-400">Hanzi Pinyin</span></h1>
          <p class="text-[10px] text-slate-500 uppercase tracking-widest font-medium">Enterprise Grade v3.2 • Template Preview</p>
        </div>
      </div>
    </header>
    <main class="flex flex-1 overflow-hidden p-8 items-center justify-center bg-[#0a0a0b]">
        <div class="max-w-2xl text-center space-y-4 bg-white/5 p-8 rounded-xl border border-white/10 shadow-2xl relative overflow-hidden">
                <div class="absolute top-4 left-4 w-4 h-4 border-t border-l border-cyan-500/50"></div>
                <div class="absolute top-4 right-4 w-4 h-4 border-t border-r border-cyan-500/50"></div>
                <div class="absolute bottom-4 left-4 w-4 h-4 border-b border-l border-cyan-500/50"></div>
                <div class="absolute bottom-4 right-4 w-4 h-4 border-b border-r border-cyan-500/50"></div>
            
            <svg viewBox="0 0 24 24" fill="none" stroke="#00f3ff" stroke-width="1.5" class="w-16 h-16 mx-auto opacity-80 mb-6 drop-shadow-[0_0_15px_rgba(0,243,255,0.6)]">
                <path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/>
            </svg>
            <h2 class="text-2xl font-bold text-white tracking-widest uppercase">Project Ready for Download</h2>
            <p class="text-slate-400 font-mono text-sm">The <strong>web/index.html</strong> (Frontend) and <strong>main.py</strong> (Eel Backend) files have been successfully updated with Authentication, API Key Settings, and History Advanced Filters.</p>
            <div class="p-4 bg-black/40 text-left rounded-lg text-xs font-mono text-cyan-400/80 border border-cyan-900/40 mt-4 leading-loose overflow-x-auto">
                <div class="text-white mb-2 font-bold uppercase tracking-widest border-b border-white/10 pb-2">Compile Instructions (PyInstaller)</div>
                pip install -r requirements.txt<br/>
                pyinstaller --onefile --noconsole --icon=icon.ico --hidden-import fitz --hidden-import pymupdf --name "Bintang OCR Hanzi Pinyin" main.py
            </div>
            
            <p class="text-xs text-slate-500 mt-8">Please check the project settings to export or download the ZIP.</p>
        </div>
    </main>
  </div>
`;

function AppPreview() {
  return <div dangerouslySetInnerHTML={{ __html: HTML_CONTENT }} className="w-full h-full" />;
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppPreview />
  </StrictMode>
);

setTimeout(() => {
    const loadingScreen = document.getElementById('loading-screen');
    const appContainer = document.getElementById('app-container');
    if (loadingScreen && appContainer) {
        loadingScreen.style.opacity = '0';
        setTimeout(() => {
            loadingScreen.style.display = 'none';
            appContainer.classList.remove('hidden');
        }, 500);
    }
}, 3000);

