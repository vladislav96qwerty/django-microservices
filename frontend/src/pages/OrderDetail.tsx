import { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import api from '@/api/client';
import type { Order } from '@/types';

export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [cancelling, setCancelling] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    api
      .get<Order>(`/orders/${id}/`)
      .then((resp) => setOrder(resp.data))
      .catch(() => setError('Order not found'))
      .finally(() => setLoading(false));
  }, [id]);

  const onCancel = async () => {
    if (!order) return;
    setCancelling(true);
    try {
      const { data } = await api.post<Order>(`/orders/${order.id}/cancel/`);
      setOrder(data);
    } catch {
      setError('Failed to cancel order');
    } finally {
      setCancelling(false);
    }
  };

  if (loading) return <div className="container mx-auto p-8">Loading…</div>;
  if (error || !order) {
    return (
      <div className="container mx-auto p-8">
        <p className="text-red-600 mb-4">{error ?? 'Order not found'}</p>
        <button onClick={() => navigate('/profile')} className="btn-ghost">
          Back to profile
        </button>
      </div>
    );
  }

  const canCancel = !['cancelled', 'delivered', 'shipped'].includes(order.status);

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Order #{order.id}</h1>
        <Link to="/profile" className="text-primary hover:underline">
          ← All orders
        </Link>
      </div>

      <div className="card p-4 mb-6">
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div>
            <div className="text-gray-500">Status</div>
            <div className="font-semibold uppercase">{order.status}</div>
          </div>
          <div>
            <div className="text-gray-500">Total</div>
            <div className="font-semibold">${order.total}</div>
          </div>
          <div className="col-span-2">
            <div className="text-gray-500">Shipping address</div>
            <div>{order.shipping_address}</div>
          </div>
          <div className="col-span-2">
            <div className="text-gray-500">Placed</div>
            <div>{new Date(order.created_at).toLocaleString()}</div>
          </div>
        </div>
      </div>

      <h2 className="text-xl font-semibold mb-3">Items</h2>
      <ul className="space-y-2 mb-6">
        {order.items.map((item) => (
          <li key={item.id} className="card p-3 flex justify-between items-center">
            <div>
              <div className="font-medium">{item.book_title}</div>
              <div className="text-sm text-gray-500">
                {item.quantity} × ${item.unit_price}
              </div>
            </div>
            <div className="font-semibold">${item.subtotal}</div>
          </li>
        ))}
      </ul>

      {canCancel && (
        <button onClick={onCancel} disabled={cancelling} className="btn-ghost">
          {cancelling ? 'Cancelling…' : 'Cancel order'}
        </button>
      )}
    </div>
  );
}
