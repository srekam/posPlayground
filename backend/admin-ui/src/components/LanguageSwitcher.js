import React from 'react';
import { Button, ButtonGroup } from '@mui/material';
import { useTranslation } from 'react-i18next';

const LanguageSwitcher = () => {
  const { i18n } = useTranslation();

  const handleLanguageChange = (language) => {
    i18n.changeLanguage(language);
  };

  return (
    <ButtonGroup size="small" variant="outlined">
      <Button 
        onClick={() => handleLanguageChange('en')}
        color={i18n.language === 'en' ? 'primary' : 'inherit'}
        variant={i18n.language === 'en' ? 'contained' : 'outlined'}
      >
        EN
      </Button>
      <Button 
        onClick={() => handleLanguageChange('th')}
        color={i18n.language === 'th' ? 'primary' : 'inherit'}
        variant={i18n.language === 'th' ? 'contained' : 'outlined'}
      >
        TH
      </Button>
    </ButtonGroup>
  );
};

export default LanguageSwitcher;
