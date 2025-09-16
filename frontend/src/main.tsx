import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './index.css'
import App from './App'
import Login from './pages/Login'
import Posts from './pages/Posts'
import Editor from './pages/Editor'
import Settings from './pages/Settings'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<App />}>
          <Route index element={<Navigate to="/posts" replace />} />
          <Route path="/posts" element={<Posts />} />
          <Route path="/editor" element={<Editor />} />
          <Route path="/editor/:id" element={<Editor />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
)
