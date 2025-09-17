function normalizeUrl(raw: string) {
  const value = raw.trim()
  if (!value) return ''
  const lower = value.toLowerCase()
  if (value.startsWith('@')) {
    const username = value.replace(/^@+/, '').trim()
    return username ? `https://t.me/${username}` : ''
  }
  if (lower.startsWith('http://') || lower.startsWith('https://') || lower.startsWith('tg://')) {
    return value
  }
  if (lower.startsWith('t.me/') || lower.startsWith('telegram.me/') || lower.startsWith('telegram.dog/')) {
    return `https://${value}`
  }
  if (lower.startsWith('www.')) {
    return `https://${value}`
  }
  return `https://${value}`
}

export default function ButtonLinkRow({value,onChange,onRemove}:{value:{title:string,url:string},onChange:(v:any)=>void,onRemove:()=>void}){
  return (
    <div className="flex gap-2 items-center">
      <input className="border rounded px-2 py-1 flex-1" placeholder="Название" value={value.title} onChange={e=>onChange({...value,title:e.target.value})} />
      <input
        className="border rounded px-2 py-1 flex-[2]"
        placeholder="https://ссылка или @username"
        value={value.url}
        onChange={e=>onChange({...value,url:e.target.value})}
        onBlur={e=>onChange({...value,url:normalizeUrl(e.target.value)})}
      />
      <button onClick={onRemove} className="px-2 py-1 border rounded">×</button>
    </div>
  )
}
