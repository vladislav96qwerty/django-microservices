export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  phone?: string;
  address?: string;
  avatar?: string | null;
  preferred_language?: 'en' | 'uk';
  is_verified?: boolean;
  date_joined?: string;
}

export interface Author {
  id: number;
  name: string;
  bio?: string;
  birth_date?: string | null;
}

export interface Category {
  id: number;
  name: string;
  slug: string;
}

export interface BookListItem {
  id: number;
  title: string;
  slug: string;
  isbn: string;
  author_name: string;
  price: string;
  cover: string | null;
  stock: number;
  is_in_stock: boolean;
  language: string;
}

export interface BookDetail {
  id: number;
  title: string;
  slug: string;
  isbn: string;
  author: Author;
  categories: Category[];
  description: string;
  cover: string | null;
  price: string;
  stock: number;
  is_in_stock: boolean;
  pages: number;
  language: string;
  publication_date?: string | null;
  is_active: boolean;
  average_rating: number | null;
  reviews: Review[];
}

export interface Review {
  id: number;
  book: number;
  rating: number;
  text: string;
  created_at: string;
}

export interface CartItem {
  bookId: number;
  title: string;
  price: string;
  quantity: number;
  cover?: string | null;
}

export interface Order {
  id: number;
  status: string;
  total: string;
  shipping_address: string;
  items: OrderItem[];
  created_at: string;
}

export interface OrderItem {
  id: number;
  book: number;
  book_title: string;
  quantity: number;
  unit_price: string;
  subtotal: string;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface AuthTokens {
  access: string;
  refresh: string;
}
