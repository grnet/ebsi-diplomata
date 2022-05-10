import React from 'react';
import NotFound from '@digigov/ui/app/NotFound';
import { Main, Side } from '@digigov/ui/layouts/Basic';
import CommonLayout from 'ui/components/CommonLayout';

const NotFoundPage = () => {
  return (
    <CommonLayout>
      <Main>
        <NotFound />
      </Main>
      <Side></Side>
    </CommonLayout>
  );
};

export default NotFoundPage;
