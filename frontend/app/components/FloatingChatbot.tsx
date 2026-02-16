"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { sendChatMessage } from "@/lib/api";

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your AI assistant. How can I help you manage your tasks today?",
      sender: "bot",
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (inputValue.trim() === "") return;

    // Get the JWT token from localStorage
    const token = localStorage.getItem('jwt_token');
    if (!token) {
      // Handle case where user is not authenticated
      const newUserMessage = {
        id: messages.length + 1,
        text: inputValue,
        sender: "user",
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, newUserMessage]);
      setInputValue("");

      const errorResponse = {
        id: messages.length + 2,
        text: "Please log in to use the AI assistant.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorResponse]);
      return;
    }

    const newUserMessage = {
      id: messages.length + 1,
      text: inputValue,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, newUserMessage]);
    setInputValue("");

    try {
      // Call the backend API
      const response = await sendChatMessage(inputValue, token);

      // Extract the response text from the backend response
      // The backend returns a ChatResponse with a 'response' field
      let responseText = "I processed your request.";

      // Check if response has the expected structure
      if (response && typeof response === 'object') {
        if (response.response) {
          responseText = response.response;
        } else if (response.message) {
          responseText = response.message;
        } else if (response.reply) {
          responseText = response.reply;
        } else {
          // If none of the expected fields exist, try to stringify the response
          responseText = JSON.stringify(response).substring(0, 200) + '...';
        }
      } else if (typeof response === 'string') {
        responseText = response;
      }

      const botResponse = {
        id: messages.length + 2,
        text: responseText,
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, botResponse]);

      // Check if the response indicates a task operation and trigger a refresh
      // Look for keywords that indicate task operations
      const lowerCaseResponse = responseText.toLowerCase();

      if (lowerCaseResponse.includes("task") && (lowerCaseResponse.includes("created") || lowerCaseResponse.includes("added"))) {
        // Dispatch a custom event to notify other parts of the app to refresh tasks
        window.dispatchEvent(new CustomEvent('taskCreated'));
      } else if (lowerCaseResponse.includes("task") && (lowerCaseResponse.includes("deleted") || lowerCaseResponse.includes("removed"))) {
        // Dispatch a custom event to notify other parts of the app to refresh tasks after deletion
        // Extract task title from the response for immediate UI update
        const titleMatch = responseText.match(/task\s+['"]([^'"]+)['"]/i);
        const taskTitle = titleMatch ? titleMatch[1] : null;

        window.dispatchEvent(new CustomEvent('taskDeleted', {
          detail: { taskTitle: taskTitle } // Pass the task title if available
        }));
      } else if (lowerCaseResponse.includes("task") && (lowerCaseResponse.includes("updated") || lowerCaseResponse.includes("modified") || lowerCaseResponse.includes("changed"))) {
        // Dispatch a custom event to notify other parts of the app to refresh tasks after update
        const titleMatch = responseText.match(/task\s+['"]([^'"]+)['"]/i);
        const taskTitle = titleMatch ? titleMatch[1] : null;

        window.dispatchEvent(new CustomEvent('taskUpdated', {
          detail: { taskTitle: taskTitle } // Pass the task title if available
        }));
      } else if (lowerCaseResponse.includes("task") && lowerCaseResponse.includes("complete")) {
        // Dispatch a custom event to notify other parts of the app to refresh tasks after completion
        const titleMatch = responseText.match(/task\s+['"]([^'"]+)['"]/i);
        const taskTitle = titleMatch ? titleMatch[1] : null;

        window.dispatchEvent(new CustomEvent('taskUpdated', {
          detail: { taskTitle: taskTitle, completed: true } // Mark as completed
        }));
      }
    } catch (error) {
      console.error('Error sending message to chatbot:', error);

      const errorResponse = {
        id: messages.length + 2,
        text: "Sorry, I encountered an error processing your request. Please try again.",
        sender: "bot",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorResponse]);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const closeChat = () => {
    setIsOpen(false);
  };

  return (
    <>
      {/* Floating Chatbot Button */}
      <motion.button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gray-100 rounded-full shadow-lg flex items-center justify-center cursor-pointer hover:scale-110 transition-all duration-200 group md:bottom-6 md:right-6 sm:bottom-4 sm:right-4"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        animate={{
          boxShadow: [
            "0 0 20px rgba(59, 130, 246, 0.3)",
            "0 0 30px rgba(59, 130, 246, 0.5)",
            "0 0 20px rgba(59, 130, 246, 0.3)",
          ],
        }}
        transition={{
          boxShadow: {
            duration: 2000,
            repeat: Infinity,
            repeatType: "reverse",
          },
        }}
        aria-label="Open chatbot"
      >
        <svg
          width="40"
          height="40"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-black"
        >
          <rect
            x="6"
            y="7"
            width="12"
            height="10"
            rx="2"
            stroke="currentColor"
            strokeWidth="2"
          />
          <circle cx="9" cy="12" r="1.5" fill="currentColor" />
          <circle cx="15" cy="12" r="1.5" fill="currentColor" />
          <line
            x1="10"
            y1="16"
            x2="14"
            y2="16"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <line
            x1="12"
            y1="4"
            x2="12"
            y2="6"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <circle
            cx="12"
            cy="3"
            r="1"
            stroke="currentColor"
            strokeWidth="2"
          />
          <line
            x1="6"
            y1="12"
            x2="4"
            y2="12"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
          <line
            x1="20"
            y1="12"
            x2="18"
            y2="12"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          />
        </svg>
      </motion.button>

      {/* Chatbot Panel */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              className="fixed inset-0 bg-black bg-opacity-50 z-40 sm:z-30"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={closeChat}
            />

            {/* Chat Panel */}
            <motion.div
              className="fixed top-[10%] m-[2%] -translate-x-1/2 -translate-y-1/2 w-[95%] h-[75vh] md:top-auto md:left-auto md:translate-x-0 md:translate-y-0 md:bottom-24 md:right-6 md:w-[25rem] md:max-w-md md:h-[400px] bg-white rounded-xl shadow-2xl z-50 flex flex-col overflow-hidden"
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: 100, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 500 }}
            >
              {/* Header */}
              <div className="bg-gray-200 p-4 text-black bg-opacity-90 backdrop-blur-sm sm:p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-gray-500 bg-opacity-20 rounded-full flex items-center justify-center sm:w-7 sm:h-7">
                      <svg
                        width="24"
                        height="24"
                        viewBox="0 0 24 24"
                        fill="none"
                        xmlns="http://www.w3.org/2000/svg"
                        className="text-black sm:w-5 sm:h-5"
                      >
                        <rect
                          x="6"
                          y="7"
                          width="12"
                          height="10"
                          rx="2"
                          stroke="currentColor"
                          strokeWidth="2"
                        />
                        <circle cx="9" cy="12" r="1.5" fill="currentColor" />
                        <circle cx="15" cy="12" r="1.5" fill="currentColor" />
                        <line
                          x1="10"
                          y1="16"
                          x2="14"
                          y2="16"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                        />
                        <line
                          x1="12"
                          y1="4"
                          x2="12"
                          y2="6"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                        />
                        <circle
                          cx="12"
                          cy="3"
                          r="1"
                          stroke="currentColor"
                          strokeWidth="2"
                        />
                        <line
                          x1="6"
                          y1="12"
                          x2="4"
                          y2="12"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                        />
                        <line
                          x1="20"
                          y1="12"
                          x2="18"
                          y2="12"
                          stroke="currentColor"
                          strokeWidth="2"
                          strokeLinecap="round"
                        />
                      </svg>
                    </div>
                    <span className="font-semibold sm:text-sm">Chatbot</span>
                  </div>
                  <button
                    onClick={closeChat}
                    className="text-white hover:bg-opacity-20 rounded-full p-1 transition-colors sm:p-0.5"
                    aria-label="Close chat"
                  >
                    <svg
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      className="text-black sm:w-4 sm:h-4"
                    >
                      <path
                        d="M19 6.41L17.59 5L12 10.59L6.41 5L5 6.41L10.59 12L5 17.59L6.41 19L12 13.41L17.59 19L19 17.59L13.41 12L19 6.41Z"
                        fill="currentColor"
                      />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Messages Area */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 sm:p-3" style={{ backgroundImage: "url('https://st4.depositphotos.com/20547288/37963/i/450/depositphotos_379633208-stock-photo-panoramic-fog-mist-texture-overlays.jpg')", backgroundSize: 'cover', backgroundPosition: 'center' }}>
                {messages.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex ${message.sender === "user" ? "justify-end" : "justify-start"}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-2xl sm:px-3 sm:py-1.5 sm:text-sm ${
                        message.sender === "user"
                          ? "bg-white text-black rounded-br-md"
                          : "bg-white text-gray-800 shadow-sm rounded-bl-md"
                      }`}
                    >
                      <div className="flex items-start space-x-2">
                        {message.sender === "bot" && (
                          <div className="w-6 h-6 bg-gray-100 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 sm:w-5 sm:h-5">
                            <svg
                              width="20"
                              height="20"
                              viewBox="0 0 24 24"
                              fill="none"
                              xmlns="http://www.w3.org/2000/svg"
                              className="text-black sm:w-4 sm:h-4"
                            >
                              <rect
                                x="6"
                                y="7"
                                width="12"
                                height="10"
                                rx="2"
                                stroke="currentColor"
                                strokeWidth="2"
                              />
                              <circle
                                cx="9"
                                cy="12"
                                r="1.5"
                                fill="currentColor"
                              />
                              <circle
                                cx="15"
                                cy="12"
                                r="1.5"
                                fill="currentColor"
                              />
                              <line
                                x1="10"
                                y1="16"
                                x2="14"
                                y2="16"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                              />
                              <line
                                x1="12"
                                y1="4"
                                x2="12"
                                y2="6"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                              />
                              <circle
                                cx="12"
                                cy="3"
                                r="1"
                                stroke="currentColor"
                                strokeWidth="2"
                              />
                              <line
                                x1="6"
                                y1="12"
                                x2="4"
                                y2="12"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                              />
                              <line
                                x1="20"
                                y1="12"
                                x2="18"
                                y2="12"
                                stroke="currentColor"
                                strokeWidth="2"
                                strokeLinecap="round"
                              />
                            </svg>
                          </div>
                        )}
                        <div>
                          <p className="text-sm text-black sm:text-xs">{message.text}</p>
                          <p
                            className={`text-xs mt-1 sm:text-xs ${message.sender === "user" ? "text-black" : "text-gray-800"}`}
                          >
                            {message.timestamp.toLocaleTimeString([], {
                              hour: "2-digit",
                              minute: "2-digit",
                            })}
                          </p>
                        </div>
                        {message.sender === "user" && (
                          <div className="w-6 h-6 bg-gray-200 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 sm:w-5 sm:h-5">
                            <svg
                              width="12"
                              height="12"
                              viewBox="0 0 24 24"
                              fill="none"
                              xmlns="http://www.w3.org/2000/svg"
                              className="text-black sm:w-4 sm:h-4"
                            >
                              <path
                                d="M12 12C14.21 12 16 10.21 16 8C16 5.79 14.21 4 12 4C9.79 4 8 5.79 8 8C8 10.21 9.79 12 12 12ZM12 14C9.33 14 4 15.34 4 18V20H20V18C20 15.34 14.67 14 12 14Z"
                                fill="currentColor"
                              />
                            </svg>
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-gray-200 p-4 bg-white bg-opacity-90 backdrop-blur-sm sm:p-3">
                <div className="flex items-center space-x-2">
                  <div className="flex-1 relative">
                    <textarea
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={handleKeyPress}
                      placeholder="Type here..."
                      className="w-full text-black px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-black resize-none max-h-20 sm:px-3 sm:py-1.5 sm:text-sm"
                      rows={1}
                      style={{ minHeight: "40px" }}
                    />
                  </div>
                  <motion.button
                    onClick={handleSendMessage}
                    disabled={!inputValue.trim()}
                    className={`w-10 h-10 rounded-full flex items-center justify-center sm:w-9 sm:h-9 ${
                      inputValue.trim()
                        ? "bg-black text-white hover:opacity-90"
                        : "bg-gray-300 text-gray-500 cursor-not-allowed"
                    } transition-colors`}
                    whileHover={inputValue.trim() ? { scale: 1.05 } : {}}
                    whileTap={inputValue.trim() ? { scale: 0.95 } : {}}
                    aria-label="Send message"
                  >
                    <svg
                      width="20"
                      height="20"
                      viewBox="0 0 24 24"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      className="text-current sm:w-5 sm:h-5"
                    >
                      <path
                        d="M2.01 21L23 12L2.01 3L2 10L17 12L2 14L2.01 21Z"
                        fill="currentColor"
                      />
                    </svg>
                  </motion.button>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default FloatingChatbot;
