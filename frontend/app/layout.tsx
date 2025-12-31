import type { Metadata } from "next";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import "./globals.css";

export const metadata: Metadata = {
  title: "Treq Assistente Operacional",
  description: "Assistente operacional inteligente para Sotreq",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="pt-BR" className="h-full overflow-hidden">
      <body className="h-full overflow-hidden">
        <div className="h-full overflow-hidden">
          <NuqsAdapter>{children}</NuqsAdapter>
        </div>
      </body>
    </html>
  );
}

