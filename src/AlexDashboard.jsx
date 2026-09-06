import React, { useState, useEffect, useRef } from 'react';

const CircularProgress = ({ percentage, label }) => {
  const radius = 40;
  const safePercentage = Math.max(0, Math.min(100, percentage || 0));
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (safePercentage / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
      <svg width="120" height="120" style={{ transform: 'rotate(-90deg)' }}>
        <circle cx="60" cy="60" r={radius} fill="none" stroke="#2a2a2a" strokeWidth="6" />
        <circle
          cx="60"
          cy="60"
          r={radius}
          fill="none"
          stroke="#00d9a3"
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          style={{ transition: 'stroke-dashoffset 0.3s ease' }}
        />
        <text x="60" y="67" textAnchor="middle" style={{ fontSize: '14px', fontWeight: 600, fill: '#00d9a3', transform: 'rotate(90deg)', transformOrigin: '60px 60px' }}>
          {Math.round(safePercentage)}%
        </text>
      </svg>
      <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase' }}>
        {label}
      </div>
    </div>
  );
};

const ThinkingAnimation = () => (
  <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
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

const FilePreviewModal = ({ file, content, onSend, onCancel }) => {
  const isImage = file.type.startsWith('image/');
  const isText = file.type.startsWith('text/');

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 200
    }}>
      <div style={{
        background: '#1a1a1a',
        border: '1px solid #2a2a2a',
        borderRadius: '8px',
        padding: '20px',
        maxWidth: '600px',
        maxHeight: '80vh',
        overflowY: 'auto',
        color: '#cccccc'
      }}>
        <h3 style={{ marginBottom: '12px', color: '#00d9a3' }}>📎 {file.name}</h3>
        <div style={{ fontSize: '11px', color: '#888888', marginBottom: '16px' }}>
          {(file.size / 1024).toFixed(2)} KB
        </div>

        {/* Preview */}
        <div style={{
          background: '#0a0a0a',
          border: '1px solid #2a2a2a',
          borderRadius: '4px',
          padding: '12px',
          marginBottom: '16px',
          maxHeight: '400px',
          overflowY: 'auto'
        }}>
          {isImage ? (
            <img src={content} style={{ maxWidth: '100%', borderRadius: '4px' }} alt="preview" />
          ) : isText ? (
            <pre style={{ fontSize: '11px', whiteSpace: 'pre-wrap', wordBreak: 'break-word', color: '#888888' }}>
              {content.substring(0, 1000)}
              {content.length > 1000 ? '\n...' : ''}
            </pre>
          ) : (
            <div style={{ color: '#888888', fontSize: '12px' }}>
              ✓ Archivo listo para enviar
            </div>
          )}
        </div>

        {/* Botones */}
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <button
            onClick={onCancel}
            style={{
              background: '#1a1a1a',
              border: '1px solid #2a2a2a',
              color: '#888888',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '11px'
            }}
          >
            Cancelar
          </button>
          <button
            onClick={onSend}
            style={{
              background: 'rgba(0, 217, 163, 0.1)',
              border: '1px solid #00d9a3',
              color: '#00d9a3',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '11px'
            }}
          >
            Enviar archivo
          </button>
        </div>
      </div>
    </div>
  );
};

const AlexDashboard = () => {
  const [messages, setMessages] = useState([
    { id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState(() => Math.random().toString(36).substring(7));
  const [chats, setChats] = useState([]);
  const [chatName, setChatName] = useState('Nuevo chat');
  const [showNewChat, setShowNewChat] = useState(true);
  const fileInputRef = useRef(null);
  const [stats, setStats] = useState({ cpu: 0, ram: 0, model: 'Claude-Haiku-4.5', connected: false });
  const [activeSection, setActiveSection] = useState('Alex Core');
  const messagesEndRef = useRef(null);
  const [previewFile, setPreviewFile] = useState(null);
  const [previewContent, setPreviewContent] = useState('');

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStats();
    loadChats();
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (messages.length > 1) {
      const chatData = {
        id: chatId,
        name: chatName,
        messages: messages,
        section: activeSection,
        updated: new Date().toISOString()
      };
      fetch(`http://127.0.0.1:8000/chats/${chatId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chatData)
      });
    }
  }, [messages, chatId, chatName, activeSection]);

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

  const loadChats = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/chats');
      if (response.ok) {
        const data = await response.json();
        setChats(Object.entries(data).map(([id, chat]) => ({
          id: chat.id || id,
          name: chat.name || 'Chat sin nombre',
          updated: chat.updated || new Date().toISOString()
        })));
      }
    } catch (error) {
      console.error('Error cargando chats:', error);
    }
  };

  const newChat = () => {
  const newId = Math.random().toString(36).substring(7);
  setChatId(newId);
  setChatName('Chat ' + new Date().toLocaleDateString());
  setMessages([{ id: 1, role: 'assistant', text: '¿Qué?', timestamp: new Date() }]);
};

  const loadChat = (id) => {
    fetch(`http://127.0.0.1:8000/chats/${id}`)
      .then(r => r.json())
      .then(data => {
        setChatId(data.id || id);
        setChatName(data.name || 'Chat sin nombre');
        setMessages(data.messages.map(m => ({ ...m, timestamp: new Date(m.timestamp) })));
        setActiveSection(data.section || 'Alex Core');
      });
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
    const file = e.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      setPreviewFile(file);
      setPreviewContent(reader.result);
    };
    reader.readAsDataURL(file);
  };

  const sendFile = () => {
    if (!previewFile) return;
    const fileMessage = {
      id: messages.length + 1,
      role: 'user',
      text: `📎 Archivo: ${previewFile.name}`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, fileMessage]);
    setPreviewFile(null);
    setPreviewContent('');
    fileInputRef.current.value = '';
  };

  const tools = [
    { name: 'Alex Core', icon: '⚙' },
    { name: 'Automatizaciones', icon: '⚡' },
    { name: 'General', icon: '📋' },
    { name: 'Nuevo proyecto', icon: '🔧' },
    { name: 'Búsqueda web', icon: '🔍' },
    { name: 'Documentos', icon: '📚' },
    { name: 'FastAPI setup', icon: '🎤' },
    { name: 'Frontend TUI', icon: '🖥' },
    { name: 'Voice cloning', icon: '🔊' }
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#0a0a0a', color: '#cccccc', fontFamily: "'JetBrains Mono', monospace", fontSize: '13px' }}>
      {/* Modal de vista previa */}
      {previewFile && (
        <FilePreviewModal
          file={previewFile}
          content={previewContent}
          onSend={sendFile}
          onCancel={() => {
            setPreviewFile(null);
            setPreviewContent('');
            fileInputRef.current.value = '';
          }}
        />
      )}

      {/* Header */}
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, height: '50px', background: '#1a1a1a', borderBottom: '1px solid #2a2a2a', display: 'flex', alignItems: 'center', padding: '0 20px', justifyContent: 'space-between', zIndex: 100 }}>
        <div style={{ fontWeight: 600, fontSize: '14px', color: '#00d9a3', letterSpacing: '2px' }}>A.L.E.X</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', fontSize: '11px', color: '#888888' }}>
          <span>{chatName}</span>
          <span>|</span>
          <span>v0.3</span>
          <span>|</span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: stats.connected ? '#00d9a3' : '#666666' }}></div>
            {stats.connected ? 'connected' : 'offline'}
          </span>
        </div>
      </div>

      {/* Main container */}
      <div style={{ display: 'flex', width: '100%', marginTop: '50px' }}>
        {/* Sidebar - Chats y Tools */}
        <div style={{ width: '240px', background: '#1a1a1a', borderRight: '1px solid #2a2a2a', overflowY: 'auto', padding: '20px 0', display: 'flex', flexDirection: 'column' }}>
          
          {/* Chats */}
          <div style={{ padding: '0 16px', marginBottom: '20px' }}>
            <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>
              Chats
            </div>
            <button
            onClick={newChat}
            style={{
            width: '100%',
            background: 'rgba(0, 217, 163, 0.1)',
            border: '1px solid #00d9a3',
            color: '#00d9a3',
            padding: '8px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px',
            marginBottom: '8px'
          }}
          >
            + Nuevo chat
            </button>
            <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
              {chats.map(chat => (
                <div
                  key={chat.id}
                  onClick={() => loadChat(chat.id)}
                  style={{
                    padding: '8px',
                    marginBottom: '4px',
                    background: chatId === chat.id ? 'rgba(0, 217, 163, 0.1)' : '#0a0a0a',
                    border: chatId === chat.id ? '1px solid #00d9a3' : '1px solid #2a2a2a',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '11px',
                    color: chatId === chat.id ? '#00d9a3' : '#888888',
                    transition: 'all 0.2s',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#2a2a2a'}
                  onMouseLeave={(e) => e.currentTarget.style.background = chatId === chat.id ? 'rgba(0, 217, 163, 0.1)' : '#0a0a0a'}
                >
                  {chat.name}
                </div>
              ))}
            </div>
          </div>

          {/* Tools - No interactivas */}
          <div style={{ flex: 1, overflowY: 'auto', paddingTop: '20px', borderTop: '1px solid #2a2a2a' }}>
            <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase', letterSpacing: '1px', padding: '0 16px', marginBottom: '8px' }}>
              Herramientas activas
            </div>
            {tools.map((tool, idx) => (
              <div
                key={idx}
                style={{
                  padding: '10px 16px',
                  color: activeSection === tool.name ? '#00d9a3' : '#555555',
                  fontSize: '11px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  opacity: activeSection === tool.name ? 1 : 0.5,
                  transition: 'all 0.2s'
                }}
              >
                <span>{tool.icon}</span>
                <span>{tool.name}</span>
              </div>
            ))}
          </div>
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
                    maxWidth: '80%',
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
        <input type="file" ref={fileInputRef} onChange={handleFileUpload} style={{ display: 'none' }} />
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
        <button onClick={() => {
          setMessages([{ id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }]);
        }} style={{ background: '#1a1a1a', border: '1px solid #2a2a2a', color: '#888888', padding: '8px 12px', borderRadius: '4px', cursor: 'pointer', fontSize: '11px', whiteSpace: 'nowrap' }}>
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
