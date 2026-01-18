import { LoginForm } from "@/src/features/auth/components/LoginForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-treq-gray-50 relative overflow-hidden">
      {/* Background elements for premium feel */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-treq-yellow/10 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-treq-yellow/5 rounded-full blur-[100px]" />

      <div className="relative z-10 w-full flex justify-center p-4">
        <LoginForm />
      </div>

      {/* Footer info */}
      <div className="absolute bottom-8 text-treq-gray-400 text-xs font-medium tracking-widest uppercase">
        &copy; {new Date().getFullYear()} Treq Operations
      </div>
    </div>
  );
}
