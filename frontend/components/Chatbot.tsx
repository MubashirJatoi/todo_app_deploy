// 'use client';

// import { useState, useRef, useEffect } from 'react';
// import { useSession } from 'next-auth/react';
// import { sendChatMessage } from '@/lib/api';

// interface Message {
//   id: string;
//   content: string;
//   role: 'user' | 'assistant';
//   timestamp: Date;
// }

// export default function Chatbot() {
//   const [messages, setMessages] = useState<Message[]>([]);
//   const [inputValue, setInputValue] = useState('');
//   const [isLoading, setIsLoading] = useState(false);
//   const messagesEndRef = useRef<null | HTMLDivElement>(null);
//   const { data: session } = useSession();

//   const scrollToBottom = () => {
//     messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   };

//   useEffect(() => {
//     scrollToBottom();
//   }, [messages]);

//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
//     if (!inputValue.trim() || !session?.accessToken || isLoading) return;

//     const userMessage: Message = {
//       id: Date.now().toString(),
//       content: inputValue,
//       role: 'user',
//       timestamp: new Date(),
//     };

//     setMessages(prev => [...prev, userMessage]);
//     setInputValue('');
//     setIsLoading(true);

//     try {
//       // Send message to AI chatbot backend
//       const response = await sendChatMessage(inputValue, session.accessToken);

//       const assistantMessage: Message = {
//         id: (Date.now() + 1).toString(),
//         content: response.message || response.reply || 'I processed your request.',
//         role: 'assistant',
//         timestamp: new Date(),
//       };

//       setMessages(prev => [...prev, assistantMessage]);
//     } catch (error) {
//       console.error('Error sending message:', error);

//       const errorMessage: Message = {
//         id: (Date.now() + 1).toString(),
//         content: 'Sorry, I encountered an error processing your request. Please try again.',
//         role: 'assistant',
//         timestamp: new Date(),
//       };

//       setMessages(prev => [...prev, errorMessage]);
//     } finally {
//       setIsLoading(false);
//     }
//   };

//   return (
//     <div className="flex flex-col h-full max-w-4xl mx-auto bg-white rounded-lg shadow-md border border-gray-200">
//       <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
//         <h2 className="text-xl font-semibold text-gray-800">AI Todo Assistant</h2>
//         <p className="text-sm text-gray-600">Ask me to manage your tasks with natural language</p>
//       </div>

//       <div className="flex-1 overflow-y-auto p-4 space-y-4 max-h-96">
//         {messages.length === 0 ? (
//           <div className="text-center py-8 text-gray-500">
//             <p>Hello! I'm your AI Todo Assistant.</p>
//             <p className="mt-2 text-sm">Try commands like:</p>
//             <ul className="mt-2 text-xs text-left list-disc list-inside space-y-1">
//               <li>Add a task to buy groceries</li>
//               <li>Mark my meeting prep task as complete</li>
//               <li>Show me urgent tasks</li>
//               <li>Delete the shopping task</li>
//             </ul>
//           </div>
//         ) : (
//           messages.map((message) => (
//             <div
//               key={message.id}
//               className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
//             >
//               <div
//                 className={`max-w-[80%] rounded-lg px-4 py-2 ${
//                   message.role === 'user'
//                     ? 'bg-blue-500 text-white rounded-br-none'
//                     : 'bg-gray-200 text-gray-800 rounded-bl-none'
//                 }`}
//               >
//                 <div className="whitespace-pre-wrap">{message.content}</div>
//                 <div
//                   className={`text-xs mt-1 ${
//                     message.role === 'user' ? 'text-blue-100' : 'text-gray-500'
//                   }`}
//                 >
//                   {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
//                 </div>
//               </div>
//             </div>
//           ))
//         )}
//         {isLoading && (
//           <div className="flex justify-start">
//             <div className="bg-gray-200 text-gray-800 rounded-lg rounded-bl-none px-4 py-2">
//               <div className="flex space-x-2">
//                 <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
//                 <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
//                 <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
//               </div>
//             </div>
//           </div>
//         )}
//         <div ref={messagesEndRef} />
//       </div>

//       <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
//         <div className="flex space-x-2">
//           <input
//             type="text"
//             value={inputValue}
//             onChange={(e) => setInputValue(e.target.value)}
//             placeholder="Ask me to manage your tasks..."
//             disabled={!session || isLoading}
//             className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
//           />
//           <button
//             type="submit"
//             disabled={!inputValue.trim() || !session || isLoading}
//             className="bg-blue-500 hover:bg-blue-600 text-white rounded-lg px-4 py-2 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed"
//           >
//             Send
//           </button>
//         </div>
//         {!session && (
//           <p className="mt-2 text-sm text-red-500">
//             Please log in to use the AI Todo Assistant
//           </p>
//         )}
//       </form>
//     </div>
//   );
// }