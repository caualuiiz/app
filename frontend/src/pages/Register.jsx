import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useAuth } from "@/contexts/AuthContext";
import { formatApiError } from "@/lib/api";

export default function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    name: "",
    email: "",
    password: "",
    password_confirm: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (form.password !== form.password_confirm) {
      setError("As senhas não coincidem");
      return;
    }
    setLoading(true);
    try {
      await register(form);
      toast.success("Conta criada com sucesso!");
      navigate("/onboarding", { replace: true });
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
            Crie sua conta
          </h1>
          <p className="text-sm text-slate-500 mt-2">
            Comece agora — configuraremos sua empresa no próximo passo.
          </p>
        </div>

        <form
          onSubmit={onSubmit}
          className="bg-white shadow-sm border border-slate-200 rounded-xl p-6 md:p-8 space-y-5"
          data-testid="register-form"
        >
          <div className="space-y-2">
            <Label htmlFor="name">Nome completo</Label>
            <Input
              id="name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Seu nome"
              minLength={2}
              required
              data-testid="register-name-input"
            />
          </div>
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
              data-testid="register-email-input"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Senha</Label>
            <Input
              id="password"
              type="password"
              autoComplete="new-password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="Mínimo 8 caracteres"
              minLength={8}
              required
              data-testid="register-password-input"
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password_confirm">Confirmar senha</Label>
            <Input
              id="password_confirm"
              type="password"
              autoComplete="new-password"
              value={form.password_confirm}
              onChange={(e) => setForm({ ...form, password_confirm: e.target.value })}
              placeholder="Repita a senha"
              minLength={8}
              required
              data-testid="register-password-confirm-input"
            />
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2" data-testid="register-error">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700" disabled={loading} data-testid="register-submit-btn">
            {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <UserPlus className="h-4 w-4 mr-2" />}
            Criar conta
          </Button>

          <p className="text-sm text-center text-slate-500">
            Já possui uma conta?{" "}
            <Link to="/login" className="text-indigo-600 hover:text-indigo-700 font-medium" data-testid="go-to-login">
              Faça login
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}
