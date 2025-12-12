import type { HealthResponse } from "./health";

export type { HealthResponse };

// UUID type alias
export type UUID = string;

// Client types
export interface ClientResponse {
  id: UUID;
  name: string;
  email: string;
  phone: string | null;
  address: string | null;
  data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ClientCreate {
  name: string;
  email: string;
  phone?: string;
  address?: string;
  data?: Record<string, unknown>;
}

export interface ClientUpdate {
  name?: string;
  email?: string;
  phone?: string;
  address?: string;
  data?: Record<string, unknown>;
}

// Invoice types
export interface InvoiceResponse {
  id: UUID;
  client_id: UUID;
  invoice_number: string;
  amount: number;
  currency: string;
  status: string;
  issue_date: string;
  due_date: string | null;
  duplicate_hash: string | null;
  extracted_entities: Record<string, unknown> | null;
  data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface InvoiceCreate {
  client_id: UUID;
  invoice_number: string;
  amount: number;
  currency?: string;
  status?: string;
  issue_date: string;
  due_date?: string;
  duplicate_hash?: string;
  extracted_entities?: Record<string, unknown>;
  data?: Record<string, unknown>;
}

export interface InvoiceUpdate {
  invoice_number?: string;
  amount?: number;
  currency?: string;
  status?: string;
  issue_date?: string;
  due_date?: string;
  duplicate_hash?: string;
  extracted_entities?: Record<string, unknown>;
  data?: Record<string, unknown>;
}

// Contract types
export interface ContractResponse {
  id: UUID;
  client_id: UUID;
  contract_number: string;
  title: string;
  status: string;
  start_date: string;
  end_date: string | null;
  extracted_entities: Record<string, unknown> | null;
  rule_references: Record<string, unknown> | null;
  data: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ContractCreate {
  client_id: UUID;
  contract_number: string;
  title: string;
  status?: string;
  start_date: string;
  end_date?: string;
  extracted_entities?: Record<string, unknown>;
  rule_references?: Record<string, unknown>;
  data?: Record<string, unknown>;
}

export interface ContractUpdate {
  contract_number?: string;
  title?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  extracted_entities?: Record<string, unknown>;
  rule_references?: Record<string, unknown>;
  data?: Record<string, unknown>;
}

// Audit Result types
export interface AuditResultResponse {
  id: UUID;
  invoice_id: UUID | null;
  contract_id: UUID | null;
  rule_id: string;
  status: string;
  extracted_entities: Record<string, unknown> | null;
  variance_metrics: Record<string, unknown> | null;
  rule_references: Record<string, unknown> | null;
  findings: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface AuditResultCreate {
  invoice_id?: UUID;
  contract_id?: UUID;
  rule_id: string;
  status?: string;
  extracted_entities?: Record<string, unknown>;
  variance_metrics?: Record<string, unknown>;
  rule_references?: Record<string, unknown>;
  findings?: Record<string, unknown>;
}

export interface AuditResultUpdate {
  status?: string;
  extracted_entities?: Record<string, unknown>;
  variance_metrics?: Record<string, unknown>;
  rule_references?: Record<string, unknown>;
  findings?: Record<string, unknown>;
}

// Audit Log types
export interface AuditLogResponse {
  id: UUID;
  client_id: UUID | null;
  entity_type: string;
  entity_id: UUID;
  action: string;
  status: string;
  changes: Record<string, unknown> | null;
  error_message: string | null;
  data: Record<string, unknown> | null;
  created_at: string;
}

export interface AuditLogCreate {
  client_id?: UUID;
  entity_type: string;
  entity_id: UUID;
  action: string;
  status?: string;
  changes?: Record<string, unknown>;
  error_message?: string;
  data?: Record<string, unknown>;
}
