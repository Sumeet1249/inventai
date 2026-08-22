import React from 'react';

export default function PDFPreview({ paperId }: { paperId: string }) {
  return (
    <div className="bg-gray-800 p-4 rounded-lg h-64 flex items-center justify-center">
      <p className="text-gray-400">PDF Preview for {paperId}</p>
    </div>
  );
}
