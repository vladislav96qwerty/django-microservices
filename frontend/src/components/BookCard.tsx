import { Link } from 'react-router-dom';
import type { BookListItem } from '@/types';

interface Props {
  book: BookListItem;
}

export default function BookCard({ book }: Props) {
  return (
    <Link to={`/books/${book.slug}`} className="card p-4 hover:shadow-md transition block">
      <div className="aspect-[3/4] bg-gray-100 rounded mb-3 overflow-hidden flex items-center justify-center">
        {book.cover ? (
          <img src={book.cover} alt={book.title} className="object-cover w-full h-full" />
        ) : (
          <span className="text-gray-400 text-sm px-4 text-center">{book.title}</span>
        )}
      </div>
      <h3 className="font-semibold text-gray-900 line-clamp-2">{book.title}</h3>
      <p className="text-sm text-gray-600">{book.author_name}</p>
      <div className="flex justify-between items-center mt-2">
        <span className="font-bold text-primary">${book.price}</span>
        <span className={book.is_in_stock ? 'text-green-600 text-xs' : 'text-red-600 text-xs'}>
          {book.is_in_stock ? `In stock (${book.stock})` : 'Out of stock'}
        </span>
      </div>
    </Link>
  );
}
