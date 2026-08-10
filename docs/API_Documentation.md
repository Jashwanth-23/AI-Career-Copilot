# API Documentation

## Overview
This document will detail the RESTful API endpoints exposed by the FastAPI backend for the AI Career Copilot platform.

## Planned Modules
1. **Authentication Endpoints (`/api/v1/auth`)**
   - User Registration (`POST /register`)
   - User Login (`POST /login`)
   - Refresh Token (`POST /refresh`)
2. **User Profile (`/api/v1/user`)**
   - Get Profile (`GET /me`)
   - Update Profile (`PUT /me`)
3. **Resume Services (`/api/v1/resume`)**
   - Upload & Parse Resume (`POST /upload`)
   - Analyze & Score Resume (`POST /analyze`)
4. **Interview Preparation (`/api/v1/interview`)**
   - Generate Interview Questions (`POST /generate-questions`)
   - Evaluate Responses (`POST /evaluate`)
5. **Career Roadmap (`/api/v1/roadmap`)**
   - Generate Career Plan (`POST /generate-roadmap`)
6. **AI Chatbot (`/api/v1/chatbot`)**
   - Send Message (`POST /message`)
