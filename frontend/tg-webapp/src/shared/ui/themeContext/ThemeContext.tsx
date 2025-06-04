import React, { createContext, useState, useContext, ReactNode } from 'react';
import { Theme } from '../../types';


interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode,
  initTheme?: 'light' | 'dark',
}

export const ThemeProvider = ({ children, initTheme }: ThemeProviderProps) => {
  const [theme, setTheme] = useState<Theme>(initTheme ?? 'light');

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
