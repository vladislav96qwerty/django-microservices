import { Link } from 'react-router-dom';
import { useCartStore } from '@/store/cart';

export default function CartPage() {
  const { items, remove, updateQuantity, totalAmount } = useCartStore();

  if (items.length === 0) {
    return (
      <div className="container mx-auto p-8">
        <h1 className="text-2xl font-bold mb-4">Your cart is empty</h1>
        <Link to="/" className="btn-primary">Browse books</Link>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Cart</h1>
      <div className="space-y-3">
        {items.map((item) => (
          <div key={item.bookId} className="card p-4 flex items-center justify-between">
            <div>
              <h3 className="font-semibold">{item.title}</h3>
              <p className="text-sm text-gray-500">${item.price}</p>
            </div>
            <div className="flex items-center gap-3">
              <input
                type="number"
                min={1}
                value={item.quantity}
                onChange={(e) => updateQuantity(item.bookId, parseInt(e.target.value || '1', 10))}
                className="input w-20"
              />
              <button onClick={() => remove(item.bookId)} className="btn-ghost">Remove</button>
            </div>
          </div>
        ))}
      </div>
      <div className="mt-6 flex justify-between items-center">
        <div className="text-xl font-bold">Total: ${totalAmount().toFixed(2)}</div>
        <Link to="/checkout" className="btn-primary">Checkout</Link>
      </div>
    </div>
  );
}
