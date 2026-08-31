import { Injectable, inject } from '@angular/core';
import { ApiService } from '../../../core/api/api.service';
import {
  ParseTextResponse,
  Quote,
  QuoteListItem,
  VoiceToTextResponse,
} from '../models/quote.model';

@Injectable({ providedIn: 'root' })
export class QuoteApiService {
  private api = inject(ApiService);

  list(skip = 0, limit = 20) {
    return this.api.get<QuoteListItem[]>(`/quotes?skip=${skip}&limit=${limit}`);
  }

  get(id: number) {
    return this.api.get<Quote>(`/quotes/${id}`);
  }

  create(data: Partial<Quote>) {
    return this.api.post<Quote>('/quotes', data);
  }

  update(id: number, data: Partial<Quote>) {
    return this.api.put<Quote>(`/quotes/${id}`, data);
  }

  delete(id: number) {
    return this.api.delete(`/quotes/${id}`);
  }

  duplicate(id: number) {
    return this.api.post<Quote>(`/quotes/${id}/duplicate`, {});
  }

  parseText(text: string) {
    return this.api.post<ParseTextResponse>('/quotes/parse-text', { text });
  }

  voiceToText(audioBlob: Blob) {
    const formData = new FormData();
    formData.append('file', audioBlob, 'audio.webm');
    return this.api.upload<VoiceToTextResponse>('/quotes/voice-to-text', formData);
  }

  generatePdf(id: number) {
    return this.api.postBlob(`/quotes/${id}/generate-pdf`);
  }

  sendEmail(id: number, recipientEmail?: string) {
    return this.api.post<{ message: string }>(`/quotes/${id}/send-email`, {
      recipient_email: recipientEmail ?? null,
    });
  }
}
