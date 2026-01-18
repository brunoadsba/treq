import { redirect } from 'next/navigation'

export default function HomePage() {
  // Redirecionar para a página de chat (o chat verificará o login no lado do cliente)
  redirect('/chat')
}

