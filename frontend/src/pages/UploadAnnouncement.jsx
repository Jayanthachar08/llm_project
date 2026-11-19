import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { announcementAPI } from '../services/api';
import {
  UploadCloud,
  FileText,
  Sparkles,
  AlertCircle,
  Database,
  ArrowRight,
  CheckCircle2,
  Image as ImageIcon
} from 'lucide-react';

const UploadAnnouncement = () => {
  const [activeTab, setActiveTab] = useState('file'); // 'file' or 'text'
  const [file, setFile] = useState(null);
  const [pastedText, setPastedText] = useState('');
  const [useRAG, setUseRAG] = useState(true);
  const [loading, setLoading] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    setStatusMessage('Reading document & running OCR...');

    try {
      let extractedText = '';
      let announcementId = null;

      if (activeTab === 'file') {
        if (!file) {
          setError('Please select a PDF or image document.');
          setLoading(false);
          return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('auto_rag_index', useRAG.toString());

        setStatusMessage('Extracting document text via PyMuPDF / OCR...');
        const uploadRes = await announcementAPI.uploadFile(formData);
        extractedText = uploadRes.data.extracted_text;
        announcementId = uploadRes.data.id;
      } else {
        if (!pastedText.trim() || pastedText.trim().length < 10) {
          setError('Please provide at least 10 characters of academic announcement text.');
          setLoading(false);
          return;
        }

        setStatusMessage('Saving announcement & running Input Guardrails...');
        const pasteRes = await announcementAPI.pasteText(pastedText);
        extractedText = pasteRes.data.extracted_text;
        announcementId = pasteRes.data.id;
      }

      setStatusMessage('Querying Google GenAI with RAG context...');
      const extractRes = await announcementAPI.extractTasks({
        text: extractedText,
        announcement_id: announcementId,
        use_rag: useRAG
      });

      // Pass extracted candidate tasks to the Review & Confirmation page
      navigate('/review', {
        state: {
          tasks: extractRes.data.tasks || [],
          raw_summary: extractRes.data.raw_summary,
          ambiguity_detected: extractRes.data.ambiguity_detected,
          announcement_id: announcementId,
          extracted_text: extractedText
        }
      });
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Failed to process academic announcement. Please try again.');
    } finally {
      setLoading(false);
      setStatusMessage('');
    }
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div>
        <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">
          Upload Academic Announcement
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Provide college circulars, syllabus notices, or faculty messages. Google GenAI and RAG will extract deadlines and structured tasks.
        </p>
      </div>

      {error && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-center space-x-2 text-rose-700 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-6">
        <div className="flex border-b border-slate-100">
          <button
            onClick={() => setActiveTab('file')}
            className={`pb-3 px-4 text-xs font-semibold border-b-2 transition flex items-center space-x-2 ${
              activeTab === 'file'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload Document (PDF / Image)</span>
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`pb-3 px-4 text-xs font-semibold border-b-2 transition flex items-center space-x-2 ${
              activeTab === 'text'
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-800'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Paste Notice Text</span>
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {activeTab === 'file' ? (
            <div className="border-2 border-dashed border-slate-200 hover:border-indigo-400 rounded-2xl p-8 text-center transition bg-slate-50/50">
              <input
                type="file"
                id="file-upload"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={handleFileChange}
                className="hidden"
              />
              <label htmlFor="file-upload" className="cursor-pointer space-y-3 block">
                <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto shadow-sm">
                  <UploadCloud className="w-6 h-6" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-slate-800">
                    {file ? file.name : 'Choose academic PDF or image'}
                  </p>
                  <p className="text-xs text-slate-400 mt-1">
                    Supports text-based PDFs (PyMuPDF) and scanned notices/photos (Tesseract OCR) up to 15MB
                  </p>
                </div>
                <span className="inline-block px-3 py-1 bg-white border border-slate-200 rounded-lg text-xs font-medium text-slate-700 shadow-sm">
                  {file ? 'Change File' : 'Browse Files'}
                </span>
              </label>
            </div>
          ) : (
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase tracking-wider mb-2">
                Paste Faculty Message / Announcement Text
              </label>
              <textarea
                rows={6}
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="Example: Students must complete the DBMS assignment and submit it before November 15. The Computer Networks assignment is due on November 18. The DBMS internal examination will be conducted on November 19. Students should prepare all five modules."
                className="w-full p-4 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 transition font-mono leading-relaxed"
              ></textarea>
            </div>
          )}

          {/* RAG Context Retrieval Toggle */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Database className="w-5 h-5 text-indigo-600" />
              <div>
                <span className="text-xs font-semibold text-slate-900 block">
                  Enable RAG Knowledge Retrieval
                </span>
                <span className="text-[11px] text-slate-500">
                  Search previously indexed syllabi & circulars in ChromaDB to verify subjects and deadlines
                </span>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={useRAG}
                onChange={(e) => setUseRAG(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600"></div>
            </label>
          </div>

          {/* Processing Status Banner */}
          {loading && (
            <div className="p-3 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center space-x-3 text-xs text-indigo-700">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
              <span>{statusMessage}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold text-sm rounded-xl transition shadow-md shadow-indigo-100 flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>{loading ? 'Analyzing with Google GenAI...' : 'Extract Academic Tasks'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default UploadAnnouncement;
