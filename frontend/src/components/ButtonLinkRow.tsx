export default function ButtonLinkRow({value,onChange,onRemove}:{value:{title:string,url:string},onChange:(v:any)=>void,onRemove:()=>void}){
  return (
    <div className="flex gap-2 items-center">
      <input className="border rounded px-2 py-1 flex-1" placeholder="Название" value={value.title} onChange={e=>onChange({...value,title:e.target.value})} />
      <input className="border rounded px-2 py-1 flex-[2]" placeholder="http://ссылка" value={value.url} onChange={e=>onChange({...value,url:e.target.value})} />
      <button onClick={onRemove} className="px-2 py-1 border rounded">−</button>
    </div>
  )
}
