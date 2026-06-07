

https://github.com/user-attachments/assets/f0407639-2abb-4e6a-9c3b-ce8079b2d386






# PixAI

PixAI is an AI-powered image assistant that helps users interact with their photos in a conversational way.

Users can:

* Generate caption suggestions
* Receive image editing recommendations
* Apply image enhancements
* Generate alternate image styles (Black & White, Pencil Sketch, Cartoon, Ghibli-style, etc.)
* Chat naturally about uploaded images

---

## Architecture

```text
React Frontend
      │
      ▼
Spring Boot WebFlux API
      │
      ▼
Python MCP Server
      │
      ▼
Gemini API
```

---

## Tech Stack

### Frontend

* React
* TypeScript
* Vite
* React Query
* Tailwind CSS

### Backend

* Kotlin
* Spring Boot WebFlux
* Reactive MongoDB
* OpenAPI / Swagger

### AI Layer

* Python
* FastAPI
* MCP Server
* Gemini

### Database

* MongoDB

---

## Local Development

### Backend

```bash
cd backend/pixai-api
./gradlew bootRun
```

Backend runs on:

```text
http://localhost:8081
```

Swagger:

```text
http://localhost:8081/swagger-ui/index.html
```

---

## Build

```bash
cd backend/pixai-api
./gradlew clean build
```

---

## Current Status

### Completed

* Spring Boot setup
* WebFlux
* MongoDB connectivity
* OpenAPI integration
* Global exception handling
* Health endpoint

### In Progress

* Conversation domain
* Persistence layer
* MCP integration
* Image upload workflow
