export default function PostCard({post, onEdit, onDelete}:{post:any; onEdit:()=>void; onDelete:()=>void}){
  const dt = parseUtc(post.scheduled_at)
  return (
    <div className="bg-white rounded-2xl shadow p-4 flex gap-4 items-start">
      <div className="flex-1">
        <div className="text-gray-500 text-sm">Публикация: {dt.toLocaleString()}</div>
        {post.text && <p className="mt-2 whitespace-pre-wrap">{post.text}</p>}
        {post.buttons?.length>0 && (
          <div className="mt-2 flex flex-wrap gap-2">
            {post.buttons.map((b:any,i:number)=> (
              <span key={i} className="px-2 py-1 border rounded text-xs">{b.title}</span>
            ))}
          </div>
        )}
        {post.media?.length>0 && (
          <div className="mt-3 text-xs text-gray-500">Медиа: {post.media.map((m:any)=>m.type).join(', ')}</div>
        )}
        {post.status!=='scheduled' && (
          <div className="mt-2 text-xs">Статус: <b>{post.status}</b> {post.error && <span className="text-red-600">({post.error})</span>}</div>
        )}
      </div>
      <div className="flex gap-2">
        <button onClick={onEdit} title="Редактировать" className="p-2 border rounded">✏️</button>
        <button onClick={onDelete} title="Удалить" className="p-2 border rounded">🗑️</button>
      </div>
    </div>
  )
}

function parseUtc(value:string){
  // If backend returns naive ISO without timezone, treat it as UTC by appending 'Z'
  // so it renders correctly in local time with toLocaleString().
  if(typeof value === 'string' && value && !/Z|[\+\-]\d{2}:?\d{2}$/.test(value)){
    return new Date(value + 'Z')
  }
  return new Date(value)
}
