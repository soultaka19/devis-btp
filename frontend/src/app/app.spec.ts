import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { provideTranslateService } from '@ngx-translate/core';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    // No stored token: the app renders the unauthenticated layout (bare router outlet)
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), provideHttpClient(), provideTranslateService()],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('should render the router outlet without authentication', async () => {
    const fixture = TestBed.createComponent(App);
    await fixture.whenStable();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(fixture.componentInstance.authStore.isAuthenticated()).toBe(false);
    expect(compiled.querySelector('router-outlet')).not.toBeNull();
    expect(compiled.querySelector('mat-sidenav-container')).toBeNull();
  });

  it('should toggle the layout mode and persist it', () => {
    const fixture = TestBed.createComponent(App);
    const app = fixture.componentInstance;
    expect(app.layoutMode()).toBe('sidebar');
    app.toggleLayout();
    expect(app.layoutMode()).toBe('toolbar');
    expect(localStorage.getItem('btp_layout_mode')).toBe('toolbar');
  });
});
