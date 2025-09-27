import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translation files
import enItems from './locales/en/items.json';
import thItems from './locales/th/items.json';
import enSettings from './locales/en/settings.json';
import thSettings from './locales/th/settings.json';

const resources = {
  en: {
    items: enItems,
    settings: enSettings,
  },
  th: {
    items: thItems,
    settings: thSettings,
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'en',
    debug: process.env.NODE_ENV === 'development',
    
    interpolation: {
      escapeValue: false, // React already does escaping
    },
    
    // Language detection options
    detection: {
      order: ['localStorage', 'navigator', 'htmlTag'],
      caches: ['localStorage'],
    },
    
    // Namespace configuration
    ns: ['items', 'settings'],
    defaultNS: 'items',
  });

export default i18n;
