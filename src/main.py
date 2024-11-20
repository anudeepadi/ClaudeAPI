from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uvicorn

from claudesync.configmanager import InMemoryConfigManager
from claudesync.providers.claude_ai import ClaudeAIProvider
from claudesync.exceptions import ProviderError, ConfigurationError

app = FastAPI(title="ClaudeSync API")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic models for request/response
class LoginRequest(BaseModel):
    session_key: str
    expires: str

class LoginResponse(BaseModel):
    message: str
    expires: datetime

class Organization(BaseModel):
    id: str
    name: str

class Project(BaseModel):
    id: str
    name: str
    archived_at: Optional[str] = None

class ProjectCreate(BaseModel):
    name: str
    description: str = ""

class ChatMessage(BaseModel):
    prompt: str
    timezone: str = "UTC"

class ChatCreate(BaseModel):
    chat_name: str = ""
    project_uuid: Optional[str] = None

# Global config and provider instances
config = InMemoryConfigManager()
provider = None

def get_provider():
    if not provider:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return provider

@app.post("/auth/login", response_model=LoginResponse)
async def login(login_data: LoginRequest):
    global provider
    try:
        config.set("claude_api_url", "https://api.claude.ai/api")
        provider = ClaudeAIProvider(config)
        
        # Parse the expiry date
        expiry = datetime.strptime(login_data.expires, "%a, %d %b %Y %H:%M:%S %Z")
        
        # Store session key
        config.set_session_key("claude.ai", login_data.session_key, expiry)
        
        return LoginResponse(
            message="Successfully authenticated with claude.ai",
            expires=expiry
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/organizations", response_model=List[Organization])
async def get_organizations(provider: ClaudeAIProvider = Depends(get_provider)):
    try:
        orgs = provider.get_organizations()
        return orgs
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/organizations/{org_id}/projects", response_model=List[Project])
async def get_projects(
    org_id: str,
    include_archived: bool = False,
    provider: ClaudeAIProvider = Depends(get_provider)
):
    try:
        projects = provider.get_projects(org_id, include_archived)
        return projects
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/organizations/{org_id}/projects")
async def create_project(
    org_id: str,
    project_data: ProjectCreate,
    provider: ClaudeAIProvider = Depends(get_provider)
):
    try:
        project = provider.create_project(
            org_id,
            project_data.name,
            project_data.description
        )
        return project
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/organizations/{org_id}/chats")
async def create_chat(
    org_id: str,
    chat_data: ChatCreate,
    provider: ClaudeAIProvider = Depends(get_provider)
):
    try:
        chat = provider.create_chat(
            org_id,
            chat_data.chat_name,
            chat_data.project_uuid
        )
        return chat
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/organizations/{org_id}/chats")
async def get_chats(
    org_id: str,
    provider: ClaudeAIProvider = Depends(get_provider)
):
    try:
        chats = provider.get_chat_conversations(org_id)
        return chats
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/organizations/{org_id}/chats/{chat_id}")
async def get_chat(
    org_id: str,
    chat_id: str,
    provider: ClaudeAIProvider = Depends(get_provider)
):
    try:
        chat = provider.get_chat_conversation(org_id, chat_id)
        return chat
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/organizations/{org_id}/chats/{chat_id}/messages")
async def send_message(
    org_id: str,
    chat_id: str,
    message: ChatMessage,
    provider: ClaudeAIProvider = Depends(get_provider)
):
    try:
        # Create StreamingResponse for the message stream
        async def message_stream():
            for event in provider.send_message(org_id, chat_id, message.prompt, message.timezone):
                yield f"data: {json.dumps(event)}\n\n"
                
        return StreamingResponse(
            message_stream(),
            media_type="text/event-stream"
        )
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/organizations/{org_id}/chats")
async def delete_chats(
    org_id: str,
    chat_ids: List[str],
    provider: ClaudeAIProvider = Depends(get_provider)
):
    try:
        result = provider.delete_chat(org_id, chat_ids)
        return result
    except ProviderError as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)