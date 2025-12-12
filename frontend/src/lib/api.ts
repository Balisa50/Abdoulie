const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message?: string
  ) {
    super(message || `API Error: ${status} ${statusText}`);
    this.name = "ApiError";
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_URL}${path}`;

  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = new ApiError(response.status, response.statusText);
    throw error;
  }

  const data: T = await response.json();
  return data;
}

export async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  return request<T>(path, { ...options, method: "GET" });
}

export async function postJson<T>(path: string, body: unknown, options?: RequestInit): Promise<T> {
  return request<T>(path, {
    ...options,
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function putJson<T>(path: string, body: unknown, options?: RequestInit): Promise<T> {
  return request<T>(path, {
    ...options,
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export async function deleteJson<T>(path: string, options?: RequestInit): Promise<T> {
  return request<T>(path, { ...options, method: "DELETE" });
}
