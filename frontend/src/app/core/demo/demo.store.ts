import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, tap } from 'rxjs';
import { ApiService } from '../api/api.service';
import { SandboxSession, SandboxStatus } from './demo.model';

/**
 * State of the disposable demo sandbox.
 *
 * The visitor must know, at all times, two things the backend enforces: when
 * the space disappears, and how many AI attempts are left. Both are read from
 * the API, never guessed - the countdown is cosmetic, the expiry is the
 * server's.
 */
@Injectable({ providedIn: 'root' })
export class DemoStore {
  private api = inject(ApiService);

  readonly expiresAt = signal<Date | null>(null);
  readonly aiCallsTotal = signal(0);
  readonly aiCallsRemaining = signal(0);

  /** Ticks every second so the countdown recomputes. Only runs in a sandbox. */
  private now = signal(Date.now());
  private ticker: ReturnType<typeof setInterval> | null = null;

  readonly isDemo = computed(() => this.expiresAt() !== null);

  readonly secondsLeft = computed(() => {
    const end = this.expiresAt();
    if (!end) return 0;
    return Math.max(0, Math.floor((end.getTime() - this.now()) / 1000));
  });

  readonly expired = computed(() => this.isDemo() && this.secondsLeft() === 0);

  /** `mm:ss`, or `h min` above an hour - a ticking second is noise at that range. */
  readonly timeLeft = computed(() => {
    const total = this.secondsLeft();
    if (total >= 3600) {
      const hours = Math.floor(total / 3600);
      const minutes = Math.floor((total % 3600) / 60);
      return `${hours} h ${String(minutes).padStart(2, '0')}`;
    }
    const minutes = Math.floor(total / 60);
    const seconds = total % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  });

  create(): Observable<SandboxSession> {
    return this.api
      .post<SandboxSession>('/demo/sandbox', {})
      .pipe(
        tap((session) =>
          this.adopt(session.sandbox_expires_at, session.ai_calls_total, session.ai_calls_remaining)
        )
      );
  }

  /**
   * Ask the API what the stored token is worth.
   *
   * Needed after a page reload: the token survives in localStorage, the
   * countdown does not.
   */
  refresh(): void {
    this.api.get<SandboxStatus>('/demo/status').subscribe({
      next: (status) => {
        if (status.is_demo && status.sandbox_expires_at) {
          this.adopt(
            status.sandbox_expires_at,
            status.ai_calls_total ?? 0,
            status.ai_calls_remaining ?? 0
          );
        } else {
          this.clear();
        }
      },
      error: () => this.clear(),
    });
  }

  /**
   * Record the attempts left, as reported by an AI answer.
   *
   * Every answer carries the count, cached or not, so the banner stays exact
   * without a second round trip - and a cached answer visibly costs nothing.
   */
  noteRemaining(remaining: number | null | undefined): void {
    if (typeof remaining === 'number') {
      this.aiCallsRemaining.set(Math.max(0, remaining));
    }
  }

  clear(): void {
    this.expiresAt.set(null);
    this.aiCallsTotal.set(0);
    this.aiCallsRemaining.set(0);
    this.stopTicking();
  }

  private adopt(expiresAt: string, total: number, remaining: number): void {
    this.expiresAt.set(new Date(expiresAt));
    this.aiCallsTotal.set(total);
    this.aiCallsRemaining.set(Math.max(0, remaining));
    this.startTicking();
  }

  private startTicking(): void {
    if (this.ticker !== null || typeof setInterval === 'undefined') return;
    this.now.set(Date.now());
    this.ticker = setInterval(() => this.now.set(Date.now()), 1000);
  }

  private stopTicking(): void {
    if (this.ticker !== null) {
      clearInterval(this.ticker);
      this.ticker = null;
    }
  }
}
