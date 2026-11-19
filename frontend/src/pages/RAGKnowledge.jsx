import React, { useState } from 'react';
import { ragAPI } from '../services/api';
import {
  Database,
  Search,
  BookOpen,
  FileText,
  RefreshCw,
  Plus,
  CheckCircle2,
  AlertCircle,
  Layers,
  ArrowRight
} from 'lucide-react';

const RAGKnowledge = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  // Ingest form state
  const [docName, setDocName] = useState('');
  const [docText, setDocText] = useState('');
  const [ingesting, setIngesting] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    setError('');
    try {
      const res = await ragAPI.search(query, 4);
      setResults(res.data || []);
      if (res.data.length === 0) {
        setMessage('No semantic matches found in vector index.');
      } else {
        setMessage(`Retrieved ${res.data.length} relevant academic chunks from ChromaDB.`);
      }
    } catch (err) {
      console.error(err);
      setError('Search failed in ChromaDB vector store.');
    } finally {
      setSearching(false);
    }
  };

  const handleIngest = async (e) => {
    e.preventDefault();
    if (!docName.trim() || !docText.trim()) return;
    setIngesting(true);
    setError('');
    setMessage('');
    try {
      const res = await ragAPI.ingest({
        document_name: docName,
        text: docText,
        source_type: 'pdf'
      });
      setMessage(res.data.message || 'Document ingested into vector collection.');
      setDocName('');
      setDocText('');
    } catch (err) {
      console.error(err);
      setError('Failed to ingest document into ChromaDB.');
    } finally {
      setIngesting(false);
    }
  };

  const handleReindex = async () => {
    try {
      setSearching(true);
      const res = await ragAPI.reindex();
      setMessage(res.data.message || 'Vector embeddings rebuilt successfully.');
    } catch (err) {
      console.error(err);
      setError('Reindexing failed.');
    } finally {
      setSearching(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-indigo-600 text-xs font-semibold uppercase tracking-wider mb-1">
            <Database className="w-4 h-4" />
            <span>Retrieval-Augmented Generation (RAG)</span>
          </div>
          <h1 className="text-xl md:text-2xl font-bold text-slate-900 tracking-tight">Academic Knowledge Base</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            ChromaDB vector store with semantic embeddings, user-level isolation, and source page attribution.
          </p>
        </div>

        <button
          onClick={handleReindex}
          className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold text-xs rounded-xl flex items-center space-x-1.5 transition self-start"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Re-index Vector Store</span>
        </button>
      </div>

      {message && (
        <div className="p-3.5 bg-indigo-50 border border-indigo-100 rounded-xl flex items-center space-x-2 text-indigo-800 text-xs">
          <CheckCircle2 className="w-4 h-4 text-indigo-600 flex-shrink-0" />
          <span>{message}</span>
        </div>
      )}

      {error && (
        <div className="p-3.5 bg-rose-50 border border-rose-200 rounded-xl flex items-center space-x-2 text-rose-700 text-xs">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Semantic Search Box */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Semantic Vector Query</h3>
        <p className="text-xs text-slate-500">
          Query your indexed academic knowledge base to retrieve syllabus rules, prerequisites, and source citations.
        </p>

        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. DBMS normalization rules, CN lab socket programming requirements..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={searching}
            className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-semibold transition disabled:opacity-50"
          >
            {searching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {/* Retrieved Results with Source Citations */}
        {results.length > 0 && (
          <div className="space-y-3 pt-3 border-t border-slate-100">
            <h4 className="text-xs font-bold text-slate-800">Retrieved Chunks ({results.length})</h4>
            <div className="space-y-2">
              {results.map((r, idx) => (
                <div key={idx} className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2 text-xs">
                  <div className="flex items-center justify-between text-[11px] text-slate-500">
                    <span className="font-bold text-indigo-700 flex items-center space-x-1">
                      <FileText className="w-3.5 h-3.5" />
                      <span>{r.document_name} • Page {r.page_number}</span>
                    </span>
                    <span className="bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full text-[10px] font-semibold">
                      Cosine Distance: {r.distance}
                    </span>
                  </div>
                  <p className="text-slate-800 leading-relaxed font-mono text-[11px] bg-white p-3 rounded-lg border border-slate-100">
                    {r.content}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Ingest New Reference Document */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-900">Ingest Reference Document into RAG</h3>
        <p className="text-xs text-slate-500">
          Store syllabus guidelines, grading rubrics, or lab manuals. Each chunk is indexed with page attribution.
        </p>

        <form onSubmit={handleIngest} className="space-y-3">
          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Document Title</label>
            <input
              type="text"
              required
              value={docName}
              onChange={(e) => setDocName(e.target.value)}
              placeholder="e.g. 18CS71_DBMS_Syllabus.pdf"
              className="w-full px-3 py-2 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-700 mb-1">Document Content / Text</label>
            <textarea
              rows={4}
              required
              value={docText}
              onChange={(e) => setDocText(e.target.value)}
              placeholder="Paste syllabus text or academic manual content here..."
              className="w-full p-3 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-600 outline-none font-mono"
            ></textarea>
          </div>

          <button
            type="submit"
            disabled={ingesting}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-semibold transition disabled:opacity-50"
          >
            {ingesting ? 'Indexing in ChromaDB...' : 'Ingest Document'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default RAGKnowledge;
