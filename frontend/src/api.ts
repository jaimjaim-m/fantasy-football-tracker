const PASSWORD_KEY = "ff_hub_password";

export function getHubPassword(): string {
  return sessionStorage.getItem(PASSWORD_KEY) || "";
}

export function setHubPassword(password: string) {
  sessionStorage.setItem(PASSWORD_KEY, password);
}

export function clearHubPassword() {
  sessionStorage.removeItem(PASSWORD_KEY);
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers || {});
  const password = getHubPassword();
  if (password) headers.set("X-Hub-Password", password);
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path, { ...init, headers, credentials: "include" });
  if (response.status === 401) {
    const err = new Error("unauthorized");
    (err as Error & { status: number }).status = 401;
    throw err;
  }
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const data = await response.json();
      detail = data.detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  if (response.headers.get("content-type")?.includes("application/json")) {
    return response.json() as Promise<T>;
  }
  return response as unknown as T;
}

export async function downloadPdf(report: string) {
  const headers = new Headers();
  const password = getHubPassword();
  if (password) headers.set("X-Hub-Password", password);
  const response = await fetch(`/api/export/pdf/${report}`, { headers, credentials: "include" });
  if (!response.ok) {
    throw new Error("PDF download failed");
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `${report}_report.pdf`;
  a.click();
  URL.revokeObjectURL(url);
}
