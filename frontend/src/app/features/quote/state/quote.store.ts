import { Injectable, computed, inject, signal } from '@angular/core';
import { ChatMessage, LineItem, ParsedClientInfo, Quote, QuoteListItem } from '../models/quote.model';
import { QuoteApiService } from '../services/quote-api.service';
import { LanguageService } from '../../../core/i18n/language.service';
import { DemoStore } from '../../../core/demo/demo.store';

@Injectable({ providedIn: 'root' })
export class QuoteStore {
  private api = inject(QuoteApiService);
  private lang = inject(LanguageService);
  private demo = inject(DemoStore);

  readonly draftQuote = signal<Partial<Quote>>({
    client_name: '',
    client_address: '',
    client_email: '',
    client_phone: '',
    title: '',
    description: '',
    line_items: [],
  });

  readonly lineItems = signal<LineItem[]>([]);
  readonly chatMessages = signal<ChatMessage[]>([]);
  readonly quotes = signal<QuoteListItem[]>([]);
  readonly currentQuote = signal<Quote | null>(null);
  readonly loading = signal(false);
  readonly parsingStatus = signal<'idle' | 'parsing' | 'done' | 'error'>('idle');
  readonly error = signal<string | null>(null);

  readonly totals = computed(() => {
    const items = this.lineItems();
    let subtotalHt = 0;
    let totalVat = 0;

    for (const item of items) {
      const ht = item.quantity * item.unit_price;
      subtotalHt += ht;
      totalVat += ht * item.vat_rate / 100;
    }

    return {
      subtotal_ht: Math.round(subtotalHt * 100) / 100,
      total_vat: Math.round(totalVat * 100) / 100,
      total_ttc: Math.round((subtotalHt + totalVat) * 100) / 100,
    };
  });

  loadQuotes() {
    this.loading.set(true);
    this.api.list().subscribe({
      next: (quotes) => {
        this.quotes.set(quotes);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || this.lang.instant('QUOTE_STORE.ERROR_LOAD'));
        this.loading.set(false);
      },
    });
  }

  loadQuote(id: number) {
    this.chatMessages.set([]);
    this.parsingStatus.set('idle');
    this.error.set(null);
    this.loading.set(true);
    this.api.get(id).subscribe({
      next: (quote) => {
        this.currentQuote.set(quote);
        this.lineItems.set(quote.line_items);
        this.draftQuote.set(quote);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail || this.lang.instant('QUOTE_STORE.ERROR_LOAD'));
        this.loading.set(false);
      },
    });
  }

  parseText(text: string) {
    if (this.isEmailCommand(text)) {
      this.chatMessages.update((msgs) => [
        ...msgs,
        { role: 'user' as const, text, timestamp: new Date() },
      ]);
      this.sendEmail();
      return;
    }

    if (this.isPdfCommand(text)) {
      this.chatMessages.update((msgs) => [
        ...msgs,
        { role: 'user' as const, text, timestamp: new Date() },
      ]);
      this.downloadPdf();
      return;
    }

    this.parsingStatus.set('parsing');
    this.chatMessages.update((msgs) => [
      ...msgs,
      { role: 'user' as const, text, timestamp: new Date() },
    ]);
    this.api.parseText(text).subscribe({
      next: (result) => {
        // Every answer reports the attempts left, cached or not: the banner
        // must never claim more than the server will grant.
        this.demo.noteRemaining(result.ai_calls_remaining);
        const items = result.line_items;
        if (result.title) {
          this.draftQuote.update((d) => d.title ? d : { ...d, title: result.title });
        }
        if (result.client) {
          this.applyClientInfo(result.client);
        }
        const summary = this.buildAiSummary(items, result.client);
        this.chatMessages.update((msgs) => [
          ...msgs,
          { role: 'ai' as const, text: summary, items, expanded: false, timestamp: new Date() },
        ]);
        this.addItemsProgressively(items);
      },
      error: (err) => {
        if (err.error?.code === 'AI_QUOTA_EXHAUSTED') {
          this.demo.noteRemaining(0);
        }
        // A quota or budget refusal carries an explanatory message: showing the
        // generic parsing error instead would leave the visitor guessing.
        this.chatMessages.update((msgs) => [
          ...msgs,
          {
            role: 'ai' as const,
            text: err.error?.detail || this.lang.instant('QUOTE_STORE.ERROR_PARSING'),
            timestamp: new Date(),
          },
        ]);
        this.parsingStatus.set('error');
      },
    });
  }

  private isEmailCommand(text: string): boolean {
    const lower = text.toLowerCase().trim();
    const hasEmail = /mail|email|e-mail/.test(lower);
    const hasAction = /envoi|envoie|envoyer|transmet|transmettre|exp[ée]di|send/.test(lower);
    const hasTarget = /devis|facture|document|quote/.test(lower);
    return hasAction && (hasEmail || hasTarget);
  }

  private isPdfCommand(text: string): boolean {
    const lower = text.toLowerCase().trim();
    const hasPdf = lower.includes('pdf');
    const hasAction = /t[ée]l[ée]charge|g[ée]n[èe]re|exporte|imprime|download|generate/.test(lower);
    const hasTarget = /devis|facture|document|quote/.test(lower);
    return hasPdf && (hasAction || hasTarget);
  }

  downloadPdf() {
    const draft = this.draftQuote();
    const quoteId = draft.id as number | undefined;

    if (!quoteId) {
      this.chatMessages.update((msgs) => [
        ...msgs,
        { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.SAVING_BEFORE_PDF'), timestamp: new Date() },
      ]);
      this.loading.set(true);
      const data = { ...draft, line_items: this.lineItems() };
      this.api.create(data).subscribe({
        next: (quote) => {
          this.currentQuote.set(quote);
          this.draftQuote.update((d) => ({ ...d, id: quote.id }));
          this.loading.set(false);
          this.triggerPdfDownload(quote.id);
        },
        error: (err) => {
          this.error.set(err.error?.detail || this.lang.instant('QUOTE_STORE.ERROR_SAVE'));
          this.loading.set(false);
          this.chatMessages.update((msgs) => [
            ...msgs,
            { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.ERROR_SAVE_QUOTE'), timestamp: new Date() },
          ]);
        },
      });
      return;
    }

    this.triggerPdfDownload(quoteId);
  }

  private triggerPdfDownload(id: number) {
    this.chatMessages.update((msgs) => [
      ...msgs,
      { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.GENERATING_PDF'), timestamp: new Date() },
    ]);
    this.loading.set(true);

    this.api.generatePdf(id).subscribe({
      next: (blob) => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `devis-${id}.pdf`;
        a.click();
        URL.revokeObjectURL(url);

        this.loading.set(false);
        this.chatMessages.update((msgs) => [
          ...msgs,
          { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.PDF_SUCCESS'), timestamp: new Date() },
        ]);
      },
      error: () => {
        this.loading.set(false);
        this.chatMessages.update((msgs) => [
          ...msgs,
          { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.ERROR_PDF'), timestamp: new Date() },
        ]);
      },
    });
  }

  sendEmail() {
    const draft = this.draftQuote();
    const clientEmail = draft.client_email;

    if (!clientEmail) {
      this.chatMessages.update((msgs) => [
        ...msgs,
        {
          role: 'ai' as const,
          text: this.lang.instant('QUOTE_STORE.NO_EMAIL'),
          timestamp: new Date(),
        },
      ]);
      return;
    }

    const quoteId = draft.id as number | undefined;

    if (!quoteId) {
      this.chatMessages.update((msgs) => [
        ...msgs,
        { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.SAVING_BEFORE_SEND'), timestamp: new Date() },
      ]);
      this.loading.set(true);
      const data = { ...draft, line_items: this.lineItems() };
      this.api.create(data).subscribe({
        next: (quote) => {
          this.currentQuote.set(quote);
          this.draftQuote.update((d) => ({ ...d, id: quote.id }));
          this.loading.set(false);
          this.triggerSendEmail(quote.id, clientEmail);
        },
        error: (err) => {
          this.error.set(err.error?.detail || this.lang.instant('QUOTE_STORE.ERROR_SAVE'));
          this.loading.set(false);
          this.chatMessages.update((msgs) => [
            ...msgs,
            { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.ERROR_SAVE_QUOTE'), timestamp: new Date() },
          ]);
        },
      });
      return;
    }

    this.triggerSendEmail(quoteId, clientEmail);
  }

  private triggerSendEmail(id: number, email: string) {
    this.chatMessages.update((msgs) => [
      ...msgs,
      { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.SENDING'), timestamp: new Date() },
    ]);
    this.loading.set(true);

    this.api.sendEmail(id, email).subscribe({
      next: () => {
        this.loading.set(false);
        this.chatMessages.update((msgs) => [
          ...msgs,
          { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.EMAIL_SUCCESS'), timestamp: new Date() },
        ]);
      },
      error: (err) => {
        this.loading.set(false);
        this.chatMessages.update((msgs) => [
          ...msgs,
          {
            role: 'ai' as const,
            text: err.error?.detail || this.lang.instant('QUOTE_STORE.ERROR_EMAIL'),
            timestamp: new Date(),
          },
        ]);
      },
    });
  }

  private buildAiSummary(items: LineItem[], client?: ParsedClientInfo | null): string {
    const parts: string[] = [];

    if (items.length) {
      const descriptions = items.map((i) => i.description);
      const preview = descriptions.slice(0, 3).join(', ');
      const suffix = descriptions.length > 3 ? '...' : '';
      parts.push(this.lang.instant('QUOTE_STORE.AI_LINES_ADDED', {
        count: items.length,
        preview: preview + suffix,
      }));
    }

    if (client?.name) {
      parts.push(this.lang.instant('QUOTE_STORE.AI_CLIENT', { name: client.name }));
    }

    return parts.join(' | ') || this.lang.instant('QUOTE_STORE.AI_NO_DATA');
  }

  private applyClientInfo(client: ParsedClientInfo) {
    this.draftQuote.update((draft) => ({
      ...draft,
      ...(client.name && !draft.client_name ? { client_name: client.name } : {}),
      ...(client.address && !draft.client_address ? { client_address: client.address } : {}),
      ...(client.email && !draft.client_email ? { client_email: client.email } : {}),
      ...(client.phone && !draft.client_phone ? { client_phone: client.phone } : {}),
    }));
  }

  private addItemsProgressively(items: LineItem[], index = 0) {
    if (index >= items.length) {
      this.parsingStatus.set('done');
      return;
    }
    this.lineItems.update((current) => [...current, items[index]]);
    setTimeout(() => this.addItemsProgressively(items, index + 1), 150);
  }

  addLineItem(item: LineItem) {
    this.lineItems.update((items) => [...items, item]);
  }

  updateLineItem(index: number, item: LineItem) {
    this.lineItems.update((items) => items.map((it, i) => (i === index ? item : it)));
  }

  removeLineItem(index: number) {
    this.lineItems.update((items) => items.filter((_, i) => i !== index));
  }

  updateDraftField(field: string, value: any) {
    this.draftQuote.update((draft) => ({ ...draft, [field]: value }));
  }

  saveQuote() {
    this.loading.set(true);
    this.chatMessages.update((msgs) => [
      ...msgs,
      { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.SAVING'), timestamp: new Date() },
    ]);
    const draft = this.draftQuote();
    const data = { ...draft, line_items: this.lineItems() };

    const obs = draft.id
      ? this.api.update(draft.id as number, data)
      : this.api.create(data);

    obs.subscribe({
      next: (quote) => {
        this.currentQuote.set(quote);
        this.draftQuote.update((d) => ({ ...d, id: quote.id }));
        this.loading.set(false);
        this.chatMessages.update((msgs) => [
          ...msgs,
          { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.SAVE_SUCCESS'), timestamp: new Date() },
        ]);
      },
      error: (err) => {
        this.error.set(err.error?.detail || this.lang.instant('QUOTE_STORE.ERROR_SAVE'));
        this.loading.set(false);
        this.chatMessages.update((msgs) => [
          ...msgs,
          { role: 'ai' as const, text: this.lang.instant('QUOTE_STORE.ERROR_SAVE_QUOTE'), timestamp: new Date() },
        ]);
      },
    });
  }

  resetDraft() {
    this.draftQuote.set({
      client_name: '',
      client_address: '',
      client_email: '',
      client_phone: '',
      title: '',
      description: '',
      line_items: [],
    });
    this.lineItems.set([]);
    this.chatMessages.set([]);
    this.currentQuote.set(null);
    this.parsingStatus.set('idle');
    this.error.set(null);
  }
}
