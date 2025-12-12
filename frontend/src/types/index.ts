export type Client = {
  id: string;
  name: string;
  email: string;
  phone?: string;
  address?: string;
  data?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type Invoice = {
  id: string;
  client_id: string;
  invoice_number: string;
  amount: number;
  currency: string;
  status: string;
  issue_date: string;
  due_date?: string;
  duplicate_hash?: string;
  extracted_entities?: Record<string, unknown>;
  data?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type Contract = {
  id: string;
  client_id: string;
  contract_number: string;
  title: string;
  status: string;
  start_date: string;
  end_date?: string;
  extracted_entities?: Record<string, unknown>;
  rule_references?: Record<string, unknown>;
  data?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type AuditResult = {
  id: string;
  invoice_id?: string;
  contract_id?: string;
  rule_id: string;
  status: string;
  extracted_entities?: Record<string, unknown>;
  variance_metrics?: Record<string, unknown>;
  rule_references?: Record<string, unknown>;
  findings?: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

export type ListResponse<T> = {
  items: T[];
  total: number;
  skip: number;
  limit: number;
};
