import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useBooksStore } from '@/store/books';
import { useCartStore } from '@/store/cart';

export default function BookDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { current, fetchBook, loading } = useBooksStore();
  const addToCart = useCartStore((s) => s.add);

  useEffect(() => {
    if (slug) fetchBook(slug);
  }, [slug, fetchBook]);

  if (loading || !current) {
    return <div className="container mx-auto p-8">Loading…</div>;
  }

  const onAdd = () => {
    addToCart({
      bookId: current.id,
      title: current.title,
      price: current.price,
      quantity: 1,
      cover: current.cover,
    });
    navigate('/cart');
  };

  return (
    <div className="container mx-auto px-4 py-8 grid md:grid-cols-3 gap-8">
      <div>
        <div className="aspect-[3/4] bg-gray-100 rounded overflow-hidden flex items-center justify-center">
          {current.cover ? (
            <img src={current.cover} alt={current.title} className="object-cover w-full h-full" />
          ) : (
            <span className="text-gray-400 text-sm">{current.title}</span>
          )}
        </div>
      </div>
      <div className="md:col-span-2">
        <h1 className="text-3xl font-bold mb-2">{current.title}</h1>
        <p className="text-gray-600 mb-4">by {current.author.name}</p>
        <p className="text-2xl font-bold text-primary mb-4">${current.price}</p>
        <p className="text-sm text-gray-500 mb-2">ISBN: {current.isbn}</p>
        <p className="text-sm text-gray-500 mb-4">{current.pages} pages · {current.language.toUpperCase()}</p>
        <p className="mb-6">{current.description}</p>
        <button onClick={onAdd} disabled={!current.is_in_stock} className="btn-primary">
          {current.is_in_stock ? 'Add to cart' : 'Out of stock'}
        </button>

        <section className="mt-8">
          <h2 className="text-xl font-semibold mb-2">
            Reviews {current.average_rating != null && `(avg ${current.average_rating})`}
          </h2>
          {current.reviews.length === 0 ? (
            <p className="text-gray-500">No reviews yet.</p>
          ) : (
            <ul className="space-y-3">
              {current.reviews.map((r) => (
                <li key={r.id} className="card p-3">
                  <div className="font-semibold">Rating: {r.rating}/5</div>
                  <p className="text-gray-700">{r.text}</p>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </div>
  );
}
