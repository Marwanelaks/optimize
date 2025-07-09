import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface TypingAnimationProps {
  text: string;
  className?: string;
}

export const TypingAnimation: React.FC<TypingAnimationProps> = ({ text, className = '' }) => {
  const [displayText, setDisplayText] = useState('');
  const [isTyping, setIsTyping] = useState(true);

  useEffect(() => {
    let index = 0;
    const timer = setInterval(() => {
      if (index < text.length) {
        setDisplayText(text.slice(0, index + 1));
        index++;
      } else {
        setIsTyping(false);
        clearInterval(timer);
      }
    }, 100);

    return () => clearInterval(timer);
  }, [text]);

  return (
    <div className={className}>
      {displayText}
      {isTyping && (
        <motion.span
          className="ml-1 text-blue-500"
          animate={{ opacity: [0, 1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity }}
        >
          |
        </motion.span>
      )}
    </div>
  );
};