import React, { useState } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

const DatasetUpload = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    
    if (!file) return;

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      return;
    }

    setUploading(true);
    setError(null);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/upload-dataset`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(`Dataset uploaded successfully! ${data.stats.totalPapers} papers, ${data.stats.totalCountries} countries loaded.`);
        
        // Notify parent component
        if (onUploadSuccess) {
          onUploadSuccess(data.stats);
        }
        
        // Reload the page after 2 seconds to show new data
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      } else {
        setError(data.detail || 'Failed to upload dataset');
      }
    } catch (err) {
      setError('Error uploading file. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="inline-block">
      <label
        htmlFor="csv-upload"
        className="inline-flex items-center gap-2 px-4 h-10 bg-white hover:bg-gray-50 text-teal-600 border border-teal-600 rounded-lg cursor-pointer transition-colors text-sm font-medium"
      >
        {uploading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Uploading...
          </>
        ) : (
          <>
            <Upload className="w-4 h-4" />
            Upload CSV
          </>
        )}
      </label>
      <input
        id="csv-upload"
        type="file"
        accept=".csv"
        onChange={handleFileUpload}
        disabled={uploading}
        className="hidden"
      />
      
      {/* Success Message */}
      {message && (
        <div className="fixed top-4 right-4 z-50 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg shadow-lg flex items-start gap-2 max-w-md">
          <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Success!</p>
            <p className="text-sm">{message}</p>
          </div>
        </div>
      )}
      
      {/* Error Message */}
      {error && (
        <div className="fixed top-4 right-4 z-50 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg shadow-lg flex items-start gap-2 max-w-md">
          <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
          <div>
            <p className="font-medium">Error</p>
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default DatasetUpload;
