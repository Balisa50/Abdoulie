import type { Metadata } from "next";

import { PlaceholderPage } from "@/components/PlaceholderPage";

export const metadata: Metadata = {
  title: "Invoices | Tesseract",
};

export default function InvoicesPage() {
  return (
    <PlaceholderPage
      title="Invoices"
      description="Invoice ingestion & review UI scaffold. Next step: list invoices and show extracted entities."
    />
  );
}
