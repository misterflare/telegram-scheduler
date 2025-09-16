import { useState } from 'react'
import { login } from '../lib/api'

export default function Login(){
  const [username,setUsername]=useState('')
  const [password,setPassword]=useState('')
  const [err,setErr]=useState('')
  async function onSubmit(e:any){
    e.preventDefault()
    try{ await login(username,password); location.href='/' }catch(e:any){ setErr(e.message) }
  }
  return (
    <div className="h-screen flex items-center justify-center">
      <form onSubmit={onSubmit} className="bg-white p-6 rounded-2xl shadow w-full max-w-sm space-y-3">
        <h1 className="text-lg font-semibold">Вход</h1>
        <input value={username} onChange={e=>setUsername(e.target.value)} placeholder="Логин" className="border rounded px-3 py-2 w-full" />
        <input value={password} onChange={e=>setPassword(e.target.value)} placeholder="Пароль" type="password" className="border rounded px-3 py-2 w-full" />
        {err && <div className="text-red-600 text-sm">{err}</div>}
        <button className="w-full bg-black text-white rounded px-3 py-2">Войти</button>
      </form>
    </div>
  )
}
