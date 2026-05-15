import React from 'react';

export const AIAnalysisReport = ({ reportData }: { reportData: any }) => {
  // Try to safely parse confidence score
  const scoreRaw = reportData.confidence_score || reportData.confidenceScore || 0;
  const scoreBase100 = (parseFloat(scoreRaw) * 100).toFixed(0);
  
  const scoreColor = parseInt(scoreBase100) > 70 ? 'border-emerald-500 text-emerald-400' : 'border-red-500 text-red-400';
  
  const risks = reportData.architectural_risks || reportData.architecturalRisks || [];
  const recommendations = reportData.recommendations || [];
  const components = reportData.identified_components || reportData.identifiedComponents || [];

  return (
    <div className="p-8 bg-slate-900 border border-slate-700 shadow-2xl rounded-2xl mx-auto w-full text-white animate-fade-in text-left">
      {/* HEADER SCORE */}
      <div className="flex justify-between items-center border-b border-slate-700 pb-6 mb-6">
        <div>
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-emerald-400">
            System Architecture Diagnostics
          </h1>
          <p className="text-slate-400 mt-2 text-sm">{reportData.security_posture || "Postura de seguranca analisada."}</p>
        </div>
        <div className={`flex items-center justify-center p-4 rounded-full border-4 w-24 h-24 ${scoreColor}`}>
          <span className="text-2xl font-black">{scoreBase100}%</span>
        </div>
      </div>

      {/* COMPONENTS IDENTIFIED */}
      {components.length > 0 && (
        <div className="mb-6">
          <h3 className="text-slate-300 font-bold mb-3 flex items-center">
            <span className="mr-2">☁️</span> Componentes Identificados
          </h3>
          <div className="flex flex-wrap gap-2">
            {components.map((comp: any, i: number) => (
              <div key={i} className="bg-slate-800 border border-slate-600 px-3 py-1.5 rounded-lg text-sm flex items-center">
                <span className="font-semibold text-blue-300 mr-2">{comp.name || comp}</span>
                {comp.category && <span className="text-xs text-slate-400 px-2 bg-slate-900 rounded-full">{comp.category}</span>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* RISKS AND RECOMMENDATIONS */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="bg-red-950/30 p-5 rounded-xl border border-red-900/50">
          <h3 className="text-red-400 font-bold mb-4 flex items-center text-lg">⚠️ Architectural Risks</h3>
          <ul className="space-y-4">
            {risks.map((risk: any, i: number) => {
              const text = typeof risk === 'string' ? risk : risk.risk;
              const severity = risk.severity || 'Medium';
              const sevColor = severity === 'High' || severity === 'Alta' ? 'bg-red-600 text-white' : (severity === 'Medium' || severity === 'Média' ? 'bg-orange-500 text-white' : 'bg-yellow-500 text-black');
              
              return (
              <li key={i} className="text-sm bg-red-900/20 p-4 rounded-lg text-red-200 border-l-4 border-red-500 flex flex-col">
                <div className="flex justify-between items-start mb-2">
                  <span className="font-semibold">{text}</span>
                  {typeof risk !== 'string' && <span className={`text-xs px-2 py-0.5 rounded-full font-bold ml-2 shrink-0 ${sevColor}`}>{severity}</span>}
                </div>
                {risk.affected_components && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {risk.affected_components.map((c: string, idx: number) => (
                      <span key={idx} className="text-xs bg-red-950 px-2 py-1 rounded text-red-300 border border-red-800">
                        {c}
                      </span>
                    ))}
                  </div>
                )}
              </li>
            )})}
          </ul>
        </div>
        
        <div className="bg-emerald-950/30 p-5 rounded-xl border border-emerald-900/50">
          <h3 className="text-emerald-400 font-bold mb-4 flex items-center text-lg">🛡️ Actionable Recommendations</h3>
          <ul className="space-y-4">
            {recommendations.map((rec: any, i: number) => {
              const text = typeof rec === 'string' ? rec : rec.recommendation;
              const effortColor = rec.effort === 'High' ? 'text-orange-400 bg-orange-950/50' : (rec.effort === 'Medium' ? 'text-yellow-400 bg-yellow-950/50' : 'text-blue-400 bg-blue-950/50');
              
              return (
              <li key={i} className="text-sm bg-emerald-900/20 p-4 rounded-lg text-emerald-200 border-l-4 border-emerald-500 flex flex-col">
                <div className="mb-2">
                  <span className="font-medium">{text}</span>
                </div>
                {typeof rec !== 'string' && (
                  <div className="flex justify-between items-center mt-2 border-t border-emerald-900/30 pt-2">
                    <span className="text-xs text-emerald-400/80 font-mono tracking-tight">{rec.framework}</span>
                    <span className={`text-xs px-2 py-0.5 rounded border border-current ${effortColor}`}>
                      Effort: {rec.effort}
                    </span>
                  </div>
                )}
              </li>
            )})}
          </ul>
        </div>
      </div>
    </div>
  );
};