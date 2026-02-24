import { Component, inject, input, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { VoiceRecorderService } from '../../services/voice-recorder.service';
import { QuoteApiService } from '../../services/quote-api.service';

@Component({
  selector: 'app-voice-input-button',
  standalone: true,
  imports: [MatButtonModule, MatIconModule, TranslateModule],
  template: `
    <button class="mic-btn" [class.recording]="voiceService.isRecording()"
            [class.inline]="inline()"
            (click)="toggleRecording()">
      <mat-icon>{{ voiceService.isRecording() ? 'stop' : 'mic' }}</mat-icon>
      @if (!inline()) {
        <div class="wave wave-1" [class.active]="voiceService.isRecording()"></div>
        <div class="wave wave-2" [class.active]="voiceService.isRecording()"></div>
        <div class="wave wave-3" [class.active]="voiceService.isRecording()"></div>
      }
    </button>
    @if (!inline() && voiceService.isRecording()) {
      <span class="recording-label">{{ 'QUOTE.RECORDING' | translate }}</span>
    }
    @if (!inline() && voiceService.error()) {
      <span class="error-label">{{ voiceService.error() }}</span>
    }
  `,
  styles: [`
    :host {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .mic-btn {
      position: relative;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      border: none;
      background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
      color: white;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.3s ease;
      box-shadow: 0 2px 8px rgba(var(--accent-rgb), 0.3);
      flex-shrink: 0;

      mat-icon {
        z-index: 2;
        position: relative;
      }

      &:hover {
        transform: scale(1.05);
        box-shadow: 0 4px 16px rgba(var(--accent-rgb), 0.4);
      }

      &.recording {
        background: linear-gradient(135deg, var(--danger) 0%, #E74C3C 100%);
        box-shadow: 0 2px 8px rgba(192, 57, 43, 0.4);
        animation: pulse 1.5s infinite;
      }

      /* Inline mode: smaller, flat, no shadow */
      &.inline {
        width: 36px;
        height: 36px;
        background: transparent;
        color: var(--text-secondary);
        box-shadow: none;

        mat-icon {
          font-size: 22px;
          width: 22px;
          height: 22px;
        }

        &:hover {
          color: var(--primary);
          background: rgba(0, 0, 0, 0.04);
          transform: none;
          box-shadow: none;
        }

        &.recording {
          color: white;
          background: linear-gradient(135deg, var(--danger) 0%, #E74C3C 100%);
          box-shadow: 0 0 0 3px rgba(192, 57, 43, 0.2);
        }
      }
    }

    /* Concentric wave rings */
    .wave {
      position: absolute;
      border-radius: 50%;
      border: 2px solid var(--danger);
      opacity: 0;
      pointer-events: none;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      width: 48px;
      height: 48px;

      &.active {
        animation: wave-expand 2s infinite;
      }

      &.wave-2.active { animation-delay: 0.4s; }
      &.wave-3.active { animation-delay: 0.8s; }
    }

    @keyframes wave-expand {
      0% {
        width: 48px;
        height: 48px;
        opacity: 0.6;
      }
      100% {
        width: 80px;
        height: 80px;
        opacity: 0;
      }
    }

    @keyframes pulse {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.08); }
    }

    .recording-label {
      color: var(--danger);
      font-size: 13px;
      font-weight: 500;
      animation: blink 1.5s infinite;
    }

    @keyframes blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.5; }
    }

    .error-label {
      color: var(--danger);
      font-size: 12px;
    }
  `],
})
export class VoiceInputButtonComponent {
  voiceService = inject(VoiceRecorderService);
  private quoteApi = inject(QuoteApiService);

  inline = input(false);
  transcriptReady = output<string>();

  async toggleRecording() {
    if (this.voiceService.isRecording()) {
      const blob = this.voiceService.stopRecording();

      const transcript = this.voiceService.transcript();
      if (transcript) {
        this.transcriptReady.emit(transcript);
        return;
      }

      if (blob) {
        this.quoteApi.voiceToText(blob).subscribe({
          next: (res) => this.transcriptReady.emit(res.text),
        });
      }
    } else {
      await this.voiceService.startRecording();
    }
  }
}
