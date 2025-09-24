import os
import json
import requests
import time
from typing import Dict, Any, Tuple, Optional
from app.models.schemas import MusicPrompt
from dotenv import load_dotenv

load_dotenv()

class CozeMusicService:
    def __init__(self):
        # Coze API配置 - 使用更简单的对话接口
        self.api_url = "https://api.coze.cn/v3/chat"
        self.token = os.getenv("COZE_TOKEN")
        self.bot_id = os.getenv("COZE_BOT_ID")
        if not self.token:
            raise RuntimeError("COZE_TOKEN is not set. Please configure it in your environment.")
        if not self.bot_id:
            raise RuntimeError("COZE_BOT_ID is not set. Please configure it in your environment.")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        print("初始化CozeMusicService (使用对话接口)")
    
    def _validate_and_fix_parameters(self, music_prompt: MusicPrompt) -> MusicPrompt:
        """验证和修复参数，确保符合接口要求"""
        print(f"🔧 开始验证接口 {music_prompt.interface} 的参数...")
        
        # gen_song 和 lyrics_gen_song 的 mood 映射
        song_mood_mapping = {
            'happy': 'Happy',
            'energetic': 'Dynamic/Energetic', 
            'emotional': 'Sentimental/Melancholic/Lonely',
            'sentimental': 'Sentimental/Melancholic/Lonely',
            'melancholic': 'Sentimental/Melancholic/Lonely',
            'lonely': 'Sentimental/Melancholic/Lonely',
            'sad': 'Sorrow/Sad',
            'sorrow': 'Sorrow/Sad',
            'inspirational': 'Inspirational/Hopeful',
            'hopeful': 'Inspirational/Hopeful',
            'nostalgic': 'Nostalgic/Memory',
            'memory': 'Nostalgic/Memory',
            'excited': 'Excited',
            'chill': 'Chill',
            'calm': 'Chill',
            'peaceful': 'Chill',
            'romantic': 'Romantic'
        }
        
        song_mood_valid_values = [
            'Happy', 'Dynamic/Energetic', 'Sentimental/Melancholic/Lonely',
            'Inspirational/Hopeful', 'Nostalgic/Memory', 'Excited', 
            'Sorrow/Sad', 'Chill', 'Romantic'
        ]
        
        # 处理gen_bgm接口参数验证
        if music_prompt.interface == 'gen_bgm':
            # 验证bgm的mood参数（数组格式）
            bgm_mood_valid_values = [
                'positive', 'uplifting', 'energetic', 'happy', 'bright', 'optimistic', 
                'hopeful', 'cool', 'dreamy', 'fun', 'light', 'powerful', 'calm', 
                'confident', 'joyful', 'dramatic', 'peaceful', 'playful', 'soft', 
                'groovy', 'reflective', 'easy', 'relaxed', 'lively', 'smooth', 
                'romantic', 'intense', 'elegant', 'mellow', 'emotional', 
                'sentimental', 'cheerful', 'contemplative'
            ]
            
            if music_prompt.mood:
                fixed_mood = []
                for mood_item in music_prompt.mood:
                    if mood_item.lower() in bgm_mood_valid_values:
                        fixed_mood.append(mood_item.lower())
                    else:
                        # 尝试映射
                        mood_mapping = {
                            'sad': 'emotional',
                            'melancholic': 'sentimental', 
                            'lonely': 'sentimental',
                            'excited': 'energetic',
                            'chill': 'calm'
                        }
                        mapped_mood = mood_mapping.get(mood_item.lower())
                        if mapped_mood and mapped_mood in bgm_mood_valid_values:
                            print(f"🔧 修复BGM mood参数: {mood_item} → {mapped_mood}")
                            fixed_mood.append(mapped_mood)
                        else:
                            print(f"⚠️ 未知BGM mood值 {mood_item}，使用默认值 'happy'")
                            fixed_mood.append('happy')
                music_prompt.mood = fixed_mood if fixed_mood else ['happy']
            else:
                music_prompt.mood = ['happy']
            
            # 验证instrument参数
            bgm_instrument_valid_values = [
                'piano', 'drums', 'guitar', 'percussion', 'synth', 'electric guitar', 
                'acoustic guitar', 'bass guitar', 'brass', 'violin', 'cello', 'flute', 
                'organ', 'trumpet', 'ukulele', 'saxophone', 'double bass', 'harp', 
                'glockenspiel', 'synthesizer', 'keyboard', 'marimba', 'bass', 'banjo', 'strings'
            ]
            
            if music_prompt.instrument:
                fixed_instruments = []
                for instrument in music_prompt.instrument:
                    if instrument.lower() in bgm_instrument_valid_values:
                        fixed_instruments.append(instrument.lower())
                    else:
                        print(f"⚠️ 未知BGM instrument值 {instrument}，使用默认值 'piano'")
                        fixed_instruments.append('piano')
                music_prompt.instrument = fixed_instruments if fixed_instruments else ['piano']
            else:
                music_prompt.instrument = ['piano']
            
            # 验证genre参数
            bgm_genre_valid_values = [
                'corporate', 'dance/edm', 'orchestral', 'chill out', 'rock', 'hip hop', 
                'folk', 'funk', 'ambient', 'holiday', 'jazz', 'kids', 'world', 'travel', 
                'commercial', 'advertising', 'driving', 'cinematic', 'upbeat', 'epic', 
                'inspiring', 'business', 'video game', 'dark', 'pop', 'trailer', 
                'modern', 'electronic', 'documentary', 'soundtrack', 'fashion', 
                'acoustic', 'movie', 'tv', 'high tech', 'industrial'
            ]
            
            if music_prompt.genre:
                fixed_genres = []
                for genre in music_prompt.genre:
                    if genre.lower() in bgm_genre_valid_values:
                        fixed_genres.append(genre.lower())
                    else:
                        genre_mapping = {
                            'classical': 'orchestral',
                            'edm': 'dance/edm',
                            'hiphop': 'hip hop',
                            'techno': 'electronic'
                        }
                        mapped_genre = genre_mapping.get(genre.lower())
                        if mapped_genre and mapped_genre in bgm_genre_valid_values:
                            print(f"🔧 修复BGM genre参数: {genre} → {mapped_genre}")
                            fixed_genres.append(mapped_genre)
                        else:
                            print(f"⚠️ 未知BGM genre值 {genre}，使用默认值 'ambient'")
                            fixed_genres.append('ambient')
                music_prompt.genre = fixed_genres if fixed_genres else ['ambient']
            else:
                music_prompt.genre = ['ambient']
            
            # 验证theme参数
            bgm_theme_valid_values = [
                'inspirational', 'motivational', 'achievement', 'discovery', 'every day', 
                'love', 'technology', 'lifestyle', 'journey', 'meditation', 'drama', 
                'children', 'hope', 'fantasy', 'holiday', 'health', 'family', 'real estate', 
                'media', 'kids', 'science', 'education', 'progress', 'world', 'vacation', 
                'training', 'christmas', 'sales'
            ]
            
            if music_prompt.theme:
                fixed_themes = []
                for theme in music_prompt.theme:
                    if theme.lower() in bgm_theme_valid_values:
                        fixed_themes.append(theme.lower())
                    else:
                        print(f"⚠️ 未知BGM theme值 {theme}，使用默认值 'meditation'")
                        fixed_themes.append('meditation')
                music_prompt.theme = fixed_themes if fixed_themes else ['meditation']
            else:
                music_prompt.theme = ['meditation']
            
            # 打印修复后的参数
            print(f"✅ BGM参数验证完成:")
            print(f"   Mood: {music_prompt.mood}")
            print(f"   Genre: {music_prompt.genre}")
            print(f"   Theme: {music_prompt.theme}")
            print(f"   Instrument: {music_prompt.instrument}")
            print(f"   Duration: {music_prompt.duration}")
        
        elif music_prompt.interface in ['gen_song', 'lyrics_gen_song']:
            # 修复mood参数
            if music_prompt.mood_single:
                # 先尝试直接匹配
                if music_prompt.mood_single not in song_mood_valid_values:
                    # 尝试映射
                    mapped_mood = song_mood_mapping.get(music_prompt.mood_single.lower())
                    if mapped_mood:
                        print(f"🔧 修复mood参数: {music_prompt.mood_single} → {mapped_mood}")
                        music_prompt.mood_single = mapped_mood
                    else:
                        # 默认值
                        print(f"⚠️ 未知mood值 {music_prompt.mood_single}，使用默认值 'Happy'")
                        music_prompt.mood_single = 'Happy'
            else:
                music_prompt.mood_single = 'Happy'
            
            # 修复genre参数
            song_genre_valid_values = ['Folk', 'Pop', 'Rock', 'Chinese Style', 'Hip Hop/Rap', 'R&B/Soul', 'Punk', 'Electronic', 'Jazz', 'Reggae', 'DJ']
            if music_prompt.genre_single:
                if music_prompt.genre_single not in song_genre_valid_values:
                    # 简单映射
                    genre_mapping = {
                        'pop': 'Pop',
                        'rock': 'Rock', 
                        'electronic': 'Electronic',
                        'jazz': 'Jazz',
                        'folk': 'Folk',
                        'hip hop': 'Hip Hop/Rap',
                        'rap': 'Hip Hop/Rap',
                        'punk': 'Punk',
                        'reggae': 'Reggae',
                        'r&b': 'R&B/Soul',
                        'soul': 'R&B/Soul',
                        'chinese': 'Chinese Style'
                    }
                    mapped_genre = genre_mapping.get(music_prompt.genre_single.lower())
                    if mapped_genre:
                        print(f"🔧 修复genre参数: {music_prompt.genre_single} → {mapped_genre}")
                        music_prompt.genre_single = mapped_genre
                    else:
                        print(f"⚠️ 未知genre值 {music_prompt.genre_single}，使用默认值 'Pop'")
                        music_prompt.genre_single = 'Pop'
            else:
                music_prompt.genre_single = 'Pop'
            
            # 修复timbre参数
            timbre_valid_values = ['Warm', 'Bright', 'Husky', 'Electrified voice', 'Sweet_AUDIO_TIMBRE', 'Cute_AUDIO_TIMBRE', 'Loud and sonorous', 'Powerful', 'Sexy/Lazy']
            if music_prompt.timbre:
                if music_prompt.timbre not in timbre_valid_values:
                    timbre_mapping = {
                        'warm': 'Warm',
                        'bright': 'Bright',
                        'husky': 'Husky', 
                        'sweet': 'Sweet_AUDIO_TIMBRE',
                        'cute': 'Cute_AUDIO_TIMBRE',
                        'powerful': 'Powerful',
                        'soft': 'Warm',
                        'lazy': 'Sexy/Lazy',
                        'sexy': 'Sexy/Lazy'
                    }
                    mapped_timbre = timbre_mapping.get(music_prompt.timbre.lower())
                    if mapped_timbre:
                        print(f"🔧 修复timbre参数: {music_prompt.timbre} → {mapped_timbre}")
                        music_prompt.timbre = mapped_timbre
                    else:
                        print(f"⚠️ 未知timbre值 {music_prompt.timbre}，使用默认值 'Warm'")
                        music_prompt.timbre = 'Warm'
            else:
                music_prompt.timbre = 'Warm'
            
            # 修复gender参数
            if music_prompt.gender not in ['Male', 'Female']:
                gender_mapping = {'male': 'Male', 'female': 'Female', 'man': 'Male', 'woman': 'Female', '男': 'Male', '女': 'Female'}
                mapped_gender = gender_mapping.get(music_prompt.gender.lower() if music_prompt.gender else '')
                if mapped_gender:
                    print(f"🔧 修复gender参数: {music_prompt.gender} → {mapped_gender}")
                    music_prompt.gender = mapped_gender
                else:
                    print(f"⚠️ 未知gender值 {music_prompt.gender}，使用默认值 'Male'")
                    music_prompt.gender = 'Male'
            
            # 打印修复后的参数
            print(f"✅ Song参数验证完成:")
            print(f"   Mood: {music_prompt.mood_single}")
            print(f"   Genre: {music_prompt.genre_single}")
            print(f"   Timbre: {music_prompt.timbre}")
            print(f"   Gender: {music_prompt.gender}")
            if music_prompt.interface == 'gen_song':
                print(f"   Prompt: {music_prompt.prompt}")
            else:
                print(f"   Lyrics: {music_prompt.lyrics[:50] if music_prompt.lyrics else 'None'}...")
            print(f"   Duration: {music_prompt.duration}")
        
        return music_prompt

    def _format_music_prompt(self, music_prompt: MusicPrompt) -> str:
        """将MusicPrompt格式化为Coze插件能理解的文本"""
        try:
            # 首先验证和修复参数
            music_prompt = self._validate_and_fix_parameters(music_prompt)
            
            if music_prompt.interface == "gen_bgm":
                # 针对插件优化的参数格式
                mood_list = music_prompt.mood or ["happy"]
                genre_list = music_prompt.genre or ["ambient"] 
                theme_list = music_prompt.theme or ["meditation"]
                instrument_list = music_prompt.instrument or ["piano"]
                
                # 确保参数值符合教程.txt中的选项
                valid_moods = ["positive", "uplifting", "energetic", "happy", "bright", "optimistic", 
                              "hopeful", "cool", "dreamy", "fun", "light", "powerful", "calm", 
                              "confident", "joyful", "dramatic", "peaceful", "playful", "soft", 
                              "groovy", "reflective", "easy", "relaxed", "lively", "smooth", 
                              "romantic", "intense", "elegant", "mellow", "emotional", 
                              "sentimental", "cheerful", "contemplative"]
                
                # 过滤无效的mood值
                mood_list = [m for m in mood_list if m in valid_moods]
                if not mood_list:
                    mood_list = ["peaceful"]
                
                prompt_text = f"""请使用gen_bgm接口生成背景音乐。

参数要求：
- Mood: {mood_list}
- Text: {music_prompt.text or '关于星空的背景纯音乐'}  
- Genre: {genre_list}
- Theme: {theme_list}
- Duration: {music_prompt.duration}
- Instrument: {instrument_list}

请严格使用这些参数调用gen_bgm接口生成音乐。"""
            
            elif music_prompt.interface == "gen_song":
                prompt_text = f"""请使用gen_song接口生成有人声的歌曲。

参数要求：
- Mood: {music_prompt.mood_single or 'Happy'}
- Genre: {music_prompt.genre_single or 'Pop'}
- Timbre: {music_prompt.timbre or 'Warm'}
- Gender: {music_prompt.gender or 'Male'}
- Prompt: {music_prompt.prompt or '关于星空的歌'}
- Duration: {music_prompt.duration}

请严格使用这些参数调用gen_song接口生成音乐。"""
            
            elif music_prompt.interface == "lyrics_gen_song":
                prompt_text = f"""请使用lyrics_gen_song接口根据歌词生成音乐。

参数要求：
- Mood: {music_prompt.mood_single or 'Happy'}
- Genre: {music_prompt.genre_single or 'Pop'}
- Lyrics: {music_prompt.lyrics or '星空下的浪漫夜晚'}
- Timbre: {music_prompt.timbre or 'Warm'}
- Gender: {music_prompt.gender or 'Male'}
- Duration: {music_prompt.duration}

请严格使用这些参数调用lyrics_gen_song接口生成音乐。"""
            
            else:
                prompt_text = f"请生成一首音乐，要求：{music_prompt.text or '优美的背景音乐'}"
            
            return prompt_text
            
        except Exception as e:
            print(f"格式化音乐提示词失败: {e}")
            return "请生成一首优美的背景音乐"
    
    def generate_music(self, music_prompt: MusicPrompt) -> Tuple[bool, str, Optional[str]]:
        """
        调用Coze对话API生成音乐
        返回: (success, music_url_or_error_message, lyrics)
        """
        try:
            # 格式化提示词
            prompt_text = self._format_music_prompt(music_prompt)
            print(f"发送给Coze的提示词: {prompt_text}")
            
            # 构建对话请求数据 - 使用v3/chat接口
            payload = {
                "bot_id": self.bot_id,
                "user_id": "music_generator_user",  # 固定用户ID
                "stream": False,  # 使用非流式响应
                "auto_save_history": True,  # 保存对话记录以便查看结果
                "additional_messages": [
                    {
                        "role": "user",
                        "content": prompt_text,
                        "content_type": "text"
                    }
                ],
                "meta_data": {
                    "interface_type": music_prompt.interface,
                    "duration": str(music_prompt.duration)
                }
            }
            
            print(f"发送对话API请求到Coze: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            
            # 发送请求
            response = requests.post(self.api_url, headers=self.headers, json=payload)
            print(f"Coze对话API响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Coze对话API响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                
                # 获取对话ID和会话ID
                chat_id = result.get("data", {}).get("id")
                conversation_id = result.get("data", {}).get("conversation_id") 
                
                if not chat_id:
                    return False, "未能获取对话ID", None
                
                print(f"对话创建成功，Chat ID: {chat_id}, Conversation ID: {conversation_id}")
                
                # 等待对话完成并获取结果
                music_url, lyrics = self._wait_for_chat_completion(chat_id, conversation_id)
                if music_url:
                    return True, music_url, lyrics
                else:
                    return False, "音乐生成超时或失败", None
                    
            else:
                error_msg = f"Coze对话API调用失败: {response.status_code} - {response.text}"
                print(error_msg)
                return False, error_msg, None
                
        except Exception as e:
            error_msg = f"调用Coze对话API失败: {str(e)}"
            print(error_msg)
            return False, error_msg, None
    
    def _wait_for_chat_completion(self, chat_id: str, conversation_id: str, max_wait_time: int = 300, poll_interval: int = 2) -> Tuple[Optional[str], Optional[str]]:
        """
        等待对话完成并获取音乐生成结果
        返回: (music_url, lyrics)
        """
        print(f"开始等待对话完成，Chat ID: {chat_id}")
        
        # 构建查询对话详情的URL
        chat_detail_url = f"https://api.coze.cn/v3/chat/retrieve?chat_id={chat_id}&conversation_id={conversation_id}"
        
        start_time = time.time()
        while time.time() - start_time < max_wait_time:
            try:
                # 查询对话状态
                response = requests.get(chat_detail_url, headers=self.headers)
                if response.status_code == 200:
                    result = response.json()
                    chat_status = result.get("data", {}).get("status")
                    
                    print(f"对话状态: {chat_status}")
                    
                    # 检查是否完成
                    if chat_status in ["completed", "failed", "canceled"]:
                        if chat_status == "completed":
                            # 获取对话消息
                            return self._get_chat_messages(chat_id, conversation_id)
                        else:
                            print(f"对话失败，状态: {chat_status}")
                            return None, None
                    elif chat_status == "required_action":
                        print("对话需要用户操作")
                        return None, None
                
                print(f"等待对话完成... ({int(time.time() - start_time)}s)")
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"等待对话完成时出错: {e}")
                time.sleep(poll_interval)
        
        print("对话等待超时")
        return None, None

    def _get_chat_messages(self, chat_id: str, conversation_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        获取对话消息内容，处理插件调用的多条响应
        返回: (music_url, lyrics)
        """
        try:
            # 构建查询消息的URL
            messages_url = f"https://api.coze.cn/v3/chat/message/list?chat_id={chat_id}&conversation_id={conversation_id}"
            
            response = requests.get(messages_url, headers=self.headers)
            print(f"消息查询响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                messages = result.get("data", [])
                
                print(f"收到 {len(messages)} 条消息")
                
                plugin_success = False
                error_messages = []
                
                # 分析所有AI回复消息
                for message in messages:
                    if message.get("role") == "assistant" and message.get("content"):
                        content = message.get("content")
                        print(f"AI回复内容: {content}")
                        
                        # 检查是否是插件执行成功的指标
                        if self._is_plugin_success_indicator(content):
                            plugin_success = True
                            print("检测到插件可能执行成功的指标")
                        
                        # 收集错误信息
                        error_info = self._extract_error_info(content)
                        if error_info:
                            error_messages.append(error_info)
                        
                        # 尝试解析音乐链接
                        music_url, lyrics = self._parse_music_response(content)
                        if music_url:
                            return music_url, lyrics
                
                # 如果没找到音乐链接，尝试直接使用最后一条非错误消息作为可能的链接
                print("尝试从最后一条消息中提取可能的音乐链接...")
                for message in reversed(messages):
                    if message.get("role") == "assistant" and message.get("content"):
                        content = message.get("content").strip()
                        print(f"检查消息内容: {content[:100]}...")
                        
                        # 如果内容看起来像一个URL
                        if (content.startswith(('http://', 'https://')) and 
                            ('music' in content.lower() or 'audio' in content.lower() or 
                             '.mp3' in content.lower() or '.wav' in content.lower())):
                            print(f"找到可能的音乐链接: {content}")
                            return content, None
                
                # 如果没找到音乐链接但插件似乎成功了，返回提示信息
                if plugin_success:
                    print("⚠️ 插件执行成功但未找到音乐链接")
                    return None, "插件执行成功但未找到音乐链接，请检查插件配置"
                
                # 如果有错误信息，返回错误详情
                if error_messages:
                    error_detail = "; ".join(error_messages)
                    print(f"插件执行失败: {error_detail}")
                    return None, error_detail
                
                print("未找到包含音乐链接的AI回复")
                return None, None
            else:
                print(f"获取消息失败: {response.status_code} - {response.text}")
                return None, None
                
        except Exception as e:
            print(f"获取对话消息时出错: {e}")
            return None, None

    def _is_plugin_success_indicator(self, content: str) -> bool:
        """检查内容是否表明插件执行成功"""
        success_indicators = [
            "音乐生成成功",
            "生成完成", 
            "下载链接",
            "音乐已生成",
            "http://", 
            "https://",
            "音频文件",
            "音乐文件",
            ".mp3",
            ".wav", 
            ".m4a",
            "播放",
            "下载",
            "音乐链接",
            "音频链接",
            "生成的音乐",
            "您的音乐",
            "音乐作品"
        ]
        
        content_lower = content.lower()
        return any(indicator.lower() in content_lower for indicator in success_indicators)

    def _extract_error_info(self, content: str) -> Optional[str]:
        """从消息中提取错误信息"""
        try:
            # 尝试解析JSON错误响应
            if content.strip().startswith('{'):
                try:
                    json_content = json.loads(content.strip())
                    if 'code' in json_content and json_content.get('code') != 0:
                        return f"错误代码: {json_content.get('code')}, 信息: {json_content.get('msg', '未知错误')}"
                except json.JSONDecodeError:
                    pass
            
            # 检查文本错误信息
            error_keywords = ["错误", "失败", "error", "failed", "参数输入错误", "调用失败"]
            content_lower = content.lower()
            
            if any(keyword in content_lower for keyword in error_keywords):
                return content[:200] + ("..." if len(content) > 200 else "")
                
        except Exception as e:
            print(f"提取错误信息时出错: {e}")
        
        return None
    
    def _parse_music_response(self, content: str) -> Tuple[Optional[str], Optional[str]]:
        """
        解析Coze返回的音乐生成结果
        支持两种格式：
        1. 简单文本格式: "第一行是音乐下载链接后面是歌词"
        2. 插件调用格式: JSON格式的插件响应
        """
        try:
            # 首先尝试解析JSON格式（插件调用）
            if content.strip().startswith('{') and content.strip().endswith('}'):
                try:
                    plugin_response = json.loads(content.strip())
                    
                    # 检查是否是插件调用成功的响应
                    if 'name' in plugin_response and 'yinleshengcheng' in plugin_response.get('name', ''):
                        print(f"检测到音乐生成插件调用: {plugin_response.get('name')}")
                        
                        # 插件调用本身不包含结果，需要等待后续消息
                        return None, None
                    
                    # 检查是否是插件执行结果
                    if 'code' in plugin_response:
                        if plugin_response['code'] == 0 and 'data' in plugin_response:
                            # 成功响应，尝试从data中提取音乐信息
                            data = plugin_response['data']
                            if isinstance(data, dict):
                                # 检查嵌套的SongDetail结构
                                song_detail = data.get('SongDetail', {})
                                if song_detail:
                                    music_url = song_detail.get('AudioUrl')
                                    lyrics = song_detail.get('Lyrics') or song_detail.get('Captions')
                                    
                                    if music_url:
                                        print(f"从插件响应的SongDetail中解析到音乐链接: {music_url}")
                                        if lyrics:
                                            print(f"解析到歌词: {lyrics[:100]}...")
                                        return music_url, lyrics
                                
                                # 备用：检查其他可能的字段
                                music_url = data.get('music_url') or data.get('url') or data.get('download_url') or data.get('AudioUrl')
                                lyrics = data.get('lyrics') or data.get('lyric') or data.get('Lyrics')
                                if music_url:
                                    print(f"从插件响应的data中解析到音乐链接: {music_url}")
                                    return music_url, lyrics
                        else:
                            # 插件执行失败
                            error_msg = plugin_response.get('msg', '未知错误')
                            print(f"插件执行失败: {plugin_response.get('code')} - {error_msg}")
                            return None, None
                            
                except json.JSONDecodeError:
                    pass  # 不是JSON格式，继续尝试文本解析
            
            # 尝试简单文本格式解析
            lines = content.strip().split('\n')
            if not lines:
                return None, None
            
            # 第一行应该是音乐下载链接
            first_line = lines[0].strip()
            
            # 检查第一行是否包含有效的URL
            if ('http' in first_line and 
                ('.mp3' in first_line or '.wav' in first_line or '.m4a' in first_line or 
                 'music' in first_line.lower() or 'audio' in first_line.lower())):
                
                music_url = first_line
                # 其余行作为歌词
                lyrics = '\n'.join(lines[1:]).strip() if len(lines) > 1 else None
                
                print(f"解析到音乐链接: {music_url}")
                if lyrics:
                    print(f"解析到歌词: {lyrics[:100]}...")
                
                return music_url, lyrics
            
            # 如果第一行不是链接，尝试在整个内容中查找URL
            import re
            url_pattern = r'https?://[^\s]+(?:\.mp3|\.wav|\.m4a|music|audio)[^\s]*'
            urls = re.findall(url_pattern, content, re.IGNORECASE)
            
            if urls:
                music_url = urls[0]
                # 移除URL后的内容作为歌词
                lyrics_content = re.sub(url_pattern, '', content, flags=re.IGNORECASE).strip()
                lyrics = lyrics_content if lyrics_content else None
                
                print(f"从内容中提取到音乐链接: {music_url}")
                return music_url, lyrics
            
            print(f"未找到有效的音乐链接，内容: {content[:100]}...")
            return None, None
            
        except Exception as e:
            print(f"解析音乐响应失败: {e}")
            return None, None

# 全局Coze音乐服务实例
coze_music_service = CozeMusicService()
  