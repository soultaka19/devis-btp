import { Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { TranslateModule, TranslateService } from '@ngx-translate/core';
import { VoiceInputButtonComponent } from '../voice/voice-input-button.component';
import { ChatHistoryComponent } from '../chat/chat-history.component';
import { ChatMessage } from '../../models/quote.model';

@Component({
  selector: 'app-quote-input-panel',
  standalone: true,
  imports: [
    FormsModule,
    MatIconModule,
    MatProgressSpinnerModule,
    TranslateModule,
    VoiceInputButtonComponent,
    ChatHistoryComponent,
  ],
  template: `
    <div class="input-panel">
      <div class="panel-header">
        <mat-icon class="panel-icon">edit_note</mat-icon>
        <h3>{{ 'QUOTE.WORK_DESCRIPTION' | translate }}</h3>
      </div>

      <!-- Chat history -->
      @if (chatMessages().length || parsingStatus() === 'parsing') {
        <app-chat-history
          [messages]="chatMessages()"
          [isParsing]="parsingStatus() === 'parsing'"
        />
      }

      <!-- Chat input bar -->
      <div class="chat-input-bar">
        <app-voice-input-button [inline]="true" (transcriptReady)="onTranscript($event)" />

        <input type="text" class="chat-input"
               [(ngModel)]="text"
               [placeholder]="'QUOTE.PLACEHOLDER' | translate"
               (keydown.enter)="onParse()" />

        <button class="send-btn" (click)="onParse()"
                [disabled]="!text || parsingStatus() === 'parsing'">
          @if (parsingStatus() === 'parsing') {
            <mat-spinner diameter="20"></mat-spinner>
          } @else {
            <mat-icon>send</mat-icon>
          }
        </button>
      </div>
    </div>
  `,
  styles: [`
    .input-panel {
      background: white;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 24px;
    }

    .panel-header {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 16px;

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
      }
    }

    .panel-icon {
      color: var(--primary) !important;
    }

    .chat-input-bar {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 6px 6px 6px 8px;
      border: 1px solid var(--border);
      border-radius: 24px;
      background: var(--surface);
      transition: border-color 0.2s ease, box-shadow 0.2s ease;

      &:focus-within {
        border-color: var(--primary-light);
        box-shadow: 0 0 0 3px rgba(27, 42, 74, 0.08);
      }
    }

    .chat-input {
      flex: 1;
      border: none;
      outline: none;
      background: transparent;
      font-family: inherit;
      font-size: 14px;
      color: var(--text-primary);
      padding: 8px 4px;
      min-width: 0;

      &::placeholder {
        color: var(--text-secondary);
        opacity: 0.7;
      }
    }

    .send-btn {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      border: none;
      background: var(--primary);
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      transition: background 0.2s ease, transform 0.15s ease;

      mat-icon {
        font-size: 20px;
        width: 20px;
        height: 20px;
      }

      &:hover:not(:disabled) {
        background: var(--primary-dark, var(--primary));
        transform: scale(1.05);
      }

      &:disabled {
        background: var(--border);
        color: var(--text-secondary);
        cursor: not-allowed;
      }
    }
  `],
})
export class QuoteInputPanelComponent {
  parsingStatus = input<'idle' | 'parsing' | 'done' | 'error'>('idle');
  chatMessages = input<ChatMessage[]>([]);
  parseRequest = output<string>();

  text = '';

  onParse() {
    if (this.text.trim()) {
      this.parseRequest.emit(this.text.trim());
      this.text = '';
    }
  }

  onTranscript(transcript: string) {
    this.text = this.text ? this.text + ' ' + transcript : transcript;
  }
}
