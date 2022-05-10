import React, { useEffect } from 'react';
import Head from 'next/head';
import { useTranslation } from '@digigov/ui/app/i18n';
import { useRouter } from 'next/router';
import BasicLayout, { Top, Content, Bottom } from '@digigov/ui/layouts/Basic';
import Header, {
  HeaderTitle,
  HeaderContent,
  HeaderSection,
} from '@digigov/ui/app/Header';
import GovGRLogo from '@digigov/ui/govgr/Logo';
import GovGRFooter from '@digigov/ui/govgr/Footer';

const CommonLayout = ({ children }) => {
  const { t, i18n } = useTranslation();
  useEffect(() => {
    i18n.changeLanguage('en');
    localStorage.setItem('locale', 'en');
  }, [i18n]);
  const router = useRouter();
  const notHome = router.asPath !== '/';
  return (
    <BasicLayout>
      <Head />
      <Top>
        <Header>
          <HeaderSection>
            <HeaderContent>
              <GovGRLogo />
              {notHome && (
                <>
                  <HeaderTitle>{t('app.name')}</HeaderTitle>
                </>
              )}
            </HeaderContent>
          </HeaderSection>
        </Header>
      </Top>
      <Content>{children}</Content>
      <Bottom>
        <GovGRFooter />
      </Bottom>
    </BasicLayout>
  );
};

export default CommonLayout;
