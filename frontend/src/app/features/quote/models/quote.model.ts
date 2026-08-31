export type QuoteStatus = 'draft' | 'sent' | 'accepted' | 'rejected';

export interface LineItem {
  id?: number;
  description: string;
  unit: string;
  quantity: number;
  unit_price: number;
  vat_rate: number;
  total_ht?: number;
  position?: number;
}

export interface Quote {
  id: number;
  reference: string;
  status: QuoteStatus;
  client_name: string;
  client_address: string;
  client_email: string;
  client_phone: string;
  title: string;
  description: string;
  subtotal_ht: number;
  total_vat: number;
  total_ttc: number;
  line_items: LineItem[];
  created_at?: string;
}

export interface ParsedClientInfo {
  name?: string | null;
  address?: string | null;
  email?: string | null;
  phone?: string | null;
}

export interface ParseTextResponse {
  title: string;
  line_items: LineItem[];
  client: ParsedClientInfo | null;
  // Served from cache: the same model output, without a new call - so without
  // spending one of the sandbox attempts.
  from_cache?: boolean;
  // Attempts left in a demo sandbox; null for a real account, under no quota.
  ai_calls_remaining?: number | null;
}

export interface VoiceToTextResponse {
  text: string;
  duration_ms: number;
  from_cache?: boolean;
  ai_calls_remaining?: number | null;
}

export interface ChatMessage {
  role: 'user' | 'ai';
  text: string;
  items?: LineItem[];
  expanded?: boolean;
  timestamp: Date;
}

export interface QuoteListItem {
  id: number;
  reference: string;
  status: QuoteStatus;
  client_name: string;
  title: string;
  total_ttc: number;
  created_at: string;
}
