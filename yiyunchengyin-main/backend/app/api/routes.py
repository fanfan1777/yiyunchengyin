import os
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Body
from fastapi.responses import JSONResponse
from typing import Optional
from app.models.schemas import (
    UserInput, InputType, ClarificationResponse, APIResponse, 
    SessionStatus
)
from app.services.session_manager import session_manager
from app.services.ai_service import ai_service
from app.services.coze_music_service import coze_music_service
from app.models.models import User
from app.models.db import SessionLocal
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from passlib.hash import bcrypt
from sqlalchemy.orm import Session

router = APIRouter()

# 配置文件上传限制
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}

@router.post("/analyze/text")
async def analyze_text(
    text_content: str = Form(...),
    session_id: Optional[str] = Form(None)
):
    """分析文本输入"""
    try:
        # 创建用户输入对象
        user_input = UserInput(
            session_id=session_id,
            input_type=InputType.TEXT,
            text_content=text_content
        )
        
        # 创建或获取会话
        if not session_id:
            session_id = session_manager.create_session(user_input)
        else:
            session = session_manager.get_session(session_id)
            if not session:
                return JSONResponse(
                    status_code=404,
                    content=APIResponse(
                        success=False,
                        message="会话不存在",
                        session_id=session_id
                    ).dict()
                )
        
        # 调用AI服务分析
        ai_analysis = ai_service.analyze_input(user_input)
        
        # 更新会话
        session_manager.update_ai_analysis(session_id, ai_analysis)
        
        # 构建响应
        response_data = {
            "understanding": ai_analysis.understanding,
            "music_elements": ai_analysis.music_elements,
            "needs_clarification": ai_analysis.needs_clarification
        }
        
        if ai_analysis.needs_clarification and ai_analysis.clarification_questions:
            response_data["clarification_questions"] = [
                {
                    "question_id": q.question_id,
                    "question": q.question,
                    "options": q.options
                }
                for q in ai_analysis.clarification_questions
            ]
        
        return JSONResponse(content=APIResponse(
            success=True,
            message="文本分析完成",
            data=response_data,
            session_id=session_id
        ).dict())
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                success=False,
                message=f"文本分析失败: {str(e)}",
                session_id=session_id
            ).dict()
        )

@router.post("/analyze/image")
async def analyze_image(
    image: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    """分析图片输入（内存处理，不落地）"""
    try:
        # 验证文件类型和大小
        if not image.filename:
            raise HTTPException(status_code=400, detail="未提供文件名")
        
        file_extension = os.path.splitext(image.filename)[1].lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"不支持的文件类型。支持的类型: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # 检查文件大小并读取内容
        content = await image.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件过大。最大允许大小: {MAX_FILE_SIZE/1024/1024}MB"
            )
        
        # 创建用户输入对象（不再写入磁盘）
        user_input = UserInput(
            session_id=session_id,
            input_type=InputType.IMAGE,
            image_filename=None
        )
        
        # 创建或获取会话
        if not session_id:
            session_id = session_manager.create_session(user_input)
        else:
            session = session_manager.get_session(session_id)
            if not session:
                return JSONResponse(
                    status_code=404,
                    content=APIResponse(
                        success=False,
                        message="会话不存在",
                        session_id=session_id
                    ).dict()
                )
        
        # 调用AI服务分析（使用内存字节流）
        ai_analysis = ai_service.analyze_input(user_input, image_bytes=content)
        
        # 更新会话
        session_manager.update_ai_analysis(session_id, ai_analysis)
        
        # 构建响应
        response_data = {
            "understanding": ai_analysis.understanding,
            "music_elements": ai_analysis.music_elements,
            "needs_clarification": ai_analysis.needs_clarification
        }
        
        if ai_analysis.needs_clarification and ai_analysis.clarification_questions:
            response_data["clarification_questions"] = [
                {
                    "question_id": q.question_id,
                    "question": q.question,
                    "options": q.options
                }
                for q in ai_analysis.clarification_questions
            ]
        
        return JSONResponse(content=APIResponse(
            success=True,
            message="图片分析完成",
            data=response_data,
            session_id=session_id
        ).dict())
        
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                success=False,
                message=f"图片分析失败: {str(e)}",
                session_id=session_id
            ).dict()
        )

@router.post("/clarify")
async def submit_clarification(clarification: ClarificationResponse):
    """提交澄清回答"""
    try:
        # 获取会话
        session = session_manager.get_session(clarification.session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content=APIResponse(
                    success=False,
                    message="会话不存在",
                    session_id=clarification.session_id
                ).dict()
            )
        
        # 添加澄清回答
        session_manager.add_clarification_response(clarification.session_id, clarification)
        
        # 检查是否还需要更多澄清
        updated_session = session_manager.get_session(clarification.session_id)
        if (updated_session.ai_analysis and 
            updated_session.ai_analysis.clarification_questions and
            len(updated_session.clarification_history) < len(updated_session.ai_analysis.clarification_questions)):
            
            # 还有未回答的问题
            remaining_questions = updated_session.ai_analysis.clarification_questions[len(updated_session.clarification_history):]
            return JSONResponse(content=APIResponse(
                success=True,
                message="澄清回答已收到，请继续回答剩余问题",
                data={
                    "needs_more_clarification": True,
                    "remaining_questions": [
                        {
                            "question_id": q.question_id,
                            "question": q.question,
                            "options": q.options
                        }
                        for q in remaining_questions
                    ]
                },
                session_id=clarification.session_id
            ).dict())
        
        # 所有问题都已回答，生成最终音乐提示词
        session_data = {
            "original_input": updated_session.original_input.dict(),
            "ai_analysis": updated_session.ai_analysis.dict() if updated_session.ai_analysis else {},
            "clarification_history": [resp.dict() for resp in updated_session.clarification_history]
        }
        
        final_prompt = ai_service.generate_final_prompt(session_data)
        session_manager.set_final_prompt(clarification.session_id, final_prompt)
        
        return JSONResponse(content=APIResponse(
            success=True,
            message="澄清完成，音乐提示词已生成",
            data={
                "needs_more_clarification": False,
                "final_prompt": final_prompt.dict(),
                "ready_for_generation": True
            },
            session_id=clarification.session_id
        ).dict())
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                success=False,
                message=f"澄清处理失败: {str(e)}",
                session_id=clarification.session_id
            ).dict()
        )

@router.post("/generate/{session_id}")
async def generate_music(session_id: str, request: Optional[dict] = None):
    """生成音乐"""
    try:
        # 获取会话
        session = session_manager.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content=APIResponse(
                    success=False,
                    message="会话不存在",
                    session_id=session_id
                ).dict()
            )
        
        # 如果有用户参数，使用用户参数生成提示词；否则使用现有的final_prompt
        if request:
            print(f"🎯 接收到用户音乐参数: {request}")
            
            # 将用户参数保存到session中，并重新生成final_prompt
            session_data = {
                'original_input': session.original_input.__dict__ if session.original_input else {},
                'ai_analysis': session.ai_analysis.__dict__ if session.ai_analysis else {},
                'clarification_history': session.clarification_history,
                'user_music_params': request  # 新增用户参数
            }
            
            # 使用AI服务重新生成音乐提示词，结合用户参数
            session.final_prompt = ai_service.generate_final_prompt_with_user_params(session_data, request)
            print(f"🎵 根据用户参数重新生成提示词: {session.final_prompt}")
        
        elif not session.final_prompt:
            return JSONResponse(
                status_code=400,
                content=APIResponse(
                    success=False,
                    message="未找到音乐生成提示词，请先完成澄清流程或提供音乐参数",
                    session_id=session_id
                ).dict()
            )
        
        # 更新状态为生成中
        session_manager.update_session_status(session_id, SessionStatus.GENERATING)
        
        # 调用Coze音乐生成API
        print(f"开始为会话 {session_id} 生成音乐")
        success, result, lyrics = coze_music_service.generate_music(session.final_prompt)
        
        if not success:
            # 音乐生成失败
            session_manager.set_error_status(session_id)
            
            # 分析错误类型并提供友好的错误信息
            error_message = result
            if "参数输入错误" in result:
                error_message = "音乐生成参数不正确，请尝试调整音乐风格或主题设置"
            elif "702323005" in result:
                error_message = "音乐生成服务参数错误，建议重新选择音乐风格和乐器组合"
            elif "插件执行失败" in result:
                error_message = "音乐生成插件调用失败，请稍后重试或联系管理员"
            elif "未返回音乐链接" in result:
                error_message = "音乐生成完成但未获取到下载链接，请重新生成"
            
            return JSONResponse(
                status_code=500,
                content=APIResponse(
                    success=False,
                    message=f"音乐生成失败: {error_message}",
                    data={
                        "error_detail": result,
                        "suggestions": [
                            "尝试选择不同的音乐风格组合",
                            "检查输入的文字描述是否过长或包含特殊字符", 
                            "稍后重新尝试生成",
                            "如果问题持续，请联系技术支持"
                        ]
                    },
                    session_id=session_id
                ).dict()
            )
        
        # 音乐生成成功
        music_url = result
        print(f"音乐生成成功: {music_url}")
        
        # 更新会话
        session_manager.set_generated_music(session_id, music_url)
        
        # 构建响应数据
        response_data = {
            "music_url": music_url,
            "music_prompt": session.final_prompt.dict(),
            "generation_completed": True
        }
        
        # 如果有歌词，添加到响应中
        if lyrics:
            response_data["lyrics"] = lyrics
            print(f"包含歌词: {lyrics[:100]}...")
        
        return JSONResponse(content=APIResponse(
            success=True,
            message="音乐生成完成",
            data=response_data,
            session_id=session_id
        ).dict())
        
    except Exception as e:
        session_manager.set_error_status(session_id)
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                success=False,
                message=f"音乐生成失败: {str(e)}",
                session_id=session_id
            ).dict()
        )

@router.get("/session/{session_id}")
async def get_session_status(session_id: str):
    """获取会话状态"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            return JSONResponse(
                status_code=404,
                content=APIResponse(
                    success=False,
                    message="会话不存在",
                    session_id=session_id
                ).dict()
            )
        
        return JSONResponse(content=APIResponse(
            success=True,
            message="会话状态获取成功",
            data={
                "session": session.dict()
            },
            session_id=session_id
        ).dict())
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                success=False,
                message=f"获取会话状态失败: {str(e)}",
                session_id=session_id
            ).dict()
        )

@router.get("/sessions")
async def list_sessions():
    """列出所有会话（用于调试）"""
    try:
        sessions = {
            session_id: session.dict() 
            for session_id, session in session_manager.sessions.items()
        }
        
        return JSONResponse(content=APIResponse(
            success=True,
            message="会话列表获取成功",
            data={"sessions": sessions}
        ).dict())
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content=APIResponse(
                success=False,
                message=f"获取会话列表失败: {str(e)}"
            ).dict()
        )

@router.post("/register")
def register(user: dict = Body(...)):
    db: Session = SessionLocal()
    try:
        if db.query(User).filter(User.username == user['username']).first():
            raise HTTPException(status_code=400, detail="用户名已存在")
        password = user['password'][:72]  # 截断密码为72字节
        new_user = User(
            username=user['username'],
            email=user['email'],
            hashed_password=bcrypt.hash(password)
        )
        db.add(new_user)
        db.commit()
        return {"success": True, "message": "注册成功"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
    finally:
        db.close()

@router.post("/login")
def login(user: dict = Body(...)):
    db: Session = SessionLocal()
    db_user = db.query(User).filter(User.username == user['username']).first()
    db.close()
    if not db_user or not bcrypt.verify(user['password'], db_user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    return {"success": True, "message": "登录成功"}
