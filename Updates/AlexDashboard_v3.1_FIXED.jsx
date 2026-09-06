import React, { useState, useEffect, useRef } from 'react';

const CircularProgress = ({ percentage, label }) => {
  const radius = 40;
  const safePercentage = Math.max(0, Math.min(100, percentage || 0));
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (safePercentage / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
      <svg width="100" height="100" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="50" cy="50" r={radius} fill="none" stroke="#2a2a2a" strokeWidth="6" />
        <circle
          cx="50"
          cy="50"
          r={radius}
          fill="none"
          stroke="#00d9a3"
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.3s ease' }}
        />
      </svg>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: '16px', fontWeight: 600, color: '#00d9a3' }}>
          {Math.round(safePercentage)}%
        </div>
        <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase' }}>
          {label}
        </div>
      </div>
    </div>
  );
};

const ThinkingAnimation = () => (
  <div style={{ display: 'flex', gap: '6px', alignItems: 'center', justifyContent: 'center' }}>
    <style>{`
      @keyframes bounce {
        0%, 80%, 100% { transform: translateY(0); opacity: 0.6; }
        40% { transform: translateY(-8px); opacity: 1; }
      }
      .thinking-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #00d9a3;
        animation: bounce 1.2s infinite;
      }
      .dot-1 { animation-delay: 0s; }
      .dot-2 { animation-delay: 0.2s; }
      .dot-3 { animation-delay: 0.4s; }
    `}</style>
    <div className="thinking-dot dot-1"></div>
    <div className="thinking-dot dot-2"></div>
    <div className="thinking-dot dot-3"></div>
  </div>
);

const AlexDashboard = () => {
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef(null);
  const [stats, setStats] = useState({ cpu: 0, ram: 0, model: 'qwen:7b', connected: false });
  const [activeSection, setActiveSection] = useState('Alex Core');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/resources');
      if (response.ok) {
        const data = await response.json();
        const ramUsed = data.ram ? parseFloat(String(data.ram).split(' ')[0]) : 0;
        const ramPercent = Math.min(100, (ramUsed / 15.9) * 100);
        setStats({
          cpu: Math.max(0, Math.min(100, data.cpu || 0)),
          ram: ramPercent,
          model: data.model || 'qwen:7b',
          connected: true
        });
      }
    } catch (error) {
      setStats(prev => ({ ...prev, connected: false }));
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMessage = { id: messages.length + 1, role: 'user', text: input, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input })
      });
      const data = await response.json();
      setMessages(prev => [...prev, { id: prev.length + 1, role: 'assistant', text: data.reply || 'Sin respuesta', timestamp: new Date() }]);
    } catch (error) {
      setMessages(prev => [...prev, { id: prev.length + 1, role: 'assistant', text: `Error: ${error.message}`, timestamp: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    const fileNames = files.map(f => f.name);
    const fileMessage = { id: messages.length + 1, role: 'user', text: `Archivos: ${fileNames.join(', ')}`, timestamp: new Date() };
    setMessages(prev => [...prev, fileMessage]);
  };

  const clearChat = () => {
    setMessages([{ id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }]);
  };

  const menuItems = [
    { section: 'Core', items: ['Alex Core', 'Automatizaciones'] },
    { section: 'Nav', items: ['General', 'Nuevo proyecto'] },
    { section: 'Tools', items: ['Búsqueda web', 'Documentos'] },
    { section: 'Modules', items: ['FastAPI setup', 'Frontend TUI', 'Voice cloning'] }
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0a', color: '#cccccc', fontFamily: "'JetBrains Mono', monospace", fontSize: '13px' }}>
      {/* Header */}
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, height: '50px', background: '#1a1a1a', borderBottom: '1px solid #2a2a2a', display: 'flex', alignItems: 'center', padding: '0 20px', justifyContent: 'space-between', zIndex: 100 }}>
        <div style={{ fontWeight: 600, fontSize: '14px', color: '#00d9a3', letterSpacing: '2px' }}>A.L.E.X</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '11px', color: '#888888' }}>
          <span>v0.2</span>
          <span>|</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: stats.connected ? '#00d9a3' : '#666666' }}></div>
            {stats.connected ? 'connected' : 'offline'}
          </span>
        </div>
      </div>

      {/* Main container */}
      <div style={{ display: 'flex', width: '100%', marginTop: '50px' }}>
        {/* Sidebar */}
        <div style={{ width: '240px', background: '#1a1a1a', borderRight: '1px solid #2a2a2a', overflowY: 'auto', padding: '20px 0' }}>
          {menuItems.map((section, idx) => (
            <div key={idx}>
              <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase', letterSpacing: '1px', padding: '0 16px', marginBottom: '8px' }}>
                {section.section}
              </div>
              {section.items.map((item, itemIdx) => (
                <div
                  key={itemIdx}
                  onClick={() => setActiveSection(item)}
                  style={{
                    padding: '10px 16px',
                    cursor: 'pointer',
                    borderLeft: activeSection === item ? '2px solid #00d9a3' : '2px solid transparent',
                    color: activeSection === item ? '#00d9a3' : '#888888',
                    fontSize: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    background: activeSection === item ? 'rgba(0, 217, 163, 0.05)' : 'transparent',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.background = '#2a2a2a'; e.currentTarget.style.color = '#00d9a3'; }}
                  onMouseLeave={(e) => { e.currentTarget.style.background = activeSection === item ? 'rgba(0, 217, 163, 0.05)' : 'transparent'; e.currentTarget.style.color = activeSection === item ? '#00d9a3' : '#888888'; }}
                >
                  ⚙ {item}
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Main content */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', paddingBottom: '120px', overflow: 'hidden' }}>
          {/* Stats */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', padding: '20px', background: '#0a0a0a' }}>
            <CircularProgress percentage={stats.cpu} label="CPU" />
            <CircularProgress percentage={stats.ram} label="RAM" />
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
              <div style={{ fontSize: '12px', color: '#00d9a3', fontWeight: 600 }}>{stats.model}</div>
              <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase' }}>Modelo</div>
            </div>
          </div>

          {/* Chat */}
          <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {messages.map((msg) => (
              <div key={msg.id} style={{ display: 'flex', gap: '8px', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                <div>
                  <div style={{ fontSize: '10px', color: '#666666', marginBottom: '4px' }}>{msg.role === 'user' ? 'Tú' : 'Alex'}</div>
                  <div style={{
                    maxWidth: '60%',
                    padding: '10px 12px',
                    borderRadius: '4px',
                    background: msg.role === 'user' ? 'rgba(0, 217, 163, 0.1)' : '#1a1a1a',
                    border: msg.role === 'user' ? '1px solid #00d9a3' : '1px solid #2a2a2a',
                    color: msg.role === 'user' ? '#e0e0e0' : '#b0b0b0',
                    wordWrap: 'break-word'
                  }}>
                    {msg.text}
                  </div>
                  <div style={{ fontSize: '10px', color: '#555555', marginTop: '4px' }}>
                    {msg.timestamp.toLocaleTimeString('es-ES', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div style={{ display: 'flex', gap: '8px' }}>
                <div>
                  <div style={{ fontSize: '10px', color: '#666666', marginBottom: '4px' }}>Alex</div>
                  <div style={{ padding: '10px 12px', background: '#1a1a1a', borderRadius: '4px', border: '1px solid #2a2a2a' }}>
                    <ThinkingAnimation />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>
      </div>

      {/* Footer */}
      <div style={{ position: 'fixed', bottom: 0, left: 0, right: 0, height: '120px', background: '#1a1a1a', borderTop: '1px solid #2a2a2a', padding: '12px 20px', display: 'flex', gap: '8px', alignItems: 'flex-start' }}>
        <input type="file" ref={fileInputRef} onChange={handleFileUpload} style={{ display: 'none' }} multiple />
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Escribe tu mensaje..."
          disabled={loading}
          style={{
            flex: 1,
            background: '#0a0a0a',
            border: '1px solid #2a2a2a',
            color: '#cccccc',
            padding: '8px 12px',
            borderRadius: '4px',
            fontFamily: "'JetBrains Mono', monospace",
            fontSize: '12px',
            outline: 'none'
          }}
        />
        <button onClick={() => fileInputRef.current?.click()} style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', color: '#888888', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', whiteSpace: 'nowrap' }}>
          📎 Archivo
        </button>
        <button onClick={clearChat} style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', color: '#888888', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', whiteSpace: 'nowrap' }}>
          🗑 Limpiar
        </button>
        <button onClick={sendMessage} disabled={loading} style={{ background: 'rgba(0, 217, 163, 0.1)', borderColor: '#00d9a3', border: '1px solid #00d9a3', color: '#00d9a3', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', whiteSpace: 'nowrap' }}>
          ➜ {loading ? 'Pensando...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
};

export default AlexDashboard;
