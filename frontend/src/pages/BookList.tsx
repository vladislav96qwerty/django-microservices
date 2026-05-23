import { useEffect } from 'react';
import { useBooksStore } from '@/store/books';
import BookCard from '@/components/BookCard';

export default function BookListPage() {
  const { list, count, loading, search, setSearch, fetchBooks } = useBooksStore();

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchBooks();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Books</h1>
        <form onSubmit={onSearch} className="flex gap-2">
          <input
            className="input"
            placeholder="Search by title, ISBN, author…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn-primary">Search</button>
        </form>
      </div>

      {loading && <p className="text-gray-500">Loading…</p>}
      {!loading && list.length === 0 && (
        <p className="text-gray-500">No books found.</p>
      )}

      <p className="text-sm text-gray-500 mb-4">{count} title{count === 1 ? '' : 's'}</p>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {list.map((book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>
    </div>
  );
}
