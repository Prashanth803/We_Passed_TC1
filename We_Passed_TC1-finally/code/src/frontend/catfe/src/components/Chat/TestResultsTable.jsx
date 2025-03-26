
import React from "react";
import "./TestResultsTable.css";



export default function TestResultsTable({apiResponse}) {
   console.log("apiResponse: in table ", apiResponse)
 var testResults=[];
 testResults = apiResponse
 
 


 // Ensure testResults is a string
 console.log("testResults: ", testResults)

 


     
  return (
    <div className="container">
      <h2 className="heading">Test Execution Results</h2>
      <table className="test-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Status</th>
            <th>Reason</th>
          </tr>
        </thead>
        <tbody>
          {  
             testResults.map((test, index) => (
            <tr key={index}>
              <td>{index + 1}</td>
              <td>
                <span className={`status-badge ${test.passes ? "pass" : "fail"}`}>
                  {test.passes ? "Pass" : "Fail"}
                </span>
              </td>
              <td>
                {test.reason ? (
                  <details>
                    <summary>View Details</summary>
                    <p>{test.bdd}</p>
                    <p>{      }</p>
                    <p>{test.reason}</p>
                  
                  </details>
                ) : (
                  "No issues detected"
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}


