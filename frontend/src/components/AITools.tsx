import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Code,
  RefreshCw,
  Search,
  FileText,
  Zap,
  Download,
  Eye,
  Settings,
  Copy
} from 'lucide-react';
import { Bar, Pie } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

interface AnalysisResult {
  performance_score?: number;
  seo_score?: number;
  accessibility_score?: number;
  suggestions?: string[];
  optimization_potential?: number;
  converted?: string;
  message?: string;
  error?: string;
}

export const AITools: React.FC = () => {
  const [activeTab, setActiveTab] = useState('analyze');
  const [code, setCode] = useState('');
  const [url, setUrl] = useState('');
  const [prompt, setPrompt] = useState('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [selectedFileType, setSelectedFileType] = useState('css');

  const tools = [
    {
      id: 'analyze',
      label: 'Code Analyzer',
      icon: Code,
      description: 'Analyze your code for performance issues'
    },
    {
      id: 'convert',
      label: 'Format Converter',
      icon: RefreshCw,
      description: 'Convert between different file formats'
    },
    {
      id: 'seo',
      label: 'SEO Checker',
      icon: Search,
      description: 'Check your website for SEO optimization'
    },
    {
      id: 'suggestions',
      label: 'AI Suggestions',
      icon: Zap,
      description: 'Get AI-powered optimization suggestions'
    }
  ];

  const fileTypes = [
    { value: 'html', label: 'HTML' },
    { value: 'css', label: 'CSS' },
    { value: 'scss', label: 'SCSS' },
    { value: 'js', label: 'JavaScript' },
    { value: 'ts', label: 'TypeScript' }
  ];

  const conversionTypes = [
    { from: 'css', to: 'scss', label: 'CSS to SCSS' },
    { from: 'scss', to: 'css', label: 'SCSS to CSS' },
    { from: 'js', to: 'ts', label: 'JS to TS' },
    { from: 'html', to: 'jsx', label: 'HTML to JSX' }
  ];

  const cleanConvertedCode = (code: string) => {
    // Remove markdown code blocks if present
    return code.replace(/^```[a-z]*\n/, '').replace(/\n```$/, '');
  };

  const handleAnalyze = async () => {
    if (!code.trim()) return;

    setIsProcessing(true);
    try {
      const response = await fetch('http://localhost:8000/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          code,
          file_type: selectedFileType
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result.analysis || result);
      } else {
        const error = await response.json();
        setAnalysisResult({ error: error.detail || 'Analysis failed' });
      }
    } catch (error) {
      setAnalysisResult({ error: error instanceof Error ? error.message : 'Analysis failed' });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleConvert = async (from: string, to: string) => {
    if (!code.trim()) return;

    setIsProcessing(true);
    try {
      const response = await fetch(`http://localhost:8000/ai/convert?target_format=${from}_to_${to}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: code,
          file_type: from
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const convertedCode = cleanConvertedCode(result.converted);
        setCode(convertedCode);
        setAnalysisResult({
          converted: convertedCode,
          message: `Successfully converted from ${from} to ${to}`
        });
      } else {
        const error = await response.json();
        setAnalysisResult({ error: error.detail || 'Conversion failed' });
      }
    } catch (error) {
      setAnalysisResult({ error: error instanceof Error ? error.message : 'Conversion failed' });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSeoCheck = async () => {
    if (!url.trim()) return;
    setIsProcessing(true);

    try {
      const response = await fetch(`http://localhost:8000/ai/seo-analyze?url=${encodeURIComponent(url)}`, {
        method: 'POST', // or whatever method your backend expects
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result.analysis || result);
      } else {
        const error = await response.json();
        setAnalysisResult({ error: error.detail || 'SEO analysis failed' });
      }
    } catch (error) {
      setAnalysisResult({ error: error instanceof Error ? error.message : 'SEO analysis failed' });
    } finally {
      setIsProcessing(false);
    }
  };

  const handleSuggest = async () => {
    if (!prompt.trim()) return;

    setIsProcessing(true);
    try {
      const response = await fetch('http://localhost:8000/ai/suggest', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          code: code || undefined
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
      } else {
        const error = await response.json();
        setAnalysisResult({ error: error.detail || 'Suggestion failed' });
      }
    } catch (error) {
      setAnalysisResult({ error: error instanceof Error ? error.message : 'Suggestion failed' });
    } finally {
      setIsProcessing(false);
    }
  };

  const getChartData = () => {
    if (!analysisResult || analysisResult.error) return null;

    return {
      labels: ['Performance', 'SEO', 'Accessibility'].filter(
        (_, i) => analysisResult.performance_score !== undefined ||
          analysisResult.seo_score !== undefined ||
          analysisResult.accessibility_score !== undefined
      ),
      datasets: [
        {
          label: 'Scores',
          data: [
            analysisResult.performance_score,
            analysisResult.seo_score,
            analysisResult.accessibility_score
          ].filter(score => score !== undefined),
          backgroundColor: [
            'rgba(54, 162, 235, 0.7)',
            'rgba(255, 99, 132, 0.7)',
            'rgba(75, 192, 192, 0.7)'
          ].slice(0, [
            analysisResult.performance_score,
            analysisResult.seo_score,
            analysisResult.accessibility_score
          ].filter(score => score !== undefined).length),
          borderColor: [
            'rgba(54, 162, 235, 1)',
            'rgba(255, 99, 132, 1)',
            'rgba(75, 192, 192, 1)'
          ].slice(0, [
            analysisResult.performance_score,
            analysisResult.seo_score,
            analysisResult.accessibility_score
          ].filter(score => score !== undefined).length),
          borderWidth: 1,
        },
      ],
    };
  };

  const getPieData = () => {
    if (!analysisResult || !analysisResult.optimization_potential) return null;

    return {
      labels: ['Optimized', 'Potential'],
      datasets: [
        {
          data: [
            100 - analysisResult.optimization_potential,
            analysisResult.optimization_potential
          ],
          backgroundColor: [
            'rgba(75, 192, 192, 0.7)',
            'rgba(153, 102, 255, 0.7)'
          ],
          borderColor: [
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)'
          ],
          borderWidth: 1,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Performance Analysis',
        font: {
          size: 16
        }
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function (value: any) {
            return value + '%';
          }
        }
      }
    }
  };

  const pieOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Optimization Potential',
        font: {
          size: 16
        }
      },
    },
  };

  // Reset analysis when changing tabs
  useEffect(() => {
    setAnalysisResult(null);
  }, [activeTab]);

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
            AI Optimization Tools
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Advanced AI-powered tools for code optimization and analysis
          </p>
        </motion.div>

        {/* Tool Tabs */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="flex flex-wrap gap-2 mb-8"
        >
          {tools.map((tool) => (
            <motion.button
              key={tool.id}
              onClick={() => setActiveTab(tool.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all ${activeTab === tool.id
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800'
                }`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <tool.icon className="w-4 h-4" />
              <span>{tool.label}</span>
            </motion.button>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.4 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Input
            </h3>

            {activeTab === 'analyze' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2 mb-2">
                  <label className="text-sm text-gray-600 dark:text-gray-300">File Type:</label>
                  <select
                    value={selectedFileType}
                    onChange={(e) => setSelectedFileType(e.target.value)}
                    className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm"
                  >
                    {fileTypes.map((type) => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="Paste your code here for analysis..."
                  className="w-full h-64 p-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm"
                />
                <motion.button
                  onClick={handleAnalyze}
                  disabled={!code.trim() || isProcessing}
                  className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 px-4 rounded-lg font-medium hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isProcessing ? (
                    <>
                      <RefreshCw className="w-4 h-4 inline mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Code className="w-4 h-4 inline mr-2" />
                      Analyze Code
                    </>
                  )}
                </motion.button>
              </div>
            )}

            {activeTab === 'convert' && (
              <div className="space-y-4">
                <div className="flex items-center space-x-2 mb-2">
                  <label className="text-sm text-gray-600 dark:text-gray-300">Source Type:</label>
                  <select
                    value={selectedFileType}
                    onChange={(e) => setSelectedFileType(e.target.value)}
                    className="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-sm"
                  >
                    {fileTypes.map((type) => (
                      <option key={type.value} value={type.value}>{type.label}</option>
                    ))}
                  </select>
                </div>
                <textarea
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  placeholder="Paste your code here for conversion..."
                  className="w-full h-48 p-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white font-mono text-sm"
                />
                <div className="grid grid-cols-2 gap-3">
                  {conversionTypes.map((conv) => (
                    <motion.button
                      key={`${conv.from}_${conv.to}`}
                      onClick={() => handleConvert(conv.from, conv.to)}
                      disabled={!code.trim() || isProcessing}
                      className="bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                    >
                      {conv.label}
                    </motion.button>
                  ))}
                </div>
              </div>
            )}

            {activeTab === 'seo' && (
              <div className="space-y-4">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter website URL to check..."
                  className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <motion.button
                  onClick={handleSeoCheck}
                  disabled={!url.trim() || isProcessing}
                  className="w-full bg-green-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Search className="w-4 h-4 inline mr-2" />
                  Check SEO
                </motion.button>
              </div>
            )}

            {activeTab === 'suggestions' && (
              <div className="space-y-4">
                <textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  placeholder="Describe what you want to optimize..."
                  className="w-full h-32 p-4 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <motion.button
                  onClick={handleSuggest}
                  disabled={!prompt.trim() || isProcessing}
                  className="w-full bg-gradient-to-r from-purple-500 to-pink-600 text-white py-3 px-4 rounded-lg font-medium hover:from-purple-600 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <Zap className="w-4 h-4 inline mr-2" />
                  Get AI Suggestions
                </motion.button>
              </div>
            )}
          </motion.div>

          {/* Results Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6"
          >
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Results
            </h3>

            {isProcessing ? (
              <div className="flex items-center justify-center h-64">
                <div className="text-center">
                  <RefreshCw className="w-8 h-8 text-blue-600 animate-spin mx-auto mb-4" />
                  <p className="text-gray-600 dark:text-gray-300">Processing...</p>
                </div>
              </div>
            ) : analysisResult ? (
              <div className="space-y-6">
                {analysisResult.error ? (
                  <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg text-red-600 dark:text-red-300">
                    <p className="font-medium">Error:</p>
                    <p>{analysisResult.error}</p>
                  </div>
                ) : (
                  <>
                    {(analysisResult.performance_score !== undefined ||
                      analysisResult.seo_score !== undefined ||
                      analysisResult.accessibility_score !== undefined) && (
                        <>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {getChartData() && (
                              <div className="h-64">
                                <Bar data={getChartData()} options={chartOptions} />
                              </div>
                            )}
                            {getPieData() && (
                              <div className="h-64">
                                <Pie data={getPieData()} options={pieOptions} />
                              </div>
                            )}
                          </div>
                          <div className="grid grid-cols-2 gap-4 mb-4">
                            {analysisResult.performance_score !== undefined && (
                              <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg">
                                <h4 className="font-medium text-blue-800 dark:text-blue-200">Performance</h4>
                                <p className="text-2xl font-bold text-blue-600 dark:text-blue-300">
                                  {analysisResult.performance_score}%
                                </p>
                              </div>
                            )}
                            {analysisResult.seo_score !== undefined && (
                              <div className="bg-pink-50 dark:bg-pink-900/20 p-4 rounded-lg">
                                <h4 className="font-medium text-pink-800 dark:text-pink-200">SEO</h4>
                                <p className="text-2xl font-bold text-pink-600 dark:text-pink-300">
                                  {analysisResult.seo_score}%
                                </p>
                              </div>
                            )}
                            {analysisResult.accessibility_score !== undefined && (
                              <div className="bg-teal-50 dark:bg-teal-900/20 p-4 rounded-lg">
                                <h4 className="font-medium text-teal-800 dark:text-teal-200">Accessibility</h4>
                                <p className="text-2xl font-bold text-teal-600 dark:text-teal-300">
                                  {analysisResult.accessibility_score}%
                                </p>
                              </div>
                            )}
                            {analysisResult.optimization_potential !== undefined && (
                              <div className="bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg">
                                <h4 className="font-medium text-purple-800 dark:text-purple-200">Optimization Potential</h4>
                                <p className="text-2xl font-bold text-purple-600 dark:text-purple-300">
                                  {analysisResult.optimization_potential}%
                                </p>
                              </div>
                            )}
                          </div>
                          {analysisResult.suggestions && (
                            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                              <h4 className="font-medium text-gray-900 dark:text-white mb-2">Optimization Suggestions</h4>
                              <ul className="list-disc pl-5 space-y-2 text-gray-800 dark:text-gray-200">
                                {analysisResult.suggestions.map((suggestion: string, index: number) => (
                                  <li key={index}>{suggestion}</li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </>
                      )}

                    {analysisResult.converted && (
                      <div className="space-y-4">
                        <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                          <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                            {analysisResult.message || 'Converted Code'}
                          </h4>
                          <pre className="text-sm text-gray-900 dark:text-white whitespace-pre-wrap font-mono">
                            {analysisResult.converted}
                          </pre>
                        </div>
                        <div className="flex space-x-2">
                          <motion.button
                            onClick={() => navigator.clipboard.writeText(analysisResult.converted || '')}
                            className="flex-1 bg-gray-600 text-white py-2 px-4 rounded-lg hover:bg-gray-700 transition-all"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <Copy className="w-4 h-4 inline mr-2" />
                            Copy Code
                          </motion.button>
                          <motion.button
                            onClick={() => {
                              const blob = new Blob([analysisResult.converted || ''], { type: 'text/plain' });
                              const url = URL.createObjectURL(blob);
                              const a = document.createElement('a');
                              a.href = url;
                              a.download = `converted.${analysisResult.message?.split('to ')[1] || 'txt'}`;
                              a.click();
                            }}
                            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-all"
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                          >
                            <Download className="w-4 h-4 inline mr-2" />
                            Download
                          </motion.button>
                        </div>
                      </div>
                    )}
                  </>
                )}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
                <div className="text-center">
                  <FileText className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <p>Results will appear here after processing</p>
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* Additional Tools */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.8 }}
          className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          {[
            {
              title: 'Performance Monitor',
              description: 'Real-time performance tracking',
              icon: Settings,
              color: 'blue'
            },
            {
              title: 'Code Quality Score',
              description: 'Get quality metrics for your code',
              icon: Zap,
              color: 'purple'
            },
            {
              title: 'Optimization History',
              description: 'Track your optimization progress',
              icon: FileText,
              color: 'green'
            }
          ].map((tool, index) => (
            <motion.div
              key={tool.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.9 + index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow cursor-pointer"
              whileHover={{ scale: 1.02 }}
            >
              <div className={`p-3 bg-${tool.color}-100 dark:bg-${tool.color}-900/30 rounded-lg w-fit mb-4`}>
                <tool.icon className={`w-6 h-6 text-${tool.color}-600 dark:text-${tool.color}-300`} />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {tool.title}
              </h3>
              <p className="text-gray-600 dark:text-gray-300">
                {tool.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </div>
  );
};