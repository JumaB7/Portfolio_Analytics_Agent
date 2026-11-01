import { NgClass } from '@angular/common';
import {
  ChangeDetectionStrategy,
  Component,
  computed,
  inject,
  signal,
} from '@angular/core';
import { FormsModule } from '@angular/forms';
import { finalize } from 'rxjs';

import { ChatTurn } from '../../models/chat.models';
import { readApiErrorMessage } from '../../services/api-error';
import { ChatApiService } from '../../services/chat-api.service';
import { ToolResultsComponent } from '../tool-results/tool-results.component';

@Component({
  selector: 'app-chat-page',
  standalone: true,
  imports: [FormsModule, NgClass, ToolResultsComponent],
  templateUrl: './chat-page.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatPageComponent {
  private readonly chatApi = inject(ChatApiService);

  readonly draft = signal('');
  readonly turns = signal<ChatTurn[]>([]);
  readonly sending = signal(false);

  readonly samplePrompts = [
    'What were our total sales last month?',
    'Which product category generated the most revenue last month?',
    'How did sales change compared with the previous month?',
    'Which products have the lowest sales last month?',
  ] as const;

  readonly canSend = computed(() => this.draft().trim().length > 0 && !this.sending());

  useSample(prompt: string): void {
    this.draft.set(prompt);
  }

  send(): void {
    const message = this.draft().trim();
    if (!message || this.sending()) {
      return;
    }

    const turnId = crypto.randomUUID();
    this.turns.update((existing) => [
      {
        id: turnId,
        question: message,
        loading: true,
      },
      ...existing,
    ]);
    this.draft.set('');
    this.sending.set(true);

    this.chatApi
      .sendMessage(message)
      .pipe(finalize(() => this.sending.set(false)))
      .subscribe({
        next: (response) => {
          this.turns.update((existing) =>
            existing.map((turn) =>
              turn.id === turnId
                ? { ...turn, loading: false, response }
                : turn
            )
          );
        },
        error: (err: unknown) => {
          const detail = readApiErrorMessage(err);
          this.turns.update((existing) =>
            existing.map((turn) =>
              turn.id === turnId
                ? { ...turn, loading: false, error: detail }
                : turn
            )
          );
        },
      });
  }

  onEnter(event: Event): void {
    const keyboard = event as KeyboardEvent;
    if (keyboard.shiftKey) {
      return;
    }
    keyboard.preventDefault();
    this.send();
  }
}
