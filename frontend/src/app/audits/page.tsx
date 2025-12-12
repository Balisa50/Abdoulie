import type { Metadata } from "next";

import { PlaceholderPage } from "@/components/PlaceholderPage";

export const metadata: Metadata = {
  title: "Audits | Tesseract",
};

export default function AuditsPage() {
  return (
    <PlaceholderPage
      title="Audits"
      description="Audit results UI scaffold. Next step: surface variance metrics and audit logs."
    />
  );
}
