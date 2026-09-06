import React, { useState, useEffect, useRef } from 'react';

// Componente para barra circular de porcentaje
const CircularProgress = ({ percentage, label }) => {
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

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
          {Math.round(percentage)}%
        </div>
        <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase' }}>
          {label}
        </div>
      </div>
    </div>
  );
};

// Componente para animación de thinking
const ThinkingAnimation = () => (
  <div style={{
    display: 'flex',
    gap: '6px',
    alignItems: 'center',
    justifyContent: 'center',
    height: '20px'
  }}>
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

  const [stats, setStats] = useState({
    cpu: 0,
    ram: 0,
    model: 'qwen:7b',
    connected: false
  });

  const [activeSection, setActiveSection] = useState('Alex Core');
  const messagesEndRef = useRef(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchStats();
    const statsInterval = setInterval(fetchStats, 3000);
    return () => clearInterval(statsInterval);
  }, []);

  const fetchStats = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/resources');
      if (response.ok) {
        const data = await response.json();
        setStats(prev => ({
          ...prev,
          cpu: Math.min(100, Math.max(0, data.cpu || 0)),
          ram: Math.min(100, Math.max(0, (data.ram / 16) * 100)),
          connected: true
        }));
      }
    } catch (error) {
      setStats(prev => ({ ...prev, connected: false }));
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || loading) return;

    const userMessage = {
      id: messages.length + 1,
      role: 'user',
      text: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: input })
      });

      if (!response.ok) throw new Error('Error de respuesta');

      const data = await response.json();

      const assistantMessage = {
        id: messages.length + 2,
        role: 'assistant',
        text: data.reply || 'Sin respuesta',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage = {
        id: messages.length + 2,
        role: 'assistant',
        text: `Error: ${error.message}. ¿Backend levantado?`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
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
    setUploadedFiles(prev => [...prev, ...fileNames]);
    
    // Optional: agregar mensaje mostrando archivos subidos
    const fileMessage = {
      id: messages.length + 1,
      role: 'user',
      text: `Archivos subidos: ${fileNames.join(', ')}`,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, fileMessage]);
  };

  const clearChat = () => {
    setMessages([{ id: 1, role: 'assistant', text: '¿Qué necesitás?', timestamp: new Date() }]);
    setUploadedFiles([]);
  };

  const menuItems = [
    { section: 'Core', items: ['Alex Core', 'Automatizaciones'] },
    { section: 'Nav', items: ['General', 'Nuevo proyecto'] },
    { section: 'Tools', items: ['Búsqueda web', 'Documentos'] },
    { section: 'Modules', items: ['FastAPI setup', 'Frontend TUI', 'Voice cloning', 'Manipulaciones - Amisadal', 'Sarcasmo como defensa', 'Patrones - Erick Corona', 'Procrastinar?'] }
  ];

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerLogo}>A.L.E.X</div>
        <div style={styles.headerRight}>
          <span>v0.2</span>
          <span> | </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <div style={{
              ...styles.statusDot,
              background: stats.connected ? '#00d9a3' : '#666666'
            }}></div>
            {stats.connected ? 'connected' : 'offline'}
          </span>
        </div>
      </div>

      {/* Main Grid */}
      <div style={styles.mainGrid}>
        {/* Sidebar */}
        <div style={styles.sidebar}>
          {menuItems.map((section, idx) => (
            <div key={idx} style={styles.sidebarSection}>
              <div style={styles.sidebarLabel}>{section.section}</div>
              {section.items.map((item, itemIdx) => (
                <div
                  key={itemIdx}
                  style={{
                    ...styles.sidebarItem,
                    ...(activeSection === item && styles.sidebarItemActive)
                  }}
                  onClick={() => setActiveSection(item)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = '#2a2a2a';
                    e.currentTarget.style.color = '#00d9a3';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = activeSection === item ? 'rgba(0, 217, 163, 0.05)' : 'transparent';
                    e.currentTarget.style.color = activeSection === item ? '#00d9a3' : '#888888';
                  }}
                >
                  <span style={styles.sidebarIcon}>⚙</span>
                  <span style={{ fontSize: '12px' }}>{item}</span>
                </div>
              ))}
            </div>
          ))}
        </div>

        {/* Main Content */}
        <div style={styles.mainContent}>
          {/* Stats Row - Barras Circulares */}
          <div style={styles.statsRow}>
            <CircularProgress percentage={stats.cpu} label="CPU" />
            <CircularProgress percentage={stats.ram} label="RAM" />
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', justifyContent: 'center' }}>
              <div style={{ fontSize: '12px', color: '#00d9a3', fontWeight: 600, textAlign: 'center' }}>
                {stats.model}
              </div>
              <div style={{ fontSize: '10px', color: '#666666', textTransform: 'uppercase', textAlign: 'center' }}>
                Modelo
              </div>
            </div>
          </div>

          {/* Chat Area */}
          <div style={styles.chatArea}>
            {messages.map((msg) => (
              <div key={msg.id} style={{
                ...styles.message,
                ...(msg.role === 'user' && styles.messageUser)
              }}>
                <div>
                  <div style={styles.messageSender}>{msg.role === 'user' ? 'Tú' : 'Alex'}</div>
                  <div style={{
                    ...styles.messageContent,
                    ...(msg.role === 'user' && styles.messageContentUser)
                  }}>
                    {msg.text}
                  </div>
                  <div style={styles.timestamp}>
                    {msg.timestamp.toLocaleTimeString('es-ES', {
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit'
                    })}
                  </div>
                </div>
              </div>
            ))}
            {loading && (
              <div style={styles.message}>
                <div>
                  <div style={styles.messageSender}>Alex</div>
                  <div style={styles.messageContent}>
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
      <div style={styles.footer}>
        <div style={styles.inputWrapper}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Escribe tu mensaje..."
            disabled={loading}
            style={styles.input}
          />
        </div>
        <div style={styles.actionButtons}>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            style={{ display: 'none' }}
            multiple
          />
          <button
            style={styles.button}
            onClick={() => fileInputRef.current?.click()}
            title="Subir archivos"
          >
            📎 Archivo
          </button>
          <button
            style={styles.button}
            onClick={clearChat}
            title="Limpiar chat"
          >
            🗑 Limpiar
          </button>
          <button
            style={{ ...styles.button, ...styles.buttonSend }}
            onClick={sendMessage}
            disabled={loading}
          >
            ➜ {loading ? 'Pensando...' : 'Enviar'}
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  container: {
    display: 'grid',
    gridTemplateColumns: '240px 1fr',
    gridTemplateRows: '50px 1fr 120px',
    height: '100vh',
    background: '#0a0a0a',
    color: '#cccccc',
    fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
    fontSize: '13px',
    lineHeight: '1.5',
  },
  header: {
    gridColumn: '1 / -1',
    background: '#1a1a1a',
    borderBottom: '1px solid #2a2a2a',
    display: 'flex',
    alignItems: 'center',
    padding: '0 20px',
    justifyContent: 'space-between',
  },
  headerLogo: {
    fontWeight: 600,
    fontSize: '14px',
    color: '#00d9a3',
    letterSpacing: '2px',
  },
  headerRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '16px',
    fontSize: '11px',
    color: '#888888',
  },
  statusDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
    display: 'inline-block',
    transition: 'background 0.3s'
  },
  mainGrid: {
    display: 'grid',
    gridTemplateColumns: '240px 1fr',
  },
  sidebar: {
    background: '#1a1a1a',
    borderRight: '1px solid #2a2a2a',
    padding: '20px 0',
    overflowY: 'auto',
  },
  sidebarSection: {
    padding: '12px 0',
    borderBottom: '1px solid #2a2a2a',
  },
  sidebarLabel: {
    fontSize: '10px',
    color: '#666666',
    textTransform: 'uppercase',
    letterSpacing: '1px',
    padding: '0 16px',
    marginBottom: '8px',
  },
  sidebarItem: {
    padding: '10px 16px',
    cursor: 'pointer',
    transition: 'all 0.2s',
    borderLeft: '2px solid transparent',
    color: '#888888',
    fontSize: '12px',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  sidebarItemActive: {
    borderLeftColor: '#00d9a3',
    color: '#00d9a3',
    background: 'rgba(0, 217, 163, 0.05)',
  },
  sidebarIcon: {
    width: '16px',
    textAlign: 'center',
    fontWeight: 600,
  },
  mainContent: {
    display: 'flex',
    flexDirection: 'column',
    background: '#0a0a0a',
    overflow: 'hidden',
  },
  statsRow: {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '20px',
    padding: '20px',
    paddingBottom: '10px',
  },
  chatArea: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '12px',
  },
  message: {
    display: 'flex',
    gap: '8px',
    animation: 'slideIn 0.3s ease-out',
  },
  messageUser: {
    justifyContent: 'flex-end',
  },
  messageContent: {
    maxWidth: '60%',
    padding: '10px 12px',
    borderRadius: '4px',
    background: '#1a1a1a',
    border: '1px solid #2a2a2a',
    wordWrap: 'break-word',
    color: '#b0b0b0',
  },
  messageContentUser: {
    background: 'rgba(0, 217, 163, 0.1)',
    borderColor: '#00d9a3',
    color: '#e0e0e0',
  },
  messageSender: {
    fontSize: '10px',
    color: '#666666',
    marginBottom: '4px',
  },
  timestamp: {
    fontSize: '10px',
    color: '#555555',
    marginTop: '4px',
  },
  footer: {
    gridColumn: '1 / -1',
    background: '#1a1a1a',
    borderTop: '1px solid #2a2a2a',
    padding: '12px 20px',
    display: 'flex',
    gap: '8px',
    alignItems: 'flex-start',
  },
  inputWrapper: {
    flex: 1,
    display: 'flex',
    gap: '8px',
  },
  input: {
    flex: 1,
    background: '#0a0a0a',
    border: '1px solid #2a2a2a',
    color: '#cccccc',
    padding: '8px 12px',
    borderRadius: '4px',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '12px',
    outline: 'none',
    transition: 'all 0.2s',
    cursor: 'text',
  },
  actionButtons: {
    display: 'flex',
    gap: '8px',
  },
  button: {
    background: '#1a1a1a',
    border: '1px solid #2a2a2a',
    color: '#888888',
    padding: '8px 12px',
    borderRadius: '4px',
    cursor: 'pointer',
    fontFamily: "'JetBrains Mono', monospace",
    fontSize: '11px',
    transition: 'all 0.2s',
    whiteSpace: 'nowrap',
  },
  buttonSend: {
    background: 'rgba(0, 217, 163, 0.1)',
    borderColor: '#00d9a3',
    color: '#00d9a3',
  },
};

export default AlexDashboard;
