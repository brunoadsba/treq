"use client";

interface HeaderProps {
  title?: string;
}

export function Header({ title = "Treq Assistente Operacional" }: HeaderProps) {
  return (
    <header className="bg-sotreq-black text-white p-4 shadow-md">
      <h1 className="text-xl font-semibold">{title}</h1>
    </header>
  );
}

