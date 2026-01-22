import { Link } from 'react-router';

import { ROUTES } from '@/shared/model/routes';

import { AuthLayout } from './ui/auth-layout';
import { LoginForm } from './ui/login-form';

function LoginPage() {
  return (
    <AuthLayout
      title="Авторизация"
      description="Введите ваш email и пароль для авторизации"
      form={<LoginForm />}
      footerText={(
        <>
          Нет аккаунта?
          {' '}
          <Link to={ROUTES.REGISTER}>Зарегистрироваться</Link>
        </>
      )}
    />
  );
}

export const Component = LoginPage;
