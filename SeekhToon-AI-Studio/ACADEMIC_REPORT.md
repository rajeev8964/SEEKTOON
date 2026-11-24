# SeekhToon AI Studio – Project Report

## 1. Title
SeekhToon AI Studio: Hindi Cartoon and Story Creation Studio

## 2. Abstract
SeekhToon AI Studio is a creator-focused application concept that brings Hindi story writing, narration, cartoon visuals and video assembly into a guided workflow. The project is intended for Hindi YouTube creators, children's story channels, beginners and small creators with limited budgets. The current starter implementation provides a web dashboard, local Ollama story-generation integration, Piper narration integration, image upload preview, character-description storage and FFmpeg-based slideshow export. AI image generation is an optional provider integration. AI photo editing and consistent character-image generation remain future work.

## 3. Problem Statement
Creators often switch between separate tools for writing, voice-over, images and video editing. This fragmented workflow can increase effort and make it difficult to organize story assets. SeekhToon aims to provide a single guided workspace.

## 4. Objectives
- Provide a simple creator dashboard.
- Generate child-friendly Hindi stories from prompts.
- Convert story text into narration through a text-to-speech engine.
- Upload and preview visual assets.
- Store reusable character descriptions.
- Assemble images into an MP4 slideshow with optional narration.
- Keep API keys private and control third-party service costs.

## 5. Target Users
Hindi YouTube creators, children's story channels, beginners and small creators with limited budgets.

## 6. Proposed Modules
1. Story Generator – topic, age group and moral are sent to Ollama.
2. Voice Studio – sends text to Piper and returns a WAV file.
3. AI Image Generator – optional Hugging Face inference endpoint.
4. AI Photo Editor – planned; upload preview is implemented, AI editing is not.
5. Character Studio – saves character name, description and style in SQLite.
6. Video Generator – uses FFmpeg to create a simple slideshow MP4.

## 7. Technology Stack
Frontend: HTML, CSS and JavaScript. Backend: Python FastAPI. Story model: Ollama with Qwen 2.5 3B. Text-to-speech: Piper. Image inference: optional Hugging Face API. Video: FFmpeg. Local database: SQLite.

## 8. System Architecture
Browser UI → FastAPI REST API → local AI services/provider APIs → generated files and SQLite database. In online deployment, the frontend and backend are hosted separately and the AI services must be reachable through secured endpoints.

## 9. Workflow
Idea/topic → Hindi story → scene planning (future extension) → narration → visual assets → MP4 slideshow export. The current MVP supports story, narration, uploads, character records and slideshow assembly when their dependencies are configured.

## 10. Security and Cost Principles
Store API keys in backend environment variables. Never expose keys in browser JavaScript or public repositories. Check provider quotas and pricing before enabling paid calls. Apply upload size/type restrictions. A public deployment must add authentication, rate limiting, strict CORS, persistent storage and access controls.

## 11. Current Implementation Status
Working in the starter source: FastAPI application, health endpoint, Ollama story route, Piper route (after configuration), upload preview, SQLite character CRUD and FFmpeg slideshow route (after installation). Optional image generation requires provider credentials and a supported model. AI photo editing, character visual consistency, full timeline editing and production deployment hardening are not complete.

## 12. Testing Plan
- Verify `/api/health`.
- Generate a Hindi story after confirming Ollama and the selected model.
- Generate a WAV file after configuring Piper and a Hindi voice.
- Upload valid PNG/JPG/WEBP images and reject unsupported formats.
- Create, list and delete a character.
- Generate an MP4 after installing FFmpeg and uploading image assets.
- Test provider errors and missing configuration messages.
- Verify secrets are not present in frontend files or version control.

## 13. Limitations
Results depend on local hardware, model quality, voice availability, external provider quotas and hosting resources. SQLite and local file storage are for development only. A cloud host cannot automatically access AI services running on a private laptop.

## 14. Future Scope
AI-powered photo editing with masking, consistent character image generation, scene-by-scene storyboard generation, richer video editing, subtitles, project export, user authentication, cloud database and object storage.

## 15. Conclusion
SeekhToon AI Studio provides a foundation for a guided Hindi story-to-cartoon workflow. The MVP combines local AI and open-source media tools while keeping unfinished integrations clearly identified. The next development stages are to validate each module, improve visual generation, complete photo editing, enhance video assembly and harden online deployment.
