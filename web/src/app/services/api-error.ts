import { HttpErrorResponse } from '@angular/common/http';
import {
  API_ERROR_UNKNOWN,
  httpFailureMessage,
} from '../constants/api-error.constants';

export interface ApiErrorBody {
  code?: string;
  message?: string;
}

export function readApiErrorMessage(err: unknown): string {
  if (!(err instanceof HttpErrorResponse)) {
    return API_ERROR_UNKNOWN;
  }

  const detail = err.error?.detail;

  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }

  if (detail && typeof detail === 'object') {
    const body = detail as ApiErrorBody;
    if (body.message) {
      return body.code ? `${body.message} (${body.code})` : body.message;
    }
  }

  return httpFailureMessage(err.status);
}
