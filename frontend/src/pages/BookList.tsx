import { useEffect } from 'react';
import { useBooksStore } from '@/store/books';
import BookCard from '@/components/BookCard';
import { useT } from '@/i18n';

export default function BookListPage() {
  const {
    list,
    count,
    loading,
    search,
    page,
    pageSize,
    hasNext,
    hasPrev,
    setSearch,
    setPage,
    fetchBooks,
  } = useBooksStore();
  const t = useT();

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks, page]);

  const onSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchBooks();
  };

  const totalPages = Math.max(1, Math.ceil(count / pageSize));

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6 flex-wrap gap-3">
        <h1 className="text-3xl font-bold">{t('books.title')}</h1>
        <form onSubmit={onSearch} className="flex gap-2">
          <input
            className="input"
            placeholder={t('books.search.placeholder')}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <button type="submit" className="btn-primary">{t('books.search.button')}</button>
        </form>
      </div>

      {loading && <p className="text-gray-500">{t('books.loading')}</p>}
      {!loading && list.length === 0 && (
        <p className="text-gray-500">{t('books.empty')}</p>
      )}

      <p className="text-sm text-gray-500 mb-4">
        {count} {count === 1 ? t('books.titles') : t('books.titles_plural')}
      </p>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
        {list.map((book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>

      {count > pageSize && (
        <div className="mt-6 flex items-center justify-center gap-3">
          <button
            type="button"
            className="btn-ghost"
            disabled={!hasPrev || loading}
            onClick={() => setPage(page - 1)}
          >
            ← {t('common.previous')}
          </button>
          <span className="text-sm text-gray-600">
            {t('common.page')} {page} {t('common.of')} {totalPages}
          </span>
          <button
            type="button"
            className="btn-ghost"
            disabled={!hasNext || loading}
            onClick={() => setPage(page + 1)}
          >
            {t('common.next')} →
          </button>
        </div>
      )}
    </div>
  );
}
