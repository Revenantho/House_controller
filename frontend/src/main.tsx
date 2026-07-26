import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App'
import { AuthProvider } from './context/AuthContext'
import { DeviceStateProvider } from './context/DeviceStateContext'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <AuthProvider>
        <DeviceStateProvider>
          <App />
        </DeviceStateProvider>
      </AuthProvider>
    </BrowserRouter>
  </StrictMode>,
)
