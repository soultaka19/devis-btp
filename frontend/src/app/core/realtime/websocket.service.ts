import { Injectable, signal } from '@angular/core';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { environment } from '../../../environments/environment';
import { retry, timer } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class WebSocketService {
  private socket$: WebSocketSubject<any> | null = null;
  readonly connected = signal(false);

  connect(path: string) {
    const token = localStorage.getItem('access_token');
    const url = `${environment.wsUrl}${path}?token=${token}`;

    this.socket$ = webSocket({
      url,
      openObserver: { next: () => this.connected.set(true) },
      closeObserver: { next: () => this.connected.set(false) },
    });

    return this.socket$.pipe(
      retry({ delay: () => timer(3000) })
    );
  }

  send(data: any) {
    this.socket$?.next(data);
  }

  disconnect() {
    this.socket$?.complete();
    this.socket$ = null;
    this.connected.set(false);
  }
}
