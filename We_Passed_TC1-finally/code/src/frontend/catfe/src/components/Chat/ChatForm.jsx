import React, { useState, useRef } from 'react';
import './ChatForm.css';
import axios from 'axios';
import TestResultsTable from './TestResultsTable';
import ReactJson from 'react-json-view';

function ChatForm() {
  const [messages, setMessages] = useState([]);
  const [results, setResults] = useState('');
  const [step, setStep] = useState(0);
  const [formVisible, setFormVisible] = useState(true);
  const [isBDDEditable, setIsBDDEditable] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [isTestDone, setIsTestDone] = useState(false);
  const [testResults, setTestResults] = useState([]);
  const [isJson, setIsJson] = useState(false);

  const steps = ['Read Code', 'Generate BDD', 'Start Testing'];

  const contextRef = useRef('');
  const apiRef = useRef('');
  const githubLinkRef = useRef('');
  const bddEditRef = useRef('');

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
      default:
        break;
    }
  };

  const handleButtonClick = async (action) => {
    let requestData = {};
    let hittingAPI = '';

    switch (action) {
      case 'Read Code':
        requestData = { githubLink: githubLinkRef.current };
        hittingAPI = 'http://localhost:5000/github';
        break;
      case 'Generate BDD':
        requestData = { context: contextRef.current };
        hittingAPI = 'http://127.0.0.1:5000/catfe/context';
        break;
      case 'Start Testing':
        requestData = {
          base_url: apiRef.current,
          bdds: bddEditRef.current ? bddEditRef.current.value : results,
        };
        hittingAPI = 'http://127.0.0.1:5000/function';
        break;
      default:
        return;
    }

    try {
      const response = await fetch(hittingAPI, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      const responseData = await response.json();
      let aiResponse = responseData.result || responseData;

      if (typeof aiResponse === 'string' && aiResponse.startsWith('{')) {
        try {
          const parsedResponse = JSON.parse(aiResponse);
          setResults(parsedResponse);
          setIsJson(true);
        } catch (error) {
          setResults(aiResponse);
          setIsJson(false);
        }
      } else if (typeof aiResponse === 'object') {
        setResults(aiResponse);
        setIsJson(true);
      } else {
        setResults(aiResponse);
        setIsJson(false);
      }

      setMessages([...messages, { text: `User request for ${action}.`, sender: 'user' }]);

      if (action === 'Start Testing') {
        setTestResults(responseData);
        setIsTestDone(true);
      }

      setStep(steps.indexOf(action) + 1);
      setFormVisible(false);
    } catch (error) {
      console.error('API Error:', error);
      const errorMessage = `Error processing ${action}: ${error.message}`;
      setMessages([...messages, { text: errorMessage, sender: 'ai' }]);
      setResults(errorMessage);
      setIsJson(false);
    }
  };

  const handleEditToggle = () => {
    setIsEditing(!isEditing);
  };

  return (
    <div className="chat-container">
      <div className="results-section">
        <div className="result-display">
          <h3>Result:</h3>
          <div className="result-content">
            {isJson ? (
              <ReactJson src={results} theme="monokai" collapsed={2} displayDataTypes={false} indentWidth={2} />
            ) : (
              <>
                {isBDDEditable && isEditing ? (
                  <textarea ref={bddEditRef} defaultValue={results} className="editable-bdd" />
                ) : (
                  <pre className="pretty-result">{results}</pre>
                )}
                {isBDDEditable && (
                  <button type="button" onClick={handleEditToggle} className="edit-button">
                    {isEditing ? 'View' : 'Edit'}
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {isTestDone && <TestResultsTable apiResponse={testResults} />}

      <div className="chat-messages">
        <div className="messages-content">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.sender === 'user' ? 'user' : 'ai'}`}>
              {message.text}
            </div>
          ))}
        </div>
      </div>

      {formVisible && (
        <form className="chat-input-form">
          <input type="text" name="context" defaultValue={contextRef.current} onChange={handleChange} placeholder="Context" className="chat-input" />
          <input type="text" name="api" defaultValue={apiRef.current} onChange={handleChange} placeholder="Deploy Link" className="chat-input" />
          <input type="text" name="githubLink" defaultValue={githubLinkRef.current} onChange={handleChange} placeholder="GitHub Link" className="chat-input" />
        </form>
      )}

      <div className="stepper">
        <div className="stepper-line">
          {steps.map((_, index) => (
            <div key={index} className={`step-circle ${index < step ? 'completed' : ''}`} />
          ))}
        </div>
        <div className="stepper-labels">
          {steps.map((action, index) => (
            <button key={index} type="button" className={`step-label ${index < step ? 'completed' : ''}`} onClick={() => handleButtonClick(action)} disabled={index !== step}>
              {action}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

export default ChatForm;
