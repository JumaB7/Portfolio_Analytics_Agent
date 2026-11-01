/** FastAPI-style error detail when `detail` is an object. */
export interface ApiErrorBody {
  code?: string;
  message?: string;
}
