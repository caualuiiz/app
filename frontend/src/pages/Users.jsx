import { useEffect, useState } from "react";
import { toast } from "sonner";
import { Loader2, Plus, Trash2, UserCog, UserPlus } from "lucide-react";
import AppShell from "@/components/AppShell";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { api, formatApiError, ROLE_LABELS } from "@/lib/api";
import { useAuth } from "@/contexts/AuthContext";

export default function UsersPage() {
  const { user, role } = useAuth();
  const isOwner = role === "OWNER";

  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ email: "", name: "", role: "PROFESSIONAL" });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const { data } = await api.get("/memberships");
      setMembers(data);
    } catch (err) {
      toast.error(formatApiError(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const invite = async (e) => {
    e.preventDefault();
    setError("");
    setSaving(true);
    try {
      await api.post("/memberships", form);
      setOpen(false);
      setForm({ email: "", name: "", role: "PROFESSIONAL" });
      toast.success("Membro adicionado");
      load();
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSaving(false);
    }
  };

  const changeRole = async (id, newRole) => {
    try {
      await api.patch(`/memberships/${id}`, { role: newRole });
      toast.success("Função atualizada");
      load();
    } catch (err) {
      toast.error(formatApiError(err));
    }
  };

  const remove = async (id) => {
    try {
      await api.delete(`/memberships/${id}`);
      toast.success("Membro removido");
      load();
    } catch (err) {
      toast.error(formatApiError(err));
    }
  };

  return (
    <AppShell title="Membros">
      <div className="max-w-5xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900" style={{ fontFamily: "'Plus Jakarta Sans'" }}>
              Equipe da empresa
            </h2>
            <p className="text-sm text-slate-500">
              Gerencie quem pode acessar sua empresa e com qual permissão.
            </p>
          </div>
          {isOwner && (
            <Dialog open={open} onOpenChange={setOpen}>
              <DialogTrigger asChild>
                <Button className="bg-indigo-600 hover:bg-indigo-700" data-testid="open-invite-dialog">
                  <UserPlus className="h-4 w-4 mr-2" /> Adicionar membro
                </Button>
              </DialogTrigger>
              <DialogContent data-testid="invite-dialog">
                <DialogHeader>
                  <DialogTitle>Adicionar membro</DialogTitle>
                  <DialogDescription>
                    Se o e-mail ainda não estiver cadastrado, uma nova conta será criada com senha temporária exibida uma única vez.
                  </DialogDescription>
                </DialogHeader>
                <form onSubmit={invite} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="i-email">E-mail</Label>
                    <Input
                      id="i-email"
                      type="email"
                      required
                      value={form.email}
                      onChange={(e) => setForm({ ...form, email: e.target.value })}
                      data-testid="invite-email-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="i-name">Nome (opcional se usuário já existe)</Label>
                    <Input
                      id="i-name"
                      value={form.name}
                      onChange={(e) => setForm({ ...form, name: e.target.value })}
                      data-testid="invite-name-input"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Função</Label>
                    <Select
                      value={form.role}
                      onValueChange={(v) => setForm({ ...form, role: v })}
                    >
                      <SelectTrigger data-testid="invite-role-select">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="MANAGER">Gerente</SelectItem>
                        <SelectItem value="PROFESSIONAL">Profissional</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {error && (
                    <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md px-3 py-2" data-testid="invite-error">
                      {error}
                    </div>
                  )}
                  <DialogFooter>
                    <Button
                      type="button"
                      variant="ghost"
                      onClick={() => setOpen(false)}
                      data-testid="invite-cancel-btn"
                    >
                      Cancelar
                    </Button>
                    <Button
                      type="submit"
                      className="bg-indigo-600 hover:bg-indigo-700"
                      disabled={saving}
                      data-testid="invite-submit-btn"
                    >
                      {saving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <Plus className="h-4 w-4 mr-2" />}
                      Adicionar
                    </Button>
                  </DialogFooter>
                </form>
              </DialogContent>
            </Dialog>
          )}
        </div>

        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          {loading ? (
            <div className="p-6 flex items-center gap-2 text-slate-500">
              <Loader2 className="h-4 w-4 animate-spin" /> Carregando membros…
            </div>
          ) : members.length === 0 ? (
            <div className="p-10 text-center text-slate-500">
              <UserCog className="h-10 w-10 mx-auto text-slate-300 mb-3" />
              Nenhum membro por aqui ainda.
            </div>
          ) : (
            <Table data-testid="members-table">
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>E-mail</TableHead>
                  <TableHead>Função</TableHead>
                  <TableHead>Status</TableHead>
                  {isOwner && <TableHead className="text-right">Ações</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {members.map((m) => (
                  <TableRow key={m.id} data-testid={`member-row-${m.id}`}>
                    <TableCell className="font-medium text-slate-900">
                      {m.user_name}
                      {m.user_id === user?.id && (
                        <Badge variant="outline" className="ml-2 text-[10px]">Você</Badge>
                      )}
                    </TableCell>
                    <TableCell className="text-slate-600">{m.user_email}</TableCell>
                    <TableCell>
                      {isOwner && m.user_id !== user?.id ? (
                        <Select
                          value={m.role}
                          onValueChange={(v) => changeRole(m.id, v)}
                        >
                          <SelectTrigger className="w-40" data-testid={`role-select-${m.id}`}>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="OWNER">Proprietário</SelectItem>
                            <SelectItem value="MANAGER">Gerente</SelectItem>
                            <SelectItem value="PROFESSIONAL">Profissional</SelectItem>
                          </SelectContent>
                        </Select>
                      ) : (
                        <Badge
                          className={
                            m.role === "OWNER"
                              ? "bg-indigo-600 hover:bg-indigo-600"
                              : m.role === "MANAGER"
                              ? "bg-sky-600 hover:bg-sky-600"
                              : "bg-slate-500 hover:bg-slate-500"
                          }
                        >
                          {ROLE_LABELS[m.role]}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge variant={m.status === "ACTIVE" ? "default" : "outline"} className={m.status === "ACTIVE" ? "bg-emerald-600 hover:bg-emerald-600" : ""}>
                        {m.status}
                      </Badge>
                    </TableCell>
                    {isOwner && (
                      <TableCell className="text-right">
                        {m.user_id !== user?.id && (
                          <AlertDialog>
                            <AlertDialogTrigger asChild>
                              <Button variant="ghost" size="icon" className="text-red-600 hover:text-red-700" data-testid={`remove-member-${m.id}`}>
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </AlertDialogTrigger>
                            <AlertDialogContent>
                              <AlertDialogHeader>
                                <AlertDialogTitle>Remover membro?</AlertDialogTitle>
                                <AlertDialogDescription>
                                  {m.user_name} perderá acesso a esta empresa. Você pode adicioná-lo novamente depois.
                                </AlertDialogDescription>
                              </AlertDialogHeader>
                              <AlertDialogFooter>
                                <AlertDialogCancel>Cancelar</AlertDialogCancel>
                                <AlertDialogAction
                                  className="bg-red-600 hover:bg-red-700"
                                  onClick={() => remove(m.id)}
                                  data-testid={`confirm-remove-${m.id}`}
                                >
                                  Remover
                                </AlertDialogAction>
                              </AlertDialogFooter>
                            </AlertDialogContent>
                          </AlertDialog>
                        )}
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </div>
      </div>
    </AppShell>
  );
}
