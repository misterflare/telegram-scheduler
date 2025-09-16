import { Link, useLocation } from 'react-router-dom'

export default function Navbar(){
  const loc = useLocation()
  const tabs = [
    { to: '/posts', label: 'Текущие посты' },
    { to: '/editor', label: 'Подготовка/редактирование' },
    { to: '/settings', label: 'Настройки' },
  ]
  return (
    <header className="bg-white border-b">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <div className="font-semibold">Telegram Scheduler</div>
        <nav className="flex gap-4">
          {tabs.map(t=> (
            <Link key={t.to} to={t.to} className={`text-sm ${loc.pathname.startsWith(t.to)?'font-semibold':''}`}>{t.label}</Link>
          ))}
        </nav>
      </div>
    </header>
  )
}
