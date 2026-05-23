import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuthStore } from '@/store/auth';

export default function RegisterPage() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
  });
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const register = useAuthStore((s) => s.register);
  const navigate = useNavigate();

  const onChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      await register(form);
      navigate('/');
    } catch {
      setError('Registration failed. Check the fields and try again.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-md">
      <h1 className="text-3xl font-bold mb-6">Create account</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="label">Username</label>
          <input className="input" name="username" value={form.username} onChange={onChange} required />
        </div>
        <div>
          <label className="label">Email</label>
          <input className="input" name="email" type="email" value={form.email} onChange={onChange} required />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="label">First name</label>
            <input className="input" name="first_name" value={form.first_name} onChange={onChange} />
          </div>
          <div>
            <label className="label">Last name</label>
            <input className="input" name="last_name" value={form.last_name} onChange={onChange} />
          </div>
        </div>
        <div>
          <label className="label">Password</label>
          <input className="input" name="password" type="password" value={form.password} onChange={onChange} required />
        </div>
        <div>
          <label className="label">Confirm password</label>
          <input
            className="input"
            name="password_confirm"
            type="password"
            value={form.password_confirm}
            onChange={onChange}
            required
          />
        </div>
        {error && <p className="text-red-600">{error}</p>}
        <button type="submit" disabled={busy} className="btn-primary w-full">
          {busy ? 'Creating account…' : 'Create account'}
        </button>
      </form>
      <p className="mt-4 text-sm text-gray-600">
        Already registered? <Link to="/login" className="text-primary">Log in</Link>
      </p>
    </div>
  );
}
