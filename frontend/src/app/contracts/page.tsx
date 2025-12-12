import type { Metadata } from "next";

import { PlaceholderPage } from "@/components/PlaceholderPage";

export const metadata: Metadata = {
  title: "Contracts | Tesseract",
};

export default function ContractsPage() {
  return (
    <PlaceholderPage
      title="Contracts"
      description="Contract/rules UI scaffold. Next step: browse contracts and associated rule metadata."
    />
  );
}
