from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum

class InputType(str, Enum):
    TEXT = "text"
    IMAGE = "image"

class SessionStatus(str, Enum):
    INITIAL = "initial"
    CLARIFYING = "clarifying"
    GENERATING = "generating"
    COMPLETED = "completed"
    ERROR = "error"

class UserInput(BaseModel):
    session_id: Optional[str] = None
    input_type: InputType
    text_content: Optional[str] = None
    image_filename: Optional[str] = None

class ClarificationQuestion(BaseModel):
    question: str
    options: List[str]
    question_id: str

class ClarificationResponse(BaseModel):
    session_id: str
    question_id: str
    selected_option: str

class AIAnalysis(BaseModel):
    understanding: str
    music_elements: Dict[str, Any]
    needs_clarification: bool
    clarification_questions: Optional[List[ClarificationQuestion]] = None

class MusicPrompt(BaseModel):
    interface: str  # 接口类型: gen_bgm, gen_song, lyrics_gen_song
    duration: int = 30
    
    # gen_bgm 参数
    mood: Optional[List[str]] = None  # gen_bgm 使用数组
    text: Optional[str] = None
    genre: Optional[List[str]] = None  # gen_bgm 使用数组
    theme: Optional[List[str]] = None
    instrument: Optional[List[str]] = None
    
    # gen_song 参数 (同时适用于 lyrics_gen_song)
    mood_single: Optional[str] = None  # gen_song 使用字符串
    genre_single: Optional[str] = None  # gen_song 使用字符串
    timbre: Optional[str] = None
    gender: Optional[str] = None
    prompt: Optional[str] = None  # gen_song 使用
    lyrics: Optional[str] = None  # lyrics_gen_song 使用
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "interface": "gen_bgm",
                "mood": ["happy", "bright"],
                "text": "关于星空的背景纯音乐",
                "genre": ["ambient"],
                "theme": ["meditation"],
                "duration": 30,
                "instrument": ["piano"]
            }
        }
    )

class Session(BaseModel):
    session_id: str
    status: SessionStatus
    original_input: UserInput
    ai_analysis: Optional[AIAnalysis] = None
    clarification_history: List[ClarificationResponse] = []
    final_prompt: Optional[MusicPrompt] = None
    generated_music_url: Optional[str] = None
    created_at: str
    updated_at: str

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None
