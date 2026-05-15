import React, { useEffect, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const ProcessingStatus = ({ currentAnalysisId }: { currentAnalysisId: string | null }) => {
  const [processData, setProcessData] = useState<any>(null);

  useEffect(() => {
    if (!currentAnalysisId) return;
    
    // Fetch directly from the gateway to get the real status on DB
    const fetchStatus = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/status/${currentAnalysisId}`);
        if (res.ok) {
          const data = await res.json();
          setProcessData(data); // Ex: RECEBIDO, PROCESSANDO, ANALISADO, ERRO, além de filename, created_at
        }
      } catch(e) {
        console.error(e);
      }
    };
    
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [currentAnalysisId]);

  const dbStatus = processData?.status;

  const steps = [
    { key: 'RECEBIDO', label: 'Recebido', desc: 'Diagrama enviado e aguardando processamento na fila' },
    { key: 'PROCESSANDO', label: 'Em processamento', desc: 'IA analisando imagem e extraindo componentes' },
    { key: 'ANALISADO', label: 'Analisado', desc: 'Relatório estruturado gerado com sucesso' },
    { key: 'ERRO', label: 'Erro', desc: 'Houve uma falha na análise do diagrama', isError: true }
  ];

  // Helper to determine step states based on dbStatus
  const getStepState = (stepKey: string) => {
    if (!dbStatus) return 'pending';
    if (dbStatus === 'ERRO') {
      return stepKey === 'ERRO' ? 'current' : 'pending';
    }
    
    const dbStatusIndex = steps.findIndex(s => s.key === dbStatus);
    const thisIndex = steps.findIndex(s => s.key === stepKey);
    
    if (stepKey === 'ERRO') return 'pending';
    
    if (thisIndex < dbStatusIndex) return 'completed';
    if (thisIndex === dbStatusIndex) return 'current';
    return 'pending';
  };

  return (
    <div className="p-8 bg-slate-900 border border-slate-700 shadow-2xl rounded-2xl mx-auto w-full text-white animate-fade-in text-left overflow-hidden">
      <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-400 mb-6 flex items-center">
        <svg className="w-6 h-6 mr-3 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
        </svg>
        Status do Processamento
      </h2>

      {processData && (
        <div className="mb-8 p-4 bg-slate-800 rounded-lg border border-slate-600 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <span className="block text-xs uppercase text-slate-400 font-bold mb-1">Documento Analisado</span>
            <span className="text-sm font-mono text-emerald-300 break-all">{processData.filename}</span>
          </div>
          <div>
            <span className="block text-xs uppercase text-slate-400 font-bold mb-1">Data/Hora de Envio</span>
            <span className="text-sm text-slate-200">
              {new Date(processData.created_at).toLocaleString('pt-BR', { dateStyle: 'medium', timeStyle: 'medium' })}
            </span>
          </div>
        </div>
      )}

      <div className="relative border-l border-slate-700 ml-3">
        {steps.map((step) => {
          if (step.isError && dbStatus !== 'ERRO') return null; // Show error step only if error happened
          
          const state = getStepState(step.key);
          
          return (
            <div key={step.key} className="mb-10 ml-8 relative">
              <span className={`absolute flex items-center justify-center w-8 h-8 rounded-full -left-12 ring-4 ring-slate-900 
                ${state === 'completed' ? 'bg-emerald-500' : 
                  state === 'current' ? (step.isError ? 'bg-red-500 animate-pulse' : 'bg-blue-500 animate-pulse') : 
                  'bg-slate-700'}`
              }>
                {state === 'completed' && <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>}
                {state === 'current' && !step.isError && <span className="w-3 h-3 bg-white rounded-full"></span>}
                {state === 'current' && step.isError && <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>}
              </span>
              <h3 className={`flex items-center mb-1 text-lg font-semibold ${state === 'current' ? 'text-white' : 'text-slate-400'}`}>
                {step.label}
              </h3>
              <p className="block mb-2 text-sm font-normal leading-none text-slate-500">
                {step.desc}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};