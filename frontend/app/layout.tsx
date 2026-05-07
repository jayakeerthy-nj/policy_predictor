import type { ReactNode } from "react";

export const metadata = {
  title: "Polaris Dashboard — Policy Impact Intelligence",
  description: "India-specific policy impact predictions across markets, inflation, healthcare, trade, and commodities.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <style>{`
          * { box-sizing: border-box; }
          body { 
            margin: 0; 
            padding: 0; 
            font-family: Arial, sans-serif; 
            background: #f7f8fa; 
            color: #333; 
          }
        `}</style>
      </head>
      <body>{children}</body>
    </html>
  );
}
