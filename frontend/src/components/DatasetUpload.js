import React, { useState, useRef } from 'react';
import { Upload, CheckCircle, AlertCircle, Loader2, Lock } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Input } from './ui/input';
import { Button } from './ui/button';
import { Label } from './ui/label';

const DatasetUpload = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [showPasswordDialog, setShowPasswordDialog] = useState(false);
  const [password, setPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  const handleUploadButtonClick = () => {
    // Show password dialog when upload button is clicked
    setShowPasswordDialog(true);
    setPassword('');
    setPasswordError('');
  };

  const handlePasswordSubmit = async () => {
    // Validate password is entered
    if (!password.trim()) {
      setPasswordError('Please enter a password');
      return;
    }

    // Validate password with backend before opening file picker
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append('password', password);

      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/validate-upload-password`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        // Password is valid, close dialog and open file picker
        setShowPasswordDialog(false);
        setPasswordError('');
        fileInputRef.current?.click();
      } else {
        // Invalid password
        setPasswordError('Invalid password. Please try again.');
      }
    } catch (err) {
      setPasswordError('Error validating password. Please try again.');
      console.error('Password validation error:', err);
    } finally {
      setUploading(false);
    }
  };

  const handleFileSelected = async (event) => {
    const file = event.target.files[0];
    
    if (!file) {
      // Reset password if no file selected
      setPassword('');
      return;
    }

    // Validate file type
    if (!file.name.endsWith('.csv')) {
      setError('Please upload a CSV file');
      setPassword('');
      return;
    }

    setSelectedFile(file);
    await uploadFile(file);
  };

  const uploadFile = async (file) => {
    setUploading(true);
    setError(null);
    setMessage(null);

    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('password', password);

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
        if (response.status === 401) {
          setError('Invalid password. Please try again.');
        } else {
          setError(data.detail || 'Failed to upload dataset');
        }
      }
    } catch (err) {
      setError('Error uploading file. Please try again.');
      console.error('Upload error:', err);
    } finally {
      setUploading(false);
      setPassword('');
      setSelectedFile(null);
      // Reset file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  return (
    <>
      <div className="inline-block">
        <button
          onClick={handleUploadButtonClick}
          disabled={uploading}
          className="inline-flex items-center gap-2 px-4 h-10 bg-white hover:bg-gray-50 text-teal-600 border border-teal-600 rounded-lg cursor-pointer transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
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
        </button>
        
        {/* Hidden file input */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelected}
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

      {/* Password Dialog */}
      <Dialog open={showPasswordDialog} onOpenChange={setShowPasswordDialog}>
        <DialogContent className="sm:max-w-md bg-white z-[9999]">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-gray-900">
              <Lock className="w-5 h-5 text-teal-600" />
              Authentication Required
            </DialogTitle>
            <DialogDescription className="text-gray-600">
              Please enter the password to upload a new dataset.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="password" className="text-gray-700">Password</Label>
              <Input
                id="password"
                type="password"
                placeholder="Enter password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setPasswordError('');
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handlePasswordSubmit();
                  }
                }}
                className="col-span-3 bg-white border-gray-300"
                autoFocus
              />
              {passwordError && (
                <p className="text-sm text-red-600">{passwordError}</p>
              )}
            </div>
          </div>
          
          <DialogFooter className="gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setShowPasswordDialog(false);
                setPassword('');
                setPasswordError('');
              }}
              disabled={uploading}
              className="border-gray-300 text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </Button>
            <Button
              type="button"
              onClick={handlePasswordSubmit}
              disabled={uploading}
              className="bg-teal-600 hover:bg-teal-700 text-white"
            >
              {uploading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin mr-2" />
                  Validating...
                </>
              ) : (
                'Continue'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default DatasetUpload;
