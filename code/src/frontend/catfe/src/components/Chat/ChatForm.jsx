import React, { useState } from 'react';
import './ChatForm.css';

function ChatForm() {
  const [messages, setMessages] = useState([]);
  const [formData, setFormData] = useState({
    context: '',
    api: '',
    githubLink: '',
    testingCriteria: '',
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const userMessage = `Context: ${formData.context}\nAPI: ${formData.api}\nGitHub Link: ${formData.githubLink}\nTesting Criteria: ${formData.testingCriteria}`;
    setMessages([...messages, { text: userMessage, sender: 'user' }]);

   
    setTimeout(() => {
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: `AI response to: ${userMessage}`, sender: 'ai' },
      ]);
    }, 1000);

    setFormData({
      context: '',
      api: '',
      githubLink: '',
      testingCriteria: '',
    });
  };

  return (
    <div className="chat-container">
      <div className="chat-messages">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`message ${message.sender === 'user' ? 'user' : 'ai'}`}
          >
            {message.text}
          </div>
        ))}
      </div>
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          name="context"
          value={formData.context}
          onChange={handleChange}
          placeholder="Context"
          className="chat-input"
        />
        <input
          type="text"
          name="api"
          value={formData.api}
          onChange={handleChange}
          placeholder="API"
          className="chat-input"
        />
        <input
          type="text"
          name="githubLink"
          value={formData.githubLink}
          onChange={handleChange}
          placeholder="GitHub Link"
          className="chat-input"
        />
        <textarea
          name="testingCriteria"
          value={formData.testingCriteria}
          onChange={handleChange}
          placeholder="Testing Criteria"
          className="chat-input"
        />
        <button type="submit" className="send-button">
          Generate
        </button>
      </form>
    </div>
  );
}

export default ChatForm;