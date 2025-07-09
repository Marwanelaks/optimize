import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import { 
  Upload, 
  Github, 
  History, 
  BarChart3, 
  Settings, 
  Download,
  Play,
  Pause,
  RefreshCw,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { FileUpload } from './FileUpload';


interface DashboardProps {
  onNavigate: (section: string) => void;
}

interface OptimizationResult {
  download_url: string;
  report: {
    stats?: {
      total_files?: number;
      size_reduction?: number;
      [key: string]: any;
    };
    [key: string]: any;
  };
  message: string;
}

export const Dashboard: React.FC<DashboardProps> = ({ onNavigate }) => {
  const [activeTab, setActiveTab] = useState('upload');
  const [githubUrl, setGithubUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState<OptimizationResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [progressMessage, setProgressMessage] = useState('');

  const recentProjects = [
    {
      id: 1,
      name: 'E-commerce Website',
      type: 'ZIP Upload',
      optimized: '2 hours ago',
      improvement: '+45%',
      status: 'completed'
    },
    {
      id: 2,
      name: 'React Portfolio',
      type: 'GitHub',
      optimized: '1 day ago',
      improvement: '+32%',
      status: 'completed'
    },
    {
      id: 3,
      name: 'Blog Platform',
      type: 'ZIP Upload',
      optimized: '3 days ago',
      improvement: '+28%',
      status: 'completed'
    },
  ];

 const handleFileUpload = async (file: File) => {
  setIsProcessing(true);
  setProgress(0);
  setResult(null);
  setError(null);

  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:8000/optimize/upload', {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || 'Upload failed');
    }

    // Get the blob
    const blob = await response.blob();
    
    // Verify the ZIP file
    const zipValid = await verifyZipFile(blob);
    if (!zipValid) {
      throw new Error('Invalid ZIP file received from server');
    }

    // Get optimization report from headers
    const report = response.headers.get('X-Optimization-Report');
    
    setResult({
      download_url: window.URL.createObjectURL(blob),
      report: report ? JSON.parse(report) : null,
      message: 'Optimization complete!'
    });

  } catch (err) {
    setError(err instanceof Error ? err.message : 'Upload failed');
    console.error('Upload error:', err);
  } finally {
    setIsProcessing(false);
  }
};

// ZIP verification function
const verifyZipFile = async (blob: Blob): Promise<boolean> => {
  return new Promise((resolve) => {
    // Check file size
    if (blob.size < 4) {
      resolve(false);
      return;
    }

    // Check magic number (PK header)
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const arr = new Uint8Array(reader.result as ArrayBuffer);
        resolve(arr[0] === 0x50 && arr[1] === 0x4B); // PK header
      } catch {
        resolve(false);
      }
    };
    reader.readAsArrayBuffer(blob.slice(0, 4));
  });
};

const handleDownload = () => {
  if (!result?.download_url) return;

  const a = document.createElement('a');
  a.href = result.download_url;
  a.download = 'optimized-website.zip';
  document.body.appendChild(a);
  a.click();

  // Clean up
  setTimeout(() => {
    document.body.removeChild(a);
    window.URL.revokeObjectURL(result.download_url);
  }, 100);
};

  const handleGithubOptimization = async () => {
    if (!githubUrl) return;

    setIsProcessing(true);
    setProgress(0);
    setResult(null);
    setError(null);
    setProgressMessage('Starting GitHub optimization...');

    try {
      const response = await axios.get(
        `http://localhost:8000/optimize/github?repo_url=${encodeURIComponent(githubUrl)}`,
        { responseType: 'blob' }
      );

      try {
        const report = JSON.parse(response.headers['x-optimization-report'] || '{}');
        setResult({
          download_url: URL.createObjectURL(response.data),
          report,
          message: 'Optimization complete!'
        });
      } catch (e) {
        console.error('Could not parse optimization report', e);
        setResult({
          download_url: URL.createObjectURL(response.data),
          report: null,
          message: 'Optimization complete (no report available)'
        });
      }

    } catch (err) {
      const errorMessage = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message
        : err instanceof Error 
          ? err.message 
          : 'GitHub optimization failed';
      setError(errorMessage);
      console.error('GitHub optimization error:', err);
    } finally {
      setIsProcessing(false);
      setProgress(100);
      setProgressMessage('Optimization complete!');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 pt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="mb-8"
        >
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Dashboard
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Optimize your website performance with AI-powered tools
          </p>
        </motion.div>

        {/* Quick Stats */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8"
        >
          {[
            { label: 'Projects Optimized', value: '23', icon: BarChart3 },
            { label: 'Avg. Speed Boost', value: '+35%', icon: RefreshCw },
            { label: 'Files Processed', value: '1.2K', icon: Upload },
            { label: 'Storage Used', value: '45MB', icon: Settings },
          ].map((stat, index) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 + index * 0.1 }}
              className="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 dark:text-gray-400">
                    {stat.label}
                  </p>
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">
                    {stat.value}
                  </p>
                </div>
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-lg">
                  <stat.icon className="w-6 h-6 text-blue-600" />
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg mb-6 flex items-start"
          >
            <AlertCircle className="w-5 h-5 text-red-500 dark:text-red-300 mr-3 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                Error
              </h3>
              <p className="text-sm text-red-700 dark:text-red-300">
                {error}
              </p>
            </div>
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {/* Optimization Options */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8"
            >
              <div className="flex space-x-4 mb-6">
                <button
                  onClick={() => setActiveTab('upload')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    activeTab === 'upload'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Upload className="w-4 h-4 inline mr-2" />
                  File Upload
                </button>
                <button
                  onClick={() => setActiveTab('github')}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    activeTab === 'github'
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  <Github className="w-4 h-4 inline mr-2" />
                  GitHub Repo
                </button>
              </div>

              {activeTab === 'upload' && (
                <FileUpload
                  onFileUpload={handleFileUpload}
                  isUploading={isProcessing}
                  progress={progress}
                />
              )}

              {activeTab === 'github' && (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      GitHub Repository URL
                    </label>
                    <input
                      type="url"
                      value={githubUrl}
                      onChange={(e) => setGithubUrl(e.target.value)}
                      placeholder="https://github.com/username/repository"
                      className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                  </div>
                  <motion.button
                    onClick={handleGithubOptimization}
                    disabled={!githubUrl || isProcessing}
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    {isProcessing ? (
                      <>
                        <RefreshCw className="w-4 h-4 inline mr-2 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Play className="w-4 h-4 inline mr-2" />
                        Optimize Repository
                      </>
                    )}
                  </motion.button>
                </div>
              )}
            </motion.div>

            {/* Processing Status */}
            {isProcessing && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8"
              >
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Processing Status
                </h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600 dark:text-gray-300">
                      {progressMessage}
                    </span>
                    <span className="text-sm font-medium text-blue-600">
                      {progress}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <motion.div
                      className="bg-gradient-to-r from-blue-500 to-purple-600 h-2 rounded-full"
                      initial={{ width: 0 }}
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {progress < 50 
                      ? "Initializing optimization process..." 
                      : progress < 80 
                        ? "Applying AI-powered optimizations..." 
                        : "Finalizing your optimized package..."}
                  </div>
                </div>
              </motion.div>
            )}

            {/* Results Display */}
            {result && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 mb-8"
              >
                <div className="flex items-start">
                  <CheckCircle className="w-5 h-5 text-green-500 dark:text-green-400 mr-3 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                      Optimization Complete!
                    </h3>
                    <p className="text-gray-600 dark:text-gray-300 mb-4">
                      {result.message}
                    </p>

                    {result.report && (
                      <div className="mb-6">
                        <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                          Optimization Results:
                        </h4>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              Files Processed
                            </p>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">
                              {result.report.stats?.total_files || 'N/A'}
                            </p>
                          </div>
                          <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              Size Reduction
                            </p>
                            <p className="text-xl font-bold text-gray-900 dark:text-white">
                              {result.report.stats?.size_reduction 
                                ? `${result.report.stats.size_reduction.toFixed(2)}%` 
                                : 'N/A'}
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    <motion.a
                      href="#"
                      onClick={(e) => {
                        e.preventDefault();
                        handleDownload();
                      }}
                      className="w-full bg-gradient-to-r from-green-500 to-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:from-green-600 hover:to-blue-700 transition-all block text-center"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      <Download className="w-4 h-4 inline mr-2" />
                      Download Optimized Files
                    </motion.a>
                  </div>
                </div>
              </motion.div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Recent Projects */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.6 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                <History className="w-5 h-5 mr-2" />
                Recent Projects
              </h3>
              <div className="space-y-3">
                {recentProjects.map((project) => (
                  <div
                    key={project.id}
                    className="border border-gray-200 dark:border-gray-700 rounded-lg p-3 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white text-sm">
                        {project.name}
                      </h4>
                      <span className="text-xs text-green-600 dark:text-green-400 font-medium">
                        {project.improvement}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>{project.type}</span>
                      <span>{project.optimized}</span>
                    </div>
                  </div>
                ))}
              </div>
              <button
                onClick={() => onNavigate('projects')}
                className="w-full mt-4 text-center text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium text-sm"
              >
                View All Projects
              </button>
            </motion.div>

            {/* Quick Actions */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.8 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
            >
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <motion.button
                  onClick={() => onNavigate('ai-tools')}
                  className="w-full text-left p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-purple-100 dark:bg-purple-900/30 rounded-lg">
                      <Settings className="w-4 h-4 text-purple-600" />
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white text-sm">
                        AI Tools
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        Advanced optimization tools
                      </p>
                    </div>
                  </div>
                </motion.button>
                
                {result && (
                  <motion.button
                    onClick={handleDownload}
                    className="w-full text-left p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="p-2 bg-green-100 dark:bg-green-900/30 rounded-lg">
                        <Download className="w-4 h-4 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900 dark:text-white text-sm">
                          Download Results
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          Get optimized files
                        </p>
                      </div>
                    </div>
                  </motion.button>
                )}
              </div>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};