import type { Metadata } from "next"
import { Inter } from "next/font/google"
import "./globals.css"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "Groww Mutual Fund Assistant - Verified Facts Only",
  description: "Official regulated mutual fund factsheet Q&A assistant referencing AMC, AMFI, and SEBI documentation.",
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} h-full bg-slate-50/30 overflow-hidden`}>
        {children}
      </body>
    </html>
  )
}
