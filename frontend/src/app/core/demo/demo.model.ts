/** What `POST /demo/sandbox` returns: a ready-to-use session, no account asked. */
export interface SandboxSession {
  access_token: string;
  token_type: string;
  user: { id: number; email: string; full_name: string };
  sandbox_expires_at: string;
  ai_calls_total: number;
  ai_calls_remaining: number;
}

/** What `GET /demo/status` returns. A real account answers `is_demo: false`. */
export interface SandboxStatus {
  is_demo: boolean;
  sandbox_expires_at?: string;
  ai_calls_total?: number;
  ai_calls_remaining?: number;
}
