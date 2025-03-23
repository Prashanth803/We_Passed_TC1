// components/Chat/ChatForm.jsx
import React, { useState, useRef } from 'react';
import './ChatForm.css';

function ChatForm() {
  const [messages, setMessages] = useState([]);
  const [results, setResults] = useState({
    'Read Code': '',
    'Generate BDD': '',
    'Start Testing': '',
    'Show Results': '',
  });
  const [step, setStep] = useState(0);
  const [formVisible, setFormVisible] = useState(true);

  const steps = ['Read Code', 'Generate BDD', 'Start Testing', 'Show Results'];

  // Using useRef to store input values
  const contextRef = useRef('');
  const apiRef = useRef('');
  const githubLinkRef = useRef('');
  const testingCriteriaRef = useRef('');

  const handleChange = (e) => {
    switch (e.target.name) {
      case 'context':
        contextRef.current = e.target.value;
        break;
      case 'api':
        apiRef.current = e.target.value;
        break;
      case 'githubLink':
        githubLinkRef.current = e.target.value;
        break;
      case 'testingCriteria':
        testingCriteriaRef.current = e.target.value;
        break;
      default:
        break;
    }
  };

  const handleButtonClick = async (action) => {
    let requestData = {};

    switch (action) {
      case 'Read Code':
        requestData = {
          githubLink: githubLinkRef.current,
        };
        break;
      case 'Generate BDD':
        requestData = {
          context: contextRef.current,
        };
        break;
      case 'Start Testing':
        requestData = {
          api: apiRef.current,
        };
        break;
      case 'Show Results':
        requestData = {};
        break;
      default:
        requestData = {};
    }

    try {

      
      const response = await fetch(`http://127.0.0.1:5000/github`, {
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
      const aiResponse = responseData.result || `API response for ${action}: ${JSON.stringify(responseData)}`;
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
            defaultValue={contextRef.current}
            onChange={handleChange}
            placeholder="Context"
            className="chat-input"
          />
          <input
            type="text"
            name="api"
            defaultValue={apiRef.current}
            onChange={handleChange}
            placeholder="Deploy Link"
            className="chat-input"
          />
          <input
            type="text"
            name="githubLink"
            defaultValue={githubLinkRef.current}
            onChange={handleChange}
            placeholder="GitHub Link"
            className="chat-input"
          />
          <textarea
            name="testingCriteria"
            defaultValue={testingCriteriaRef.current}
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