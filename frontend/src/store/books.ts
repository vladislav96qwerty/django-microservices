import { create } from 'zustand';
import api from '@/api/client';
import type { BookDetail, BookListItem, Paginated } from '@/types';

interface BooksState {
  list: BookListItem[];
  count: number;
  loading: boolean;
  current: BookDetail | null;
  search: string;
  fetchBooks: (params?: Record<string, string>) => Promise<void>;
  fetchBook: (slug: string) => Promise<void>;
  setSearch: (q: string) => void;
}

export const useBooksStore = create<BooksState>((set, get) => ({
  list: [],
  count: 0,
  loading: false,
  current: null,
  search: '',
  setSearch: (q) => set({ search: q }),
  fetchBooks: async (params) => {
    set({ loading: true });
    try {
      const query: Record<string, string> = { ...(params ?? {}) };
      const search = get().search;
      if (search) query.search = search;
      const { data } = await api.get<Paginated<BookListItem>>('/books/', { params: query });
      set({ list: data.results, count: data.count });
    } finally {
      set({ loading: false });
    }
  },
  fetchBook: async (slug) => {
    set({ loading: true });
    try {
      const { data } = await api.get<BookDetail>(`/books/${slug}/`);
      set({ current: data });
    } finally {
      set({ loading: false });
    }
  },
}));
