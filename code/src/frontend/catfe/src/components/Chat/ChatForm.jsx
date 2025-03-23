// components/Chat/ChatForm.jsx
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
  const [results, setResults] = useState({
    'Read Code': '',
    'Generate BDD': '',
    'Start Testing': '',
    'Show Results': '',
  });
  const [step, setStep] = useState(0);
  const [formVisible, setFormVisible] = useState(true);

  const steps = ['Read Code', 'Generate BDD', 'Start Testing', 'Show Results'];

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleButtonClick = async (action) => {
    const requestData = {
      action: action,
      context: formData.context,
      api: formData.api,
      githubLink: formData.githubLink,
      testingCriteria: formData.testingCriteria,
    };

    try {
      const response = await fetch('http://127.0.0.1:5000/', { // Replace with your API endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const responseData = await response.json();
      const aiResponse = responseData.result || `API response for ${action}: ${JSON.stringify(responseData)}`; // Adjust as needed
      setMessages([...messages, { text: `User request for ${action}.`, sender: 'user' }]);
      setMessages([...messages, { text: aiResponse, sender: 'ai' }]);
      setResults({ ...results, [action]: aiResponse });
      setStep(steps.indexOf(action) + 1);
      setFormVisible(false);

    } catch (error) {
      console.error('API Error:', error);
      const errorMessage = `Error processing ${action}: ${error.message}`;
      setMessages([...messages, { text: errorMessage, sender: 'ai' }]);
      setResults({ ...results, [action]: errorMessage });
    }

    setFormData({
      context: '',
      api: '',
      githubLink: '',
      testingCriteria: '',
    });
  };

  return (
    <div className="chat-container">
      <div className="results-section">
        {steps.map((action) => (
          <div key={action} className="result-display">
            <h3>{action} Result:</h3>
            <p>{results[action]}</p>
          </div>
        ))}
      </div>
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
      {formVisible && (
        <form className="chat-input-form">
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
        </form>
      )}
      <div className="stepper">
        <div className="stepper-line">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`step-circle ${index < step ? 'completed' : ''}`}
            />
          ))}
        </div>
        <div className="stepper-labels">
          {steps.map((action, index) => (
            <button
              key={index}
              type="button"
              className={`step-label ${index < step ? 'completed' : ''}`}
              onClick={() => handleButtonClick(action)}
              disabled={index !== step}
            >
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ChatForm;