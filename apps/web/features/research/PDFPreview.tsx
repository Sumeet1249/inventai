import React from 'react';

interface PDFPreviewProps {
  paperId: string;
}

export default function PDFPreview({ paperId }: PDFPreviewProps) {
  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-lg">
      <h3 className="text-xl font-bold text-white mb-4">PDF Preview</h3>
      <div className="h-96 flex items-center justify-center border border-gray-700 rounded bg-gray-900 overflow-hidden relative">
         <iframe 
           src={`/api/v1/research/download/${paperId}`} 
           className="absolute top-0 left-0 w-full h-full border-none"
           title="PDF Preview"
         >
           <p className="text-gray-500 italic">Preview not available.</p>
         </iframe>
      </div>
    </div>
  );
}
