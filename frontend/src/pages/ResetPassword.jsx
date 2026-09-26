import { useMemo, useState } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, LockKeyhole } from "lucide-react";
import { api, formatApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ResetPasswordPage() {
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const token = useMemo(() => params.get("token") || "", [params]);
  const [password, setPassword] = useState("");
  const [confirmation, setConfirmation] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    if (password !== confirmation) {
      toast.error("As senhas não coincidem.");
      return;
    }
    setLoading(true);
    try {
      await api.post("/auth/reset-password", { token, password });
      toast.success("Senha redefinida. Faça login novamente.");
      navigate("/login", { replace: true });
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen auth-bg flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md bg-white shadow-sm border border-slate-200 rounded-xl p-6 md:p-8">
        <div className="mb-6 text-center">
          <LockKeyhole className="mx-auto h-10 w-10 text-indigo-600 mb-3" />
          <h1 className="text-2xl font-extrabold text-slate-900">Definir nova senha</h1>
        </div>
        {!token ? <p className="text-sm text-red-600">Token de recuperação ausente ou inválido.</p> : <form onSubmit={onSubmit} className="space-y-5" data-testid="reset-password-form">
          <div className="space-y-2"><Label htmlFor="reset-password">Nova senha</Label><Input id="reset-password" type="password" minLength={8} autoComplete="new-password" required value={password} onChange={(e) => setPassword(e.target.value)} data-testid="reset-password-input" /></div>
          <div className="space-y-2"><Label htmlFor="reset-password-confirm">Confirmar nova senha</Label><Input id="reset-password-confirm" type="password" minLength={8} autoComplete="new-password" required value={confirmation} onChange={(e) => setConfirmation(e.target.value)} data-testid="reset-password-confirm-input" /></div>
          <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700" disabled={loading} data-testid="reset-password-submit-btn">
            {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}Redefinir senha
          </Button>
        </form>}
        <Link to="/login" className="block text-center text-sm text-indigo-600 hover:text-indigo-700 mt-5">Voltar ao login</Link>
      </div>
    </div>
  );
}
