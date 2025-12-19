import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Fitness Tracker',
  description: 'Track your workouts and progress',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

