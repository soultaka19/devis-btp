import { Component, effect, inject, input, output } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { BankingInfo } from '../../../models/company.model';

@Component({
  selector: 'app-banking-form',
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, TranslateModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.BANK_NAME' | translate }}</mat-label>
        <input matInput formControlName="bank_name">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.IBAN' | translate }}</mat-label>
        <input matInput formControlName="iban">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.BIC' | translate }}</mat-label>
        <input matInput formControlName="bic">
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
export class BankingFormComponent {
  data = input<BankingInfo | null>(null);
  saving = input(false);
  save = output<BankingInfo>();

  private fb = inject(FormBuilder);
  form = this.fb.nonNullable.group({
    bank_name: ['', Validators.required],
    iban: ['', [Validators.required, Validators.minLength(15)]],
    bic: ['', [Validators.required, Validators.minLength(8)]],
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
