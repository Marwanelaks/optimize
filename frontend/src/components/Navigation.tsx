import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Menu, X, Zap } from 'lucide-react';
import { ThemeToggle } from './ThemeToggle';

interface NavigationProps {
  onNavigate: (section: string) => void;
  isLandingPage?: boolean;
}

export const Navigation: React.FC<NavigationProps> = ({ onNavigate, isLandingPage = true }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const menuItems = isLandingPage
    ? [
        { label: 'Features', href: '#features' },
        { label: 'Pricing', href: '#pricing' },
        { label: 'About', href: '#about' },
      ]
    : [
        { label: 'Dashboard', href: '#dashboard' },
        { label: 'AI Tools', href: '#ai-tools' },
        { label: 'Projects', href: '#projects' },
      ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200/20 dark:border-gray-800/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div
            className="flex items-center space-x-2 cursor-pointer"
            whileHover={{ scale: 1.05 }}
            onClick={() => onNavigate('home')}
          >
            <div className="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold text-gray-900 dark:text-white">OptimizeAI</span>
          </motion.div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center space-x-8">
            {menuItems.map((item) => (
              <motion.a
                key={item.label}
                href={item.href}
                className="text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer"
                whileHover={{ scale: 1.05 }}
                onClick={(e) => {
                  e.preventDefault();
                  onNavigate(item.href.replace('#', ''));
                }}
              >
                {item.label}
              </motion.a>
            ))}
          </div>

          {/* Actions */}
          <div className="flex items-center space-x-4">
            <ThemeToggle />
            {isLandingPage && (
              <motion.button
                className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onNavigate('app')}
              >
                Get Started
              </motion.button>
            )}
            
            {/* Mobile menu button */}
            <motion.button
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
              whileTap={{ scale: 0.95 }}
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? (
                <X className="w-6 h-6 text-gray-700 dark:text-gray-300" />
              ) : (
                <Menu className="w-6 h-6 text-gray-700 dark:text-gray-300" />
              )}
            </motion.button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden py-4 border-t border-gray-200 dark:border-gray-800"
          >
            {menuItems.map((item) => (
              <motion.a
                key={item.label}
                href={item.href}
                className="block py-2 text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer"
                onClick={(e) => {
                  e.preventDefault();
                  onNavigate(item.href.replace('#', ''));
                  setIsMenuOpen(false);
                }}
              >
                {item.label}
              </motion.a>
            ))}
          </motion.div>
        )}
      </div>
    </nav>
  );
};