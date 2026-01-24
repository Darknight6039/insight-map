'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function RegisterPage() {
  const router = useRouter()
  
  useEffect(() => {
    // Redirect to login page with register mode
    // The login page handles both login and registration
    router.replace('/login?mode=register')
  }, [router])
  
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="loading-liquid"></div>
    </div>
  )
}

