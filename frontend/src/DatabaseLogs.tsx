import React, { useEffect, useState } from 'react';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const DatabaseLogs = ({ currentAnalysisId }: { currentAnalysisId?: string | null }) => {
  const [logs, setLogs] = useState<any[]>([]);

  const fetchLogs = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/reports`);
      if (response.ok) {
        const data = await response.json();
        const mappedLogs = data
          .filter((item: any) => item.report_data?.observability?.llm_model)
          .reverse()
          .map((item: any) => {
            const report = item.report_data;
            const obs = report.observability || {};
            return {
            id: item.process_id,
            score: report.confidence_score ? `${(report.confidence_score * 100).toFixed(1)}%` : '-',
            status: "Saved in DB",
            processingTime: obs.processing_time_ms ? `${(obs.processing_time_ms / 1000).toFixed(1)}s` : '-',
            llmModel: obs.llm_model || '-',
            tokenIn: obs.token_in || 0,
            tokenOut: obs.token_out || 0
          };
        });
        setLogs(mappedLogs);
      }
    } catch (e) {
      console.error("Failed to fetch logs", e);
    }
  };

  useEffect(() => {
    fetchLogs();
    const interval = setInterval(fetchLogs, 5000);
    return () => clearInterval(interval);
  }, []);

  const allLogs = [...logs];
  
  // If we have a current run, add a mockup row for it at the top if it's not yet in the logs
  if (currentAnalysisId && !allLogs.find(l => l.id === currentAnalysisId)) {
    allLogs.unshift({
      id: currentAnalysisId,
      score: "Pending...",
      status: "Processing",
      processingTime: "-",
      llmModel: "-",
      tokenIn: 0,
      tokenOut: 0
    });
  }

  return (
    <div className="p-6 bg-slate-900 border border-slate-700 shadow-2xl rounded-2xl mx-auto w-full text-white animate-fade-in text-left overflow-hidden">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 flex items-center">
          <svg className="w-6 h-6 mr-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
          Log de Processamento
        </h2>
        <button 
          onClick={fetchLogs}
          className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 rounded-lg text-sm font-medium transition-colors flex items-center text-slate-300"
          title="Atualizar Logs"
        >
          <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
          Atualizar
        </button>
      </div>
      
      <div className="overflow-auto max-h-[400px]">
        <table className="w-full text-sm text-left text-slate-300 relative">
          <thead className="text-xs text-slate-400 uppercase bg-slate-800 whitespace-nowrap sticky top-0 z-10 shadow-md">
            <tr>
              <th scope="col" className="px-6 py-3 rounded-tl-lg bg-slate-800">Process ID</th>
              <th scope="col" className="px-6 py-3 bg-slate-800">Confidence Score</th>
              <th scope="col" className="px-6 py-3 bg-slate-800">Status</th>
              <th scope="col" className="px-6 py-3 bg-slate-800">Processing Time</th>
              <th scope="col" className="px-6 py-3 bg-slate-800">LLM Model</th>
              <th scope="col" className="px-6 py-3 bg-slate-800">Token In</th>
              <th scope="col" className="px-6 py-3 rounded-tr-lg bg-slate-800">Token Out</th>
            </tr>
          </thead>
          <tbody>
            {allLogs.map((log) => (
              <tr key={log.id} className="bg-slate-900 border-b border-slate-700 hover:bg-slate-800 transition-colors whitespace-nowrap">
                <td className="px-6 py-4 font-mono text-xs text-emerald-400">{log.id}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full bg-opacity-20 ${log.score.startsWith('8') ? 'bg-green-500 text-green-300' : (log.score.startsWith('4') || log.score.startsWith('6') ? 'bg-red-500 text-red-300' : 'bg-blue-500 text-blue-300')}`}>
                    {log.score}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-400 flex items-center">
                  <span className={`w-2 h-2 rounded-full mr-2 ${log.status === 'Processing' ? 'bg-yellow-500 animate-pulse' : 'bg-green-500'}`}></span>
                  {log.status}
                </td>
                <td className="px-6 py-4 font-mono text-xs">{log.processingTime}</td>
                <td className="px-6 py-4 font-mono text-xs">{log.llmModel}</td>
                <td className="px-6 py-4 font-mono text-xs text-blue-300">{log.tokenIn}</td>
                <td className="px-6 py-4 font-mono text-xs text-purple-300">{log.tokenOut}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 text-xs text-slate-500 font-mono">
        &gt; docker exec -it db-report psql -U user_report -d report_db -c "SELECT * FROM reports;"
      </div>
    </div>
  );
};
