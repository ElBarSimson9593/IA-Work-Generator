export interface RequestOptions extends RequestInit {
  retries?: number;
}

export async function request<T = any>(url: string, options: RequestOptions = {}): Promise<T> {
  const { retries = 0, ...init } = options;
  for (let attempt = 0; ; attempt++) {
    try {
      const resp = await fetch(url, init);
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
