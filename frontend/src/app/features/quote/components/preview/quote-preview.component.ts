import { Component, input } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { LineItem, Quote } from '../../models/quote.model';
import { CurrencyPipe } from '@angular/common';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-quote-preview',
  standalone: true,
  imports: [MatCardModule, CurrencyPipe, TranslateModule],
  template: `
    <div class="a4-page">
      <div class="preview-header">
        <div class="header-left">
          <span class="doc-type">{{ 'QUOTE.DOC_TYPE' | translate }}</span>
        </div>
        <div class="header-right">
          @if (quote()?.reference) {
            <span class="ref">{{ quote()?.reference }}</span>
          }
        </div>
      </div>

      @if (quote()?.client_name) {
        <div class="client-section">
          <span class="section-label">{{ 'QUOTE.CLIENT' | translate }}</span>
          <p class="client-name">{{ quote()?.client_name }}</p>
          @if (quote()?.client_address) {
            <p class="client-address">{{ quote()?.client_address }}</p>
          }
        </div>
      }

      @if (quote()?.title) {
        <div class="quote-title">
          <h3>{{ quote()?.title }}</h3>
        </div>
      }

      @if (lineItems().length > 0) {
        <table class="preview-table">
          <thead>
            <tr>
              <th class="col-num">#</th>
              <th class="col-desc">{{ 'QUOTE.DESCRIPTION' | translate }}</th>
              <th class="col-qty">{{ 'QUOTE.QTY' | translate }}</th>
              <th class="col-pu">{{ 'QUOTE.UNIT_PRICE' | translate }}</th>
              <th class="col-tva">{{ 'QUOTE.VAT' | translate }}</th>
              <th class="col-total">{{ 'QUOTE.TOTAL_HT' | translate }}</th>
            </tr>
          </thead>
          <tbody>
            @for (item of lineItems(); track $index) {
              <tr>
                <td class="col-num">{{ $index + 1 }}</td>
                <td class="col-desc">{{ item.description }}</td>
                <td class="col-qty">{{ item.quantity }} {{ item.unit }}</td>
                <td class="col-pu">{{ item.unit_price | currency:'EUR' }}</td>
                <td class="col-tva">{{ item.vat_rate }}%</td>
                <td class="col-total">{{ (item.quantity * item.unit_price) | currency:'EUR' }}</td>
              </tr>
            }
          </tbody>
        </table>

        <div class="totals-section">
          <div class="totals-box">
            <div class="total-row">
              <span>{{ 'QUOTE.SUBTOTAL' | translate }}</span>
              <span>{{ totals()?.subtotal_ht | currency:'EUR' }}</span>
            </div>
            <div class="total-row">
              <span>{{ 'QUOTE.VAT_TOTAL' | translate }}</span>
              <span>{{ totals()?.total_vat | currency:'EUR' }}</span>
            </div>
            <div class="total-row total-ttc">
              <span>{{ 'QUOTE.TOTAL_TTC' | translate }}</span>
              <span>{{ totals()?.total_ttc | currency:'EUR' }}</span>
            </div>
          </div>
        </div>
      } @else {
        <div class="empty-state">
          <p>{{ 'QUOTE.EMPTY_PREVIEW' | translate }}</p>
        </div>
      }

      <div class="preview-footer">
        <p>{{ 'QUOTE.PAYMENT_TERMS' | translate }}</p>
      </div>
    </div>
  `,
  styles: [`
    .a4-page {
      width: 100%;
      max-width: 595px;
      min-height: 700px;
      background: white;
      border-radius: var(--radius-sm);
      box-shadow: var(--shadow-lg);
      padding: 40px;
      font-family: 'Inter', 'Helvetica', 'Arial', sans-serif;
      font-size: 13px;
      color: var(--text-primary);
      position: relative;
    }

    /* Header */
    .preview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 20px;
      margin-bottom: 24px;
      border-bottom: 3px solid var(--primary);
      background: var(--primary);
      margin: -40px -40px 24px -40px;
      padding: 24px 40px;
      border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    }

    .doc-type {
      font-size: 28px;
      font-weight: 700;
      color: white;
      letter-spacing: 4px;
    }

    .ref {
      color: rgba(255, 255, 255, 0.8);
      font-size: 13px;
    }

    /* Client */
    .client-section {
      background: var(--surface);
      padding: 16px 20px;
      border-radius: var(--radius-sm);
      margin-bottom: 20px;
      border-left: 3px solid var(--accent);
    }

    .section-label {
      font-size: 10px;
      font-weight: 700;
      color: var(--text-secondary);
      letter-spacing: 1.5px;
      text-transform: uppercase;
    }

    .client-name {
      font-size: 15px;
      font-weight: 600;
      margin: 4px 0 0;
    }

    .client-address {
      color: var(--text-secondary);
      margin: 2px 0 0;
    }

    /* Title */
    .quote-title {
      margin-bottom: 16px;

      h3 {
        margin: 0;
        font-size: 16px;
        color: var(--primary);
      }
    }

    /* Table */
    .preview-table {
      width: 100%;
      border-collapse: collapse;
      margin: 16px 0 24px;
    }

    .preview-table thead tr {
      background: var(--accent);
    }

    .preview-table th {
      padding: 10px 12px;
      text-align: left;
      color: white;
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }

    .preview-table td {
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      font-size: 13px;
    }

    .preview-table tbody tr:nth-child(even) {
      background: #FAFBFC;
    }

    .col-num { width: 30px; text-align: center; }
    .col-desc { min-width: 180px; }
    .col-qty, .col-pu, .col-tva, .col-total { text-align: right; white-space: nowrap; }

    .preview-table th.col-qty,
    .preview-table th.col-pu,
    .preview-table th.col-tva,
    .preview-table th.col-total { text-align: right; }

    .preview-table th.col-num { text-align: center; }

    /* Totals */
    .totals-section {
      display: flex;
      justify-content: flex-end;
    }

    .totals-box {
      width: 260px;
      border: 1px solid var(--border);
      border-radius: var(--radius-sm);
      overflow: hidden;
    }

    .total-row {
      display: flex;
      justify-content: space-between;
      padding: 10px 16px;
      font-size: 13px;
      border-bottom: 1px solid var(--border);

      &:last-child { border-bottom: none; }
    }

    .total-ttc {
      background: var(--primary);
      color: white;
      font-weight: 700;
      font-size: 15px;
    }

    /* Empty State */
    .empty-state {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 300px;
      color: var(--text-secondary);
      font-style: italic;
    }

    /* Footer */
    .preview-footer {
      margin-top: 40px;
      padding-top: 16px;
      border-top: 1px solid var(--border);

      p {
        color: var(--text-secondary);
        font-size: 11px;
        margin: 0;
      }
    }
  `],
})
export class QuotePreviewComponent {
  quote = input<Partial<Quote>>();
  lineItems = input<LineItem[]>([]);
  totals = input<{ subtotal_ht: number; total_vat: number; total_ttc: number }>();
}
