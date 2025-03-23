// components/Chat/ChatForm.jsx
import React, { useState, useRef } from 'react';
import './ChatForm.css';

function ChatForm() {
  const [messages, setMessages] = useState([]);
  const [results, setResults] = useState(''); // Common results state
  const [step, setStep] = useState(0);
  const [formVisible, setFormVisible] = useState(true);

  const steps = ['Read Code', 'Generate BDD', 'Start Testing', 'Show Results'];

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
      let hittingAPI = '';
      if (action === 'Read Code') {
        hittingAPI = 'http://127.0.0.1:5000/github';
      } else if (action === 'Generate BDD') {
        hittingAPI = 'http://127.0.0.1:5000/catfe/context';
      } else if (action === 'Start Testing') {
        hittingAPI = 'http://127.0.0.1:5000/catfe/api';
      } else if (action === 'Show Results') {
        hittingAPI = 'http://127.0.0.1:5000/catfe/results';
      }
      const response = await fetch(hittingAPI, {
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
      setResults(aiResponse); // Store the response in the common results state
      setStep(steps.indexOf(action) + 1);
      setFormVisible(false);
    } catch (error) {
      console.error('API Error:', error);
      const errorMessage = `Error processing ${action}: ${error.message}`;
      setMessages([...messages, { text: errorMessage, sender: 'ai' }]);
      setResults(errorMessage); // Store the error in the common results state
    }
  };

  return (
    <div className="chat-container">
      <div className="results-section">
        <div className="result-display">
          <h3>Result:</h3>
          <div className="result-content">
            <p>{results}</p>
          </div>
        </div>
      </div>
      <div className="chat-messages">
        <div className="messages-content">
          {messages.map((message, index) => (
            <div
              key={index}
              className={`message ${message.sender === 'user' ? 'user' : 'ai'}`}
            >
              {message.text}
            </div>
          ))}
        </div>
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