import React from 'react';
import { useRouter } from 'next/router';
import BackButton from '@digigov/ui/core/Button/BackButton';
import {
  SummaryList,
  SummaryListItem,
  SummaryListItemKey,
  SummaryListItemValue,
  Button,
  Caption,
  Title
} from '@digigov/ui';
import FormBuilder, {
  Fieldset,
  FieldsetLabel,
  FieldsetCaption,
  Field,
} from '@digigov/form';
import { Main } from '@digigov/ui/layouts/Basic';
import CommonLayout from 'ui/components/CommonLayout';

const fields = [
  {
    key: 'radio_choice',
    label: { primary: 'Choose' },
    type: 'choice:single',
    required: true,
    extra: {
      options: [
        {
          label: { primary: 'Issue a verifiable credential for your diploma' },
          value: 'value1',
        },
      ],
    },
  },
]

export default function Action() {
  const router = useRouter();
  return (
    <CommonLayout>
      <Main>
        <BackButton>Back</BackButton>
        {fields && <FormBuilder
          fields={fields}
          onSubmit={console.log('success')}
        >
          <Fieldset>
            <FieldsetCaption>Issuer actions</FieldsetCaption>
            <FieldsetLabel>How do you want to proceed?</FieldsetLabel>
            {fields.map((field) => (
              <Field key={field.key} name={field.key} />
            ))}
          </Fieldset>
          <Button type="submit" onClick={() => {
            router.push('/issue/request');
          }}>Continue</Button>
        </FormBuilder>}
      </Main>
    </CommonLayout>
  );
};
