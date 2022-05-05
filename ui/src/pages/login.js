import React from 'react';
import { Main } from '@digigov/ui/layouts/Basic';
import PageTitle, { PageTitleHeading } from '@digigov/ui/app/PageTitle';
import { Paragraph } from '@digigov/ui/typography';
import { ButtonLink } from '@digigov/ui/core/Button';
import { ArrowIcon } from '@digigov/react-core';
import CommonLayout from 'ui/components/CommonLayout';
import { useRouter } from 'next/router';

export default function LoginPage() {
  const router = useRouter();
  return (
    <CommonLayout>
      <Main>
        <PageTitle>
          <PageTitleHeading>Identification required</PageTitleHeading>
        </PageTitle>
        <Paragraph>You will need to login using your wallet credentials.</Paragraph>
        <Paragraph>
          <ButtonLink href="/api/v1/google/login">
            Login with wallet
            <ArrowIcon />
          </ButtonLink>
        </Paragraph>
      </Main>
    </CommonLayout>
  );
}