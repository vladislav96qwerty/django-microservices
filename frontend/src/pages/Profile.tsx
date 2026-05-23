import { useEffect, useState } from 'react';
import api from '@/api/client';
import { useAuthStore } from '@/store/auth';
import type { Order, Paginated } from '@/types';

export default function ProfilePage() {
  const { user, fetchProfile } = useAuthStore();
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProfile().catch(() => undefined);
    api.get<Paginated<Order>>('/orders/')
      .then((resp) => setOrders(resp.data.results))
      .catch(() => setOrders([]))
      .finally(() => setLoading(false));
  }, [fetchProfile]);

  if (!user) {
    return <div className="container mx-auto p-8">Loading profile…</div>;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-3xl">
      <h1 className="text-3xl font-bold mb-6">Profile</h1>
      <section className="card p-4 mb-6">
        <h2 className="font-semibold mb-2">Account</h2>
        <dl className="grid grid-cols-2 gap-2 text-sm">
          <dt className="text-gray-500">Username</dt><dd>{user.username}</dd>
          <dt className="text-gray-500">Email</dt><dd>{user.email}</dd>
          <dt className="text-gray-500">Name</dt><dd>{user.first_name} {user.last_name}</dd>
          <dt className="text-gray-500">Phone</dt><dd>{user.phone || '—'}</dd>
          <dt className="text-gray-500">Language</dt><dd>{user.preferred_language?.toUpperCase()}</dd>
          <dt className="text-gray-500">Verified</dt><dd>{user.is_verified ? 'Yes' : 'No'}</dd>
        </dl>
      </section>

      <section>
        <h2 className="text-xl font-semibold mb-3">Your orders</h2>
        {loading ? (
          <p className="text-gray-500">Loading orders…</p>
        ) : orders.length === 0 ? (
          <p className="text-gray-500">No orders yet.</p>
        ) : (
          <ul className="space-y-3">
            {orders.map((order) => (
              <li key={order.id} className="card p-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="font-semibold">Order #{order.id}</span>
                  <span className="text-sm uppercase text-gray-500">{order.status}</span>
                </div>
                <ul className="text-sm text-gray-700">
                  {order.items.map((item) => (
                    <li key={item.id}>
                      {item.book_title} × {item.quantity} — ${item.subtotal}
                    </li>
                  ))}
                </ul>
                <div className="mt-2 font-bold">Total: ${order.total}</div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
