import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '@/api/client';
import { useCartStore } from '@/store/cart';

export default function CheckoutPage() {
  const navigate = useNavigate();
  const { items, totalAmount, clear } = useCartStore();
  const [address, setAddress] = useState('');
  const [notes, setNotes] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const payload = {
        shipping_address: address,
        notes,
        items: items.map((i) => ({ book: i.bookId, quantity: i.quantity })),
      };
      await api.post('/orders/', payload);
      clear();
      navigate('/profile');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Checkout failed';
      setError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  if (items.length === 0) {
    return (
      <div className="container mx-auto p-8">
        <p>Your cart is empty.</p>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-xl">
      <h1 className="text-3xl font-bold mb-6">Checkout</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="label">Shipping address</label>
          <input className="input" value={address} onChange={(e) => setAddress(e.target.value)} required />
        </div>
        <div>
          <label className="label">Notes</label>
          <textarea className="input" value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
        </div>
        <div className="card p-4">
          <h2 className="font-semibold mb-2">Order summary</h2>
          {items.map((i) => (
            <div key={i.bookId} className="flex justify-between text-sm">
              <span>{i.title} × {i.quantity}</span>
              <span>${(parseFloat(i.price) * i.quantity).toFixed(2)}</span>
            </div>
          ))}
          <div className="border-t mt-2 pt-2 font-bold flex justify-between">
            <span>Total</span><span>${totalAmount().toFixed(2)}</span>
          </div>
        </div>
        {error && <p className="text-red-600">{error}</p>}
        <button type="submit" disabled={submitting} className="btn-primary w-full">
          {submitting ? 'Placing order…' : 'Place order'}
        </button>
      </form>
    </div>
  );
}
