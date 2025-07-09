import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ThemeProvider } from './contexts/ThemeContext';
import { Navigation } from './components/Navigation';
import { LandingPage } from './components/LandingPage';
import { Dashboard } from './components/Dashboard';
import { AITools } from './components/AITools';

function App() {
  const [currentSection, setCurrentSection] = useState('home');

  const handleNavigate = (section: string) => {
    setCurrentSection(section);
  };

  const renderContent = () => {
    switch (currentSection) {
      case 'home':
        return <LandingPage onNavigate={handleNavigate} />;
      case 'app':
      case 'dashboard':
        return <Dashboard onNavigate={handleNavigate} />;
      case 'ai-tools':
        return <AITools />;
      default:
        return <LandingPage onNavigate={handleNavigate} />;
    }
  };

  const isLandingPage = currentSection === 'home';

  return (
    <ThemeProvider>
      <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors duration-300">
        <Navigation onNavigate={handleNavigate} isLandingPage={isLandingPage} />
        
        <AnimatePresence mode="wait">
          <motion.div
            key={currentSection}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {renderContent()}
          </motion.div>
        </AnimatePresence>
      </div>
    </ThemeProvider>
  );
}

export default App;