import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({
  baseURL: API,
  withCredentials: true,
});

/**
 * Map any FastAPI error payload to a display-safe string.
 * FastAPI 422 returns { detail: [{ msg, loc, ... }] }, which crashes React when rendered.
 */
export function formatApiError(err) {
  const detail = err?.response?.data?.detail;
  if (detail == null) return err?.message || "Erro inesperado. Tente novamente.";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((e) => (e && typeof e.msg === "string" ? e.msg : JSON.stringify(e)))
      .filter(Boolean)
      .join(" ");
  }
  if (detail && typeof detail.msg === "string") return detail.msg;
  return String(detail);
}

export const BUSINESS_TYPES = [
  { value: "BARBERSHOP", label: "Barbearia" },
  { value: "BEAUTY_SALON", label: "Salão de Beleza" },
  { value: "MANICURE", label: "Manicure" },
  { value: "AESTHETICS", label: "Estética" },
  { value: "PET_SHOP", label: "Pet Shop" },
];

export function businessTypeLabel(value) {
  return BUSINESS_TYPES.find((b) => b.value === value)?.label || value;
}

export const ROLE_LABELS = {
  OWNER: "Proprietário",
  MANAGER: "Gerente",
  PROFESSIONAL: "Profissional",
};
