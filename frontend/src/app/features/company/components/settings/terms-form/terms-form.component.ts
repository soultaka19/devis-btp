import { Component, effect, inject, input, output } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { TermsInfo } from '../../../models/company.model';

@Component({
  selector: 'app-terms-form',
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, TranslateModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.PAYMENT_TERMS' | translate }}</mat-label>
        <input matInput formControlName="payment_terms">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.VALIDITY_DAYS' | translate }}</mat-label>
        <input matInput type="number" formControlName="validity_days">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.LATE_PENALTY' | translate }}</mat-label>
        <input matInput type="number" step="0.1" formControlName="late_penalty_rate">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.GENERAL_CONDITIONS' | translate }}</mat-label>
        <textarea matInput formControlName="general_conditions" rows="4"></textarea>
      </mat-form-field>
      <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || saving()">
        {{ 'COMPANY.SAVE' | translate }}
      </button>
    </form>
  `,
  styles: [`
    form { display: flex; flex-direction: column; gap: 8px; }
    .full-width { width: 100%; }
  `],
})
export class TermsFormComponent {
  data = input<TermsInfo | null>(null);
  saving = input(false);
  save = output<TermsInfo>();

  private fb = inject(FormBuilder);
  form = this.fb.nonNullable.group({
    payment_terms: ['Paiement a 30 jours', Validators.required],
    validity_days: [30, [Validators.required, Validators.min(1)]],
    late_penalty_rate: [3.0, Validators.required],
    general_conditions: [''],
  });

  constructor() {
    effect(() => {
      const d = this.data();
      if (d) this.form.patchValue(d);
    });
  }

  onSubmit() {
    if (this.form.valid) this.save.emit(this.form.getRawValue());
  }
}
