import { isRouteErrorResponse, useRouteError } from 'react-router';

import type { ApiSchemas } from '@/shared/api/schema';

function isApiError(error: unknown): error is ApiSchemas['Error'] {
  return typeof error === 'object' && error !== null && 'message' in error && 'code' in error;
}

export function RootErrorBoundary() {
  const error = useRouteError();

  if (isRouteErrorResponse(error)) {
    return (
      <>
        <h1>{`${error.status} ${error.statusText}`}</h1>
        <p>{error.data}</p>
      </>
    );
  }

  if (isApiError(error)) {
    return (
      <div>
        <h1>Api Error</h1>
        <p>{`${error.code}: ${error.message}`}</p>
      </div>
    );
  }

  if (error instanceof Error) {
    return (
      <div>
        <h1>Error</h1>
        <p>{error.message}</p>
        <p>The stack trace is:</p>
        <pre>{error.stack}</pre>
      </div>
    );
  }

  return <h1>Unknown Error</h1>;
}
