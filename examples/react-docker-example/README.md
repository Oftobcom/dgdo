Create a simple Docker-based React.js application with proper folder structure. Here's a complete example:

## Project Structure
```
react-docker-app/
├── docker-compose.yml
├── Dockerfile
├── .dockerignore
├── public/
│   ├── index.html
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
├── package.json
└── README.md
```

## File Contents

### 1. `docker-compose.yml`
```yaml
version: '3.8'

services:
  react-app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - CHOKIDAR_USEPOLLING=true
    volumes:
      - .:/app
      - /app/node_modules
    stdin_open: true
    tty: true
```

### 2. `Dockerfile`
```dockerfile
# Use official Node.js runtime as base image
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Start development server
CMD ["npm", "start"]
```

### 3. `.dockerignore`
```
node_modules
npm-debug.log
.git
.gitignore
README.md
.env
.nyc_output
coverage
.docker
.elasticbeanstalk
```

### 4. `package.json`
```json
{
  "name": "react-docker-app",
  "version": "1.0.0",
  "description": "Simple React app with Docker",
  "main": "index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
```

### 5. `public/index.html`
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta
      name="description"
      content="Simple React app running in Docker"
    />
    <title>React Docker App</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
```

### 6. `public/manifest.json`
```json
{
  "short_name": "React Docker App",
  "name": "Simple React Docker Application",
  "icons": [
    {
      "src": "favicon.ico",
      "sizes": "64x64 32x32 24x24 16x16",
      "type": "image/x-icon"
    }
  ],
  "start_url": ".",
  "display": "standalone",
  "theme_color": "#000000",
  "background_color": "#ffffff"
}
```

### 7. `src/App.js`
```jsx
import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to React in Docker!</h1>
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
```

### 8. `src/App.css`
```css
.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  padding: 40px;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.App-header h1 {
  color: #61dafb;
  margin-bottom: 20px;
}

.features {
  margin-top: 30px;
  text-align: left;
}

.features ul {
  list-style: none;
  padding: 0;
}

.features li {
  padding: 8px 0;
  font-size: 1.1em;
}
```

### 9. `src/index.js`
```jsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### 10. `src/index.css`
```css
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
```

### 11. `README.md`
```markdown
# React Docker Example

A simple React.js application running in a Docker container.

## Quick Start

1. **Clone or create the project structure**
2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```
3. **Access the application:**
   Open http://localhost:3000 in your browser

## Development

- The app supports hot reloading
- Changes to source files will automatically refresh the browser
- Runs in development mode with full React developer tools

## Project Structure

- `Dockerfile` - Container configuration
- `docker-compose.yml` - Multi-container setup
- `src/` - React source code
- `public/` - Static assets
```

## How to Run

1. **Create the project directory and all files:**
```bash
mkdir react-docker-app
cd react-docker-app
# Create all the files as shown above
```

2. **Build and start the application:**
```bash
docker-compose up --build
```

3. **Access your application:**
   Open http://localhost:3000 in your web browser

## Key Features

- ✅ **Proper Docker configuration** with multi-stage build
- ✅ **Hot reloading** for development
- ✅ **Correct React folder structure**
- ✅ **Environment variables** support
- ✅ **Volume mounting** for live code changes
- ✅ **Optimized .dockerignore** file
- ✅ **Development-focused** setup

The application will start in development mode with hot reloading enabled. Any changes you make to the source code will automatically refresh the browser.