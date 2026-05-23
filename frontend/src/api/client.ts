import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/auth';
import { useLocaleStore } from '@/i18n';

const baseURL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '/api';

export const api: AxiosInstance = axios.create({
  baseURL,
  headers: { 'Content-Type': 'application/json' },
});

let refreshing: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refresh = useAuthStore.getState().refresh;
  if (!refresh) return null;
  try {
    const { data } = await axios.post(`${baseURL}/auth/token/refresh/`, { refresh });
    useAuthStore.getState().setTokens({ access: data.access, refresh: data.refresh ?? refresh });
    return data.access as string;
  } catch {
    useAuthStore.getState().logout();
    return null;
  }
}

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const access = useAuthStore.getState().access;
  const lang = useLocaleStore.getState().lang;
  config.headers = config.headers ?? {};
  if (access) {
    (config.headers as Record<string, string>)['Authorization'] = `Bearer ${access}`;
  }
  (config.headers as Record<string, string>)['Accept-Language'] = lang;
  return config;
});

api.interceptors.response.use(
  (resp) => resp,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    if (error.response?.status === 401 && !original._retry && original.url?.indexOf('/auth/token/') === -1) {
      original._retry = true;
      refreshing = refreshing ?? refreshAccessToken();
      const access = await refreshing;
      refreshing = null;
      if (access) {
        original.headers = original.headers ?? {};
        (original.headers as Record<string, string>)['Authorization'] = `Bearer ${access}`;
        return api(original);
      }
    }
    return Promise.reject(error);
  },
);

export default api;
