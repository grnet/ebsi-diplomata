import React, { useEffect } from 'react';
import { Main } from '@digigov/ui/layouts/Basic';
import Paragraph from '@digigov/ui/typography/Paragraph';
import { Button, Title, Caption } from '@digigov/ui';
import CommonLayout from 'ui/components/CommonLayout';

export default function Request() {
  return (
    <CommonLayout>
      <Main>
        <Caption size='xl'>Issuance request</Caption>
        <Title>
          You have requested diploma credential issuance. Proceed?
        </Title>
        <Button onClick={() => { }}>Issue</Button>
      </Main>
    </CommonLayout>
  );
};