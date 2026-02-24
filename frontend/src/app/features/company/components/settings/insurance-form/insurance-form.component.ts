import { Component, effect, inject, input, output } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { TranslateModule } from '@ngx-translate/core';
import { InsuranceInfo } from '../../../models/company.model';

@Component({
  selector: 'app-insurance-form',
  standalone: true,
  imports: [ReactiveFormsModule, MatFormFieldModule, MatInputModule, MatButtonModule, TranslateModule],
  template: `
    <form [formGroup]="form" (ngSubmit)="onSubmit()">
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.INSURER' | translate }}</mat-label>
        <input matInput formControlName="provider">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.POLICY_NUMBER' | translate }}</mat-label>
        <input matInput formControlName="policy_number">
      </mat-form-field>
      <mat-form-field class="full-width">
        <mat-label>{{ 'COMPANY.COVERAGE_ZONE' | translate }}</mat-label>
        <input matInput formControlName="coverage_zone">
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
export class InsuranceFormComponent {
  data = input<InsuranceInfo | null>(null);
  saving = input(false);
  save = output<InsuranceInfo>();

  private fb = inject(FormBuilder);
  form = this.fb.nonNullable.group({
    provider: ['', Validators.required],
    policy_number: ['', Validators.required],
    coverage_zone: ['', Validators.required],
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
