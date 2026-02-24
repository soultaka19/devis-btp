import { Component, inject, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { TranslateModule } from '@ngx-translate/core';
import { QuoteStore } from '../../state/quote.store';
import { QuoteInputPanelComponent } from '../input/quote-input-panel.component';
import { LineItemsEditorComponent } from '../editor/line-items-editor.component';
import { QuotePreviewComponent } from '../preview/quote-preview.component';

@Component({
  selector: 'app-quote-compose',
  standalone: true,
  imports: [
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    TranslateModule,
    QuoteInputPanelComponent,
    LineItemsEditorComponent,
    QuotePreviewComponent,
  ],
  template: `
    @if (store.loading()) {
      <mat-progress-bar mode="indeterminate" class="top-loader"></mat-progress-bar>
    }
    <div class="two-columns">
      <div class="left-panel">
        <app-quote-input-panel
          [parsingStatus]="store.parsingStatus()"
          [chatMessages]="store.chatMessages()"
          (parseRequest)="store.parseText($event)"
        />
        <app-line-items-editor
          [lineItems]="store.lineItems()"
          (itemChanged)="store.updateLineItem($event.index, $event.item)"
          (itemRemoved)="store.removeLineItem($event)"
          (itemAdded)="store.addLineItem($event)"
        />
        <div class="actions-bar">
          <button mat-raised-button (click)="store.downloadPdf()">
            <mat-icon>picture_as_pdf</mat-icon> {{ 'QUOTE.DOWNLOAD_PDF' | translate }}
          </button>
          <button mat-raised-button (click)="store.sendEmail()">
            <mat-icon>email</mat-icon> {{ 'QUOTE.SEND_EMAIL' | translate }}
          </button>
          <button mat-raised-button class="btn-primary" (click)="store.saveQuote()">
            <mat-icon>save</mat-icon> {{ 'QUOTE.SAVE' | translate }}
          </button>
        </div>
      </div>
      <div class="right-panel">
        <app-quote-preview
          [quote]="store.draftQuote()"
          [lineItems]="store.lineItems()"
          [totals]="store.totals()"
        />
      </div>
    </div>
  `,
  styles: [`
    .top-loader {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      z-index: 999;
    }

    .left-panel {
      display: flex;
      flex-direction: column;
      gap: 20px;
      overflow-y: auto;
      padding: 4px;
    }

    .right-panel {
      overflow-y: auto;
      padding: 24px;
      background: var(--surface);
      border-radius: var(--radius-md);
      display: flex;
      justify-content: center;
    }

    .actions-bar {
      display: flex;
      gap: 12px;
      justify-content: flex-end;
      padding: 16px 0;
      position: sticky;
      bottom: 0;
      background: white;
      border-top: 1px solid var(--border);
      margin-top: auto;
    }
  `],
})
export class QuoteComposeComponent implements OnInit {
  store = inject(QuoteStore);
  private route = inject(ActivatedRoute);

  ngOnInit() {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.store.loadQuote(+id);
    } else {
      this.store.resetDraft();
    }
  }
}
