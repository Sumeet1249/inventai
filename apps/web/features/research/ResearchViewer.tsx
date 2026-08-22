import React from 'react';

interface ResearchViewerProps {
  summary: string;
  keyFindings: string[];
}

export default function ResearchViewer({ summary, keyFindings }: ResearchViewerProps) {
  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold text-white mb-4">AI Research Synthesis</h3>
      <div className="mb-6">
        <h4 className="text-lg font-semibold text-gray-300 mb-2">Summary</h4>
        <p className="text-gray-400 leading-relaxed">{summary || "Generating summary..."}</p>
      </div>
      <div>
        <h4 className="text-lg font-semibold text-gray-300 mb-2">Key Findings</h4>
        {keyFindings && keyFindings.length > 0 ? (
          <ul className="list-disc list-inside text-gray-400 space-y-2">
            {keyFindings.map((finding, index) => (
              <li key={index}>{finding}</li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-500 italic">No key findings extracted yet.</p>
        )}
      </div>
    </div>
  );
}
