export interface RequestOptions extends RequestInit {
  retries?: number;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

function resolveUrl(path: string): string {
  if (/^https?:\/\//.test(path)) {
    return path;
  }
  const base = API_BASE_URL.replace(/\/$/, "");
  const clean = path.startsWith("/") ? path.slice(1) : path;
  return `${base}/${clean}`;
}

export async function request<T = any>(url: string, options: RequestOptions = {}): Promise<T> {
  const { retries = 0, ...init } = options;
  for (let attempt = 0; ; attempt++) {
    try {
      const resp = await fetch(resolveUrl(url), init);
      if (!resp.ok) throw new Error(`Request failed with ${resp.status}`);
      const text = await resp.text();
      try {
        return JSON.parse(text) as T;
      } catch {
        return text as unknown as T;
      }
    } catch (err) {
      if (attempt >= retries) throw err;
    }
  }
}
