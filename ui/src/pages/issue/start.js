import React from 'react';
import { useRouter } from 'next/router';
import {
  SummaryList,
  SummaryListItem,
  SummaryListItemKey,
  SummaryListItemValue,
  Button,
  Caption,
  Title
} from '@digigov/ui';
import { Main } from '@digigov/ui/layouts/Basic';
import CommonLayout from 'ui/components/CommonLayout';
import { useUserDetails } from 'ui/auth';

export default function Start() {
  const { user, processing, error } = useUserDetails();
  return processing ? 'loading...' : (error ? 'error loading token' : (user ? <Inner user={user} /> : 'redirect to login'));
};

function Inner(props) {
  const router = useRouter();
  const user = props.user;
  return (
    <CommonLayout>
      <Main>
        <Caption size='xl'>Issuance request</Caption>
        <Title>Overview of your data</Title>
        <SummaryList>
          {user &&
            user.map((field, index) => {
              return (
                <SummaryListItem key={index}>
                  <SummaryListItemKey>
                    {field.name}
                  </SummaryListItemKey>
                  <SummaryListItemValue>
                    {field.value}
                  </SummaryListItemValue>
                </SummaryListItem>
              );
            })}
        </SummaryList>
        <Button onClick={() => {
          router.push('/issue/action');
        } }>Confirm</Button>
      </Main>
    </CommonLayout>
  );
}

