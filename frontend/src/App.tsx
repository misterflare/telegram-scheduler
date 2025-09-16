import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom'
import Navbar from './components/Navbar'
import { useEffect } from 'react'

export default function App(){
  const token = localStorage.getItem('token')
  const loc = useLocation()
  const nav = useNavigate()
  useEffect(()=>{ if(!token) nav('/login') }, [loc.pathname])
  return (
    <div className="min-h-screen">
      <Navbar />
      <main className="max-w-5xl mx-auto p-4">
        <Outlet />
      </main>
    </div>
  )
}
