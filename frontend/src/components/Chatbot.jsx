import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import api from '../api/client';
import { queryClientKnowledge, PUBLIC_SUGGESTIONS } from '../utils/chatbotKnowledge';

const INITIAL_GREETING = {
  id: 'msg-welcome',
  sender: 'bot',
  text: `👋 **Welcome to the SatyaSutra Public Assistant!**

I can answer general operational questions based on our **public landing page**:

- 🌟 **What is SatyaSutra?**
- 🔄 **The 4-Stage Intelligence Pipeline**
- 🛡️ **Core Capabilities** (Ingestion, NLP, Knowledge Graph, Timeline Gaps, Contradictions)
- ⚖️ **Ethical Guardrails & Policies** (Zero Guilt Scores)
- 👥 **Public Target Use Cases** & Creators

*(Note: For security and investigative confidentiality, login credentials, internal technical architecture, and active detective case operations are strictly protected and cannot be disclosed).*`,
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
  sources: ['SatyaSutra Landing Page'],
  suggestedFollowups: PUBLIC_SUGGESTIONS.slice(0, 4),
};

export default function Chatbot() {
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState(() => {
    try {
      const saved = sessionStorage.getItem('satyasutra_chat_history');
      return saved ? JSON.parse(saved) : [INITIAL_GREETING];
    } catch {
      return [INITIAL_GREETING];
    }
  });
  const [inputValue, setInputValue] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [copiedId, setCopiedId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Save conversation to session storage
  useEffect(() => {
    try {
      sessionStorage.setItem('satyasutra_chat_history', JSON.stringify(messages));
    } catch {
      // Storage quota or disabled
    }
  }, [messages]);

  // Scroll to bottom on new messages
  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isThinking, isOpen]);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [isOpen]);

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || inputValue).trim();
    if (!query || isThinking) return;

    const userMessageId = `user-${Date.now()}`;
    const userMessage = {
      id: userMessageId,
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsThinking(true);

    try {
      // Prepare conversation history for backend context
      const historyPayload = messages.slice(-4).map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      // Call backend AI knowledge endpoint
      let response;
      try {
        response = await api.chatbot.ask(query, historyPayload);
      } catch (backendErr) {
        console.warn('Backend chatbot API unavailable, utilizing client knowledge fallback:', backendErr);
        // Instant client-side trained model fallback
        const clientRes = queryClientKnowledge(query);
        response = {
          answer: clientRes.answer,
          sources: clientRes.sources,
          suggested_followups: clientRes.suggestedFollowups,
        };
      }

      const botMessage = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: response.answer || "I found information on SatyaSutra. Let me know if you need more details!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: response.sources || ['SatyaSutra Knowledge Base'],
        suggestedFollowups: response.suggested_followups || response.suggestedFollowups || [],
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = {
        id: `err-${Date.now()}`,
        sender: 'bot',
        text: `⚠️ **Apologies, an error occurred while searching knowledge:** ${err.message || 'Unknown issue'}. Please try asking about evidence upload, the knowledge graph, timeline, or login.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        sources: ['System Alert'],
        suggestedFollowups: ['What is SatyaSutra?', 'How to upload evidence?'],
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsThinking(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleClearChat = () => {
    setMessages([INITIAL_GREETING]);
    try {
      sessionStorage.removeItem('satyasutra_chat_history');
    } catch {
      // ignore
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <div className="chatbot-root" id="satyasutra-chatbot-widget">
      {/* Floating Action Button / Launcher */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className={`chatbot-launcher-btn ${isOpen ? 'active' : ''}`}
        aria-label="Toggle SatyaSutra AI Assistant"
        title="Ask SatyaSutra AI Assistant"
        id="chatbot-toggle-button"
      >
        <div className="launcher-glow-ring"></div>
        {isOpen ? (
          <span className="launcher-icon close-icon">✕</span>
        ) : (
          <div className="launcher-icon-wrapper">
            <span className="launcher-bot-icon">🤖</span>
            <span className="launcher-pulse-dot"></span>
            <span className="launcher-badge">AI</span>
          </div>
        )}
      </button>

      {/* Floating Chat Window */}
      {isOpen && (
        <div className="chatbot-window anim-scale-up" id="chatbot-panel">
          {/* Header */}
          <div className="chatbot-header">
            <div className="chatbot-header-identity">
              <div className="chatbot-avatar">
                <span>⚖️</span>
                <span className="chatbot-status-dot online"></span>
              </div>
              <div className="chatbot-title-info">
                <div className="chatbot-main-title">
                  <span>SatyaSutra AI</span>
                  <span className="chatbot-version-pill">Public Guide</span>
                </div>
                <div className="chatbot-subtitle">Landing Page Information • Secure Assistant</div>
              </div>
            </div>

            <div className="chatbot-header-actions">
              <button
                onClick={handleClearChat}
                className="chatbot-icon-btn"
                title="Clear conversation history"
                aria-label="Clear chat"
              >
                🔄
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="chatbot-icon-btn close-btn"
                title="Minimize assistant"
                aria-label="Close chat"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Quick Info Bar */}
          <div className="chatbot-quick-bar">
            <span>🛡️ Public Information Guide • Confidential Records Protected</span>
          </div>

          {/* Conversation Stream */}
          <div className="chatbot-messages-container" id="chatbot-messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-bubble-wrapper ${msg.sender === 'user' ? 'user-wrapper' : 'bot-wrapper'}`}
              >
                {msg.sender === 'bot' && (
                  <div className="bubble-avatar">
                    <span>🔍</span>
                  </div>
                )}

                <div className={`chat-bubble ${msg.sender === 'user' ? 'user-bubble' : 'bot-bubble'}`}>
                  <div className="bubble-content markdown-body">
                    <ReactMarkdown
                      components={{
                        a: ({ href, children, ...props }) => {
                          if (href && href.startsWith('/')) {
                            return (
                              <a
                                href={href}
                                onClick={(e) => {
                                  e.preventDefault();
                                  navigate(href);
                                }}
                                className="chatbot-inline-nav-link"
                                {...props}
                              >
                                {children} ↗
                              </a>
                            );
                          }
                          return (
                            <a
                              href={href}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="chatbot-inline-nav-link"
                              {...props}
                            >
                              {children} ↗
                            </a>
                          );
                        },
                      }}
                    >
                      {msg.text}
                    </ReactMarkdown>
                  </div>

                  {/* Metadata & Actions */}
                  <div className="bubble-meta">
                    <span className="bubble-timestamp">{msg.timestamp}</span>
                    {msg.sender === 'bot' && msg.id !== 'msg-welcome' && (
                      <button
                        onClick={() => handleCopy(msg.id, msg.text)}
                        className="bubble-copy-btn"
                        title="Copy answer"
                      >
                        {copiedId === msg.id ? '✓ Copied' : '📋 Copy'}
                      </button>
                    )}
                  </div>

                  {/* Sources Tag */}
                  {msg.sources && msg.sources.length > 0 && msg.sender === 'bot' && (
                    <div className="bubble-sources">
                      <span className="sources-label">Sources:</span>
                      {msg.sources.map((src, i) => (
                        <span key={i} className="source-tag">
                          {src}
                        </span>
                      ))}
                    </div>
                  )}

                  {/* Dynamic Follow-up Suggestions on Bot Bubble */}
                  {msg.suggestedFollowups && msg.suggestedFollowups.length > 0 && msg.sender === 'bot' && (
                    <div className="bubble-followups">
                      <div className="followup-title">💡 Related inquiries:</div>
                      <div className="followup-chips">
                        {msg.suggestedFollowups.map((suggestion, idx) => (
                          <button
                            key={idx}
                            onClick={() => handleSendMessage(suggestion)}
                            className="followup-chip-btn"
                          >
                            {suggestion}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}

            {/* Thinking / Typing Indicator */}
            {isThinking && (
              <div className="chat-bubble-wrapper bot-wrapper anim-fade">
                <div className="bubble-avatar">
                  <span>🧠</span>
                </div>
                <div className="chat-bubble bot-bubble thinking-bubble">
                  <div className="thinking-dots">
                    <span className="dot dot-1"></span>
                    <span className="dot dot-2"></span>
                    <span className="dot dot-3"></span>
                  </div>
                  <span className="thinking-text">SatyaSutra Model is synthesizing answer...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Preset Prompts Drawer (when conversation is fresh) */}
          {messages.length === 1 && (
            <div className="chatbot-starter-prompts">
              <span className="starter-title">Public Inquiries:</span>
              <div className="starter-chips-grid">
                {PUBLIC_SUGGESTIONS.map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(q)}
                    className="starter-chip"
                  >
                    {q}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Input Area */}
          <div className="chatbot-input-area">
            <div className="input-box-wrapper">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about the landing page, pipeline, or capabilities..."
                rows={1}
                className="chatbot-input"
                id="chatbot-text-input"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isThinking}
                className="chatbot-send-btn"
                title="Send message (Enter)"
                aria-label="Send query"
                id="chatbot-send-button"
              >
                <svg
                  width="18"
                  height="18"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </div>
            <div className="input-footer-hint">
              <span>Press <strong>Enter</strong> to send • <strong>Shift+Enter</strong> for newline</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
