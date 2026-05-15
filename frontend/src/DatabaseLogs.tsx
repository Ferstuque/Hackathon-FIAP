import React from 'react';

// Mock data to simulate the database rows
const mockLogs = [
  {
    id: "f8d83921-1b9c-4e89-a212-f1d2a3c9b8e1",
    timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
    score: "45.0%",
    components: 6,
    status: "Saved in DB"
  },
  {
    id: "a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d",
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    score: "85.0%",
    components: 4,
    status: "Saved in DB"
  },
  {
    id: "b2c3d4e5-f6a7-8b9c-0d1e-2f3a4b5c6d7e",
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24).toISOString(),
    score: "60.0%",
    components: 8,
    status: "Saved in DB"
  }
];

export const DatabaseLogs = ({ currentAnalysisId }: { currentAnalysisId?: string | null }) => {
  const allLogs = [...mockLogs];
  
  // If we have a current run, add a mockup row for it at the top
  if (currentAnalysisId && !allLogs.find(l => l.id === currentAnalysisId)) {
    allLogs.unshift({
      id: currentAnalysisId,
      timestamp: new Date().toISOString(),
      score: "Pending/Recent",
      components: 0,
      status: "Saved in DB"
    });
  }

  return (
    <div className="p-6 bg-slate-900 border border-slate-700 shadow-2xl rounded-2xl mx-auto w-full text-white animate-fade-in text-left overflow-hidden">
      <h2 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400 mb-6 flex items-center">
        <svg className="w-6 h-6 mr-3 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" /></svg>
        Log de Processamento
      </h2>
      
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left text-slate-300">
          <thead className="text-xs text-slate-400 uppercase bg-slate-800 rounded-t-lg">
            <tr>
              <th scope="col" className="px-6 py-3 rounded-tl-lg">Process ID</th>
              <th scope="col" className="px-6 py-3">Data/Hora</th>
              <th scope="col" className="px-6 py-3">Confidence Score</th>
              <th scope="col" className="px-6 py-3">Status</th>
            </tr>
          </thead>
          <tbody>
            {allLogs.map((log) => (
              <tr key={log.id} className="bg-slate-900 border-b border-slate-700 hover:bg-slate-800 transition-colors">
                <td className="px-6 py-4 font-mono text-xs text-emerald-400">{log.id}</td>
                <td className="px-6 py-4">{new Date(log.timestamp).toLocaleString()}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded-full bg-opacity-20 ${log.score.startsWith('8') ? 'bg-green-500 text-green-300' : (log.score.startsWith('4') || log.score.startsWith('6') ? 'bg-red-500 text-red-300' : 'bg-blue-500 text-blue-300')}`}>
                    {log.score}
                  </span>
                </td>
                <td className="px-6 py-4 text-slate-400 flex items-center">
                  <span className="w-2 h-2 rounded-full bg-green-500 mr-2"></span>
                  {log.status}
                </td>
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
