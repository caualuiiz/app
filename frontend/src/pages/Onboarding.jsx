import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { ArrowRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useAuth } from "@/contexts/AuthContext";
import { BUSINESS_TYPES, api, formatApiError } from "@/lib/api";

export default function OnboardingPage() {
  const { user, refreshContext, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", business_type: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!form.business_type) {
      setError("Selecione o tipo de negócio");
      return;
    }
    setLoading(true);
    try {
      await api.post("/companies", form);
      await refreshContext();
      toast.success("Empresa criada. Bem-vindo(a)!");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen auth-bg flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-xl">
        <div className="mb-8 text-center">
          <p className="text-xs uppercase tracking-widest text-indigo-600 font-semibold mb-2">
            Passo 2 de 2
          </p>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight text-slate-900" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
            Vamos configurar sua empresa
          </h1>
          <p className="text-slate-500 mt-2">
            Olá, <span className="font-semibold text-slate-900">{user?.name}</span>. Cadastre seu estabelecimento para começar.
          </p>
        </div>

        <form
          onSubmit={onSubmit}
          className="bg-white shadow-sm border border-slate-200 rounded-xl p-6 md:p-8 space-y-6"
          data-testid="onboarding-form"
        >
          <div className="space-y-2">
            <Label htmlFor="name">Nome do estabelecimento</Label>
            <Input
              id="name"
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              placeholder="Ex: Barbearia do João"
              minLength={2}
              required
              data-testid="onboarding-company-name-input"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="business_type">Tipo de negócio</Label>
            <Select
              value={form.business_type}
              onValueChange={(v) => setForm({ ...form, business_type: v })}
            >
              <SelectTrigger id="business_type" data-testid="onboarding-business-type-select">
                <SelectValue placeholder="Selecione o segmento" />
              </SelectTrigger>
              <SelectContent>
                {BUSINESS_TYPES.map((b) => (
                  <SelectItem key={b.value} value={b.value} data-testid={`business-option-${b.value}`}>
                    {b.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2" data-testid="onboarding-error">
              {error}
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3 justify-between items-center pt-2">
            <button
              type="button"
              onClick={async () => {
                await logout();
                navigate("/login", { replace: true });
              }}
              className="text-sm text-slate-500 hover:text-slate-700"
              data-testid="onboarding-cancel"
            >
              Sair da conta
            </button>
            <Button
              type="submit"
              className="bg-indigo-600 hover:bg-indigo-700 w-full sm:w-auto"
              disabled={loading}
              data-testid="onboarding-submit-btn"
            >
              {loading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <ArrowRight className="h-4 w-4 mr-2" />}
              Concluir e ir para o painel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
