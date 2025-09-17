const rawBase = (import.meta.env.VITE_API_BASE as string) || '/api'

const base = (() => {
  if (typeof window !== 'undefined') {
    const host = window.location.hostname
    if (
      (rawBase.startsWith('http://localhost') || rawBase.startsWith('https://localhost')) &&
      host &&
      host !== 'localhost' &&
      host !== '127.0.0.1' &&
      host !== '::1'
    ) {
      return '/api'
    }
  }
  return rawBase
})()

const normalizedBase = base.endsWith('/') ? base.slice(0, -1) : base

function withBase(path: string) {
  return `${normalizedBase}${path.startsWith('/') ? path : `/${path}`}`
}

export async function api(path: string, opts: RequestInit = {}){
  const token = localStorage.getItem('token')
  const headers: any = { 'Content-Type': 'application/json', ...(opts.headers||{}) }
  if(token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(withBase(path), { ...opts, headers })
  if(res.status===401){ localStorage.removeItem('token'); location.href='/login' }
  return res
}

export async function login(username: string, password: string){
  const body = new URLSearchParams({ username, password })
  const res = await fetch(withBase('/auth/login'), { method: 'POST', body })
  if(!res.ok) throw new Error(res.status === 0 ? 'Failed to reach server' : 'Login failed')
  const data = await res.json()
  localStorage.setItem('token', data.access_token)
}
