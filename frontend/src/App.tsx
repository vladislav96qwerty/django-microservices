import { Route, Routes } from 'react-router-dom';
import Navbar from '@/components/Navbar';
import ProtectedRoute from '@/components/ProtectedRoute';
import BookListPage from '@/pages/BookList';
import BookDetailPage from '@/pages/BookDetail';
import CartPage from '@/pages/Cart';
import CheckoutPage from '@/pages/Checkout';
import LoginPage from '@/pages/Login';
import RegisterPage from '@/pages/Register';
import ProfilePage from '@/pages/Profile';
import OrderDetailPage from '@/pages/OrderDetail';

export default function App() {
  return (
    <>
      <Navbar />
      <main>
        <Routes>
          <Route path="/" element={<BookListPage />} />
          <Route path="/books/:slug" element={<BookDetailPage />} />
          <Route path="/cart" element={<CartPage />} />
          <Route
            path="/checkout"
            element={
              <ProtectedRoute>
                <CheckoutPage />
              </ProtectedRoute>
            }
          />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route
            path="/profile"
            element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            }
          />
          <Route
            path="/orders/:id"
            element={
              <ProtectedRoute>
                <OrderDetailPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<div className="container mx-auto p-8">Not Found</div>} />
        </Routes>
      </main>
    </>
  );
}
