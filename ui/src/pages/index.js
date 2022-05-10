import React, { useEffect } from 'react';
import { useTranslation } from '@digigov/ui/app/i18n';
import { Main } from '@digigov/ui/layouts/Basic';
import CallToAction from '@digigov/ui/core/Button/CallToAction';
import Paragraph from '@digigov/ui/typography/Paragraph';
import { Title } from '@digigov/ui';
import CommonLayout from 'ui/components/CommonLayout';

const Home = () => {
  const { t, i18n } = useTranslation();
  useEffect(() => {
    i18n.changeLanguage('en');
    localStorage.setItem('locale', 'en');
  }, [i18n]);
  return (
    <CommonLayout>
      <Main>
        <Title>{t('app.name')}</Title>
        <Paragraph>{t('app.intro_text')}</Paragraph>
        <CallToAction href="/login">{t('button.start')}</CallToAction>
      </Main>
    </CommonLayout>
  );
};

export default Home;
