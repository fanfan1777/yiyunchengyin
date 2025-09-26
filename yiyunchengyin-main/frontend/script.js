// 全局变量
let currentSessionId = null;
let currentClarificationQuestions = [];
let currentStep = 1;
let analysisData = null;
let selectedAnswers = {};
let isGenerating = false; // 防重复生成标志
let isSubmittingClarification = false; // 防重复澄清提交标志
const API_BASE_URL = 'http://127.0.0.1:8000/api';

// DOM元素
const stepIndicator = document.querySelector('.step-indicator');
const inputPage = document.getElementById('input-page');
const optimizationPage = document.getElementById('optimization-page');
const resultPage = document.getElementById('result-page');
const uploadArea = document.getElementById('upload-area');
const imageInput = document.getElementById('image-input');
const imagePreview = document.getElementById('image-preview');
const previewImage = document.getElementById('preview-image');
const analyzeImageBtn = document.getElementById('analyze-image-btn');
const loadingOverlay = document.getElementById('loading-overlay');
const statusIndicator = document.getElementById('status-indicator');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    initializeTabs();
    initializeUpload();
    initializeSliders();
    updateStatus('准备就绪', 'ready');
    goToStep(1);
    
    // 🔍 添加页面导航监听，调试跳转问题
    window.addEventListener('beforeunload', function(e) {
        console.log('🔍 页面即将卸载/刷新');
        console.trace('🔍 页面卸载调用栈');
    });
    
    // 监听历史记录变化
    window.addEventListener('popstate', function(e) {
        console.log('🔍 浏览器历史记录变化');
        console.log('🔍 当前URL:', window.location.href);
    });
    
    // 全局错误处理
    window.addEventListener('error', function(e) {
        console.error('🔍 全局JavaScript错误:', e.error);
        console.log('🔍 错误发生在:', e.filename, '行', e.lineno);
    });
});

// === 步骤管理 ===
function goToStep(step) {
    console.log('🔍 goToStep被调用，目标步骤:', step, '当前步骤:', currentStep);
    currentStep = step;
    
    // 更新步骤指示器
    updateStepIndicator();
    
    // 隐藏所有页面
    document.querySelectorAll('.page-section').forEach(page => {
        page.classList.remove('active');
    });
    
    // 显示当前页面
    switch(step) {
        case 1:
            inputPage.classList.add('active');
            break;
        case 2:
            optimizationPage.classList.add('active');
            break;
        case 3:
            resultPage.classList.add('active');
            break;
    }
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function updateStepIndicator() {
    const steps = stepIndicator.querySelectorAll('.step');
    steps.forEach((step, index) => {
        const stepNumber = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNumber < currentStep) {
            step.classList.add('completed');
        } else if (stepNumber === currentStep) {
            step.classList.add('active');
        }
    });
}

// === 标签页功能 ===
function initializeTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            
            // 更新标签按钮状态
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            
            // 更新内容区域
            tabContents.forEach(content => {
                content.classList.remove('active');
                if (content.id === `${tabName}-tab`) {
                    content.classList.add('active');
                }
            });
        });
    });
}

// === 文件上传功能 ===
function initializeUpload() {
    // 点击上传
    uploadArea.addEventListener('click', () => {
        imageInput.click();
    });

    // 文件选择
    imageInput.addEventListener('change', handleFileSelect);

    // 拖拽上传
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        handleFile(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    uploadArea.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('请上传支持的图片格式：JPG、PNG、GIF、BMP、WebP', 'error');
        return;
    }

    // 验证文件大小（10MB）
    if (file.size > 10 * 1024 * 1024) {
        showNotification('文件大小不能超过 10MB', 'error');
        return;
    }

    // 显示预览
    const reader = new FileReader();
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        uploadArea.style.display = 'none';
        imagePreview.style.display = 'block';
        analyzeImageBtn.disabled = false;
    };
    reader.readAsDataURL(file);
}

function removeImage() {
    imageInput.value = '';
    uploadArea.style.display = 'block';
    imagePreview.style.display = 'none';
    analyzeImageBtn.disabled = true;
}

// === 滑块控制 ===
function initializeSliders() {
    const durationSlider = document.getElementById('duration-slider');
    
    if (durationSlider) {
        durationSlider.addEventListener('input', (e) => {
            document.getElementById('duration-value').textContent = `${e.target.value}秒`;
        });
    }
}

// 旧的高级选项切换函数已删除，使用toggleParameters替代

// === 信息标签页 ===

// === API调用 ===

// 文本分析
async function analyzeText(event) {
    console.log('🔍 analyzeText函数被调用');
    
    // 🔧 强制阻止任何默认行为和事件冒泡
    if (event) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
    }
    
    const textContent = document.getElementById('text-input').value.trim();
    
    if (!textContent) {
        showNotification('请输入文字描述', 'error');
        return;
    }

    try {
        showLoading('AI正在分析您的文字描述...');
        updateStatus('分析中', 'analyzing');

        const formData = new FormData();
        formData.append('text_content', textContent);
        if (currentSessionId) {
            formData.append('session_id', currentSessionId);
        }

        const response = await fetch(`${API_BASE_URL}/analyze/text`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }

        const result = await response.json();
        hideLoading();

        if (result.success) {
            currentSessionId = result.session_id;
            analysisData = result.data;
            console.log('接收到的分析数据:', analysisData);
            console.log('理解结果类型:', typeof analysisData.understanding);
            console.log('理解结果内容:', analysisData.understanding);
            showOptimizationPage();
            showNotification('文字分析完成！', 'success');
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('分析错误:', error);
        hideLoading();
        updateStatus('分析失败', 'error');
        
        if (error.message.includes('Failed to fetch')) {
            showNotification('连接失败：请确保后端服务已启动（http://127.0.0.1:8000）', 'error');
        } else {
            showNotification(`分析失败：${error.message}`, 'error');
        }
    }
}

// 图片分析
async function analyzeImage(event) {
    console.log('🔍 analyzeImage函数被调用');
    
    // 🔧 强制阻止任何默认行为和事件冒泡
    if (event) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        console.log('🔍 已阻止事件默认行为');
    }
    
    // 🔧 临时禁用所有可能导致页面刷新的全局事件
    const originalOnBeforeUnload = window.onbeforeunload;
    const originalOnUnload = window.onunload;
    
    // 🔧 完全阻止页面卸载
    window.onbeforeunload = function(e) {
        console.log('🔍 阻止页面卸载');
        e.preventDefault();
        return false;
    };
    window.onunload = function(e) {
        console.log('🔍 阻止页面unload');
        e.preventDefault();
        return false;
    };
    
    const file = imageInput.files[0];
    
    if (!file) {
        showNotification('请先上传图片', 'error');
        return;
    }

    try {
        console.log('🔍 开始图片分析流程');
        showLoading('AI正在分析您的图片...');
        updateStatus('分析中', 'analyzing');
        
        // 🔧 临时移除防刷新警告，找出真正的刷新原因
        // window.onbeforeunload = function(e) {
        //     console.log('🔍 检测到页面即将刷新，正在阻止');
        //     e.preventDefault();
        //     e.returnValue = '';
        //     return '图片正在分析中，确定要离开吗？';
        // };

        const formData = new FormData();
        formData.append('image', file);
        if (currentSessionId) {
            formData.append('session_id', currentSessionId);
        }

        console.log('🔍 开始发送fetch请求');
        console.log('🔍 FormData内容检查:', formData.has('image'));
        
        // 🔧 使用XMLHttpRequest替代fetch，避免可能的页面刷新问题
        const response = await new Promise((resolve, reject) => {
            const xhr = new XMLHttpRequest();
            
            xhr.onload = () => {
                console.log('🔍 XMLHttpRequest请求完成，状态:', xhr.status);
                resolve({
                    ok: xhr.status >= 200 && xhr.status < 300,
                    status: xhr.status,
                    json: () => Promise.resolve(JSON.parse(xhr.responseText))
                });
            };
            
            xhr.onerror = () => {
                console.log('🔍 XMLHttpRequest请求出错');
                reject(new Error('Network error'));
            };
            
            xhr.open('POST', `${API_BASE_URL}/analyze/image`);
            xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
            
            console.log('🔍 发送XMLHttpRequest请求');
            console.log('🔍 即将发送请求，检查页面状态');
            
            // 🔧 延迟发送请求，观察是否在发送前就刷新
            setTimeout(() => {
                console.log('🔍 延迟后发送请求');
                xhr.send(formData);
            }, 100);
        });
        
        console.log('🔍 请求完成，响应状态:', response.status);

        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }

        console.log('🔍 开始解析JSON响应');
        const result = await response.json();
        console.log('🔍 JSON解析完成，结果:', result.success);
        console.log('🔍 完整result对象:', result);
        hideLoading();

        if (result.success) {
            console.log('🔍 图片分析成功，返回数据:', result);
            console.log('🔍 result.data类型:', typeof result.data);
            console.log('🔍 result.data内容:', result.data);
            
            // 🔧 详细检查数据结构
            if (!result.data) {
                console.error('🔍 ❌ result.data 为空或undefined');
                throw new Error('服务器返回的数据为空');
            }
            
            currentSessionId = result.session_id;
            analysisData = result.data;
            
            console.log('🔍 currentSessionId设置为:', currentSessionId);
            console.log('🔍 analysisData设置为:', analysisData);
            console.log('🔍 准备调用showOptimizationPage');
            
            // 🔧 确保showOptimizationPage被调用
            console.log('🔍 ===== 即将调用showOptimizationPage =====');
            showOptimizationPage();
            console.log('🔍 ===== showOptimizationPage调用完成 =====');
            
            showNotification('图片分析完成！', 'success');
            
            // 🔧 恢复原始的页面事件处理
            window.onbeforeunload = originalOnBeforeUnload;
            window.onunload = originalOnUnload;
            console.log('🔍 已恢复页面事件处理');
        } else {
            throw new Error(result.message);
        }
    } catch (error) {
        console.error('🔍 图片分析出错:', error);
        
        // 🔧 专注于错误分析
        console.log('🔍 图片分析流程出错');
        
        // 🔧 出错时也要恢复页面事件处理
        window.onbeforeunload = originalOnBeforeUnload;
        window.onunload = originalOnUnload;
        console.log('🔍 出错时恢复页面事件处理');
        
        hideLoading();
        updateStatus('分析失败', 'error');
        showNotification(`分析失败：${error.message}`, 'error');
    }
}

// === 优化页面显示 ===
function showOptimizationPage() {
    try {
        // 🐛 调试输出 - 检查图片分析跳转问题
        console.log('🔍 showOptimizationPage被调用');
        console.log('🔍 当前步骤:', currentStep);
        console.log('🔍 analysisData:', analysisData);
        console.log('🔍 analysisData类型:', typeof analysisData);
        
        // 🔧 数据有效性检查
        if (!analysisData) {
            console.error('🔍 ❌ analysisData为空');
            throw new Error('分析数据为空');
        }
        
        console.log('🔍 analysisData.needs_clarification:', analysisData.needs_clarification);
        console.log('🔍 analysisData.clarification_questions:', analysisData.clarification_questions);
    
    // 显示AI理解结果（确保是字符串格式）
    console.log('showOptimizationPage - analysisData:', analysisData);
    console.log('showOptimizationPage - understanding字段:', analysisData.understanding);
    console.log('showOptimizationPage - understanding类型:', typeof analysisData.understanding);
    
    // 简化AI理解结果，避免与第1页重复
    let understanding = '为了更好地创作音乐，请完善以下设置：';
    
    console.log('优化页面显示简化的理解结果:', understanding);
    document.getElementById('understanding-display').textContent = understanding;
    
    // 显示音乐元素
    const elementsContainer = document.getElementById('music-elements-display');
    elementsContainer.innerHTML = '';
    
    if (analysisData.music_elements) {
        Object.entries(analysisData.music_elements).forEach(([key, value]) => {
            if (value && value !== 'unknown') {
                const tag = document.createElement('div');
                tag.className = 'element-tag';
                tag.textContent = `${translateKey(key)}: ${Array.isArray(value) ? value.join(', ') : value}`;
                elementsContainer.appendChild(tag);
            }
        });
    }
    
    // 始终显示选项区域，确保用户有选择
    document.getElementById('clarification-section').style.display = 'block';
    
    // 永远先显示核心的音乐类型选择
    displayMusicTypeSelection();
    
    // 然后显示AI澄清问题（如果有的话）
    if (analysisData.needs_clarification && analysisData.clarification_questions) {
        currentClarificationQuestions = analysisData.clarification_questions;
        displayAdditionalClarifications();
    }
    
    // 切换到优化页面
    console.log('🔍 调用goToStep(2)');
    goToStep(2);
    updateStatus('优化设置', 'analyzing');
    console.log('🔍 showOptimizationPage执行完成，当前步骤应为2:', currentStep);
} catch (error) {
    console.error('🔍 showOptimizationPage出错:', error);
    try { hideLoading(); } catch (e) {}
    try { updateStatus('分析失败', 'error'); } catch (e) {}
    try { showNotification(`显示优化页面失败：${error.message}`, 'error'); } catch (e) {}
}
}

// 显示澄清问题
function displayClarificationQuestions() {
    const container = document.getElementById('questions-container');
    container.innerHTML = '';
    
    currentClarificationQuestions.forEach((question, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'question-card';
        
        questionCard.innerHTML = `
            <div class="question-title">${question.question}</div>
            <div class="question-options" data-question-id="${question.question_id}">
                ${question.options.map((option, optionIndex) => `
                    <button class="option-button" 
                            data-question-id="${question.question_id}" 
                            data-option="${option}"
                            onclick="selectOption('${question.question_id}', '${option}', this)">
                        ${option}
                    </button>
                `).join('')}
            </div>
        `;
        
        container.appendChild(questionCard);
    });
}

// 永远显示的核心音乐类型选择
function displayMusicTypeSelection() {
    const container = document.getElementById('questions-container');
    
    // 创建核心音乐类型选择区域
    const coreTypeCard = document.createElement('div');
    coreTypeCard.className = 'question-card core-selection';
    
    coreTypeCard.innerHTML = `
        <div class="question-title core-title">🎤 音乐类型（必选）</div>
        <div class="question-options" data-question-id="voice_type">
            <button class="option-button" 
                    data-question-id="voice_type" 
                    data-option="纯音乐/BGM"
                    onclick="selectOption('voice_type', '纯音乐/BGM', this)">
                纯音乐/BGM
            </button>
            <button class="option-button" 
                    data-question-id="voice_type" 
                    data-option="有人声演唱"
                    onclick="selectOption('voice_type', '有人声演唱', this)">
                有人声演唱
            </button>
        </div>
    `;
    
    container.appendChild(coreTypeCard);
    
    // 添加核心选择到全局变量中，确保后续处理能找到
    const coreQuestion = {
        question_id: 'voice_type',
        question: '🎤 音乐类型（必选）',
        options: ['纯音乐/BGM', '有人声演唱']
    };
    
    // 如果还没有currentClarificationQuestions，初始化它
    if (!currentClarificationQuestions || currentClarificationQuestions.length === 0) {
        currentClarificationQuestions = [coreQuestion];
    } else {
        // 检查是否已有核心问题，避免重复添加
        const hasVoiceType = currentClarificationQuestions.some(q => q.question_id === 'voice_type');
        if (!hasVoiceType) {
            currentClarificationQuestions.unshift(coreQuestion);
        }
    }
    
    // 更新澄清区域的标题和提示
    const clarificationTitle = document.querySelector('.clarification-section h3');
    const clarificationHint = document.querySelector('.clarification-hint');
    
    if (clarificationTitle) {
        clarificationTitle.textContent = '🎵 音乐参数设置';
    }
    if (clarificationHint) {
        clarificationHint.textContent = '请选择音乐类型和具体参数，或直接跳过使用默认设置';
    }
}

// 显示AI澄清问题作为附加选项
function displayAdditionalClarifications() {
    const container = document.getElementById('questions-container');
    
    // 添加分割线
    const separator = document.createElement('div');
    separator.className = 'section-separator';
    separator.innerHTML = '<span>AI建议的参数选择</span>';
    container.appendChild(separator);
    
    // 显示AI的澄清问题
    currentClarificationQuestions.forEach((question, index) => {
        const questionCard = document.createElement('div');
        questionCard.className = 'question-card ai-suggestion';
        
        questionCard.innerHTML = `
            <div class="question-title">${question.question}</div>
            <div class="question-options" data-question-id="${question.question_id}">
                ${question.options.map((option, optionIndex) => `
                    <button class="option-button" 
                            data-question-id="${question.question_id}" 
                            data-option="${option}"
                            onclick="selectOption('${question.question_id}', '${option}', this)">
                        ${option}
                    </button>
                `).join('')}
            </div>
        `;
        
        container.appendChild(questionCard);
    });
}

// 备用函数：如果AI没有澄清问题时的基本选项（保持兼容性）
function displayBasicMusicOptions() {
    // 现在这个函数只是调用音乐类型选择
    displayMusicTypeSelection();
}
 
// 选择选项
function selectOption(questionId, option, buttonElement) {
    // 清除同一问题的其他选项
    const optionsContainer = buttonElement.parentElement;
    optionsContainer.querySelectorAll('.option-button').forEach(btn => {
        btn.classList.remove('selected');
    });
    
    // 选中当前选项
    buttonElement.classList.add('selected');
    selectedAnswers[questionId] = option;
    
    // 根据音乐类型选择，动态显示相应参数
    if (questionId === 'voice_type') {
        updateParameterVisibility(option);
    }
}

// 根据音乐类型更新参数可见性
function updateParameterVisibility(musicType) {
    const voiceParameters = document.getElementById('voice-parameters');
    const bgmParameters = document.getElementById('bgm-parameters');
    const descriptionTextarea = document.getElementById('music-description');
    
    if (musicType === '有人声演唱') {
        // 显示人声参数，隐藏BGM参数
        if (voiceParameters) voiceParameters.style.display = 'block';
        if (bgmParameters) bgmParameters.style.display = 'none';
        if (descriptionTextarea) {
            descriptionTextarea.placeholder = '请描述歌曲的主题、情感、风格等（将作为歌曲提示词）...';
        }
        console.log('🎤 切换到有人声模式');
    } else if (musicType === '纯音乐/BGM') {
        // 显示BGM参数，隐藏人声参数  
        if (voiceParameters) voiceParameters.style.display = 'none';
        if (bgmParameters) bgmParameters.style.display = 'block';
        if (descriptionTextarea) {
            descriptionTextarea.placeholder = '请描述背景音乐的场景、氛围、用途等（将作为BGM生成提示词）...';
        }
        console.log('🎵 切换到纯音乐模式');
    }
}

// 切换参数设置区域
function toggleParameters() {
    const parametersDiv = document.getElementById('api-parameters');
    if (parametersDiv) {
        parametersDiv.classList.toggle('expanded');
    }
}

// 收集音乐生成参数
function collectMusicParameters() {
    const musicDescription = document.getElementById('music-description').value.trim();
    const duration = parseInt(document.getElementById('duration-slider').value);
    const voiceType = selectedAnswers['voice_type'] || '纯音乐/BGM';
    
    const params = {
        music_description: musicDescription,
        duration: duration,
        voice_type: voiceType
    };
    
    if (voiceType === '有人声演唱') {
        // 获取人声参数
        const gender = document.getElementById('voice-gender')?.value || 'Male';
        const timbre = document.getElementById('voice-timbre')?.value || 'Warm';
        
        params.voice_params = {
            gender: gender,
            timbre: timbre
        };
    } else {
        // 获取BGM参数
        const selectedInstruments = [];
        const instrumentCheckboxes = document.querySelectorAll('#bgm-parameters input[type="checkbox"]:checked');
        instrumentCheckboxes.forEach(cb => {
            selectedInstruments.push(cb.value);
        });
        
        params.bgm_params = {
            instruments: selectedInstruments.length > 0 ? selectedInstruments : ['piano'] // 默认钢琴
        };
    }
    
    return params;
}

// === 页面操作 ===
function skipOptimization() {
    // 防重复点击检查
    if (isGenerating) {
        showNotification('音乐正在生成中，请耐心等待...', 'warning');
        console.log('⚠️ 防重复点击：音乐生成已在进行中，忽略跳过优化请求');
        return;
    }
    
    // 直接生成音乐，不进行澄清
    generateMusic();
}

async function continueToGeneration() {
    // 防重复点击检查
    if (isGenerating) {
        showNotification('音乐正在生成中，请耐心等待...', 'warning');
        console.log('⚠️ 防重复点击：音乐生成已在进行中，忽略继续生成请求');
        return;
    }
    
    if (isSubmittingClarification) {
        showNotification('设置正在保存中，请稍候...', 'warning');
        console.log('⚠️ 澄清正在提交中，等待完成后再生成');
        return;
    }
    
    // 如果有澄清问题且用户选择了答案，先提交澄清
    if (currentClarificationQuestions.length > 0 && Object.keys(selectedAnswers).length > 0) {
        await submitAllClarifications();
    }
    
    // 生成音乐
    generateMusic();
}

// 提交所有澄清答案
async function submitAllClarifications() {
    // 防重复提交检查
    if (isSubmittingClarification) {
        console.log('⚠️ 澄清正在提交中，忽略重复请求');
        return;
    }
    
    // 检查是否有选择
    if (Object.keys(selectedAnswers).length === 0) {
        console.log('⚠️ 没有选择任何选项，跳过澄清提交');
        return;
    }
    
    try {
        isSubmittingClarification = true;
        console.log('🔄 开始提交澄清答案:', selectedAnswers);
        
        for (const [questionId, selectedOption] of Object.entries(selectedAnswers)) {
            const clarificationData = {
                session_id: currentSessionId,
                question_id: questionId,
                selected_option: selectedOption
            };

            console.log(`📤 提交澄清: ${questionId} = ${selectedOption}`);
            const response = await fetch(`${API_BASE_URL}/clarify`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(clarificationData)
            });

            const result = await response.json();
            if (!result.success) {
                throw new Error(result.message);
            }
        }
        
        console.log('✅ 所有澄清答案提交完成');
        showNotification('优化设置已保存', 'success');
    } catch (error) {
        console.error('澄清提交失败:', error);
        showNotification(`设置保存失败：${error.message}`, 'error');
    } finally {
        isSubmittingClarification = false;
    }
}

// 防重复点击功能
function setGeneratingState(generating) {
    isGenerating = generating;
    
    // 禁用/启用生成相关按钮
    const generateButtons = [
        document.querySelector('.continue-btn'),
        document.querySelector('.skip-btn'),
        document.querySelector('.regenerate-btn')
    ];
    
    generateButtons.forEach(btn => {
        if (btn) {
            btn.disabled = generating;
            if (generating) {
                btn.classList.add('disabled');
                // 保存原始文本
                if (!btn.dataset.originalText) {
                    btn.dataset.originalText = btn.innerHTML;
                }
                // 设置生成中状态
                btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 生成中...';
            } else {
                btn.classList.remove('disabled');
                // 恢复原始文本
                if (btn.dataset.originalText) {
                    btn.innerHTML = btn.dataset.originalText;
                }
            }
        }
    });
}

// 生成音乐
async function generateMusic() {
    if (!currentSessionId) {
        showNotification('请先进行分析', 'error');
        return;
    }

    // 防重复点击检查
    if (isGenerating) {
        showNotification('音乐正在生成中，请耐心等待...', 'warning');
        console.log('⚠️ 防重复点击：音乐生成已在进行中，忽略重复请求');
        return;
    }

    try {
        // 设置生成状态
        setGeneratingState(true);
        showLoading('正在生成音乐，请稍候...');
        updateStatus('生成中', 'generating');
        
        console.log('🎵 开始音乐生成...');

        // 获取真实的API参数
        const musicParams = collectMusicParameters();
        console.log('🎯 收集到的音乐参数:', musicParams);
        
        const response = await fetch(`${API_BASE_URL}/generate/${currentSessionId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(musicParams)
        });

        const result = await response.json();
        hideLoading();

        if (result.success) {
            displayGeneratedMusic(result.data);
            goToStep(3);
            updateStatus('生成完成', 'ready');
            showNotification('音乐生成成功！', 'success');
            console.log('✅ 音乐生成成功完成');
        } else {
            // 显示详细的错误信息
            showDetailedError(result.message, result.data);
            throw new Error(result.message);
        }
    } catch (error) {
        hideLoading();
        updateStatus('生成失败', 'error');
        console.log('❌ 音乐生成失败:', error.message);
        
        // 如果没有详细错误信息，显示简单通知
        if (!error.detailed) {
            showNotification(`音乐生成失败：${error.message}`, 'error');
        }
    } finally {
        // 无论成功还是失败，都要重置生成状态
        setGeneratingState(false);
        console.log('🔓 音乐生成状态已重置');
    }
}

// 显示生成的音乐
function displayGeneratedMusic(data) {
    console.log('显示音乐数据:', data);
    
    // 设置生成时间
    const now = new Date();
    document.getElementById('generation-time').textContent = 
        `生成于 ${now.toLocaleString()}`;
    
    // 设置音频播放器
    const audioPlayer = document.getElementById('audio-player');
    console.log('音乐链接:', data.music_url);
    
    if (data.music_url) {
        audioPlayer.src = data.music_url;
        console.log('音频播放器源已设置:', audioPlayer.src);
        
        // 尝试加载音频
        audioPlayer.load();
        
        // 添加加载事件监听
        audioPlayer.addEventListener('loadedmetadata', function() {
            console.log('音频元数据已加载，时长:', audioPlayer.duration);
        });
        
        audioPlayer.addEventListener('error', function(e) {
            console.error('音频加载错误:', e);
            showNotification('音频加载失败，请检查音乐链接是否有效', 'error');
        });
    } else {
        console.warn('没有音乐链接');
        showNotification('未获取到音乐链接', 'warning');
    }
    
    // 显示歌词（如果有）
    if (data.lyrics) {
        const lyricsSection = document.getElementById('lyrics-section');
        const lyricsDisplay = document.getElementById('lyrics-display');
        
        // 显示歌词区域和内容
        lyricsSection.style.display = 'block';
        lyricsDisplay.innerHTML = `<pre class="lyrics-text">${data.lyrics}</pre>`;
        console.log('显示歌词:', data.lyrics);
    } else {
        // 隐藏歌词区域
        const lyricsSection = document.getElementById('lyrics-section');
        lyricsSection.style.display = 'none';
        console.log('无歌词内容');
    }
}

// 重新生成音乐
async function regenerateMusic() {
    // 防重复点击检查
    if (isGenerating) {
        showNotification('音乐正在生成中，请耐心等待...', 'warning');
        console.log('⚠️ 防重复点击：重新生成被阻止，音乐生成已在进行中');
        return;
    }
    
    if (confirm('确定要重新生成音乐吗？这将使用当前设置重新创作。')) {
        await generateMusic();
    }
}

// 下载音乐
function downloadMusic() {
    const audioPlayer = document.getElementById('audio-player');
    if (audioPlayer.src) {
        const link = document.createElement('a');
        link.href = audioPlayer.src;
        link.download = `generated_music_${currentSessionId}.mp3`;
        link.click();
        showNotification('开始下载音乐文件', 'success');
    } else {
        showNotification('没有可下载的音乐文件', 'error');
    }
}

// 分享音乐
function shareMusic() {
    if (navigator.share) {
        navigator.share({
            title: 'AI生成的音乐',
            text: '我用AI生成了一首音乐，快来听听吧！',
            url: window.location.href
        });
    } else {
        // 复制链接到剪贴板
        navigator.clipboard.writeText(window.location.href).then(() => {
            showNotification('链接已复制到剪贴板', 'success');
        });
    }
}

// 开始新会话
function startNewSession() {
    // 防重复检查 - 如果正在生成音乐，提醒用户
    if (isGenerating) {
        const confirmed = confirm('音乐正在生成中，确定要放弃当前生成并开始新的创作吗？');
        if (!confirmed) {
            return;
        }
    }
    
    if (confirm('确定要开始新的音乐创作吗？当前进度将会丢失。')) {
        // 重置所有状态
        currentSessionId = null;
        currentClarificationQuestions = [];
        analysisData = null;
        selectedAnswers = {};
        
        // 重置生成状态和按钮
        setGeneratingState(false);
        isSubmittingClarification = false;
        
        // 清空输入
        document.getElementById('text-input').value = '';
        const musicDescription = document.getElementById('music-description');
        if (musicDescription) musicDescription.value = '';
        removeImage();
        
        // 重置滑块
        document.getElementById('duration-slider').value = 30;
        document.getElementById('duration-value').textContent = '30秒';
        
        // 重置选择器
        const voiceGender = document.getElementById('voice-gender');
        const voiceTimbre = document.getElementById('voice-timbre');
        if (voiceGender) voiceGender.value = 'Male';
        if (voiceTimbre) voiceTimbre.value = 'Warm';
        
        // 清空乐器选择
        const instrumentCheckboxes = document.querySelectorAll('#bgm-parameters input[type="checkbox"]');
        instrumentCheckboxes.forEach(cb => cb.checked = false);
        
        // 回到第一步
        goToStep(1);
        updateStatus('准备就绪', 'ready');
        showNotification('已开始新的创作会话', 'info');
    }
}

// === 工具函数 ===

// 更新状态指示器
function updateStatus(text, type) {
    const statusText = statusIndicator.querySelector('.status-text');
    const statusDot = statusIndicator.querySelector('.status-dot');
    
    statusText.textContent = text;
    statusDot.className = `status-dot ${type}`;
}

// 显示加载指示器
function showLoading(text = '加载中...') {
    const loadingText = document.querySelector('.loading-text');
    loadingText.textContent = text;
    loadingOverlay.style.display = 'flex';
}

// 隐藏加载指示器
function hideLoading() {
    loadingOverlay.style.display = 'none';
}

// 显示详细错误信息
function showDetailedError(message, errorData) {
    // 创建详细错误模态框
    const modal = document.createElement('div');
    modal.className = 'error-modal-overlay';
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0,0,0,0.7);
        z-index: 10001;
        display: flex;
        align-items: center;
        justify-content: center;
        backdrop-filter: blur(5px);
    `;
    
    const content = document.createElement('div');
    content.className = 'error-modal-content';
    content.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 30px;
        max-width: 500px;
        width: 90%;
        max-height: 70vh;
        overflow-y: auto;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        animation: errorModalShow 0.3s ease;
    `;
    
    let suggestionsHTML = '';
    if (errorData && errorData.suggestions && errorData.suggestions.length > 0) {
        suggestionsHTML = `
            <div class="error-suggestions">
                <h4 style="color: #f59e0b; margin-bottom: 15px;">💡 解决建议：</h4>
                <ul style="margin: 0; padding-left: 20px; color: #666;">
                    ${errorData.suggestions.map(suggestion => `<li style="margin-bottom: 8px;">${suggestion}</li>`).join('')}
                </ul>
            </div>
        `;
    }
    
    content.innerHTML = `
        <div class="error-header" style="display: flex; align-items: center; margin-bottom: 20px;">
            <div style="width: 48px; height: 48px; background: #fee2e2; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 15px;">
                <span style="font-size: 24px;">⚠️</span>
            </div>
            <div>
                <h3 style="color: #ef4444; margin: 0; font-size: 20px;">音乐生成失败</h3>
                <p style="color: #666; margin: 5px 0 0 0; font-size: 14px;">遇到了一些技术问题</p>
            </div>
        </div>
        
        <div class="error-message" style="margin-bottom: 20px;">
            <p style="color: #333; font-size: 16px; line-height: 1.5; margin: 0;">${message}</p>
        </div>
        
        ${suggestionsHTML}
        
        <div class="error-actions" style="margin-top: 30px; display: flex; gap: 10px; justify-content: flex-end;">
            <button onclick="closeErrorModal()" style="padding: 10px 20px; border: 1px solid #ddd; background: white; border-radius: 6px; cursor: pointer; color: #666;">
                关闭
            </button>
            <button onclick="closeErrorModal(); goToStep(2);" style="padding: 10px 20px; border: none; background: #3b82f6; color: white; border-radius: 6px; cursor: pointer;">
                重新配置
            </button>
        </div>
    `;
    
    // 添加样式动画
    if (!document.querySelector('#error-modal-styles')) {
        const styles = document.createElement('style');
        styles.id = 'error-modal-styles';
        styles.textContent = `
            @keyframes errorModalShow {
                from { transform: scale(0.9); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    modal.appendChild(content);
    document.body.appendChild(modal);
    
    // 点击背景关闭
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeErrorModal();
        }
    });
    
    // 标记为详细错误，避免重复显示  
    const error = new Error(message);
    error.detailed = true;
    throw error;
}

// 关闭错误模态框
function closeErrorModal() {
    const modal = document.querySelector('.error-modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// 显示通知
function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 3000);
}

// 翻译键名
function translateKey(key) {
    const translations = {
        'style': '风格',
        'mood': '情绪',
        'instruments': '乐器',
        'tempo': '节奏',
        'genre': '类型',
        'atmosphere': '氛围'
    };
    return translations[key] || key;
}

// 错误处理
window.addEventListener('error', function(event) {
    console.error('JavaScript错误:', event.error);
    hideLoading();
    showNotification('发生了一个错误，请刷新页面重试', 'error');
});

// 网络错误处理
window.addEventListener('unhandledrejection', function(event) {
    console.error('未处理的Promise拒绝:', event.reason);
    hideLoading();
    showNotification('网络连接错误，请检查后端服务是否启动', 'error');
});