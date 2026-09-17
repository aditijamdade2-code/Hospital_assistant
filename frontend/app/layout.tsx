import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Oscar Multispeciality Hospital — OPD Multilingual Assistant',
  description: 'Assistive clinical intake, red-flag safety, and protocol triage system.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col antialiased bg-slate-50 text-slate-900">
        {children}
      </body>
    </html>
  );
}
