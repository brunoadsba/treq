# Treq Enterprise - Task List

## Sprint 4: Frontend Integration (Current)
- [x] **Setup & Architecture**
    - [x] Create `frontend/src/features/agent` directory structure
    - [x] Define types for Agent State and Tool Outputs (Typescript)
    - [x] Implement API Service (`agentService.ts`)
    - [x] **Global Rename:** "Sotreq" -> "Treq" (Completed)
- [x] **Agent Chat Component**
    - [x] Implement `UserBubble` and `AgentBubble` components
    - [x] Implement `ChatInput` component
    - [x] Implement `AgentChatContainer` (State Management)
    - [x] Implement `ToolOutputCard` (Visualizing Jira/Slack actions)
    - [x] Integrate with `POST /agent/chat` API
- [x] **Page Integration**
    - [x] Create `/agent` page route
    - [ ] Add navigation menu item for Agent
- [/] **Polish & Validation**
    - [ ] Add loading skeletons/spinners
    - [ ] Handle error states (Rate Limit 429)
    - [//] Manual E2E verification

## Completed Sprints (Legacy History)
- [x] Sprint 1.1: LangGraph Core (Backend)
- [x] Sprint 1.2: RLS Security
- [x] Sprint 2.1: Confluence Connector
- [x] Sprint 2.2: Slack Connector
- [x] Sprint 2.3: Agent Tools
- [x] Sprint 3.1: LangSmith Tracing
- [x] Sprint 3.2: Rate Limiting
- [x] Sprint 3.3: Refactor SSOT
