'use client'

import { motion } from 'framer-motion'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { FileText, Bell } from 'lucide-react'
import AxialLogo from './AxialLogo'

export default function Navbar() {
  const pathname = usePathname()

  const navLinks = [
    { href: '/', label: 'Rapports', icon: FileText },
    { href: '/watches', label: 'Veilles', icon: Bell },
  ]

  return (
    <motion.nav
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      className="navbar-glass z-50"
    >
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center">
          <AxialLogo size={36} />
        </Link>

        {/* Navigation links */}
        <div className="flex items-center gap-2">
          {navLinks.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href
            return (
              <Link
                key={href}
                href={href}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl transition-all ${
                  isActive
                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="text-sm font-medium">{label}</span>
              </Link>
            )
          })}
        </div>

        {/* Status indicator */}
        <div className="flex items-center gap-2 px-4 py-2 glass rounded-xl">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span className="text-sm text-gray-300">Système opérationnel</span>
        </div>
      </div>
    </motion.nav>
  )
}
