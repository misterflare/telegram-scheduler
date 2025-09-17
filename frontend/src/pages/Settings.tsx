import { useEffect, useState } from 'react'
import { api } from '../lib/api'

export default function Settings(){
  const [bot,setBot]=useState('')
  const [channel,setChannel]=useState('')
  const [timezone,setTimezone]=useState('')
  const [oldPass,setOldPass]=useState('')
  const [newPass,setNewPass]=useState('')
  const [show,setShow]=useState(false)
  const [testText,setTestText]=useState('Тестовая публикация для проверки связи')

  async function load(){
    const res = await api('/settings/')
    const data = await res.json()
    setBot(data.bot_token||'')
    setChannel(data.channel_id||'')
    setTimezone(data.timezone||'')
  }
  useEffect(()=>{ load() },[])

  async function save(){
    await api('/settings/', { method:'PUT', body: JSON.stringify({ bot_token: bot.includes('*')?undefined:bot, channel_id: channel, timezone: timezone }) })
    load()
  }

  async function changePass(){
    const confirm = (document.getElementById('confirm') as HTMLInputElement).value
    await api('/settings/password', { method:'POST', body: JSON.stringify({ old_password: oldPass, new_password: newPass, new_password_confirm: confirm }) })
    setOldPass(''); setNewPass(''); (document.getElementById('confirm') as HTMLInputElement).value=''
    alert('Пароль обновлён')
  }

  async function testPosting(){
    const res = await api('/settings/test', { method:'POST', body: JSON.stringify({ text: testText }) })
    if(res.ok){
      alert('Тестовое сообщение отправлено успешно')
    } else {
      const t = await res.text().catch(()=> '')
      alert('Не получилось отправить тест: ' + t)
    }
  }

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-semibold">Настройки</h1>

      <div className="bg-white p-4 rounded-2xl shadow space-y-3">
        <div>
          <label className="block text-sm font-medium">Токен бота</label>
          <input value={bot} onChange={e=>setBot(e.target.value)} className="border rounded px-3 py-2 w-full" placeholder="123456:ABC..." />
        </div>
        <div>
          <label className="block text-sm font-medium">ID/юзернейм канала</label>
          <input value={channel} onChange={e=>setChannel(e.target.value)} className="border rounded px-3 py-2 w-full" placeholder="@channel_or_-100..." />
        </div>
        <div>
          <label className="block text-sm font-medium">Тайм-зона (например, Europe/Moscow)</label>
          <input value={timezone} onChange={e=>setTimezone(e.target.value)} className="border rounded px-3 py-2 w-full" placeholder="Europe/Moscow" />
        </div>
        <button onClick={save} className="bg-black text-white rounded px-4 py-2">Сохранить</button>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow space-y-3">
        <label className="block text-sm font-medium">Обновить пароль</label>
        <div className="flex gap-2 items-center">
          <input type={show? 'text':'password'} value={oldPass} onChange={e=>setOldPass(e.target.value)} placeholder="Текущий пароль" className="border rounded px-3 py-2" />
          <input type={show? 'text':'password'} value={newPass} onChange={e=>setNewPass(e.target.value)} placeholder="Новый пароль" className="border rounded px-3 py-2" />
          <input id="confirm" type={show? 'text':'password'} placeholder="Повтор пароля" className="border rounded px-3 py-2" />
          <label className="text-sm flex items-center gap-1"><input type="checkbox" onChange={e=>setShow(e.target.checked)} /> Показать</label>
        </div>
        <button onClick={changePass} className="border rounded px-4 py-2">Сменить пароль</button>
      </div>

      <div className="bg-white p-4 rounded-2xl shadow space-y-3">
        <label className="block text-sm font-medium">Текст для тестовой публикации</label>
        <textarea value={testText} onChange={e=>setTestText(e.target.value)} rows={3} className="w-full border rounded p-2" />
        <button onClick={testPosting} className="border rounded px-4 py-2">Отправить тест</button>
        <div className="text-xs text-gray-500">Сообщение придёт в канал, чтобы проверить доступ. Убедитесь, что бот добавлен и имеет права администратора.</div>
      </div>
    </div>
  )
}
