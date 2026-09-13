import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Loader2 } from "lucide-react";
import axios from "axios";
import LandingPreview from "@/components/LandingPreview";

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function PublicLandingPage() {
  const { slug } = useParams();
  const [data, setData] = useState(null);
  const [err, setErr] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const { data } = await axios.get(`${BACKEND}/api/public/${slug}`);
        setData(data); document.title = data.company.name;
      } catch (e) { setErr(e?.response?.data?.detail || "Página não disponível"); }
    })();
  }, [slug]);

  const resolveUrl = (path) => path?.startsWith("/api/uploads/file/")
    ? `${BACKEND}/api/public/uploads/${path.replace("/api/uploads/file/", "")}` : `${BACKEND}${path}`;

  if (err) return <div className="min-h-screen flex items-center justify-center text-slate-500">{err}</div>;
  if (!data) return <div className="min-h-screen flex items-center justify-center"><Loader2 className="h-6 w-6 animate-spin text-slate-400"/></div>;
  return <div className="min-h-screen bg-white" data-testid="public-landing"><LandingPreview state={data.state} company={data.company} services={data.services} publicMode resolveUrl={resolveUrl}/></div>;
}
