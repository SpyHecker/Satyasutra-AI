import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import api from '../api/client';
import { queryClientKnowledge } from '../utils/chatbotKnowledge';

const INITIAL_GREETING = {
  id: 'msg-welcome',
  sender: 'bot',
  text: `👋 **Hi! How can I help you today?**\n\nAsk me anything about SatyaSutra's platform, pipeline, or capabilities.`,
  timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
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
        const clientRes = queryClientKnowledge(query);
        response = {
          answer: clientRes.answer,
        };
      }

      const botMessage = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: response.answer || "I found information on SatyaSutra. Let me know if you need more details!",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error('Chat error:', err);
      const errorMessage = {
        id: `err-${Date.now()}`,
        sender: 'bot',
        text: `⚠️ **Unable to complete request:** ${err.message || 'Please try again later.'}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
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
      {/* Floating Action Launcher Button */}
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className={`chatbot-launcher-btn ${isOpen ? 'active' : ''}`}
        aria-label="Toggle SatyaSutra AI Assistant"
        title="Chat with SatyaSutra Assistant"
        id="chatbot-toggle-button"
      >
        {isOpen ? (
          <span className="launcher-icon close-icon">✕</span>
        ) : (
          <svg
            className="launcher-chat-svg"
            width="21"
            height="21"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
          </svg>
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
              </div>
              <div className="chatbot-title-info">
                <div className="chatbot-main-title">SatyaSutra AI</div>
                <div className="chatbot-status-row">
                  <span className="chatbot-status-dot online"></span>
                  <span className="chatbot-subtitle">Assistant</span>
                </div>
              </div>
            </div>

            <div className="chatbot-header-actions">
              <button
                onClick={handleClearChat}
                className="chatbot-icon-btn"
                title="Clear chat"
                aria-label="Clear chat"
              >
                🔄
              </button>
              <button
                onClick={() => setIsOpen(false)}
                className="chatbot-icon-btn close-btn"
                title="Close chat"
                aria-label="Close chat"
              >
                ✕
              </button>
            </div>
          </div>

          {/* Conversation Messages */}
          <div className="chatbot-messages-container" id="chatbot-messages">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-bubble-wrapper ${msg.sender === 'user' ? 'user-wrapper' : 'bot-wrapper'}`}
              >
                <div className={`chat-bubble ${msg.sender === 'user' ? 'user-bubble' : 'bot-bubble'}`}>
                  <div className="bubble-content markdown-body">
                    <ReactMarkdown
                      components={{
                        a: ({ href, children, ...props }) => {
                          const isInternal = href && href.startsWith('/');
                          return (
                            <a
                              href={href}
                              onClick={isInternal ? (e) => {
                                e.preventDefault();
                                navigate(href);
                              } : undefined}
                              target={isInternal ? undefined : '_blank'}
                              rel={isInternal ? undefined : 'noopener noreferrer'}
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

                  <div className="bubble-meta">
                    <span className="bubble-timestamp">{msg.timestamp}</span>
                    {msg.sender === 'bot' && (
                      <button
                        onClick={() => handleCopy(msg.id, msg.text)}
                        className="bubble-copy-btn"
                        title="Copy text"
                      >
                        {copiedId === msg.id ? '✓ Copied' : 'Copy'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}

            {/* Thinking / Typing Indicator */}
            {isThinking && (
              <div className="chat-bubble-wrapper bot-wrapper anim-fade">
                <div className="chat-bubble bot-bubble thinking-bubble">
                  <div className="thinking-dots">
                    <span className="dot dot-1"></span>
                    <span className="dot dot-2"></span>
                    <span className="dot dot-3"></span>
                  </div>
                  <span className="thinking-text">Thinking...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="chatbot-input-area">
            <div className="input-box-wrapper">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question..."
                rows={1}
                className="chatbot-input"
                id="chatbot-text-input"
              />
              <button
                onClick={() => handleSendMessage()}
                disabled={!inputValue.trim() || isThinking}
                className="chatbot-send-btn"
                title="Send"
                aria-label="Send message"
                id="chatbot-send-button"
              >
                <svg
                  width="15"
                  height="15"
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
          </div>
        </div>
      )}
    </div>
  );
}
