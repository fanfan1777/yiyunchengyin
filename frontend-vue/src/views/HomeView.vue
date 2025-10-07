<template>
  <div>
    <StepIndicator :current="currentStep" :labels="['输入创意','优化设置','生成音乐']" />

    <!-- 第一步：输入 -->
    <section :class="['page-section', { active: currentStep === 1 }]" id="input-page">
      <div class="input-tabs">
        <button class="tab-btn" :class="{ active: activeTab === 'text' }" @click="activeTab = 'text'">
          <i class="fas fa-keyboard"></i> 文字描述
        </button>
        <button class="tab-btn" :class="{ active: activeTab === 'image' }" @click="activeTab = 'image'">
          <i class="fas fa-image"></i> 图片上传
        </button>
      </div>

      <div class="tab-content" :class="{ active: activeTab === 'text' }" id="text-tab">
        <div class="input-group">
          <label for="text-input">描述您想要的音乐</label>
          <textarea id="text-input" v-model.trim="textContent" rows="4" placeholder="例如：一首安静的钢琴曲，适合在雨夜阅读时聆听..."></textarea>
        </div>
        <button type="button" class="analyze-btn" @click="analyzeText">
          <i class="fas fa-magic"></i> 开始分析
        </button>
      </div>

      <div class="tab-content" :class="{ active: activeTab === 'image' }" id="image-tab">
        <div class="upload-area" @click="chooseFile" @dragover.prevent="dragOver = true" @dragleave.prevent="dragOver = false" @drop.prevent="onDrop" :class="{ dragover: dragOver }">
          <div class="upload-content">
            <i class="fas fa-cloud-upload-alt"></i>
            <p>拖拽图片到此处或点击上传</p>
            <p class="upload-hint">支持 JPG、PNG、GIF、BMP、WebP，最大 10MB</p>
          </div>
          <input ref="fileInput" type="file" accept="image/*" hidden @change="onFileChange" />
        </div>

        <div class="image-preview" v-show="previewUrl">
          <img :src="previewUrl" alt="预览图片" />
          <button class="remove-btn" @click="removeImage"><i class="fas fa-times"></i></button>
        </div>
        <button type="button" class="analyze-btn" :disabled="!file" @click="analyzeImage">
          <i class="fas fa-magic"></i> 分析图片
        </button>
      </div>
    </section>

    <!-- 第二步：优化设置 -->
    <section :class="['page-section', { active: currentStep === 2 }]" id="optimization-page">
      <div class="understanding-card">
        <h3><i class="fas fa-music"></i> 音乐创作向导</h3>
        <div class="understanding-text">为了更好地创作音乐，请完善以下设置：</div>
        <div class="music-elements-display">
          <div v-for="(v, k) in analysisData.music_elements || {}" :key="k" class="element-tag">
            {{ translateKey(k) }}: {{ Array.isArray(v) ? v.join(', ') : v }}
          </div>
        </div>
      </div>

      <div class="clarification-section">
        <h3><i class="fas fa-sliders-h"></i> 音乐参数设置</h3>
        <p class="clarification-hint">请选择音乐类型和参数，或跳过使用默认设置</p>
        <div class="questions-container">
          <div class="question-card core-selection">
            <div class="question-title core-title">🎤 音乐类型（必选）</div>
            <div class="question-options">
              <button class="option-button" :class="{ selected: voiceType === '纯音乐/BGM' }" @click="selectVoiceType('纯音乐/BGM')">纯音乐/BGM</button>
              <button class="option-button" :class="{ selected: voiceType === '有人声演唱' }" @click="selectVoiceType('有人声演唱')">有人声演唱</button>
            </div>
          </div>

          <div class="question-card ai-suggestion" v-for="q in clarificationQuestions" :key="q.question_id">
            <div class="question-title">{{ q.question }}</div>
            <div class="question-options">
              <button v-for="opt in q.options" :key="opt" class="option-button" :class="{ selected: selectedAnswers[q.question_id] === opt }" @click="selectOption(q.question_id, opt)">{{ opt }}</button>
            </div>
          </div>
        </div>
      </div>

      <div class="music-description-section">
        <h4><i class="fas fa-edit"></i> 音乐描述</h4>
        <div class="input-group">
          <textarea v-model.trim="musicDescription" rows="3" :placeholder="voiceType === '有人声演唱' ? '描述歌曲主题、情感、风格等…' : '描述背景音乐的场景、氛围、用途等…'"></textarea>
          <small class="description-hint">📝 此描述将作为音乐生成的核心提示词，请尽可能详细</small>
        </div>
      </div>

      <div class="api-parameters" :class="{ expanded: parametersExpanded }">
        <div class="parameters-header" @click="parametersExpanded = !parametersExpanded">
          <h4><i class="fas fa-sliders-h"></i> 参数设置</h4>
          <i class="fas fa-chevron-down toggle-icon"></i>
        </div>
        <div class="parameters-content">
          <div class="option-group">
            <label for="duration-slider">音乐时长 (秒)</label>
            <div class="slider-container">
              <input id="duration-slider" type="range" min="30" max="240" v-model.number="duration" />
              <span class="slider-value">{{ duration }}秒</span>
            </div>
          </div>

          <div class="voice-parameters" v-show="voiceType === '有人声演唱'">
            <div class="option-group">
              <label>演唱者性别</label>
              <select v-model="voiceGender">
                <option value="Male">男声</option>
                <option value="Female">女声</option>
              </select>
            </div>
            <div class="option-group">
              <label>音色风格</label>
              <select v-model="voiceTimbre">
                <option value="Warm">温暖</option>
                <option value="Bright">明亮</option>
                <option value="Husky">沙哑</option>
                <option value="Sweet_AUDIO_TIMBRE">甜美</option>
                <option value="Powerful">有力</option>
              </select>
            </div>
          </div>

          <div class="bgm-parameters" v-show="voiceType === '纯音乐/BGM'">
            <div class="option-group">
              <label>主要乐器</label>
              <div class="instruments-grid">
                <label class="checkbox-item"><input type="checkbox" value="piano" v-model="bgmInstruments" /> 钢琴</label>
                <label class="checkbox-item"><input type="checkbox" value="guitar" v-model="bgmInstruments" /> 吉他</label>
                <label class="checkbox-item"><input type="checkbox" value="violin" v-model="bgmInstruments" /> 小提琴</label>
                <label class="checkbox-item"><input type="checkbox" value="drums" v-model="bgmInstruments" /> 鼓</label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="page-actions">
        <button class="back-btn" @click="goToStep(1)"><i class="fas fa-arrow-left"></i> 返回修改</button>
        <button class="skip-btn" @click="generateMusic(true)"><i class="fas fa-forward"></i> 跳过设置</button>
        <button class="continue-btn" @click="generateMusic(false)"><i class="fas fa-arrow-right"></i> 继续生成</button>
      </div>
    </section>

    <!-- 第三步：结果 -->
    <section :class="['page-section', { active: currentStep === 3 }]" id="result-page">
      <div class="result-header">
        <h2><i class="fas fa-music"></i> 您的专属音乐</h2>
        <p class="generation-time">{{ generationTime }}</p>
      </div>
      <AudioPlayer :src="musicUrl || undefined" :fileName="`generated_music_${sessionId}.mp3`" />
      <div class="lyrics-section" v-show="lyrics">
        <div class="lyrics-card">
          <h3><i class="fas fa-music"></i> 歌词</h3>
          <div class="lyrics-display"><pre class="lyrics-text">{{ lyrics }}</pre></div>
        </div>
      </div>
      <div class="page-actions">
        <button class="back-btn" @click="goToStep(2)"><i class="fas fa-arrow-left"></i> 调整参数</button>
        <button class="regenerate-btn" @click="regenerate"><i class="fas fa-redo"></i> 重新生成</button>
        <button class="new-btn" @click="startNew"><i class="fas fa-plus"></i> 创建新音乐</button>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, inject } from 'vue';
import StepIndicator from '../components/StepIndicator.vue';
import AudioPlayer from '../components/AudioPlayer.vue';
import { useUI } from '../composables/ui';

type UpdateStatus = (t: string, type: 'ready'|'analyzing'|'generating'|'error') => void;
const updateStatus = inject<UpdateStatus>('updateStatus')!;
const ui = useUI();

const API_BASE = import.meta.env.VITE_API_BASE ?? '/api';

const currentStep = ref(1);
const activeTab = ref<'text'|'image'>('text');
const textContent = ref('');
const fileInput = ref<HTMLInputElement | null>(null);
const file = ref<File | null>(null);
const previewUrl = ref('');
const dragOver = ref(false);

const sessionId = ref<string | null>(null);
const analysisData = ref<any>({});
const clarificationQuestions = ref<Array<{question_id:string;question:string;options:string[]}>>([]);
const selectedAnswers = ref<Record<string,string>>({});

const voiceType = ref<'纯音乐/BGM'|'有人声演唱'>('纯音乐/BGM');
const parametersExpanded = ref(false);
const musicDescription = ref('');
const duration = ref(30);
const voiceGender = ref<'Male'|'Female'>('Male');
const voiceTimbre = ref('Warm');
const bgmInstruments = ref<string[]>([]);

const musicUrl = ref('');
const lyrics = ref('');
const generationTime = ref('');

function goToStep(step: number) {
  currentStep.value = step;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function chooseFile() {
  fileInput.value?.click();
}

  function onFileChange(e: Event) {
    const target = e.target as HTMLInputElement;
    const f = target.files?.[0];
    if (f) setFile(f);
  }

function onDrop(e: DragEvent) {
  dragOver.value = false;
  const f = e.dataTransfer?.files?.[0];
  if (f) setFile(f);
}

function setFile(f: File) {
  if (f.size > 10 * 1024 * 1024) { ui.showNotification('文件大小不能超过 10MB', 'error'); return; }
  const types = ['image/jpeg','image/png','image/gif','image/bmp','image/webp'];
  if (!types.includes(f.type)) { ui.showNotification('请上传支持的图片格式', 'error'); return; }
  file.value = f;
  const reader = new FileReader();
  reader.onload = e => { previewUrl.value = String(e.target?.result || ''); };
  reader.readAsDataURL(f);
}

function removeImage() {
  file.value = null; previewUrl.value = '';
}

function selectVoiceType(v: '纯音乐/BGM'|'有人声演唱') { voiceType.value = v; }
function selectOption(qid: string, opt: string) { selectedAnswers.value[qid] = opt; }

function translateKey(k: string) {
  const map: Record<string,string> = { style:'风格', mood:'情绪', instruments:'乐器', tempo:'节奏', genre:'类型', atmosphere:'氛围' };
  return map[k] ?? k;
}

async function analyzeText() {
  if (!textContent.value.trim()) { ui.showNotification('请输入文字描述', 'error'); return; }
  try {
    ui.showLoading('AI正在分析您的文字描述...');
    updateStatus('分析中', 'analyzing');
    const form = new FormData();
    form.append('text_content', textContent.value.trim());
    if (sessionId.value) form.append('session_id', sessionId.value);
    const res = await fetch(`${API_BASE}/analyze/text`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    ui.hideLoading();
    if (json.success) {
      sessionId.value = json.session_id;
      analysisData.value = json.data || {};
      clarificationQuestions.value = analysisData.value.clarification_questions || [];
      ui.showNotification('文字分析完成！', 'success');
      goToStep(2);
      updateStatus('优化设置', 'analyzing');
    } else {
      throw new Error(json.message || '分析失败');
    }
  } catch (e: any) {
    ui.hideLoading();
    updateStatus('分析失败', 'error');
    ui.showNotification(`分析失败：${e.message}`, 'error');
  }
}

async function analyzeImage() {
  if (!file.value) { ui.showNotification('请先上传图片', 'error'); return; }
  try {
    ui.showLoading('AI正在分析您的图片...');
    updateStatus('分析中', 'analyzing');
    const form = new FormData();
    form.append('image', file.value);
    if (sessionId.value) form.append('session_id', sessionId.value);
    const res = await fetch(`${API_BASE}/analyze/image`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    ui.hideLoading();
    if (json.success) {
      sessionId.value = json.session_id;
      analysisData.value = json.data || {};
      clarificationQuestions.value = analysisData.value.clarification_questions || [];
      ui.showNotification('图片分析完成！', 'success');
      goToStep(2);
      updateStatus('优化设置', 'analyzing');
    } else { throw new Error(json.message || '分析失败'); }
  } catch (e: any) {
    ui.hideLoading(); updateStatus('分析失败', 'error'); ui.showNotification(`分析失败：${e.message}`, 'error');
  }
}

function collectParams() {
  const base: any = { music_description: musicDescription.value, duration: duration.value, voice_type: voiceType.value };
  if (voiceType.value === '有人声演唱') {
    base.voice_params = { gender: voiceGender.value, timbre: voiceTimbre.value };
  } else {
    base.bgm_params = { instruments: bgmInstruments.value.length ? bgmInstruments.value : ['piano'] };
  }
  return base;
}

async function submitClarificationsIfAny() {
  if (!sessionId.value) return;
  const entries = Object.entries(selectedAnswers.value);
  for (const [qid, opt] of entries) {
    const res = await fetch(`${API_BASE}/clarify`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ session_id: sessionId.value, question_id: qid, selected_option: opt }) });
    const json = await res.json(); if (!json.success) throw new Error(json.message || '澄清提交失败');
  }
}

async function generateMusic(skip: boolean) {
  if (!sessionId.value) { ui.showNotification('请先进行分析', 'error'); return; }
  try {
    ui.showLoading('正在生成音乐，请稍候...'); updateStatus('生成中', 'generating');
    if (!skip && Object.keys(selectedAnswers.value).length) await submitClarificationsIfAny();
    const res = await fetch(`${API_BASE}/generate/${sessionId.value}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(collectParams()) });
    const json = await res.json(); ui.hideLoading();
    if (json.success) {
      const data = json.data || {};
      musicUrl.value = data.music_url || '';
      lyrics.value = data.lyrics || '';
      generationTime.value = new Date().toLocaleString();
      goToStep(3); updateStatus('生成完成', 'ready'); ui.showNotification('音乐生成成功！', 'success');
    } else {
      updateStatus('生成失败', 'error'); ui.showNotification(`音乐生成失败：${json.message}`, 'error');
    }
  } catch (e: any) { ui.hideLoading(); updateStatus('生成失败', 'error'); ui.showNotification(`音乐生成失败：${e.message}`, 'error'); }
}

async function regenerate() { await generateMusic(false); }
function startNew() {
  if (!confirm('确定要开始新的音乐创作吗？当前进度将会丢失。')) return;
  sessionId.value = null; analysisData.value = {}; clarificationQuestions.value = []; selectedAnswers.value = {};
  textContent.value = ''; musicDescription.value = ''; duration.value = 30; voiceGender.value = 'Male'; voiceTimbre.value = 'Warm'; bgmInstruments.value = [];
  removeImage(); goToStep(1); updateStatus('准备就绪', 'ready'); ui.showNotification('已开始新的创作会话', 'info');
}
</script>

<style scoped>
</style>


