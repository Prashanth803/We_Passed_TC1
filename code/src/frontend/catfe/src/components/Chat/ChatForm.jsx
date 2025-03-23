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

  const handleButtonClick = (action) => {
    const userMessage = `Action: ${action}\nContext: ${formData.context}\nAPI: ${formData.api}\nGitHub Link: ${formData.githubLink}\nTesting Criteria: ${formData.testingCriteria}`;
    setMessages([...messages, { text: userMessage, sender: 'user' }]);

    // Simulate AI response (replace with actual AI API call)
    setTimeout(() => {
      const aiResponse = `AI response for ${action}: ${userMessage}`;
      setMessages((prevMessages) => [
        ...prevMessages,
        { text: aiResponse, sender: 'ai' },
      ]);
      setResults({ ...results, [action]: aiResponse });
      setStep(steps.indexOf(action) + 1);
      setFormVisible(false);
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