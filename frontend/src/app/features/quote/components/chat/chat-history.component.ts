import { Component, input, effect, ElementRef, viewChild } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { ChatMessage } from '../../models/quote.model';

@Component({
  selector: 'app-chat-history',
  standalone: true,
  imports: [MatIconModule, TranslateModule],
  template: `
    <div class="chat-container" #chatContainer>
      @for (msg of messages(); track msg.timestamp) {
        <div class="chat-bubble" [class.user]="msg.role === 'user'" [class.ai]="msg.role === 'ai'">
          @if (msg.role === 'user') {
            <mat-icon class="bubble-icon">person</mat-icon>
            <div class="bubble-content">{{ msg.text }}</div>
          } @else {
            <mat-icon class="bubble-icon">smart_toy</mat-icon>
            <div class="bubble-content">
              <span class="summary">{{ msg.text }}</span>
              @if (msg.items?.length) {
                <button class="expand-btn" (click)="toggleExpand(msg)">
                  {{ msg.expanded ? ('QUOTE.HIDE' | translate) : ('QUOTE.SHOW_DETAIL' | translate) }}
                </button>
                @if (msg.expanded) {
                  <ul class="items-list">
                    @for (item of msg.items; track item.description) {
                      <li>{{ item.quantity }} {{ item.unit }} — {{ item.description }} — {{ item.unit_price }}€</li>
                    }
                  </ul>
                }
              }
            </div>
          }
        </div>
      }
      @if (isParsing()) {
        <div class="chat-bubble ai typing">
          <mat-icon class="bubble-icon">smart_toy</mat-icon>
          <div class="bubble-content">
            <span class="typing-dots">{{ 'QUOTE.ANALYZING' | translate }}</span>
          </div>
        </div>
      }
    </div>
  `,
  styles: [`
    .chat-container {
      display: flex;
      flex-direction: column;
      gap: 12px;
      max-height: 300px;
      overflow-y: auto;
      padding: 8px 4px;
    }

    .chat-bubble {
      display: flex;
      gap: 10px;
      max-width: 85%;
      animation: fadeIn 0.3s ease;

      &.user {
        align-self: flex-end;
        flex-direction: row-reverse;

        .bubble-content {
          background: var(--primary);
          color: white;
          border-radius: 16px 16px 4px 16px;
        }

        .bubble-icon {
          color: var(--primary) !important;
        }
      }

      &.ai {
        align-self: flex-start;

        .bubble-content {
          background: var(--surface);
          color: var(--text-primary);
          border: 1px solid var(--border);
          border-radius: 16px 16px 16px 4px;
        }

        .bubble-icon {
          color: var(--accent) !important;
        }
      }
    }

    .bubble-icon {
      flex-shrink: 0;
      margin-top: 4px;
      font-size: 20px;
      width: 20px;
      height: 20px;
    }

    .bubble-content {
      padding: 10px 14px;
      font-size: 13px;
      line-height: 1.5;
    }

    .summary {
      font-weight: 500;
    }

    .expand-btn {
      display: inline-block;
      margin-top: 6px;
      background: none;
      border: none;
      color: var(--primary);
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      padding: 0;
      text-decoration: underline;

      &:hover {
        color: var(--primary-dark, var(--primary));
      }
    }

    .items-list {
      margin: 8px 0 0;
      padding-left: 16px;
      font-size: 12px;
      color: var(--text-secondary);

      li {
        margin-bottom: 4px;
      }
    }

    .typing .typing-dots {
      &::after {
        content: '';
        animation: dots 1.5s steps(4, end) infinite;
      }
    }

    @keyframes dots {
      0%   { content: ''; }
      25%  { content: '.'; }
      50%  { content: '..'; }
      75%  { content: '...'; }
      100% { content: ''; }
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(8px); }
      to   { opacity: 1; transform: translateY(0); }
    }
  `],
})
export class ChatHistoryComponent {
  messages = input<ChatMessage[]>([]);
  isParsing = input<boolean>(false);

  private chatContainer = viewChild<ElementRef>('chatContainer');

  constructor() {
    effect(() => {
      this.messages();
      this.isParsing();
      setTimeout(() => this.scrollToBottom());
    });
  }

  toggleExpand(msg: ChatMessage) {
    msg.expanded = !msg.expanded;
  }

  private scrollToBottom() {
    const el = this.chatContainer()?.nativeElement;
    if (el) {
      el.scrollTop = el.scrollHeight;
    }
  }
}
