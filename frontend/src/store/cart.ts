import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CartItem } from '@/types';

interface CartState {
  items: CartItem[];
  add: (item: CartItem) => void;
  remove: (bookId: number) => void;
  updateQuantity: (bookId: number, quantity: number) => void;
  clear: () => void;
  totalQuantity: () => number;
  totalAmount: () => number;
}

export const useCartStore = create<CartState>()(
  persist(
    (set, get) => ({
      items: [],
      add: (item) =>
        set((state) => {
          const existing = state.items.find((i) => i.bookId === item.bookId);
          if (existing) {
            return {
              items: state.items.map((i) =>
                i.bookId === item.bookId
                  ? { ...i, quantity: i.quantity + item.quantity }
                  : i,
              ),
            };
          }
          return { items: [...state.items, item] };
        }),
      remove: (bookId) => set((state) => ({ items: state.items.filter((i) => i.bookId !== bookId) })),
      updateQuantity: (bookId, quantity) =>
        set((state) => ({
          items: state.items.map((i) =>
            i.bookId === bookId ? { ...i, quantity: Math.max(1, quantity) } : i,
          ),
        })),
      clear: () => set({ items: [] }),
      totalQuantity: () => get().items.reduce((sum, i) => sum + i.quantity, 0),
      totalAmount: () =>
        get().items.reduce((sum, i) => sum + parseFloat(i.price) * i.quantity, 0),
    }),
    { name: 'bookshop-cart' },
  ),
);
