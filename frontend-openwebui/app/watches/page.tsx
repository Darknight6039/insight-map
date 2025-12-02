'use client'

import { motion } from 'framer-motion'
import Navbar from '../components/Navbar'
import WatchesPanel from '../components/WatchesPanel'
import ChatWidget from '../components/ChatWidget'

export default function WatchesPage() {
  return (
    <div className="min-h-screen w-full">
      <Navbar />
      
      <main className="pt-24 px-4 pb-6 w-full">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <WatchesPanel />
          </motion.div>
        </div>
      </main>

      {/* Chat Widget flottant */}
      <ChatWidget />
    </div>
  )
}
