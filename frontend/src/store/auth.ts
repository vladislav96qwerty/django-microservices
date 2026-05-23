import axios from 'axios';
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthTokens, User } from '@/types';

const baseURL = (import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '/api';

interface AuthState {
  access: string | null;
  refresh: string | null;
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  setTokens: (tokens: AuthTokens) => void;
  setUser: (user: User | null) => void;
  fetchProfile: () => Promise<void>;
}

interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      access: null,
      refresh: null,
      user: null,
      isAuthenticated: false,
      setTokens: ({ access, refresh }) =>
        set({ access, refresh, isAuthenticated: !!access }),
      setUser: (user) => set({ user }),
      login: async (username, password) => {
        const { data } = await axios.post(`${baseURL}/auth/login/`, { username, password });
        set({ access: data.access, refresh: data.refresh, isAuthenticated: true });
        await get().fetchProfile();
      },
      register: async (payload) => {
        await axios.post(`${baseURL}/auth/register/`, payload);
        await get().login(payload.username, payload.password);
      },
      logout: async () => {
        const refresh = get().refresh;
        const access = get().access;
        if (refresh && access) {
          try {
            await axios.post(
              `${baseURL}/auth/logout/`,
              { refresh },
              { headers: { Authorization: `Bearer ${access}` } },
            );
          } catch {
            // Even if the server rejects (already-blacklisted, expired) we
            // still clear local state below.
          }
        }
        set({ access: null, refresh: null, user: null, isAuthenticated: false });
      },
      fetchProfile: async () => {
        const access = get().access;
        if (!access) return;
        const { data } = await axios.get(`${baseURL}/auth/profile/`, {
          headers: { Authorization: `Bearer ${access}` },
        });
        set({ user: data });
      },
    }),
    { name: 'bookshop-auth' },
  ),
);
