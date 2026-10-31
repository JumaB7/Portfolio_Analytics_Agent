import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { ChatRequest, ChatResponse } from '../models/chat.models';

@Injectable({ providedIn: 'root' })
export class ChatApiService {
  private readonly http = inject(HttpClient);

  sendMessage(message: string): Observable<ChatResponse> {
    const body: ChatRequest = { message };
    return this.http.post<ChatResponse>('/api/chat', body);
  }
}
