import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { Camera, Image as ImageIcon, Loader2, Save } from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Card, CardContent } from "@/components/ui/card";
import { API, BUSINESS_TYPES, api, formatApiError } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

function AuthedImage({ path, alt, className, fallback }) {
  const [src, setSrc] = useState(null);
  useEffect(() => {
    if (!path) return;
    let objectUrl;
    let cancelled = false;
    (async () => {
      try {
        const url = path.startsWith("/api/") ? path.replace(/^\/api/, "") : `/uploads/file/${path}`;
        const res = await api.get(url, { responseType: "blob" });
        objectUrl = URL.createObjectURL(res.data);
        if (!cancelled) setSrc(objectUrl);
      } catch {
        if (!cancelled) setSrc(null);
      }
    })();
    return () => {
      cancelled = true;
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [path]);
  if (!path) return fallback;
  if (!src) return <div className={`${className} bg-slate-100 animate-pulse`} />;
  return <img src={src} alt={alt} className={className} />;
}

export default function CompanySettingsPage() {
  const { refreshContext, role } = useAuth();
  const [form, setForm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [uploading, setUploading] = useState({ logo: false, establishment: false });
  const logoRef = useRef(null);
  const photoRef = useRef(null);

  const isOwner = role === "OWNER";

  useEffect(() => {
    (async () => {
      try {
        const { data } = await api.get("/companies/me");
        setForm(data);
      } catch (err) {
        setError(formatApiError(err));
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const onSave = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      const payload = { ...form };
      delete payload.id;
      delete payload.slug;
      delete payload.created_at;
      delete payload.updated_at;
      delete payload.status;
      delete payload.logo_url;
      delete payload.establishment_photo_url;
      if (!isOwner) delete payload.name;
      Object.keys(payload).forEach((k) => (payload[k] === "" ? (payload[k] = null) : null));
      const { data } = await api.patch("/companies/me", payload);
      setForm(data);
      await refreshContext();
      toast.success("Empresa atualizada com sucesso");
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const onUpload = async (kind, file) => {
    if (!file) return;
    setUploading((u) => ({ ...u, [kind]: true }));
    try {
      const fd = new FormData();
      fd.append("file", file);
      const { data } = await api.post(`/uploads/company-image?kind=${kind}`, fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setForm((f) => ({
        ...f,
        [kind === "logo" ? "logo_url" : "establishment_photo_url"]: data.url,
      }));
      await refreshContext();
      toast.success("Imagem enviada");
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setUploading((u) => ({ ...u, [kind]: false }));
    }
  };

  if (loading || !form) {
    return (
      <AppShell title="Configurações da empresa">
        <div className="flex items-center gap-2 text-slate-500">
          <Loader2 className="h-4 w-4 animate-spin" /> Carregando…
        </div>
      </AppShell>
    );
  }

  return (
    <AppShell title="Configurações da empresa">
      <form onSubmit={onSave} className="max-w-4xl mx-auto space-y-6" data-testid="company-settings-form">
        <Card className="border-slate-200">
          <CardContent className="p-6 space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label>Logo da empresa</Label>
                <div className="flex items-center gap-4">
                  <div className="h-20 w-20 rounded-xl border border-slate-200 overflow-hidden bg-slate-50 flex items-center justify-center">
                    <AuthedImage
                      path={form.logo_url}
                      alt="Logo"
                      className="h-20 w-20 object-cover"
                      fallback={<ImageIcon className="h-6 w-6 text-slate-400" />}
                    />
                  </div>
                  <div>
                    <input
                      ref={logoRef}
                      type="file"
                      accept="image/png,image/jpeg,image/webp,image/gif"
                      className="hidden"
                      onChange={(e) => onUpload("logo", e.target.files?.[0])}
                      data-testid="logo-file-input"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => logoRef.current?.click()}
                      disabled={uploading.logo}
                      data-testid="upload-logo-btn"
                    >
                      {uploading.logo ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Camera className="h-4 w-4 mr-2" />}
                      Enviar logo
                    </Button>
                    <p className="text-xs text-slate-500 mt-1">PNG, JPG ou WEBP até 5MB</p>
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Foto do estabelecimento</Label>
                <div className="flex items-center gap-4">
                  <div className="h-20 w-32 rounded-xl border border-slate-200 overflow-hidden bg-slate-50 flex items-center justify-center">
                    <AuthedImage
                      path={form.establishment_photo_url}
                      alt="Foto"
                      className="h-20 w-32 object-cover"
                      fallback={<ImageIcon className="h-6 w-6 text-slate-400" />}
                    />
                  </div>
                  <div>
                    <input
                      ref={photoRef}
                      type="file"
                      accept="image/png,image/jpeg,image/webp,image/gif"
                      className="hidden"
                      onChange={(e) => onUpload("establishment", e.target.files?.[0])}
                      data-testid="photo-file-input"
                    />
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => photoRef.current?.click()}
                      disabled={uploading.establishment}
                      data-testid="upload-photo-btn"
                    >
                      {uploading.establishment ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Camera className="h-4 w-4 mr-2" />}
                      Enviar foto
                    </Button>
                    <p className="text-xs text-slate-500 mt-1">PNG, JPG ou WEBP até 5MB</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="name">Nome da empresa</Label>
                <Input
                  id="name"
                  value={form.name || ""}
                  onChange={(e) => setForm({ ...form, name: e.target.value })}
                  disabled={!isOwner}
                  required
                  data-testid="company-name-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="business_type">Tipo de negócio</Label>
                <Select
                  value={form.business_type}
                  onValueChange={(v) => setForm({ ...form, business_type: v })}
                >
                  <SelectTrigger id="business_type" data-testid="company-business-type-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {BUSINESS_TYPES.map((b) => (
                      <SelectItem key={b.value} value={b.value}>{b.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Descrição</Label>
              <Textarea
                id="description"
                rows={3}
                value={form.description || ""}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Uma breve descrição do seu negócio"
                data-testid="company-description-input"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="phone">Telefone</Label>
                <Input
                  id="phone"
                  value={form.phone || ""}
                  onChange={(e) => setForm({ ...form, phone: e.target.value })}
                  placeholder="(11) 99999-0000"
                  data-testid="company-phone-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">E-mail de contato</Label>
                <Input
                  id="email"
                  type="email"
                  value={form.email || ""}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  placeholder="contato@empresa.com"
                  data-testid="company-email-input"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="address">Endereço</Label>
              <Input
                id="address"
                value={form.address || ""}
                onChange={(e) => setForm({ ...form, address: e.target.value })}
                placeholder="Rua, número, bairro"
                data-testid="company-address-input"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="space-y-2">
                <Label htmlFor="city">Cidade</Label>
                <Input
                  id="city"
                  value={form.city || ""}
                  onChange={(e) => setForm({ ...form, city: e.target.value })}
                  data-testid="company-city-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="state">Estado</Label>
                <Input
                  id="state"
                  value={form.state || ""}
                  onChange={(e) => setForm({ ...form, state: e.target.value })}
                  placeholder="SP"
                  data-testid="company-state-input"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="zip_code">CEP</Label>
                <Input
                  id="zip_code"
                  value={form.zip_code || ""}
                  onChange={(e) => setForm({ ...form, zip_code: e.target.value })}
                  placeholder="00000-000"
                  data-testid="company-zip-input"
                />
              </div>
            </div>

            {error && (
              <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2" data-testid="company-settings-error">
                {error}
              </div>
            )}

            <div className="flex items-center justify-between">
              <div className="text-xs text-slate-500">
                Slug: <span className="font-mono">{form.slug}</span>
              </div>
              <Button type="submit" className="bg-indigo-600 hover:bg-indigo-700" disabled={saving} data-testid="save-company-btn">
                {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Save className="h-4 w-4 mr-2" />}
                Salvar alterações
              </Button>
            </div>
          </CardContent>
        </Card>
      </form>
    </AppShell>
  );
}
