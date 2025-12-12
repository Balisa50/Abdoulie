import type { Metadata } from "next";

import { PlaceholderPage } from "@/components/PlaceholderPage";

export const metadata: Metadata = {
  title: "Clients | Tesseract",
};

export default function ClientsPage() {
  return (
    <PlaceholderPage
      title="Clients"
      description="Client management UI scaffold. Next step: add list + detail pages backed by API endpoints."
    />
  );
}
