import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';
import { useLocaleStore, useT, type Lang } from '@/i18n';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const cartCount = useCartStore((s) => s.totalQuantity());
  const { lang, setLang } = useLocaleStore();
  const t = useT();
  const navigate = useNavigate();

  const onLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-primary">
          Bookshop
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-gray-700 hover:text-primary">{t('nav.books')}</Link>
          <Link to="/cart" className="text-gray-700 hover:text-primary relative">
            {t('nav.cart')}
            {cartCount > 0 && (
              <span className="ml-1 inline-flex items-center justify-center px-2 py-0.5 text-xs bg-primary text-white rounded-full">
                {cartCount}
              </span>
            )}
          </Link>
          <select
            value={lang}
            onChange={(e) => setLang(e.target.value as Lang)}
            className="text-sm border border-gray-300 rounded-md px-2 py-1 bg-white"
            aria-label="Language"
          >
            <option value="en">EN</option>
            <option value="uk">UK</option>
          </select>
          {isAuthenticated ? (
            <>
              <Link to="/profile" className="text-gray-700 hover:text-primary">
                {user?.username ?? t('nav.profile')}
              </Link>
              <button onClick={onLogout} className="btn-ghost">{t('nav.logout')}</button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-primary">{t('nav.login')}</Link>
              <Link to="/register" className="btn-primary">{t('nav.signup')}</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
