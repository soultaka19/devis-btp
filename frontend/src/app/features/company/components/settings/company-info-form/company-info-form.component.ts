import { Component, effect, inject, input, output } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { CompanyInfo } from '../../../models/company.model';

@Component({
  selector: 'app-company-info-form',
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, TranslateModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.NAME' | translate }}</mat-label>
        <input matInput formControlName="name">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.SIRET' | translate }}</mat-label>
        <input matInput formControlName="siret" maxlength="14">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.ADDRESS' | translate }}</mat-label>
        <textarea matInput formControlName="address" rows="2"></textarea>
      </mat-form-field>
      <div class="row">
        <mat-form-field>
          <mat-label>{{ 'COMPANY.POSTAL_CODE' | translate }}</mat-label>
          <input matInput formControlName="postal_code">
        </mat-form-field>
        <mat-form-field>
          <mat-label>{{ 'COMPANY.CITY' | translate }}</mat-label>
          <input matInput formControlName="city">
        </mat-form-field>
      </div>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.PHONE' | translate }}</mat-label>
        <input matInput formControlName="phone">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.EMAIL' | translate }}</mat-label>
        <input matInput formControlName="email" type="email">
      </mat-form-field>
      <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || saving()">
        {{ 'COMPANY.SAVE' | translate }}
      </button>
    </form>
  `,
  styles: [`
    form { display: flex; flex-direction: column; gap: 8px; }
    .full-width { width: 100%; }
    .row { display: flex; gap: 16px; }
    .row mat-form-field { flex: 1; }
  `],
})
export class CompanyInfoFormComponent {
  data = input<CompanyInfo | null>(null);
  saving = input(false);
  save = output<CompanyInfo>();

  private fb = inject(FormBuilder);
  form = this.fb.nonNullable.group({
    name: ['', Validators.required],
    siret: ['', [Validators.required, Validators.pattern(/^\d{14}$/)]],
    address: ['', Validators.required],
    city: ['', Validators.required],
    postal_code: ['', Validators.required],
    phone: ['', Validators.required],
    email: ['', [Validators.required, Validators.email]],
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
