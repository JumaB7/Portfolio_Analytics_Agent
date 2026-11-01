import { HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';

import {
  API_ERROR_BY_STATUS,
  API_ERROR_UNKNOWN,
} from '../constants/api-error.constants';
import { ApiErrorBody } from '../models/api-error.models';

/** Maps HTTP / API failures to user-facing copy. */
@Injectable({ providedIn: 'root' })
export class ApiErrorService {
  messageFromUnknown(err: unknown): string {
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

    return API_ERROR_BY_STATUS[err.status] ?? API_ERROR_UNKNOWN;
  }
}
