import { create } from 'zustand';
import api from '@/api/client';
import type { BookDetail, BookListItem, Paginated } from '@/types';

interface BooksState {
  list: BookListItem[];
  count: number;
  loading: boolean;
  current: BookDetail | null;
  search: string;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
  fetchBooks: (params?: Record<string, string>) => Promise<void>;
  fetchBook: (slug: string) => Promise<void>;
  setSearch: (q: string) => void;
  setPage: (page: number) => void;
}

export const useBooksStore = create<BooksState>((set, get) => ({
  list: [],
  count: 0,
  loading: false,
  current: null,
  search: '',
  page: 1,
  pageSize: 20,
  hasNext: false,
  hasPrev: false,
  setSearch: (q) => set({ search: q, page: 1 }),
  setPage: (page) => set({ page }),
  fetchBooks: async (params) => {
    set({ loading: true });
    try {
      const { page, search } = get();
      const query: Record<string, string> = { ...(params ?? {}), page: String(page) };
      if (search) query.search = search;
      const { data } = await api.get<Paginated<BookListItem>>('/books/', { params: query });
      set({
        list: data.results,
        count: data.count,
        hasNext: data.next !== null,
        hasPrev: data.previous !== null,
      });
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
