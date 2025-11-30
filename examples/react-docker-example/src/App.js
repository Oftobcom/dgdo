import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to React in Docker!</h1>
        <h2>Greetings from Rahmatjon I. Hakimov! Test</h2>
        <p>
          This is a simple React application running inside a Docker container.
        </p>
        <div className="features">
          <h2>Features:</h2>
          <ul>
            <li>✅ React 18</li>
            <li>✅ Docker containerization</li>
            <li>✅ Hot reloading</li>
            <li>✅ Proper folder structure</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;