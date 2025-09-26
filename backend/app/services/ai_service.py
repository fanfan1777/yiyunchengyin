import os
import json
import base64
import requests
import re
from typing import List, Dict, Any, Optional
from app.models.schemas import AIAnalysis, ClarificationQuestion, MusicPrompt, UserInput, InputType
from dotenv import load_dotenv

load_dotenv()

class QwenOmniService:
    def __init__(self):
        # 使用标准的DashScope环境变量名称
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise RuntimeError("DASHSCOPE_API_KEY is not set. Please configure it in your environment.")
        # 使用多模态API endpoint，支持qwen-vl-max模型
        self.api_url = os.getenv(
            "DASHSCOPE_API_URL",
            "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
        )
        # 模型名称可配置
        self.model_name = os.getenv("DASHSCOPE_MODEL", "qwen-vl-max")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-SSE": "disable"
        }
        print("初始化QwenOmniService")  # 调试信息
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """将图片编码为base64"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def encode_image_bytes_to_base64(self, image_bytes: bytes) -> str:
        """将图片字节流编码为base64"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def _clean_json_response(self, content: str) -> str:
        """清理AI响应中的markdown格式和多余文本"""
        # 移除markdown代码块标记
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*$', '', content)
        content = re.sub(r'```', '', content)
        
        # 移除开头和结尾的空白
        content = content.strip()
        
        # 尝试找到JSON部分
        # 寻找第一个 { 和最后一个 }
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            content = content[start_idx:end_idx + 1]
        
        return content
    
    def analyze_input(self, user_input: UserInput, image_path: Optional[str] = None, image_bytes: Optional[bytes] = None) -> AIAnalysis:
        """分析用户输入并返回音乐理解"""
        try:
            # 构建提示词
            system_prompt = """你是一个专业的音乐生成助手。你的任务是理解用户的输入（文字描述或图片），并分析出音乐生成所需的元素。

请严格按照以下JSON格式用中文回复，所有内容都必须是中文：

{
  "understanding": "对用户输入的中文理解和解释",
  "music_elements": {
    "style": "音乐风格（用中文，如：流行、摇滚、古典、电子等）",
    "mood": "情绪（用中文，如：愉快、悲伤、激昂、平静等）",
    "instruments": ["主要乐器列表（用中文，如：钢琴、吉他、小提琴等）"],
    "tempo": "节奏（用中文，如：慢、中等、快等）",
    "genre": "音乐类型（用中文）",
    "atmosphere": "氛围描述（用中文）"
  },
  "needs_clarification": true或false,
  "clarification_questions": [
    {
      "question": "澄清问题（中文）",
      "options": ["选项1", "选项2", "选项3", "选项4"],
      "question_id": "问题ID"
    }
  ]
}

重要要求：
1. 所有内容必须用中文
2. 严格按照JSON格式
3. 不要添加任何markdown格式或其他文本
4. 直接返回纯JSON，不要任何解释性文字
"""

            # 构建消息内容
            messages = []
            
            if user_input.input_type == InputType.TEXT:
                user_message = f"请分析这段文字描述并提取音乐元素：{user_input.text_content}"
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
            
            elif user_input.input_type == InputType.IMAGE:
                # 优先使用内存中的图片字节流
                if image_bytes is not None:
                    image_base64 = self.encode_image_bytes_to_base64(image_bytes)
                elif image_path:
                    image_base64 = self.encode_image_to_base64(image_path)
                else:
                    raise Exception("未提供图片数据")
                
                # qwen-vl-max的图片消息格式
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user", 
                        "content": [
                            {"type": "text", "text": "请分析这张图片并提取音乐元素："},
                            {"type": "image", "image": f"data:image/jpeg;base64,{image_base64}"}
                        ]
                    }
                ]
            
            # 调用API - 使用DashScope格式和qwen-vl-max模型
            payload = {
                "model": self.model_name,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 1500,
                    "result_format": "message"
                }
            }
            
            print(f"发送API请求到qwen-vl-max: {payload}")  # 调试信息
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            print(f"API响应状态码: {response.status_code}")  # 调试信息
            
            if response.status_code == 200:
                result = response.json()
                print(f"API响应内容: {result}")  # 调试信息
                
                # DashScope的响应格式解析
                if "output" in result and "choices" in result["output"]:
                    output = result["output"]
                    if len(output["choices"]) > 0:
                        message_content = output["choices"][0]["message"]["content"]
                        
                        # 处理content的不同格式
                        if isinstance(message_content, list):
                            # content是数组格式：[{'text': '...'}]
                            if len(message_content) > 0 and "text" in message_content[0]:
                                content = message_content[0]["text"]
                                print(f"✅ 成功获取AI分析内容(数组格式): {content[:100]}...")  # 调试信息
                            else:
                                print(f"❌ 数组格式解析失败: {message_content}")
                                raise Exception("API响应格式异常：数组内容无效")
                        elif isinstance(message_content, str):
                            # content是字符串格式
                            content = message_content
                            print(f"✅ 成功获取AI分析内容(字符串格式): {content[:100]}...")  # 调试信息
                        else:
                            print(f"❌ 未知的content格式: {type(message_content)}, {message_content}")
                            raise Exception(f"API响应格式异常：未知的content类型")
                    else:
                        print(f"❌ choices数组为空: {result}")
                        raise Exception("API响应格式异常：choices为空")
                elif "text" in result.get("output", {}):
                    content = result["output"]["text"]
                    print(f"✅ 成功获取AI分析内容(text格式): {content[:100]}...")  # 调试信息
                else:
                    print(f"❌ API调用返回错误: {result}")
                    if "message" in result:
                        raise Exception(f"API错误: {result['message']}")
                    else:
                        raise Exception(f"API调用失败: {result}")
                
                # 解析JSON响应
                try:
                    print(f"🔍 尝试解析JSON: {content[:200]}...")
                    
                    # 清理AI响应中的markdown格式
                    cleaned_content = self._clean_json_response(content)
                    print(f"🧹 清理后的内容: {cleaned_content[:200]}...")
                    
                    analysis_data = json.loads(cleaned_content)
                    print(f"✅ JSON解析成功: {analysis_data}")
                    return self._parse_analysis_response(analysis_data, user_input)
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"原始内容: {content[:300]}...")
                    # 如果AI没有返回JSON格式，创建一个基于内容的分析
                    return self._create_analysis_from_text(content, user_input)
            else:
                print(f"❌ HTTP请求失败: {response.status_code} - {response.text}")
                raise Exception(f"HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"AI分析错误: {str(e)}")
            return self._create_fallback_analysis(user_input)
    
    def _parse_analysis_response(self, data: Dict[str, Any], user_input: UserInput) -> AIAnalysis:
        """解析标准JSON响应并生成针对性问题"""
        # 获取AI分析的音乐元素
        music_elements = data.get("music_elements", {})
        understanding = data.get("understanding", "")
        
        # 无论AI是否返回澄清问题，我们都生成自己的2-4个针对性问题
        clarification_questions = self._generate_targeted_questions(user_input, music_elements)
        
        print(f"🎯 为标准JSON响应生成了 {len(clarification_questions)} 个针对性问题")
        
        return AIAnalysis(
            understanding=understanding,
            music_elements=music_elements,
            needs_clarification=True,  # 始终需要澄清，因为我们总是生成问题
            clarification_questions=clarification_questions
        )
    
    def _parse_text_response(self, content: str) -> AIAnalysis:
        """解析文本响应(作为备用方案)"""
        # 简单的文本解析逻辑
        music_elements = {
            "style": "pop",
            "mood": "neutral", 
            "instruments": ["piano", "guitar"],
            "tempo": "medium"
        }
        
        # 创建临时用户输入对象用于生成问题
        temp_input = UserInput(text_content=content[:100])
        clarification_questions = self._generate_targeted_questions(temp_input, music_elements)
        
        return AIAnalysis(
            understanding=content[:200] + "..." if len(content) > 200 else content,
            music_elements=music_elements,
            needs_clarification=True,
            clarification_questions=clarification_questions
        )
    
    def _create_analysis_from_text(self, content: str, user_input: UserInput) -> AIAnalysis:
        """从AI的文本响应中创建分析(当AI没有返回JSON时)"""
        print(f"📝 基于AI文本内容创建分析: {content}")
        
        # 使用AI的文本内容作为理解
        understanding = content[:300] + "..." if len(content) > 300 else content
        
        # 尝试从AI的回复中提取关键信息，然后结合智能分析
        return self._create_smart_analysis(user_input, understanding)
    
    def _create_smart_analysis(self, user_input: UserInput, understanding: str = None) -> AIAnalysis:
        """智能分析用户输入"""
        print(f"🧠 开始智能分析用户输入")
        
        if user_input.input_type == InputType.TEXT and user_input.text_content:
            text = user_input.text_content.lower()
            print(f"📝 分析文本: {text}")
            
            if not understanding:
                understanding = f"基于您的描述「{user_input.text_content}」，我来为您分析音乐需求"
            
            # 更准确的情绪分析
            mood = self._analyze_mood(text)
            style = self._analyze_style(text)
            instruments = self._analyze_instruments(text, mood)
            tempo = self._analyze_tempo(text, mood)
            
            music_elements = {
                "style": style,
                "mood": mood,
                "instruments": instruments,
                "tempo": tempo
            }
            
            print(f"🎵 分析结果: {music_elements}")
            
        else:
            understanding = understanding or "基于您上传的图片，我将为您创作一首音乐作品。"
            music_elements = {
                "style": "氛围音乐",
                "mood": "宁静",
                "instruments": ["钢琴", "弦乐"],
                "tempo": "慢"
            }
        
        # 根据用户输入生成2-4个针对性参数问题
        clarification_questions = self._generate_targeted_questions(user_input, music_elements)
        
        return AIAnalysis(
            understanding=understanding,
            music_elements=music_elements,
            needs_clarification=True,
            clarification_questions=clarification_questions
        )
    
    def _generate_targeted_questions(self, user_input: UserInput, music_elements: Dict[str, Any]) -> List[ClarificationQuestion]:
        """根据用户输入生成2-4个针对性的参数问题"""
        questions = []
        text = user_input.text_content.lower() if user_input.text_content else ""
        
        # 问题1：情感风格（基于AI分析的情绪智能生成）
        mood = music_elements.get("mood", "").lower()
        detected_emotions = self._analyze_detailed_emotions(text, mood)
        mood_options = self._generate_emotion_options(detected_emotions)
            
        questions.append(ClarificationQuestion(
            question="希望音乐表达什么情感？",
            options=mood_options,
            question_id="mood_q1"
        ))
        
        # 问题2：乐器选择（根据音乐类型）
        style = music_elements.get("style", "").lower()
        if "古典" in style or "交响" in style:
            instrument_options = ["钢琴独奏", "小提琴", "大提琴", "交响乐团"]
        elif "电子" in style or "现代" in style:
            instrument_options = ["电子合成", "电子钢琴", "合成器", "电子混合"]
        else:
            instrument_options = ["钢琴独奏", "吉他弹唱", "电子合成", "弦乐组合"]
            
        questions.append(ClarificationQuestion(
            question="偏好什么乐器组合？",
            options=instrument_options,
            question_id="instrument_q1"
        ))
        
        # 问题3：音乐用途（有条件添加）
        if len(questions) < 3:
            questions.append(ClarificationQuestion(
                question="音乐主要用于什么场合？",
                options=["个人聆听", "放松冥想", "工作学习", "情感表达"],
                question_id="purpose_q1"
            ))
        
        # 问题4：节奏偏好（根据情况添加）
        if len(questions) < 4 and not any(word in text for word in ["慢", "快", "节奏"]):
            tempo = music_elements.get("tempo", "")
            if "慢" in tempo:
                tempo_options = ["极慢深沉", "缓慢抒情", "中等节奏", "稍快一些"]
            else:
                tempo_options = ["慢节奏", "中等节奏", "快节奏", "变化节奏"]
                
            questions.append(ClarificationQuestion(
                question="希望音乐的节奏感如何？",
                options=tempo_options,
                question_id="tempo_q1"
            ))
        
        print(f"🎯 生成了 {len(questions)} 个针对性问题")
        return questions
    
    def _analyze_detailed_emotions(self, text: str, analyzed_mood: str) -> Dict[str, float]:
        """分析详细的情感类型和强度"""
        emotions = {}
        
        # 基础情感关键词库
        emotion_keywords = {
            "悲伤": ["悲伤", "难过", "哭", "哭泣", "眼泪", "伤心", "痛苦", "忧郁", "失落", "绝望", "沮丧"],
            "快乐": ["快乐", "开心", "高兴", "欢乐", "兴奋", "激动", "愉快", "欢快", "喜悦", "幸福"],
            "平静": ["平静", "宁静", "安静", "平和", "冷静", "淡然", "祥和", "沉静", "悠然"],
            "愤怒": ["愤怒", "生气", "气愤", "怒火", "暴怒", "恼火", "愤慨", "愤恨", "怒气"],
            "焦虑": ["焦虑", "紧张", "担心", "忧虑", "不安", "着急", "恐慌", "惊慌", "焦急"],
            "浪漫": ["浪漫", "温柔", "甜蜜", "温馨", "柔情", "深情", "爱情", "恋爱", "情深"],
            "怀旧": ["怀念", "思念", "回忆", "往昔", "过去", "怀旧", "追忆", "缅怀", "眷恋"],
            "神秘": ["神秘", "诡异", "阴暗", "黑暗", "恐怖", "诡异", "幽暗", "阴森", "诡谲"],
            "励志": ["励志", "奋斗", "努力", "坚强", "勇敢", "拼搏", "奋进", "向上", "积极"],
            "孤独": ["孤独", "寂寞", "独自", "一个人", "孤单", "孤寂", "独孤", "落寞"]
        }
        
        # 分析用户输入文本
        for emotion, keywords in emotion_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                emotions[emotion] = score
        
        # 结合AI分析的mood
        if analyzed_mood:
            for emotion in emotion_keywords:
                if emotion in analyzed_mood:
                    emotions[emotion] = emotions.get(emotion, 0) + 2  # 加权AI分析结果
        
        # 如果没有检测到明确情感，设置默认值
        if not emotions:
            emotions["平静"] = 1
            
        print(f"🎭 检测到的情感: {emotions}")
        return emotions
    
    def _generate_emotion_options(self, detected_emotions: Dict[str, float]) -> List[str]:
        """基于检测到的情感生成4个相关的情感选项"""
        # 根据主要情感生成相关选项
        emotion_families = {
            "悲伤": ["深度忧郁", "轻柔忧伤", "怀念思念", "平静接受"],
            "快乐": ["欢快活泼", "轻松愉快", "激昂兴奋", "温暖幸福"], 
            "平静": ["平静舒缓", "宁静致远", "淡然自若", "禅意深远"],
            "愤怒": ["激昂澎湃", "愤怒咆哮", "反叛不羁", "燃烧激情"],
            "焦虑": ["紧张不安", "焦虑不定", "内心挣扎", "情绪激荡"],
            "浪漫": ["温柔浪漫", "甜蜜温馨", "深情款款", "柔情似水"],
            "怀旧": ["怀念往昔", "思绪万千", "回忆如潮", "岁月如歌"],
            "神秘": ["神秘莫测", "阴暗诡异", "幽深悠远", "暗黑魅惑"],
            "励志": ["激励向上", "奋发图强", "勇敢坚毅", "拼搏进取"],
            "孤独": ["孤独寂寞", "独自沉思", "落寞无依", "孤芳自赏"]
        }
        
        # 处理复合情感或多种情感混合的情况
        if detected_emotions:
            # 找出最强烈的情感
            primary_emotion = max(detected_emotions.keys(), key=lambda k: detected_emotions[k])
            
            # 检查是否有多种情感强度相近
            max_score = detected_emotions[primary_emotion]
            similar_emotions = [k for k, v in detected_emotions.items() if v >= max_score * 0.8]
            
            if len(similar_emotions) > 1:
                # 处理混合情感，如：悲伤+怀旧，愤怒+励志等
                options = self._generate_mixed_emotion_options(similar_emotions)
            else:
                options = emotion_families.get(primary_emotion, ["平静舒缓", "温暖治愈", "神秘深邃", "激昂有力"])
        else:
            options = ["平静舒缓", "温暖治愈", "神秘深邃", "激昂有力"]
        
        print(f"🎨 主要情感: {primary_emotion if detected_emotions else '未检测'}")
        print(f"🎨 生成的情感选项: {options}")
        return options
    
    def _generate_mixed_emotion_options(self, emotions: List[str]) -> List[str]:
        """为混合情感生成选项"""
        mixed_combinations = {
            ("悲伤", "怀旧"): ["怀念忧伤", "追忆往昔", "岁月如歌", "思念绵绵"],
            ("快乐", "励志"): ["阳光励志", "积极向上", "充满希望", "奋发图强"],
            ("平静", "神秘"): ["静谧神秘", "深邃宁静", "禅意悠远", "空灵飘渺"],
            ("愤怒", "励志"): ["愤怒觉醒", "反叛精神", "燃烧斗志", "不屈不挠"],
            ("浪漫", "怀旧"): ["浪漫回忆", "往日情深", "爱的追忆", "温柔思念"],
            ("孤独", "悲伤"): ["孤独忧伤", "寂寞深沉", "独自悲伤", "落寞无依"],
            ("焦虑", "愤怒"): ["焦虑愤怒", "内心挣扎", "情绪激荡", "不安暴躁"]
        }
        
        # 尝试匹配已知的混合组合
        emotions_set = set(emotions)
        for combo, options in mixed_combinations.items():
            if set(combo).issubset(emotions_set):
                return options
        
        # 如果没有预定义组合，混合各种情感的代表选项
        mixed_options = []
        emotion_representatives = {
            "悲伤": "深度忧郁", "快乐": "欢快活泼", "平静": "宁静致远",
            "愤怒": "激昂澎湃", "焦虑": "内心挣扎", "浪漫": "温柔浪漫",
            "怀旧": "怀念往昔", "神秘": "神秘莫测", "励志": "激励向上", "孤独": "孤独沉思"
        }
        
        for emotion in emotions[:3]:  # 最多取前3个情感
            if emotion in emotion_representatives:
                mixed_options.append(emotion_representatives[emotion])
        
        # 补充到4个选项
        while len(mixed_options) < 4:
            mixed_options.append("情感复合")
            
        return mixed_options[:4]
    
    def _analyze_mood(self, text: str) -> str:
        """分析情绪"""
        # 悲伤/忧郁词汇
        sad_keywords = [
            "哭", "哭了", "哭泣", "眼泪", "流泪", "伤心", "难过", "痛苦", "忧郁", "悲伤", 
            "失落", "孤独", "绝望", "沮丧", "抑郁", "心痛", "痛哭", "悲痛", "凄凉",
            "忧伤", "哀伤", "心碎", "失望", "黯然", "凄惨", "悲凉", "哀怨"
        ]
        
        # 快乐词汇
        happy_keywords = [
            "开心", "快乐", "高兴", "愉快", "欢乐", "兴奋", "喜悦", "愉悦", "欣喜",
            "激动", "狂欢", "庆祝", "笑", "微笑", "大笑", "乐", "欢", "嗨", "哈哈"
        ]
        
        # 平静词汇
        calm_keywords = [
            "安静", "平静", "舒缓", "放松", "宁静", "冥想", "休息", "安详", "祥和",
            "温和", "柔和", "轻柔", "静谧", "安宁", "淡然", "从容", "悠闲"
        ]
        
        # 激昂词汇
        energetic_keywords = [
            "激动", "活力", "充满", "热情", "振奋", "刺激", "狂热", "火热", "燃烧",
            "澎湃", "激烈", "强烈", "猛烈", "爆发", "冲击", "震撼", "力量"
        ]
        
        # 计算各情绪的权重
        sad_score = sum(1 for word in sad_keywords if word in text)
        happy_score = sum(1 for word in happy_keywords if word in text)
        calm_score = sum(1 for word in calm_keywords if word in text)
        energetic_score = sum(1 for word in energetic_keywords if word in text)
        
        print(f"情绪得分 - 悲伤:{sad_score}, 快乐:{happy_score}, 平静:{calm_score}, 激昂:{energetic_score}")
        
        # 选择得分最高的情绪
        scores = {
            "忧郁": sad_score,
            "愉快": happy_score,
            "平静": calm_score,
            "激昂": energetic_score
        }
        
        max_mood = max(scores, key=scores.get)
        if scores[max_mood] > 0:
            print(f"检测到情绪: {max_mood}")
            return max_mood
        else:
            return "中性"
    
    def _analyze_style(self, text: str) -> str:
        """分析音乐风格"""
        style_keywords = {
            "古典": ["古典", "交响", "管弦", "巴洛克", "浪漫派", "室内乐"],
            "流行": ["流行", "pop", "现代", "热门", "主流"],
            "摇滚": ["摇滚", "rock", "重金属", "朋克", "硬核"],
            "电子": ["电子", "电音", "合成", "电子音乐", "techno", "house"],
            "爵士": ["爵士", "jazz", "蓝调", "blues", "即兴"],
            "民谣": ["民谣", "folk", "吉他", "弹唱", "原声"],
            "轻音乐": ["轻音乐", "轻松", "背景", "纯音乐", "新世纪"]
        }
        
        for style, keywords in style_keywords.items():
            if any(keyword in text for keyword in keywords):
                return style
        
        return "轻音乐"  # 默认
    
    def _analyze_instruments(self, text: str, mood: str) -> list:
        """分析乐器"""
        # 直接提到的乐器
        if "钢琴" in text:
            return ["钢琴"]
        elif any(word in text for word in ["吉他", "guitar"]):
            return ["吉他"]
        elif any(word in text for word in ["小提琴", "大提琴", "弦乐"]):
            return ["小提琴", "弦乐"]
        elif any(word in text for word in ["鼓", "打击", "节拍"]):
            return ["鼓", "打击乐"]
        elif any(word in text for word in ["萨克斯", "长笛", "管乐"]):
            return ["管乐"]
        else:
            # 根据情绪选择乐器
            mood_instruments = {
                "忧郁": ["钢琴", "大提琴"],
                "愉快": ["吉他", "小提琴"],
                "平静": ["钢琴", "长笛"],
                "激昂": ["吉他", "鼓"]
            }
            return mood_instruments.get(mood, ["钢琴"])
    
    def _analyze_tempo(self, text: str, mood: str) -> str:
        """分析节奏"""
        if any(word in text for word in ["慢", "缓", "悠扬", "舒缓", "慢慢"]):
            return "慢"
        elif any(word in text for word in ["快", "急", "激烈", "狂热", "快速"]):
            return "快"
        else:
            # 根据情绪推断节奏
            mood_tempo = {
                "忧郁": "慢",
                "愉快": "中",
                "平静": "慢",
                "激昂": "快"
            }
            return mood_tempo.get(mood, "中")
    
    def _create_fallback_analysis(self, user_input: UserInput) -> AIAnalysis:
        """创建备用分析结果（仅在API完全失败时使用）"""
        print(f"⚠️ API调用完全失败，使用备用分析")
        return self._create_smart_analysis(user_input, "API服务暂时不可用，使用本地分析")
    
    def _analyze_clarification_for_interface(self, session_data: Dict[str, Any]) -> str:
        """分析澄清回答，确定应该使用哪个音乐生成接口"""
        interface_preference = None
        
        if "clarification_history" in session_data:
            for clarification in session_data["clarification_history"]:
                question_id = clarification.get('question_id', '')
                selected_option = clarification.get('selected_option', '')
                
                # 检查音乐类型选择 (更新为新的question_id)
                if question_id in ['music_type', 'voice_type']:
                    if '纯音乐' in selected_option or 'BGM' in selected_option or '器乐演奏' in selected_option:
                        interface_preference = 'gen_bgm'
                        print(f"✅ 用户选择纯音乐/BGM: {selected_option}")
                    elif '有人声' in selected_option or '演唱' in selected_option:
                        interface_preference = 'gen_song'  # 默认为gen_song，后续可能根据歌词需求调整
                        print(f"✅ 用户选择有人声音乐: {selected_option}")
                
                # 检查是否提及了歌词相关内容
                if '歌词' in selected_option or '歌曲' in selected_option:
                    if interface_preference == 'gen_song':
                        interface_preference = 'lyrics_gen_song'
                        print(f"✅ 检测到歌词需求，调整为lyrics_gen_song")
        
        # 如果没有明确偏好，根据原始输入推断
        if not interface_preference:
            original_text = session_data.get('original_input', {}).get('text_content', '').lower()
            
            if any(keyword in original_text for keyword in ['bgm', '背景音乐', '纯音乐', '无人声', '器乐']):
                interface_preference = 'gen_bgm'
                print(f"📝 根据原始输入推断为BGM需求")
            elif any(keyword in original_text for keyword in ['歌词', '演唱', '歌曲', '唱歌']):
                interface_preference = 'lyrics_gen_song'
                print(f"📝 根据原始输入推断为歌词生成需求")
            else:
                interface_preference = 'gen_song'  # 默认值
                print(f"📝 使用默认接口gen_song")
        
        return interface_preference or 'gen_song'
    
    def generate_final_prompt_with_user_params(self, session_data: Dict[str, Any], user_params: Dict[str, Any]) -> MusicPrompt:
        """根据用户直接提供的参数生成音乐提示词（优先级更高）"""
        try:
            print(f"🎯 使用用户参数生成最终提示词: {user_params}")
            
            # 获取基本参数
            music_description = user_params.get('music_description', '')
            duration = user_params.get('duration', 30)
            voice_type = user_params.get('voice_type', '纯音乐/BGM')
            
            # 如果没有描述，使用原始输入作为备选
            if not music_description:
                original_text = session_data.get('original_input', {}).get('text_content', '')
                music_description = original_text or '创作一段音乐'
            
            # 根据音乐类型选择接口和参数
            if voice_type == '有人声演唱':
                voice_params = user_params.get('voice_params', {})
                gender = voice_params.get('gender', 'Male')
                timbre = voice_params.get('timbre', 'Warm')
                
                # 判断是否有歌词需求（用于选择gen_song vs lyrics_gen_song）
                if len(music_description) > 100 or '歌词' in music_description.lower():
                    # 长描述或包含"歌词"关键词，使用lyrics_gen_song
                    return MusicPrompt(
                        interface='lyrics_gen_song',
                        lyrics=music_description,
                        mood_single='Happy',
                        genre_single='Pop',
                        timbre=timbre,
                        gender=gender,
                        duration=duration
                    )
                else:
                    # 短描述，使用gen_song
                    return MusicPrompt(
                        interface='gen_song',
                        prompt=music_description,
                        mood_single='Happy',
                        genre_single='Pop', 
                        timbre=timbre,
                        gender=gender,
                        duration=duration
                    )
            else:
                # 纯音乐/BGM
                bgm_params = user_params.get('bgm_params', {})
                instruments = bgm_params.get('instruments', ['piano'])
                
                return MusicPrompt(
                    interface='gen_bgm',
                    text=music_description,
                    mood=['happy'],
                    genre=['ambient'], 
                    theme=['meditation'],
                    duration=duration,
                    instrument=instruments
                )
                
        except Exception as e:
            print(f"❌ 用户参数生成提示词失败: {str(e)}")
            # 失败时回退到原有逻辑
            return self.generate_final_prompt(session_data)
    
    def generate_final_prompt(self, session_data: Dict[str, Any]) -> MusicPrompt:
        """根据澄清后的信息生成最终音乐提示词"""
        try:
            # 首先分析用户的澄清回答，确定音乐类型
            interface_preference = self._analyze_clarification_for_interface(session_data)
            print(f"🔍 根据澄清回答确定接口偏好: {interface_preference}")
            
            # 构建澄清后的完整信息
            clarification_info = ""
            if "clarification_history" in session_data:
                for clarification in session_data["clarification_history"]:
                    clarification_info += f"问题: {clarification['question_id']}, 选择: {clarification['selected_option']}\n"
            
            # 根据用户输入判断使用哪种音乐生成接口
            user_text = session_data.get('original_input', {}).get('text_content', '')
            
            prompt = f"""
            基于以下信息，根据用户需求选择合适的音乐生成接口并输出对应的参数格式：

            用户原始输入: {user_text}
            原始理解: {session_data.get('ai_analysis', {}).get('understanding', '')}
            音乐元素: {json.dumps(session_data.get('ai_analysis', {}).get('music_elements', {}), ensure_ascii=False)}
            澄清信息: {clarification_info}

            **用户偏好接口**: {interface_preference}
            
            请根据用户的明确选择和需求，选择以下三种接口之一，并严格按照对应的JSON格式输出参数：
            
            重要提示：如果用户明确选择了音乐类型，请优先使用对应接口：
            - 选择"纯音乐/BGM"或"器乐演奏" → 使用 gen_bgm
            - 选择"有人声演唱" → 使用 gen_song 或 lyrics_gen_song

            **接口1：gen_bgm (生成BGM/背景音乐)**
            适用于：纯音乐、背景音乐、无人声音乐需求
            输出格式：
            {{
              "interface": "gen_bgm",
              "mood": ["情感风格"],
              "text": "歌词提示词内容（中文，小于500字符）",
              "genre": ["音乐曲风"],
              "theme": ["音乐主题"],
              "duration": 30,
              "instrument": ["使用的乐器"]
            }}

            **接口2：gen_song (音乐生成)**
            适用于：有人声演唱的歌曲需求
            输出格式：
            {{
              "interface": "gen_song",
              "mood": "情感风格",
              "genre": "音乐曲风",
              "timbre": "音色特征",
              "gender": "演唱者性别（Male/Female）",
              "prompt": "歌词提示词内容（中文，小于500字符）",
              "duration": 30
            }}

            **接口3：lyrics_gen_song (根据歌词生成音乐)**
            适用于：用户已提供具体歌词的情况
            输出格式：
            {{
              "interface": "lyrics_gen_song",
              "mood": "情感风格",
              "genre": "音乐曲风",
              "lyrics": "具体歌词内容（5-700字符）",
              "timbre": "音色特征",
              "gender": "演唱者性别（Male/Female）",
              "duration": 30
            }}

            参数值请严格从以下选项中选择：
            对于gen_bgm接口，mood选项：positive、uplifting、energetic、happy、bright、optimistic、hopeful、cool、dreamy、fun、light、powerful、calm、confident、joyful、dramatic、peaceful、playful、soft、groovy、reflective、easy、relaxed、lively、smooth、romantic、intense、elegant、mellow、emotional、sentimental、cheerful、contemplative
            
            对于gen_song和lyrics_gen_song接口，mood选项：Happy、Dynamic/Energetic、Sentimental/Melancholic/Lonely、Inspirational/Hopeful、Nostalgic/Memory、Excited、Sorrow/Sad、Chill、Romantic
            - genre选项：corporate、dance/edm、orchestral、chill out、rock、hip hop、folk、funk、ambient、holiday、jazz、kids、world、travel、commercial、advertising、driving、cinematic、upbeat、epic、inspiring、business、video game、dark、pop、trailer、modern、electronic、documentary、soundtrack、fashion、acoustic、movie、tv、high tech、industrial
            - theme选项：inspirational、motivational、achievement、discovery、every day、love、technology、lifestyle、journey、meditation、drama、children、hope、fantasy、holiday、health、family、real estate、media、kids、science、education、progress、world、vacation、training、christmas、sales
            - instrument选项：piano、drums、guitar、percussion、synth、electric guitar、acoustic guitar、bass guitar、brass、violin、cello、flute、organ、trumpet、ukulele、saxophone、double bass、harp、glockenspiel、synthesizer、keyboard、marimba、bass、banjo、strings

            重要要求：
            1. 根据用户需求智能选择最合适的接口
            2. 严格按照JSON格式输出
            3. 所有参数值必须从上述选项中选择
            4. 不要添加markdown格式或其他解释文字
            5. 直接返回纯JSON
            """
            
            messages = [
                {"role": "system", "content": "你是音乐生成专家，请根据用户的需求生成详细的中文音乐提示词，严格按照JSON格式回复。"},
                {"role": "user", "content": prompt}
            ]
            
            payload = {
                "model": self.model_name,
                "input": {
                    "messages": messages
                },
                "parameters": {
                    "temperature": 0.5,
                    "max_tokens": 800,
                    "result_format": "message"
                }
            }
            
            print(f"生成最终提示词API请求: {payload}")  # 调试信息
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            print(f"生成提示词API响应状态码: {response.status_code}")  # 调试信息
            
            if response.status_code == 200:
                result = response.json()
                print(f"生成提示词API响应: {result}")  # 调试信息
                
                # DashScope的响应格式解析
                if "output" in result and "choices" in result["output"]:
                    output = result["output"]
                    if len(output["choices"]) > 0:
                        message_content = output["choices"][0]["message"]["content"]
                        
                        # 处理content的不同格式
                        if isinstance(message_content, list):
                            # content是数组格式：[{'text': '...'}]
                            if len(message_content) > 0 and "text" in message_content[0]:
                                content = message_content[0]["text"]
                                print(f"✅ 成功获取提示词内容(数组格式): {content[:100]}...")
                            else:
                                print(f"❌ 生成提示词数组格式解析失败: {message_content}")
                                return self._create_fallback_prompt()
                        elif isinstance(message_content, str):
                            # content是字符串格式
                            content = message_content
                            print(f"✅ 成功获取提示词内容(字符串格式): {content[:100]}...")
                        else:
                            print(f"❌ 生成提示词未知格式: {type(message_content)}")
                            return self._create_fallback_prompt()
                    else:
                        print(f"生成提示词choices为空: {result}")
                        return self._create_fallback_prompt()
                elif "text" in result.get("output", {}):
                    content = result["output"]["text"]
                    print(f"✅ 成功获取提示词内容(text格式): {content[:100]}...")
                else:
                    print(f"生成提示词API返回错误: {result}")
                    return self._create_fallback_prompt()
                
                try:
                    # 清理生成提示词的响应格式
                    cleaned_content = self._clean_json_response(content)
                    print(f"🧹 清理后的提示词内容: {cleaned_content[:200]}...")
                    
                    prompt_data = json.loads(cleaned_content)
                    
                    # 根据接口类型返回不同的MusicPrompt结构
                    interface_type = prompt_data.get("interface", "gen_bgm")
                    
                    if interface_type == "gen_bgm":
                        return MusicPrompt(
                            interface=interface_type,
                            mood=prompt_data.get("mood", ["happy"]),
                            text=prompt_data.get("text", "关于星空的背景纯音乐"),
                            genre=prompt_data.get("genre", ["ambient"]),
                            theme=prompt_data.get("theme", ["meditation"]),
                            duration=prompt_data.get("duration", 30),
                            instrument=prompt_data.get("instrument", ["piano"])
                        )
                    elif interface_type == "gen_song":
                        return MusicPrompt(
                            interface=interface_type,
                            mood_single=prompt_data.get("mood", "Happy"),
                            genre_single=prompt_data.get("genre", "Pop"),
                            timbre=prompt_data.get("timbre", "Warm"),
                            gender=prompt_data.get("gender", "Male"),
                            prompt=prompt_data.get("prompt", "关于星空的歌"),
                            duration=prompt_data.get("duration", 30)
                        )
                    elif interface_type == "lyrics_gen_song":
                        return MusicPrompt(
                            interface=interface_type,
                            mood_single=prompt_data.get("mood", "Happy"),
                            genre_single=prompt_data.get("genre", "Pop"),
                            lyrics=prompt_data.get("lyrics", "星空下的浪漫夜晚"),
                            timbre=prompt_data.get("timbre", "Warm"),
                            gender=prompt_data.get("gender", "Male"),
                            duration=prompt_data.get("duration", 30)
                        )
                    else:
                        return self._create_fallback_prompt()
                        
                except json.JSONDecodeError as e:
                    print(f"❌ 生成提示词JSON解析失败: {e}")
                    print(f"原始内容: {content[:300]}...")
                    return self._create_fallback_prompt()
            else:
                return self._create_fallback_prompt()
                
        except Exception as e:
            print(f"生成最终提示词错误: {str(e)}")
            return self._create_fallback_prompt()
    
    def _create_fallback_prompt(self) -> MusicPrompt:
        """创建备用音乐提示词"""
        return MusicPrompt(
            interface="gen_bgm",
            mood=["happy", "peaceful"],
            text="创作一首优美动听的背景音乐",
            genre=["ambient"],
            theme=["meditation"],
            duration=30,
            instrument=["piano", "strings"]
        )

# 全局AI服务实例
ai_service = QwenOmniService()
