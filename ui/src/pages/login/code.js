import PageTitle, { PageTitleHeading } from '@digigov/ui/app/PageTitle';
import { Main } from '@digigov/ui/layouts/Basic';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import CommonLayout from 'ui/components/CommonLayout';
import { TOKEN_KEY, useTokenFromCode } from '../../auth';

export default function LoginCode() {
  const router = useRouter();
  const code = router.asPath.split('#')[1];
  const { token, error } = useTokenFromCode(code);
  const handleToken = async (code, token) => {
    if (!code) {
      router.replace('/login');
    } else if (token) {
      window.localStorage.setItem(TOKEN_KEY, token);
      router.replace('/issue/start');
    }
  }
  useEffect(() => {
    handleToken(code, token);
  }, [token, code]);
  return (
    <CommonLayout>
      <Main>
        <PageTitle>
          <PageTitleHeading>Identification required</PageTitleHeading>
        </PageTitle>
        {error ? 'Error' : 'Loading...'}
      </Main>
    </CommonLayout>
  );
}