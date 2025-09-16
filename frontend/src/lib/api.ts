const base = (import.meta.env.VITE_API_BASE as string) || '/api'

export async function api(path: string, opts: RequestInit = {}){
  const token = localStorage.getItem('token')
  const headers: any = { 'Content-Type': 'application/json', ...(opts.headers||{}) }
  if(token) headers['Authorization'] = `Bearer ${token}`
  const res = await fetch(`${base}${path}`, { ...opts, headers })
  if(res.status===401){ localStorage.removeItem('token'); location.href='/login' }
  return res
}

export async function login(username: string, password: string){
  const body = new URLSearchParams({ username, password })
  const res = await fetch(`${base}/auth/login`, { method: 'POST', body })
  if(!res.ok) throw new Error('Login failed')
  const data = await res.json()
  localStorage.setItem('token', data.access_token)
}
