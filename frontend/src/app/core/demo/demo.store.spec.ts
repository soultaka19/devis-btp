import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { DemoStore } from './demo.store';

describe('DemoStore', () => {
  let store: DemoStore;
  let http: HttpTestingController;

  const session = (minutes: number, total = 5, remaining = 5) => ({
    access_token: 'token',
    token_type: 'bearer',
    user: { id: 12, email: 'demo@demo.test', full_name: 'Sonia Bélanger' },
    sandbox_expires_at: new Date(Date.now() + minutes * 60_000).toISOString(),
    ai_calls_total: total,
    ai_calls_remaining: remaining,
  });

  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-08-31T12:00:00Z'));
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    store = TestBed.inject(DemoStore);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    store.clear();
    http.verify();
    vi.useRealTimers();
  });

  it('is not a demo until a sandbox is adopted', () => {
    expect(store.isDemo()).toBe(false);
    expect(store.aiCallsRemaining()).toBe(0);
  });

  it('adopts the session returned by the API', () => {
    store.create().subscribe();
    http.expectOne('http://localhost:8000/demo/sandbox').flush(session(60, 5, 5));

    expect(store.isDemo()).toBe(true);
    expect(store.aiCallsTotal()).toBe(5);
    expect(store.aiCallsRemaining()).toBe(5);
  });

  it('counts down in mm:ss below an hour', () => {
    store.create().subscribe();
    http.expectOne('http://localhost:8000/demo/sandbox').flush(session(2));

    expect(store.timeLeft()).toBe('02:00');
    vi.advanceTimersByTime(65_000);
    expect(store.timeLeft()).toBe('00:55');
    expect(store.expired()).toBe(false);
  });

  it('reports expiry once the sandbox lifetime is over', () => {
    store.create().subscribe();
    http.expectOne('http://localhost:8000/demo/sandbox').flush(session(1));

    vi.advanceTimersByTime(61_000);
    expect(store.secondsLeft()).toBe(0);
    expect(store.expired()).toBe(true);
  });

  it('records the attempts left reported by an AI answer', () => {
    store.create().subscribe();
    http.expectOne('http://localhost:8000/demo/sandbox').flush(session(60, 5, 5));

    store.noteRemaining(3);
    expect(store.aiCallsRemaining()).toBe(3);

    // A cached answer repeats the same count: it must not be read as a spend.
    store.noteRemaining(3);
    expect(store.aiCallsRemaining()).toBe(3);

    // A real account reports null; the count must stay untouched.
    store.noteRemaining(null);
    expect(store.aiCallsRemaining()).toBe(3);
  });

  it('drops the sandbox when the token belongs to a real account', () => {
    store.create().subscribe();
    http.expectOne('http://localhost:8000/demo/sandbox').flush(session(60));

    store.refresh();
    http.expectOne('http://localhost:8000/demo/status').flush({ is_demo: false });

    expect(store.isDemo()).toBe(false);
  });

  it('restores the countdown after a reload', () => {
    store.refresh();
    http.expectOne('http://localhost:8000/demo/status').flush({
      is_demo: true,
      sandbox_expires_at: new Date(Date.now() + 30 * 60_000).toISOString(),
      ai_calls_total: 5,
      ai_calls_remaining: 2,
    });

    expect(store.isDemo()).toBe(true);
    expect(store.timeLeft()).toBe('30:00');
    expect(store.aiCallsRemaining()).toBe(2);
  });
});
