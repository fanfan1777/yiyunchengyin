import uuid
from datetime import datetime
from typing import Dict, Optional
from app.models.schemas import Session, SessionStatus, UserInput, AIAnalysis, ClarificationResponse, MusicPrompt

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    def create_session(self, user_input: UserInput) -> str:
        """创建新会话"""
        session_id = str(uuid.uuid4())
        current_time = datetime.now().isoformat()
        
        session = Session(
            session_id=session_id,
            status=SessionStatus.INITIAL,
            original_input=user_input,
            created_at=current_time,
            updated_at=current_time
        )
        
        self.sessions[session_id] = session
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """获取会话信息"""
        return self.sessions.get(session_id)
    
    def update_session_status(self, session_id: str, status: SessionStatus) -> bool:
        """更新会话状态"""
        if session_id in self.sessions:
            self.sessions[session_id].status = status
            self.sessions[session_id].updated_at = datetime.now().isoformat()
            return True
        return False
    
    def update_ai_analysis(self, session_id: str, analysis: AIAnalysis) -> bool:
        """更新AI分析结果"""
        if session_id in self.sessions:
            self.sessions[session_id].ai_analysis = analysis
            self.sessions[session_id].updated_at = datetime.now().isoformat()
            if analysis.needs_clarification:
                self.sessions[session_id].status = SessionStatus.CLARIFYING
            return True
        return False
    
    def add_clarification_response(self, session_id: str, response: ClarificationResponse) -> bool:
        """添加澄清回答"""
        if session_id in self.sessions:
            self.sessions[session_id].clarification_history.append(response)
            self.sessions[session_id].updated_at = datetime.now().isoformat()
            return True
        return False
    
    def set_final_prompt(self, session_id: str, prompt: MusicPrompt) -> bool:
        """设置最终音乐提示词"""
        if session_id in self.sessions:
            self.sessions[session_id].final_prompt = prompt
            self.sessions[session_id].status = SessionStatus.GENERATING
            self.sessions[session_id].updated_at = datetime.now().isoformat()
            return True
        return False
    
    def set_generated_music(self, session_id: str, music_url: str) -> bool:
        """设置生成的音乐文件URL"""
        if session_id in self.sessions:
            self.sessions[session_id].generated_music_url = music_url
            self.sessions[session_id].status = SessionStatus.COMPLETED
            self.sessions[session_id].updated_at = datetime.now().isoformat()
            return True
        return False
    
    def set_error_status(self, session_id: str) -> bool:
        """设置错误状态"""
        if session_id in self.sessions:
            self.sessions[session_id].status = SessionStatus.ERROR
            self.sessions[session_id].updated_at = datetime.now().isoformat()
            return True
        return False

# 全局会话管理器实例
session_manager = SessionManager()
