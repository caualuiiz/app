import { useState } from "react";
import { Link } from "react-router-dom";
import { toast } from "sonner";
import { Loader2, Mail } from "lucide-react";
import { api, formatApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [devResetUrl, setDevResetUrl] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const onSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setDevResetUrl("");
    try {
      const { data } = await api.post("/auth/forgot-password", { email });
      setSubmitted(true);
      if (data.reset_url) setDevResetUrl(data.reset_url);
      toast.success("Se o e-mail existir, as instruções serão enviadas.");
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
          <Mail className="mx-auto h-10 w-10 text-indigo-600 mb-3" />
          <h1 className="text-2xl font-extrabold text-slate-900">Recuperar senha</h1>
          <p className="text-sm text-slate-500 mt-2">Informe seu e-mail para receber as instruções.</p>
        </div>
        <form onSubmit={onSubmit} className="space-y-5" data-testid="forgot-password-form">
          <div className="space-y-2">
            <Label htmlFor="forgot-email">E-mail</Label>
            <Input id="forgot-email" type="email" autoComplete="email" required value={email} onChange={(e) => setEmail(e.target.value)} data-testid="forgot-password-email-input" />
          </div>
          {submitted && <p className="text-sm text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-md px-3 py-2">Se a conta existir, o pedido foi processado.</p>}
          {devResetUrl && <p className="text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">Modo desenvolvimento: <Link className="underline break-all" to={devResetUrl.replace(window.location.origin, "")}>abrir link de redefinição</Link></p>}
          <Button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-700" disabled={loading} data-testid="forgot-password-submit-btn">
            {loading && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}Enviar instruções
          </Button>
          <Link to="/login" className="block text-center text-sm text-indigo-600 hover:text-indigo-700">Voltar ao login</Link>
        </form>
      </div>
    </div>
  );
}
