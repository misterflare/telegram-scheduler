import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import PostCard from '../components/PostCard'
import { useNavigate } from 'react-router-dom'

export default function Posts(){
  const [items,setItems]=useState<any[]>([])
  const nav = useNavigate()
  async function load(){
    const res = await api('/posts/')
    const data = await res.json(); setItems(data)
  }
  useEffect(()=>{ load() },[])
  async function remove(id:number){
    if(!confirm('Удалить пост?')) return
    await api(`/posts/${id}`, { method:'DELETE' })
    load()
  }
  return (
    <div className="space-y-3">
      <div className="flex justify-between items-center">
        <h1 className="text-xl font-semibold">Текущие/запланированные посты</h1>
        <button className="border rounded px-3 py-2" onClick={()=>nav('/editor')}>+ Создать пост</button>
      </div>
      {items.map(p=> (
        <PostCard key={p.id} post={p} onEdit={()=>nav(`/editor/${p.id}`)} onDelete={()=>remove(p.id)} />
      ))}
      {items.length===0 && <div className="text-gray-500">Постов пока нет.</div>}
    </div>
  )
}
