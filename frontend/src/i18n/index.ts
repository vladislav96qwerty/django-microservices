import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Lang = 'en' | 'uk';

type Dict = Record<string, string>;

const translations: Record<Lang, Dict> = {
  en: {
    'nav.books': 'Books',
    'nav.cart': 'Cart',
    'nav.login': 'Login',
    'nav.signup': 'Sign up',
    'nav.logout': 'Logout',
    'nav.profile': 'Profile',
    'books.title': 'Books',
    'books.search.placeholder': 'Search by title, ISBN, author…',
    'books.search.button': 'Search',
    'books.loading': 'Loading…',
    'books.empty': 'No books found.',
    'books.titles': 'title',
    'books.titles_plural': 'titles',
    'book.in_stock': 'In stock',
    'book.out_of_stock': 'Out of stock',
    'book.add_to_cart': 'Add to cart',
    'book.reviews': 'Reviews',
    'book.no_reviews': 'No reviews yet.',
    'cart.empty.title': 'Your cart is empty',
    'cart.empty.cta': 'Browse books',
    'cart.title': 'Cart',
    'cart.total': 'Total',
    'cart.checkout': 'Checkout',
    'cart.remove': 'Remove',
    'checkout.title': 'Checkout',
    'checkout.address': 'Shipping address',
    'checkout.notes': 'Notes',
    'checkout.summary': 'Order summary',
    'checkout.placing': 'Placing order…',
    'checkout.place': 'Place order',
    'auth.login.title': 'Log in',
    'auth.login.username': 'Username',
    'auth.login.password': 'Password',
    'auth.login.submit': 'Log in',
    'auth.login.busy': 'Logging in…',
    'auth.login.bad': 'Invalid credentials',
    'auth.login.no_account': "Don't have an account?",
    'auth.register.title': 'Create account',
    'auth.register.submit': 'Create account',
    'auth.register.busy': 'Creating account…',
    'auth.register.have': 'Already registered?',
    'profile.title': 'Profile',
    'profile.account': 'Account',
    'profile.orders': 'Your orders',
    'profile.no_orders': 'No orders yet.',
    'profile.loading_orders': 'Loading orders…',
    'common.previous': 'Previous',
    'common.next': 'Next',
    'common.page': 'Page',
    'common.of': 'of',
  },
  uk: {
    'nav.books': 'Книги',
    'nav.cart': 'Кошик',
    'nav.login': 'Увійти',
    'nav.signup': 'Реєстрація',
    'nav.logout': 'Вийти',
    'nav.profile': 'Профіль',
    'books.title': 'Книги',
    'books.search.placeholder': 'Пошук за назвою, ISBN, автором…',
    'books.search.button': 'Пошук',
    'books.loading': 'Завантаження…',
    'books.empty': 'Книги не знайдено.',
    'books.titles': 'книга',
    'books.titles_plural': 'книг',
    'book.in_stock': 'В наявності',
    'book.out_of_stock': 'Немає в наявності',
    'book.add_to_cart': 'Додати в кошик',
    'book.reviews': 'Відгуки',
    'book.no_reviews': 'Поки що немає відгуків.',
    'cart.empty.title': 'Ваш кошик порожній',
    'cart.empty.cta': 'Перейти до книг',
    'cart.title': 'Кошик',
    'cart.total': 'Разом',
    'cart.checkout': 'Оформити',
    'cart.remove': 'Видалити',
    'checkout.title': 'Оформлення',
    'checkout.address': 'Адреса доставки',
    'checkout.notes': 'Примітки',
    'checkout.summary': 'Підсумок замовлення',
    'checkout.placing': 'Оформлення…',
    'checkout.place': 'Оформити замовлення',
    'auth.login.title': 'Вхід',
    'auth.login.username': "Ім'я користувача",
    'auth.login.password': 'Пароль',
    'auth.login.submit': 'Увійти',
    'auth.login.busy': 'Вхід…',
    'auth.login.bad': 'Невірні дані',
    'auth.login.no_account': 'Немає облікового запису?',
    'auth.register.title': 'Створити обліковий запис',
    'auth.register.submit': 'Створити обліковий запис',
    'auth.register.busy': 'Створення…',
    'auth.register.have': 'Вже зареєстровані?',
    'profile.title': 'Профіль',
    'profile.account': 'Обліковий запис',
    'profile.orders': 'Ваші замовлення',
    'profile.no_orders': 'Замовлень ще немає.',
    'profile.loading_orders': 'Завантаження замовлень…',
    'common.previous': 'Назад',
    'common.next': 'Далі',
    'common.page': 'Сторінка',
    'common.of': 'з',
  },
};

interface LocaleState {
  lang: Lang;
  setLang: (lang: Lang) => void;
}

export const useLocaleStore = create<LocaleState>()(
  persist(
    (set) => ({
      lang: 'en',
      setLang: (lang) => set({ lang }),
    }),
    { name: 'bookshop-locale' },
  ),
);

export function useT() {
  const lang = useLocaleStore((s) => s.lang);
  return (key: string): string => translations[lang][key] ?? key;
}
