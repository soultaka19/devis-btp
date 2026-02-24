import { Component, input, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';
import { LineItem } from '../../models/quote.model';

@Component({
  selector: 'app-line-items-editor',
  standalone: true,
  imports: [
    FormsModule,
    MatTableModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatButtonModule,
    MatIconModule,
    TranslateModule,
  ],
  template: `
    <div class="editor">
      <div class="editor-header">
        <div class="editor-title">
          <mat-icon>list_alt</mat-icon>
          <h3>{{ 'QUOTE.LINE_ITEMS' | translate }}</h3>
        </div>
        <span class="line-count">{{ 'QUOTE.LINE_COUNT' | translate:{count: lineItems().length} }}</span>
      </div>

      <div class="table-wrap">
        <table mat-table [dataSource]="lineItems()" class="items-table">
          <ng-container matColumnDef="description">
            <th mat-header-cell *matHeaderCellDef>{{ 'QUOTE.DESCRIPTION' | translate }}</th>
            <td mat-cell *matCellDef="let item; let i = index">
              <input [value]="item.description"
                     (input)="onFieldChange(i, 'description', $event)" [placeholder]="'QUOTE.DESCRIPTION' | translate">
            </td>
          </ng-container>

          <ng-container matColumnDef="unit">
            <th mat-header-cell *matHeaderCellDef>{{ 'QUOTE.UNIT' | translate }}</th>
            <td mat-cell *matCellDef="let item; let i = index">
              <select [value]="item.unit" (change)="onSelectChange(i, 'unit', $event)">
                <option value="u">u</option>
                <option value="m2">m2</option>
                <option value="m">m</option>
                <option value="h">h</option>
                <option value="kg">kg</option>
                <option value="forfait">forfait</option>
              </select>
            </td>
          </ng-container>

          <ng-container matColumnDef="quantity">
            <th mat-header-cell *matHeaderCellDef>{{ 'QUOTE.QTY' | translate }}</th>
            <td mat-cell *matCellDef="let item; let i = index">
              <input type="number" [value]="item.quantity" min="0" step="0.5"
                     (input)="onNumberChange(i, 'quantity', $event)">
            </td>
          </ng-container>

          <ng-container matColumnDef="unit_price">
            <th mat-header-cell *matHeaderCellDef>{{ 'QUOTE.UNIT_PRICE' | translate }}</th>
            <td mat-cell *matCellDef="let item; let i = index">
              <input type="number" [value]="item.unit_price" min="0" step="0.01"
                     (input)="onNumberChange(i, 'unit_price', $event)">
            </td>
          </ng-container>

          <ng-container matColumnDef="vat_rate">
            <th mat-header-cell *matHeaderCellDef>{{ 'QUOTE.VAT' | translate }}</th>
            <td mat-cell *matCellDef="let item; let i = index">
              <select [value]="item.vat_rate" (change)="onNumberSelectChange(i, 'vat_rate', $event)">
                <option [value]="5.5">5.5%</option>
                <option [value]="10">10%</option>
                <option [value]="20">20%</option>
              </select>
            </td>
          </ng-container>

          <ng-container matColumnDef="total">
            <th mat-header-cell *matHeaderCellDef>{{ 'QUOTE.TOTAL_HT' | translate }}</th>
            <td mat-cell *matCellDef="let item" class="total-cell">
              {{ (item.quantity * item.unit_price).toFixed(2) }} EUR
            </td>
          </ng-container>

          <ng-container matColumnDef="actions">
            <th mat-header-cell *matHeaderCellDef></th>
            <td mat-cell *matCellDef="let item; let i = index">
              <button mat-icon-button class="delete-btn" (click)="itemRemoved.emit(i)">
                <mat-icon>delete_outline</mat-icon>
              </button>
            </td>
          </ng-container>

          <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
          <tr mat-row *matRowDef="let row; columns: displayedColumns"></tr>
        </table>
      </div>

      <button mat-stroked-button class="add-btn" (click)="addEmptyLine()">
        <mat-icon>add</mat-icon> {{ 'QUOTE.ADD_LINE' | translate }}
      </button>
    </div>
  `,
  styles: [`
    .editor {
      background: white;
      border: 1px solid var(--border);
      border-radius: var(--radius-md);
      padding: 24px;
    }

    .editor-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;
    }

    .editor-title {
      display: flex;
      align-items: center;
      gap: 10px;

      mat-icon { color: var(--primary); }

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
      }
    }

    .line-count {
      font-size: 12px;
      color: var(--text-secondary);
      background: var(--surface);
      padding: 4px 10px;
      border-radius: 12px;
    }

    .table-wrap {
      overflow-x: auto;
      margin-bottom: 16px;
    }

    .items-table {
      width: 100%;
    }

    .items-table th {
      background: var(--primary) !important;
      color: white !important;
      font-weight: 600 !important;
      font-size: 12px !important;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      padding: 10px 12px !important;
    }

    .items-table tr:nth-child(even) {
      background: var(--surface);
    }

    .items-table td {
      padding: 8px 12px !important;
      vertical-align: middle;
    }

    .total-cell {
      font-weight: 600;
      color: var(--text-primary);
      white-space: nowrap;
    }

    input, select {
      width: 100%;
      border: 1px solid var(--border);
      padding: 8px 10px;
      border-radius: var(--radius-sm);
      font-family: inherit;
      font-size: 13px;
      color: var(--text-primary);
      background: white;
      transition: border-color 0.2s ease;
      box-sizing: border-box;

      &:focus {
        outline: none;
        border-color: var(--primary-light);
      }
    }

    select {
      cursor: pointer;
    }

    .delete-btn {
      color: var(--text-secondary) !important;
      transition: color 0.2s ease !important;

      &:hover {
        color: var(--danger) !important;
      }
    }

    .mat-mdc-row {
      animation: slideIn 0.35s ease-out;
    }

    @keyframes slideIn {
      from {
        opacity: 0;
        transform: translateY(-10px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    .add-btn {
      color: var(--primary) !important;
      border-color: var(--border) !important;
      border-style: dashed !important;
      width: 100%;
      transition: all 0.2s ease !important;

      &:hover {
        border-color: var(--primary) !important;
        background: rgba(27, 42, 74, 0.04) !important;
      }
    }
  `],
})
export class LineItemsEditorComponent {
  lineItems = input<LineItem[]>([]);
  itemChanged = output<{ index: number; item: LineItem }>();
  itemRemoved = output<number>();
  itemAdded = output<LineItem>();

  displayedColumns = ['description', 'unit', 'quantity', 'unit_price', 'vat_rate', 'total', 'actions'];

  onFieldChange(index: number, field: string, event: Event) {
    const value = (event.target as HTMLInputElement).value;
    const item = { ...this.lineItems()[index], [field]: value };
    this.itemChanged.emit({ index, item });
  }

  onSelectChange(index: number, field: string, event: Event) {
    const value = (event.target as HTMLSelectElement).value;
    const item = { ...this.lineItems()[index], [field]: value };
    this.itemChanged.emit({ index, item });
  }

  onNumberChange(index: number, field: string, event: Event) {
    const value = parseFloat((event.target as HTMLInputElement).value) || 0;
    const item = { ...this.lineItems()[index], [field]: value };
    this.itemChanged.emit({ index, item });
  }

  onNumberSelectChange(index: number, field: string, event: Event) {
    const value = parseFloat((event.target as HTMLSelectElement).value) || 0;
    const item = { ...this.lineItems()[index], [field]: value };
    this.itemChanged.emit({ index, item });
  }

  addEmptyLine() {
    this.itemAdded.emit({
      description: '',
      unit: 'u',
      quantity: 1,
      unit_price: 0,
      vat_rate: 20,
    });
  }
}
