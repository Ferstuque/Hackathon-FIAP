import React, { useState, useEffect, useRef } from 'react';
import { AIAnalysisReport } from './AIAnalysisReport';
import { DatabaseLogs } from './DatabaseLogs';
import { ProcessingStatus } from './ProcessingStatus';

const API_BASE_URL = 'http://localhost:8000/api/v1';

function App() {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'processing' | 'done' | 'error' | 'human_review'>('idle');
  const [analysisId, setAnalysisId] = useState<string | null>(null);
  const [report, setReport] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'visual' | 'json' | 'logs' | 'status'>('visual');
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Efeito para fazer Polling quando estiver em processamento
  useEffect(() => {
    let intervalId: number;

    if (status === 'processing' && analysisId) {
      intervalId = window.setInterval(async () => {
        try {
          const res = await fetch(`${API_BASE_URL}/status/${analysisId}`);
          if (res.ok) {
            const data = await res.json();
            if (data.status === 'ANALISADO') {
              setStatus('done');
              fetchReport(analysisId);
            } else if (data.status === 'AGUARDANDO_REVISAO_HUMANA') {
              setStatus('human_review');
            } else if (data.status === 'ERRO') {
              setStatus('error');
              setErrorMessage('A IA falhou ao processar a imagem.');
            }
          }
        } catch (e) {
          console.error("Erro no polling", e);
        }
      }, 5000); // Consulta a cada 5 segundos
    }

    return () => clearInterval(intervalId);
  }, [status, analysisId]);

  const fetchReport = async (id: string) => {
    try {
      const res = await fetch(`${API_BASE_URL}/report/${id}`);
      if (res.ok) {
        const data = await res.json();
        setReport(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      await handleUpload(e.target.files[0]);
    }
  };

  const handleUpload = async (file: File) => {
    setStatus('uploading');
    setErrorMessage(null);
    setReport(null);
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) throw new Error('Falha no upload');
      
      const data = await res.json();
      setAnalysisId(data.id);
      setStatus('processing');
    } catch (error) {
      console.error(error);
      setStatus('error');
      setErrorMessage('Não foi possível se conectar à API. A stack do Docker está rodando?');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <header className="mb-10 text-center">
        <h1 className="text-4xl font-extrabold mb-4 text-purple-200 tracking-tight">FIAP Secure Systems</h1>
        <p className="text-xl text-purple-300">Análise Automatizada de Diagramas de Arquitetura</p>
      </header>
      
      <main className="w-full max-w-4xl bg-black/40 backdrop-blur-xl rounded-2xl p-8 shadow-2xl border border-white/10">
        
        {status === 'idle' && (
          <div 
            onClick={() => fileInputRef.current?.click()}
            className="flex flex-col items-center justify-center border-2 border-dashed border-purple-400 rounded-xl p-16 bg-purple-900/20 hover:bg-purple-900/40 transition-all cursor-pointer group"
          >
            <input 
              type="file" 
              className="hidden" 
              ref={fileInputRef} 
              onChange={handleFileChange}
              accept="image/png, image/jpeg, application/pdf"
            />
            <svg className="w-20 h-20 text-purple-300 mb-6 group-hover:scale-110 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <p className="text-2xl font-medium text-white mb-2">Arraste seu diagrama aqui</p>
            <p className="text-md text-purple-300">ou clique para selecionar (PNG, JPG, PDF)</p>
          </div>
        )}

        {status === 'uploading' && (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-300 mx-auto mb-6"></div>
            <h2 className="text-2xl font-semibold text-white">Enviando diagrama para o Servidor...</h2>
          </div>
        )}

        {status === 'processing' && (
          <div className="text-center py-20 space-y-4">
            <div className="flex justify-center mb-8">
              <div className="relative w-24 h-24">
                <div className="absolute inset-0 bg-purple-500 rounded-full animate-ping opacity-20"></div>
                <div className="absolute inset-2 bg-purple-400 rounded-full animate-pulse opacity-40"></div>
                <div className="absolute inset-4 bg-purple-300 rounded-full flex items-center justify-center shadow-[0_0_15px_rgba(216,180,254,1)]">
                   <span className="text-purple-900 font-bold">IA</span>
                </div>
              </div>
            </div>
            <h2 className="text-3xl font-semibold text-white">O Modelo de IA está "Pensando"...</h2>
            <p className="text-purple-300 text-lg">Acionando Azure Storage Queues e Agentes Gemini (SOAT + IADT)</p>
            <p className="text-sm font-mono text-purple-400 mt-4">Process ID: {analysisId}</p>
          </div>
        )}

        {status === 'error' && (
          <div className="text-center py-16">
            <svg className="w-20 h-20 text-red-400 mx-auto mb-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h2 className="text-2xl font-bold text-red-300 mb-4">{errorMessage}</h2>
            <button 
              onClick={() => setStatus('idle')}
              className="px-6 py-3 bg-purple-600 hover:bg-purple-500 text-white rounded-lg font-medium transition-colors"
            >
              Tentar Novamente
            </button>
          </div>
        )}

        {status === 'human_review' && (
          <div className="text-center py-16">
            <div className="flex justify-center mb-6">
              <svg className="w-20 h-20 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h2 className="text-3xl font-bold text-orange-300 mb-4">Revisão Manual Necessária (HITL)</h2>
            <p className="text-lg text-orange-200 mb-8 max-w-2xl mx-auto">
              O Árbitro Autônomo da IA (LLM-as-a-Judge) encontrou risco severo de alucinação ou complexidade não tratável na topologia do diagrama. Por segurança, o processo foi suspenso para intervenção humana ("Human-in-the-Loop"). Um Arquiteto de Software foi notificado e aprovará as inconsistências.
            </p>
            <button 
              onClick={() => setStatus('idle')}
              className="px-6 py-3 bg-orange-600 hover:bg-orange-500 text-white rounded-lg font-medium transition-colors"
            >
              Processar Outro Diagrama
            </button>
          </div>
        )}

        {status === 'done' && report && (
          <div className="animate-fade-in">
            <div className="flex flex-col sm:flex-row items-center justify-between mb-8 pb-4 border-b border-purple-500/30">
              <h2 className="text-2xl font-bold text-green-300 flex items-center mb-4 sm:mb-0">
                <svg className="w-8 h-8 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Análise Concluída
              </h2>
              <button 
                onClick={() => setStatus('idle')}
                className="px-4 py-2 border border-purple-400 text-purple-300 hover:bg-purple-400 hover:text-purple-900 rounded-md transition-colors text-sm font-medium"
              >
                Analisar Outro Diagrama
              </button>
            </div>

            {/* TAB NAVIGATION */}
            <div className="flex space-x-2 border-b border-slate-700/50 mb-6 overflow-x-auto whitespace-nowrap scrollbar-hide">
              <button 
                onClick={() => setActiveTab('visual')}
                className={`py-2 px-4 font-semibold text-sm transition-colors border-b-2 ${activeTab === 'visual' ? 'border-emerald-400 text-emerald-300 bg-emerald-900/10' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
              >
                📊 Relatório Visual
              </button>
              <button 
                onClick={() => setActiveTab('status')}
                className={`py-2 px-4 font-semibold text-sm transition-colors border-b-2 ${activeTab === 'status' ? 'border-indigo-400 text-indigo-300 bg-indigo-900/10' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
              >
                ⚙️ Status de Processamento
              </button>
              <button 
                onClick={() => setActiveTab('json')}
                className={`py-2 px-4 font-semibold text-sm transition-colors border-b-2 ${activeTab === 'json' ? 'border-purple-400 text-purple-300 bg-purple-900/10' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
              >
                {`{_}`} Raw JSON
              </button>
              <button 
                onClick={() => setActiveTab('logs')}
                className={`py-2 px-4 font-semibold text-sm transition-colors border-b-2 ${activeTab === 'logs' ? 'border-blue-400 text-blue-300 bg-blue-900/10' : 'border-transparent text-slate-400 hover:text-slate-200'}`}
              >
                🗄️ Log de Processamento
              </button>
            </div>
            
            {/* TAB CONTENT */}
            {activeTab === 'visual' && (
              <AIAnalysisReport reportData={report} />
            )}

            {activeTab === 'status' && (
              <ProcessingStatus currentAnalysisId={analysisId} />
            )}

            {activeTab === 'json' && (
              <div className="bg-black/50 p-6 rounded-xl border border-white/5 overflow-x-auto shadow-inner text-left">
                <pre className="text-purple-100 font-mono text-sm leading-relaxed whitespace-pre-wrap">
                  {JSON.stringify(report, null, 2)}
                </pre>
              </div>
            )}

            {activeTab === 'logs' && (
              <DatabaseLogs currentAnalysisId={analysisId} />
            )}
          </div>
        )}

      </main>
    </div>
  );
}

export default App;
