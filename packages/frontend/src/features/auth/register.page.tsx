import { Link } from 'react-router';

import { ROUTES } from '@/shared/model/routes';

import { AuthLayout } from './ui/auth-layout';
import { RegisterForm } from './ui/register-form';

function RegisterPage() {
  return (
    <AuthLayout
      title="Регистрация"
      description="Введите ваш email и пароль для регистрации"
      form={<RegisterForm />}
      footerText={(
        <>
          Уже есть аккаунт?
          {' '}
          <Link to={ROUTES.LOGIN}>Войти</Link>
        </>
      )}
    />
  );
}

export const Component = RegisterPage;
