import { useEffect, useState } from 'react'
import { api } from '../lib/api'
import { useNavigate, useParams } from 'react-router-dom'
import ButtonLinkRow from '../components/ButtonLinkRow'

export default function Editor(){
  const { id } = useParams()
  const nav = useNavigate()
  const [text,setText]=useState('')
  const [scheduledAt,setScheduledAt]=useState('')
  const [buttons,setButtons]=useState<{title:string,url:string}[]>([])
  const [media,setMedia]=useState<{type:string,path:string}[]>([])
  const [pendingFiles,setPendingFiles]=useState<FileList|null>(null)

  useEffect(()=>{ if(id) fetchPost() },[id])
  async function fetchPost(){
    const res = await api(`/posts/${id}`); const p = await res.json()
    setText(p.text||''); setScheduledAt(toInputLocal(p.scheduled_at)); setButtons(p.buttons||[]); setMedia(p.media||[])
  }

  async function uploadFiles(){
    if(!pendingFiles) return
    const form = new FormData()
    Array.from(pendingFiles).forEach(f=> form.append('files', f))
    const token = localStorage.getItem('token')
    const res = await fetch(((import.meta.env.VITE_API_BASE as string)||'/api') + '/files/upload', { method:'POST', headers:{ 'Authorization': `Bearer ${token}` }, body: form })
    const data = await res.json()
    const mapped = data.files.map((f:any)=>({ type: guessType(f.filename), path: f.path }))
    setMedia([...media, ...mapped])
    setPendingFiles(null)
  }

  function guessType(name:string){
    const ext = name.split('.').pop()?.toLowerCase() || ''
    if(['jpg','jpeg','png','webp'].includes(ext)) return 'photo'
    if(['mp4','mov','mkv','webm'].includes(ext)) return 'video'
    return 'document'
  }

  async function save(){
    if(!scheduledAt){ alert('Укажите дату и время публикации'); return }
    const payload:any = { text, buttons, media, scheduled_at: new Date(scheduledAt).toISOString() }
    const res = await api(id?`/posts/${id}`:'/posts/', { method: id?'PUT':'POST', body: JSON.stringify(payload) })
    if(res.ok){
      nav('/posts')
    } else {
      try { const err = await res.text(); alert(`Не удалось сохранить: ${err}`) } catch { alert('Не удалось сохранить пост') }
    }
  }

  async function publishNow(){
    // Ensure saved, then trigger publish-now
    if(!id){
      if(!scheduledAt){ alert('Укажите дату/время, или сохраните без него'); return }
      const payload:any = { text, buttons, media, scheduled_at: new Date(scheduledAt).toISOString() }
      const res = await api('/posts/', { method:'POST', body: JSON.stringify(payload) })
      if(!res.ok){ try { const t=await res.text(); alert(`Не удалось сохранить: ${t}`) } catch { alert('Не удалось сохранить пост') }; return }
      const created = await res.json()
      await api(`/posts/${created.id}/publish-now`, { method:'POST' })
      nav('/posts')
    } else {
      // Save latest edits first
      const payload:any = { text, buttons, media, scheduled_at: new Date(scheduledAt).toISOString() }
      const res = await api(`/posts/${id}`, { method:'PUT', body: JSON.stringify(payload) })
      if(!res.ok){ try { const t=await res.text(); alert(`Не удалось сохранить: ${t}`) } catch { alert('Не удалось сохранить пост') }; return }
      await api(`/posts/${id}/publish-now`, { method:'POST' })
      nav('/posts')
    }
  }

  function toInputLocal(isoLike:string){
    // Normalize to Date then format as yyyy-MM-ddTHH:mm in local time for input[type=datetime-local]
    // Treat naive timestamps as UTC to avoid timezone drift
    const needsZ = typeof isoLike === 'string' && isoLike && !/Z|[\+\-]\d{2}:?\d{2}$/.test(isoLike)
    const d = new Date(needsZ ? isoLike + 'Z' : isoLike)
    const pad = (n:number)=> String(n).padStart(2,'0')
    const y = d.getFullYear()
    const m = pad(d.getMonth()+1)
    const day = pad(d.getDate())
    const hh = pad(d.getHours())
    const mm = pad(d.getMinutes())
    return `${y}-${m}-${day}T${hh}:${mm}`
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">{id? 'Редактирование поста' : 'Создать пост'}</h1>

      <div className="bg-white p-4 rounded-2xl shadow space-y-3">
        <label className="block text-sm font-medium">Текст</label>
        <textarea value={text} onChange={e=>setText(e.target.value)} rows={6} className="w-full border rounded p-2" placeholder="Напишите текст, можно с эмодзи 😊" />
      </div>

      <div className="bg-white p-4 rounded-2xl shadow space-y-3">
        <label className="block text-sm font-medium">Медиафайлы</label>
        <input type="file" multiple onChange={e=>setPendingFiles(e.target.files)} />
        <button onClick={uploadFiles} className="border rounded px-3 py-1">Загрузить</button>
        {media.length>0 && (
          <ul className="text-sm text-gray-700 list-disc pl-5">
            {media.map((m,i)=> <li key={i}>{m.type} — {m.path.split('/').pop()}</li>)}
          </ul>
        )}
      </div>

      <div className="bg-white p-4 rounded-2xl shadow space-y-2">
        <div className="flex justify-between items-center">
          <label className="text-sm font-medium">Кнопки со ссылками</label>
          <button className="border rounded px-2 py-1" onClick={()=>setButtons([...buttons,{title:'',url:''}])}>+</button>
        </div>
        <div className="space-y-2">
          {buttons.map((b,i)=> (
            <ButtonLinkRow key={i} value={b} onChange={v=>{ const arr=[...buttons]; arr[i]=v; setButtons(arr) }} onRemove={()=>{ const arr=[...buttons]; arr.splice(i,1); setButtons(arr) }} />
          ))}
        </div>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow space-y-3">
        <label className="block text-sm font-medium">Дата и время публикации</label>
        <input type="datetime-local" value={scheduledAt} onChange={e=>setScheduledAt(e.target.value)} className="border rounded px-2 py-1" />
      </div>

      <div className="flex gap-2">
        <button onClick={save} className="bg-black text-white rounded px-4 py-2">Сохранить</button>
        <button onClick={publishNow} className="border rounded px-4 py-2">Опубликовать сейчас</button>
        <button onClick={()=>nav('/posts')} className="border rounded px-4 py-2">Отмена</button>
      </div>
    </div>
  )
}
