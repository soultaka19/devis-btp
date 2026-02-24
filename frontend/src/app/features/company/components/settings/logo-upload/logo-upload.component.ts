import { Component, input, output } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { TranslateModule } from '@ngx-translate/core';

@Component({
  selector: 'app-logo-upload',
  standalone: true,
  imports: [MatButtonModule, MatIconModule, TranslateModule],
  template: `
    <div class="logo-section">
      <h4>{{ 'COMPANY.LOGO' | translate }}</h4>
      @if (logoPath()) {
        <img [src]="logoPath()" alt="Logo" class="logo-preview">
      }
      <div class="upload-area" (dragover)="$event.preventDefault()" (drop)="onDrop($event)">
        <mat-icon>cloud_upload</mat-icon>
        <p>{{ 'COMPANY.DROP_LOGO' | translate }}</p>
        <button mat-stroked-button (click)="fileInput.click()">
          {{ 'COMPANY.CHOOSE_FILE' | translate }}
        </button>
        <input #fileInput type="file" accept="image/*" hidden (change)="onFileSelected($event)">
        <p class="hint">{{ 'COMPANY.FILE_HINT' | translate }}</p>
      </div>
    </div>
  `,
  styles: [`
    .logo-section { margin-top: 16px; }
    .logo-preview { max-width: 120px; max-height: 80px; margin-bottom: 8px; display: block; }
    .upload-area {
      border: 2px dashed #ccc;
      border-radius: 8px;
      padding: 24px;
      text-align: center;
    }
    .hint { font-size: 12px; color: #999; margin-top: 8px; }
    mat-icon { font-size: 48px; width: 48px; height: 48px; color: #999; }
  `],
})
export class LogoUploadComponent {
  logoPath = input<string | undefined>();
  upload = output<File>();

  onFileSelected(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (file) this.upload.emit(file);
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    const file = event.dataTransfer?.files[0];
    if (file) this.upload.emit(file);
  }
}
