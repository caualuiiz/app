import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, LogIn } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/contexts/AuthContext";
import { formatApiError } from "@/lib/api";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const data = await login(form);
      toast.success("Bem-vindo(a)!");
      const target = data.needs_onboarding ? "/onboarding" : location.state?.from?.pathname || "/dashboard";
      navigate(target, { replace: true });
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen auth-bg flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">
        <div className="mb-8 text-center">
          <div className="inline-flex h-12 w-12 items-center justify-center rounded-xl bg-indigo-600 text-white font-bold text-xl mb-4">
            G
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
            Acesso ao Sistema
          </h1>
          <p className="text-sm text-slate-500 mt-2">
            Entre com seus dados para acessar sua empresa.
          </p>
        </div>

        <form
          onSubmit={onSubmit}
          className="bg-white shadow-sm border border-slate-200 rounded-xl p-6 md:p-8 space-y-5"
          data-testid="login-form"
        >
          <div className="space-y-2">
            <Label htmlFor="email">E-mail</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              placeholder="voce@empresa.com"
              required
              data-testid="login-email-input"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="••••••••"
              required
              data-testid="login-password-input"
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2" data-testid="login-error">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700" disabled={loading} data-testid="login-submit-btn">
            {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <LogIn className="h-4 w-4 mr-2" />}
            Entrar
          </Button>

          <div className="flex items-center justify-between text-sm">
            <Link to="/register" className="text-indigo-600 hover:text-indigo-700 font-medium" data-testid="go-to-register">
              Criar nova conta
            </Link>
            <Link to="/forgot-password" className="text-indigo-600 hover:text-indigo-700 font-medium" data-testid="login-forgot-password-link">
              Esqueceu a senha?
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
