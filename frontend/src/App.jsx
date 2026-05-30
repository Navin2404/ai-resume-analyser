import React, { useState, useRef, useEffect, useCallback } from 'react';
import { 
  Bot, 
  Moon, 
  Sun, 
  UploadCloud, 
  CheckCircle, 
  Send, 
  FileText,
  Loader2
} from 'lucide-react';

const API_URL  = "https://ai-resume-analyser-l5a8.onrender.com/";

const SUGGESTED_QUESTIONS = [
  "What are the technical skills?",
  "Summarize work experience",
  "What projects has this person done?",
  "Is this suitable for a Python Developer role?",
  "Tell me the contact details"
];

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [filename, setFilename] = useState('');
  const [chunksCount, setChunksCount] = useState(0);
  const [toast, setToast] = useState(null);
  
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoadingChat, setIsLoadingChat] = useState(false);
  
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  
  // Toggle dark mode
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  // Auto scroll
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoadingChat]);

  // Toast auto-hide
  useEffect(() => {
    if (toast) {
      const timer = setTimeout(() => setToast(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [toast]);

  const showToast = (message, type = 'success') => {
    setToast({ message, type });
  };

  const handleFileUpload = async (file) => {
    if (!file) return;
    if (file.type !== 'application/pdf') {
      showToast('Please upload a valid PDF file.', 'error');
      return;
    }

    setIsUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch(`${API_URL}/upload`, {
        method: 'POST',
        body: formData,
      });
      
      const data = await res.json();
      
      if (res.ok) {
        setIsUploaded(true);
        setFilename(data.filename);
        setChunksCount(data.chunks);
        showToast('Resume uploaded successfully!');
        setMessages([{ role: 'bot', content: 'Resume analyzed successfully! What would you like to know about it?' }]);
      } else {
        showToast(data.detail || 'Upload failed', 'error');
      }
    } catch (err) {
      showToast('Error connecting to server', 'error');
    } finally {
      setIsUploading(false);
    }
  };

  const onDrop = useCallback((e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    handleFileUpload(file);
  }, []);

  const onDragOver = (e) => {
    e.preventDefault();
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    handleFileUpload(file);
  };

  const sendMessage = async (text) => {
    if (!text.trim() || isLoadingChat) return;
    
    const userMsg = text.trim();
    setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
    setInputValue('');
    setIsLoadingChat(true);

    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userMsg })
      });
      
      const data = await res.json();
      
      if (res.ok) {
        setMessages(prev => [...prev, { role: 'bot', content: data.answer }]);
      } else {
        setMessages(prev => [...prev, { role: 'bot', content: 'Sorry, I encountered an error. Please try again.' }]);
      }
    } catch (err) {
      setMessages(prev => [...prev, { role: 'bot', content: 'Error connecting to the server. Is the backend running?' }]);
    } finally {
      setIsLoadingChat(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage(inputValue);
    }
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden font-sans bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* Toast Notification */}
      {toast && (
        <div className="absolute top-20 left-1/2 transform -translate-x-1/2 z-50 animate-slide-up">
          <div className={`px-6 py-3 rounded-full shadow-lg text-white font-medium flex items-center space-x-2 ${toast.type === 'error' ? 'bg-red-500' : 'bg-green-500'}`}>
            {toast.type === 'success' && <CheckCircle className="w-5 h-5" />}
            <span>{toast.message}</span>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="h-16 flex items-center justify-between px-6 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm z-10 shrink-0 transition-colors">
        <div className="flex items-center space-x-3">
          <div className="bg-indigo-100 dark:bg-indigo-900/50 p-2 rounded-xl">
            <Bot className="w-6 h-6 text-indigo-600 dark:text-indigo-400" />
          </div>
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
            AI Resume Analyzer
          </h1>
        </div>
        <button 
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-600 dark:text-gray-300 transition-colors focus:outline-none"
          aria-label="Toggle dark mode"
        >
          {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
        </button>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden flex-col md:flex-row">
        
        {/* Left Panel - Upload Section */}
        <div className="w-full md:w-1/3 lg:w-1/4 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col p-6 shrink-0 transition-colors">
          <h2 className="text-lg font-semibold mb-6 text-gray-800 dark:text-gray-100">Upload Resume</h2>
          
          <div 
            className={`border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center text-center transition-all ${
              isUploaded 
                ? 'border-green-400 bg-green-50 dark:bg-green-900/20' 
                : 'border-gray-300 dark:border-gray-600 hover:border-indigo-400 dark:hover:border-indigo-500 hover:bg-indigo-50/50 dark:hover:bg-indigo-900/10 cursor-pointer'
            }`}
            onDrop={onDrop}
            onDragOver={onDragOver}
            onClick={() => !isUploaded && !isUploading && fileInputRef.current?.click()}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              accept=".pdf" 
              className="hidden" 
            />
            
            {isUploading ? (
              <div className="flex flex-col items-center space-y-4 animate-fade-in">
                <Loader2 className="w-12 h-12 text-indigo-500 animate-spin" />
                <p className="text-gray-600 dark:text-gray-400 font-medium">Analyzing resume...</p>
              </div>
            ) : isUploaded ? (
              <div className="flex flex-col items-center space-y-3 animate-fade-in">
                <div className="bg-green-100 dark:bg-green-900/50 p-3 rounded-full text-green-600 dark:text-green-400">
                  <CheckCircle className="w-10 h-10" />
                </div>
                <div className="text-center">
                  <p className="text-gray-800 dark:text-gray-200 font-medium truncate max-w-[200px]" title={filename}>{filename}</p>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Processed into {chunksCount} chunks</p>
                </div>
                <button 
                  onClick={(e) => { e.stopPropagation(); setIsUploaded(false); setMessages([]); }}
                  className="mt-4 text-sm text-indigo-600 dark:text-indigo-400 hover:underline focus:outline-none"
                >
                  Upload a different file
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center space-y-4 text-gray-500 dark:text-gray-400">
                <div className="bg-indigo-50 dark:bg-gray-700 p-4 rounded-full text-indigo-500 dark:text-indigo-400">
                  <UploadCloud className="w-10 h-10" />
                </div>
                <div>
                  <p className="font-medium text-gray-700 dark:text-gray-300">Click to upload</p>
                  <p className="text-sm mt-1">or drag and drop PDF here</p>
                </div>
              </div>
            )}
          </div>
          
          <div className="mt-auto pt-6 text-xs text-gray-400 dark:text-gray-500 text-center">
            Supported format: PDF up to 10MB
          </div>
        </div>

        {/* Right Panel - Chat Section */}
        <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-900 relative">
          {!isUploaded ? (
            // Empty State
            <div className="flex-1 flex flex-col items-center justify-center p-8 text-center animate-fade-in">
              <div className="w-48 h-48 mb-6 relative">
                <div className="absolute inset-0 bg-indigo-100 dark:bg-indigo-900/30 rounded-full animate-pulse blur-xl"></div>
                <div className="relative bg-white dark:bg-gray-800 rounded-full w-full h-full flex items-center justify-center shadow-sm border border-gray-100 dark:border-gray-700">
                  <FileText className="w-20 h-20 text-indigo-300 dark:text-indigo-700" />
                </div>
              </div>
              <h3 className="text-2xl font-bold text-gray-800 dark:text-gray-200 mb-2">Ready to Analyze</h3>
              <p className="text-gray-500 dark:text-gray-400 max-w-md">
                Upload a resume PDF on the left to start asking questions about skills, experience, and qualifications.
              </p>
            </div>
          ) : (
            // Chat Interface
            <>
              <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
                {messages.map((msg, idx) => (
                  <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-slide-up`} style={{animationDelay: '0.1s'}}>
                    <div className={`max-w-[85%] md:max-w-[75%] rounded-2xl p-4 ${
                      msg.role === 'user' 
                        ? 'bg-gradient-to-br from-indigo-600 to-purple-600 text-white rounded-br-sm shadow-md' 
                        : 'bg-white dark:bg-gray-800 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-700 rounded-bl-sm shadow-sm'
                    }`}>
                      <p className="whitespace-pre-wrap leading-relaxed text-sm md:text-base">
                        {msg.content}
                      </p>
                    </div>
                  </div>
                ))}
                
                {isLoadingChat && (
                  <div className="flex justify-start animate-fade-in">
                    <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-2xl rounded-bl-sm p-4 shadow-sm flex items-center space-x-2">
                      <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{animationDelay: '0ms'}}></div>
                      <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{animationDelay: '150ms'}}></div>
                      <div className="w-2 h-2 rounded-full bg-indigo-400 animate-bounce" style={{animationDelay: '300ms'}}></div>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Chat Input Area */}
              <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 p-4 md:p-6 shrink-0 z-10 transition-colors">
                {/* Suggested Questions */}
                {messages.length <= 1 && !isLoadingChat && (
                  <div className="flex flex-wrap gap-2 mb-4 animate-fade-in">
                    {SUGGESTED_QUESTIONS.map((q, i) => (
                      <button
                        key={i}
                        onClick={() => sendMessage(q)}
                        disabled={isLoadingChat}
                        className="text-xs md:text-sm bg-indigo-50 dark:bg-gray-700 text-indigo-700 dark:text-indigo-300 py-2 px-4 rounded-full hover:bg-indigo-100 dark:hover:bg-gray-600 transition-colors focus:outline-none border border-indigo-100 dark:border-gray-600 whitespace-nowrap"
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                )}
                
                <div className="flex items-center space-x-2 bg-gray-50 dark:bg-gray-900 rounded-full border border-gray-300 dark:border-gray-600 focus-within:border-indigo-500 dark:focus-within:border-indigo-400 focus-within:ring-2 focus-within:ring-indigo-200 dark:focus-within:ring-indigo-900/50 transition-all p-1 pl-4">
                  <input
                    type="text"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyPress}
                    disabled={isLoadingChat}
                    placeholder={isLoadingChat ? "Waiting for response..." : "Ask a question about the resume..."}
                    className="flex-1 bg-transparent border-none focus:outline-none text-gray-800 dark:text-gray-200 py-3 disabled:opacity-50"
                  />
                  <button
                    onClick={() => sendMessage(inputValue)}
                    disabled={!inputValue.trim() || isLoadingChat}
                    className="bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-300 dark:disabled:bg-gray-700 disabled:text-gray-500 text-white rounded-full p-3 transition-colors focus:outline-none flex-shrink-0"
                  >
                    <Send className="w-5 h-5" />
                  </button>
                </div>
                <div className="text-center mt-2">
                  <span className="text-[10px] text-gray-400 dark:text-gray-500">AI can make mistakes. Verify important information.</span>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
