import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';
import { useCartStore } from '@/store/cart';

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore();
  const cartCount = useCartStore((s) => s.totalQuantity());
  const navigate = useNavigate();

  const onLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm">
      <div className="container mx-auto px-4 py-3 flex items-center justify-between">
        <Link to="/" className="text-xl font-bold text-primary">
          Bookshop
        </Link>
        <div className="flex items-center gap-4">
          <Link to="/" className="text-gray-700 hover:text-primary">Books</Link>
          <Link to="/cart" className="text-gray-700 hover:text-primary relative">
            Cart
            {cartCount > 0 && (
              <span className="ml-1 inline-flex items-center justify-center px-2 py-0.5 text-xs bg-primary text-white rounded-full">
                {cartCount}
              </span>
            )}
          </Link>
          {isAuthenticated ? (
            <>
              <Link to="/profile" className="text-gray-700 hover:text-primary">
                {user?.username ?? 'Profile'}
              </Link>
              <button onClick={onLogout} className="btn-ghost">Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="text-gray-700 hover:text-primary">Login</Link>
              <Link to="/register" className="btn-primary">Sign up</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
