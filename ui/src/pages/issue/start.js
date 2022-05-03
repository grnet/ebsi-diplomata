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

const fields = [
  {
    name: 'email',
    value: 'adal@gmail.com',
  },
  {
    name: 'name',
    value: ' Ada',
  },
  {
    name: 'surname',
    value: ' Lovelace',
  },
  {
    name: 'DID',
    value: 'XADFFRGRGVFV2232DFDFRF',
  },
]

export default function Start() {
  const router = useRouter();
  return (
    <CommonLayout>
      <Main>
        <Caption size='xl'>Issuance request</Caption>
        <Title>Overview of your data</Title>
        <SummaryList>
          {fields &&
            fields.map((field, index) => {
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
        < Button onClick={() => {
          router.push('/issue/action');
        }}>Confirm</Button>
      </Main>
    </CommonLayout>
  );
};
