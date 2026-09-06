import React, { useState, useEffect, useRef } from 'react';

export default function AlexDashboard() {
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState({ cpu: 0, ram: '0 GB', model: 'qwen:7b', connected: false });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/resources');
        const data = await res.json();
        setStats({ ...data, connected: true });
      } catch (e) {
        setStats(prev => ({ ...prev, connected: false }));
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;
    setMessages(prev => [...prev, { id: prev.length + 1, role: 'user', text: input, timestamp: new Date() }]);
    setInput('');
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { id: prev.length + 1, role: 'assistant', text: data.reply, timestamp: new Date() }]);
    } catch (e) {
      setMessages(prev => [...prev, { id: prev.length + 1, role: 'assistant', text: 'Error: ' + e.message, timestamp: new Date() }]);
    }
    setLoading(false);
  };

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr', gridTemplateRows: '50px 1fr 120px', height: '100vh', background: '#0a0a0a', color: '#ccc', fontFamily: 'monospace' }}>
      
      {/* Header */}
      <div style={{ gridColumn: '1/-1', background: '#1a1a1a', borderBottom: '1px solid #2a2a2a', display: 'flex', alignItems: 'center', padding: '0 20px', justifyContent: 'space-between' }}>
        <div style={{ color: '#00d9a3', fontWeight: 'bold', letterSpacing: '2px' }}>A.L.E.X</div>
        <div style={{ fontSize: '11px', color: '#888' }}>
          v0.2 | <span style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', background: stats.connected ? '#00d9a3' : '#666', marginRight: '6px' }}></span>
          {stats.connected ? 'connected' : 'offline'}
        </div>
      </div>

      {/* Sidebar */}
      <div style={{ background: '#1a1a1a', borderRight: '1px solid #2a2a2a', padding: '20px 0', overflowY: 'auto' }}>
        {[
          { label: 'Core', items: ['Alex Core', 'Automatizaciones'] },
          { label: 'Nav', items: ['General', 'Nuevo proyecto'] }
        ].map((sec, i) => (
          <div key={i} style={{ borderBottom: '1px solid #2a2a2a', padding: '12px 0' }}>
            <div style={{ fontSize: '10px', color: '#666', textTransform: 'uppercase', padding: '0 16px', marginBottom: '8px' }}>{sec.label}</div>
            {sec.items.map((item, j) => (
              <div key={j} style={{ padding: '10px 16px', cursor: 'pointer', color: '#888', fontSize: '12px', borderLeft: '2px solid transparent' }}>
                ⚙ {item}
              </div>
            ))}
          </div>
        ))}
      </div>

      {/* Main Content */}
      <div style={{ display: 'flex', flexDirection: 'column', background: '#0a0a0a' }}>
        {/* Stats */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', padding: '20px' }}>
          <div style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', padding: '12px', borderRadius: '4px' }}>
            <div style={{ fontSize: '10px', color: '#666', textTransform: 'uppercase', marginBottom: '6px' }}>CPU</div>
            <div style={{ color: '#00d9a3', fontWeight: 'bold', fontSize: '18px' }}>{stats.cpu}%</div>
          </div>
          <div style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', padding: '12px', borderRadius: '4px' }}>
            <div style={{ fontSize: '10px', color: '#666', textTransform: 'uppercase', marginBottom: '6px' }}>RAM</div>
            <div style={{ color: '#00d9a3', fontWeight: 'bold', fontSize: '18px' }}>{stats.ram}</div>
          </div>
          <div style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', padding: '12px', borderRadius: '4px' }}>
            <div style={{ fontSize: '10px', color: '#666', textTransform: 'uppercase', marginBottom: '6px' }}>Model</div>
            <div style={{ color: '#00d9a3', fontWeight: 'bold', fontSize: '14px' }}>{stats.model}</div>
          </div>
        </div>

        {/* Chat */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '20px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {messages.map(msg => (
            <div key={msg.id} style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{ maxWidth: '60%' }}>
                <div style={{ fontSize: '10px', color: '#666', marginBottom: '4px' }}>{msg.role === 'user' ? 'Tú' : 'Alex'}</div>
                <div style={{ background: msg.role === 'user' ? 'rgba(0, 217, 163, 0.1)' : '#1a1a1a', border: msg.role === 'user' ? '1px solid #00d9a3' : '1px solid #2a2a2a', padding: '10px 12px', borderRadius: '4px', wordWrap: 'break-word', color: msg.role === 'user' ? '#e0e0e0' : '#b0b0b0' }}>
                  {msg.text}
                </div>
              </div>
            </div>
          ))}
          {loading && <div style={{ color: '#666' }}>Pensando...</div>}
        </div>
      </div>

      {/* Footer */}
      <div style={{ gridColumn: '1/-1', background: '#1a1a1a', borderTop: '1px solid #2a2a2a', padding: '12px 20px', display: 'flex', gap: '8px' }}>
        <input type="text" value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} placeholder="Escribe..." style={{ flex: 1, background: '#0a0a0a', border: '1px solid #2a2a2a', color: '#ccc', padding: '8px 12px', borderRadius: '4px', fontFamily: 'monospace', fontSize: '12px', outline: 'none' }} />
        <button onClick={sendMessage} disabled={loading} style={{ background: 'rgba(0, 217, 163, 0.1)', border: '1px solid #00d9a3', color: '#00d9a3', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontFamily: 'monospace', fontSize: '11px' }}>
          ➜ Enviar
        </button>
      </div>
    </div>
  );
}