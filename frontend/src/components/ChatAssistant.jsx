import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2 } from "lucide-react";

const ChatAssistant = ({ onImageUpdate }) => {
  const [messages, setMessages] = useState([
    {
      id: "welcome",
      text: "Hi! I'm your groundwater assistant 🌊\n\nI can help farmers, researchers, and water managers with:\n• Groundwater levels in any state/district\n• Compare water availability between areas\n• Find the best and worst water situations\n• Simple charts and recommendations\n\nJust ask me like: \"How is water in Punjab?\" or \"Compare districts in Kerala\"",
      isUser: false,
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      id: Date.now().toString(),
      text: inputValue,
      isUser: true,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const messageToSend = inputValue;
    setInputValue("");
    setIsLoading(true);

    try {
      // Send the question parameter (matching your updated backend)
      const response = await fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
          question: messageToSend  // Primary parameter for the updated backend
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Handle error responses from backend
      if (data.error) {
        const errorMessage = {
          id: (Date.now() + 1).toString(),
          text: `❌ ${data.error}`,
          isUser: false,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
        return;
      }
      
      // Add assistant response
      const assistantMessage = {
        id: (Date.now() + 1).toString(),
        text: data.answer || "I couldn't find that information. Try asking about a specific state or district!",
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);

      // Update image with cache-busting timestamp
      if (data.image_url) {
        const cacheBustedUrl = `${data.image_url}?t=${Date.now()}`;
        console.log("Updating image with URL:", cacheBustedUrl);
        onImageUpdate(cacheBustedUrl);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: `🔌 Can't connect to server. Make sure backend is running on http://127.0.0.1:5000`,
        isUser: false,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Quick action buttons for common questions
  const quickQuestions = [
    "Water levels in Maharashtra",
    "Compare Punjab districts", 
    "Best groundwater states",
    "Water problems in Rajasthan"
  ];

  const handleQuickQuestion = (question) => {
    setInputValue(question);
  };

  return (
    <div className="bg-surface rounded-lg border h-full flex flex-col">
      <div className="p-4 border-b">
        <h2 className="text-lg font-semibold text-foreground">INGRES Assistant 🌊</h2>
        <p className="text-sm text-muted-foreground">
          Simple groundwater answers + charts for farmers & researchers
        </p>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex items-start gap-3 animate-fade-in ${
              message.isUser ? "flex-row-reverse" : ""
            }`}
          >
            <div
              className={`flex items-center justify-center w-8 h-8 rounded-full ${
                message.isUser
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted text-muted-foreground"
              }`}
            >
              {message.isUser ? (
                <User className="w-4 h-4" />
              ) : (
                <Bot className="w-4 h-4" />
              )}
            </div>
            
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                message.isUser
                  ? "bg-chat-user-bg text-chat-user-text"
                  : "bg-chat-assistant-bg text-chat-assistant-text"
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-line">{message.text}</p>
            </div>
          </div>
        ))}
        
        {/* Quick question buttons - only show on first message */}
        {messages.length === 1 && !isLoading && (
          <div className="flex flex-col gap-2">
            <p className="text-sm text-muted-foreground px-2">💡 Quick questions:</p>
            <div className="grid grid-cols-2 gap-2">
              {quickQuestions.map((question, index) => (
                <button
                  key={index}
                  onClick={() => handleQuickQuestion(question)}
                  className="text-left px-3 py-2 text-sm bg-muted rounded-lg hover:bg-primary hover:text-primary-foreground transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}
        
        {isLoading && (
          <div className="flex items-start gap-3 animate-fade-in">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-muted text-muted-foreground">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-chat-assistant-bg text-chat-assistant-text rounded-2xl px-4 py-3">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span className="text-sm">Getting water data and making chart...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask: 'Water in Kerala' or 'Compare Bihar districts'..."
            className="flex-1 px-3 py-2 border rounded-lg bg-background text-foreground"
            style={{ border: `1px solid var(--border)` }}
            disabled={isLoading}
          />
          <button
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            className="shrink-0 px-3 py-2 bg-primary text-primary-foreground rounded-lg flex items-center justify-center"
            style={{ minWidth: '44px', minHeight: '44px' }}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatAssistant;
