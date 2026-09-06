import React, { useState, useEffect, useRef } from 'react';

interface Message {
  id: number;
  role: 'user' | 'assistant';
  text: string;
  timestamp: Date;
  memories?: string[];
}

interface Chat {
  id: string;
  name: string;
  updated: string;
}

interface Stats {
  cpu: number;
  ram: number;
  model: string;
  connected: boolean;
}

const CircularProgress: React.FC<{ percentage: number; label: string }> = ({ percentage, label }) => {
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

const ThinkingAnimation: React.FC = () => (
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

const MemoriesDisplay: React.FC<{ memories: string[] }> = ({ memories }) => {
  if (!memories || memories.length === 0) return null;

  return (
    <div style={{
      background: 'rgba(0, 217, 163, 0.05)',
      border: '1px solid rgba(0, 217, 163, 0.2)',
      borderRadius: '4px',
      padding: '8px 12px',
      marginBottom: '8px',
      fontSize: '10px',
      color: '#888888'
    }}>
      <div style={{ color: '#00d9a3', marginBottom: '4px', fontWeight: 600 }}>Memoria:</div>
      {memories.map((mem, idx) => (
        <div key={idx} style={{ marginBottom: '2px', paddingLeft: '8px' }}>
          • {mem}
        </div>
      ))}
    </div>
  );
};

const AlexDashboard: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    { id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [chatId, setChatId] = useState(() => Math.random().toString(36).substring(7));
  const [chats, setChats] = useState<Chat[]>([]);
  const [chatName, setChatName] = useState('Nuevo chat');
  const [editingChatId, setEditingChatId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [stats, setStats] = useState<Stats>({ cpu: 0, ram: 0, model: 'Claude Haiku 4.5', connected: false });
  const [activeSection, setActiveSection] = useState('Alex Core');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStats();
    loadChats();
    try {
      const lastChatId = localStorage.getItem('alex_active_chat');
      if (lastChatId) loadChat(lastChatId);
    } catch {}
    const interval = setInterval(fetchStats, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    try { localStorage.setItem('alex_active_chat', chatId); } catch {}
  }, [chatId]);

  useEffect(() => {
    if (messages.length > 1) {
      const chatData = {
        id: chatId,
        name: chatName,
        messages: messages.map(m => ({
          ...m,
          timestamp: m.timestamp.toISOString()
        })),
        section: activeSection,
        updated: new Date().toISOString()
      };
      fetch(`http://127.0.0.1:8000/chats/${chatId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(chatData)
      }).catch(() => {});
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
          model: 'Claude Opus 4.8 (Agentic)',
          connected: true
        });
      }
    } catch {
      setStats(prev => ({ ...prev, connected: false }));
    }
  };

  const loadChats = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/chats');
      if (response.ok) {
        const data = await response.json();
        setChats(Object.entries(data).map(([id, chat]: [string, any]) => ({
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

  const loadChat = (id: string) => {
    fetch(`http://127.0.0.1:8000/chats/${id}`)
      .then(r => {
        if (!r.ok) throw new Error('Chat no encontrado');
        return r.json();
      })
      .then((data: any) => {
        setChatId(data.id || id);
        setChatName(data.name || 'Chat sin nombre');
        setMessages(data.messages.map((m: any) => ({
          ...m,
          timestamp: new Date(m.timestamp)
        })));
        setActiveSection(data.section || 'Alex Core');
      })
      .catch(() => {});
  };

  const renameChat = (id: string, name: string) => {
    const trimmed = name.trim();
    if (!trimmed) return;
    fetch(`http://127.0.0.1:8000/chats/${id}/name`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: trimmed })
    })
      .then(() => {
        setChats(prev => prev.map(c => c.id === id ? { ...c, name: trimmed } : c));
        if (id === chatId) setChatName(trimmed);
      })
      .catch(() => {});
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMessage: Message = {
      id: messages.length + 1,
      role: 'user',
      text: input,
      timestamp: new Date()
    };

    // Primer mensaje real de un chat nuevo: que Alex le ponga nombre sola.
    if (messages.length === 1) {
      const currentChatId = chatId;
      fetch('http://127.0.0.1:8000/chats/autoname', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: input })
      })
        .then(r => r.json())
        .then((data: any) => {
          if (data.name) {
            setChatName(data.name);
            setChats(prev => prev.some(c => c.id === currentChatId)
              ? prev.map(c => c.id === currentChatId ? { ...c, name: data.name } : c)
              : [...prev, { id: currentChatId, name: data.name, updated: new Date().toISOString() }]);
          }
        })
        .catch(() => {});
    }

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

      const assistantMessage: Message = {
        id: messages.length + 2,
        role: 'assistant',
        text: data.reply || 'Sin respuesta',
        timestamp: new Date(),
        memories: data.memories
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: messages.length + 2,
        role: 'assistant',
        text: `Error: ${error instanceof Error ? error.message : 'Desconocido'}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
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
        {/* Sidebar */}
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
                  onClick={() => editingChatId !== chat.id && loadChat(chat.id)}
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
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = '#2a2a2a'}
                  onMouseLeave={(e) => e.currentTarget.style.background = chatId === chat.id ? 'rgba(0, 217, 163, 0.1)' : '#0a0a0a'}
                >
                  {editingChatId === chat.id ? (
                    <input
                      autoFocus
                      value={editingName}
                      onChange={(e) => setEditingName(e.target.value)}
                      onClick={(e) => e.stopPropagation()}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') {
                          renameChat(chat.id, editingName);
                          setEditingChatId(null);
                        } else if (e.key === 'Escape') {
                          setEditingChatId(null);
                        }
                      }}
                      onBlur={() => {
                        renameChat(chat.id, editingName);
                        setEditingChatId(null);
                      }}
                      style={{
                        flex: 1,
                        background: '#0a0a0a',
                        border: '1px solid #00d9a3',
                        color: '#e0e0e0',
                        fontSize: '11px',
                        padding: '2px 4px',
                        borderRadius: '2px',
                        outline: 'none',
                        fontFamily: 'inherit'
                      }}
                    />
                  ) : (
                    <>
                      <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {chat.name}
                      </span>
                      <span
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingChatId(chat.id);
                          setEditingName(chat.name);
                        }}
                        title="Renombrar"
                        style={{ opacity: 0.5, cursor: 'pointer', flexShrink: 0 }}
                      >
                        ✎
                      </span>
                    </>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Tools */}
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
              <div key={msg.id}>
                {msg.memories && msg.memories.length > 0 && (
                  <MemoriesDisplay memories={msg.memories} />
                )}
                <div style={{ display: 'flex', gap: '8px', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: '10px', color: '#666666', marginBottom: '4px' }}>
                      {msg.role === 'user' ? 'Tú' : 'Alex'}
                    </div>
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
        <input
          ref={fileInputRef}
          type="file"
          style={{ display: 'none' }}
        />
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
        <button
          onClick={() => {
            setMessages([{ id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }]);
          }}
          style={{
            background: '#1a1a1a',
            border: '1px solid #2a2a2a',
            color: '#888888',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '11px',
            whiteSpace: 'nowrap'
          }}
        >
          🗑 Limpiar
        </button>
        <button
          onClick={sendMessage}
          disabled={loading}
          style={{
            background: 'rgba(0, 217, 163, 0.1)',
            borderColor: '#00d9a3',
            border: '1px solid #00d9a3',
            color: '#00d9a3',
            padding: '8px 12px',
            borderRadius: '4px',
            cursor: loading ? 'default' : 'pointer',
            fontSize: '11px',
            whiteSpace: 'nowrap',
            opacity: loading ? 0.6 : 1
          }}
        >
          ➜ {loading ? 'Pensando...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
};

export default AlexDashboard;
