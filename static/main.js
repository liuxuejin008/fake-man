document.addEventListener('DOMContentLoaded', () => {
    // ==================== DOM 元素 ====================
    const promptInput = document.getElementById('promptInput');
    const btnRandom = document.getElementById('btnRandom');
    const btnGenerate = document.getElementById('btnGenerate');
    const placeholder = document.getElementById('placeholder');
    const generatedImage = document.getElementById('generatedImage');
    const imageActions = document.getElementById('imageActions');
    const loader = document.getElementById('loader');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const downloadBtn = document.getElementById('downloadBtn');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const shareBtn = document.getElementById('shareBtn');
    const styleTabs = document.getElementById('styleTabs');
    const historyBtn = document.getElementById('historyBtn');
    const themeBtn = document.getElementById('themeBtn');
    const historySidebar = document.getElementById('historySidebar');
    const overlay = document.getElementById('overlay');
    const closeHistory = document.getElementById('closeHistory');
    const historyList = document.getElementById('historyList');
    const clearHistory = document.getElementById('clearHistory');

    // ==================== 状态管理 ====================
    let currentStyle = 'alternate';
    let currentImageURL = '';
    let history = JSON.parse(localStorage.getItem('synth_history') || '[]');
    let isDarkTheme = true;

    // ==================== 风格预设 ====================
    const stylePresets = {
        alternate: {
            name: '伪人',
            prompts: [
                'A person standing in a hallway, slightly wrong proportions, empty eyes that stare without blinking, subtle facial asymmetry, faded photograph quality, unsettling stillness, Mandela Catalogue style',
                'A woman at a bus stop, skin too smooth and waxy, smile that extends slightly too wide, dead empty eyes, surveillance camera footage aesthetic, liminal space horror',
                'A man in a business suit, neck bent at an unnatural angle, pupils perfectly round and too black, no shadow cast properly, analog horror, VHS quality',
                'A child in a classroom, body frozen mid-motion, arms at wrong angles, eyes look directly at camera without emotion, Mandela Catalogue alternate style',
                'A figure in a doorway, face partially obscured, one arm longer than the other, skin has subtle texture pattern like static, liminal horror, analog distortion'
            ]
        },
        cyberpunk: {
            name: '赛博朋克',
            prompts: [
                '赛博朋克风格的20岁女孩，银色短发，全息投影眼镜，霓虹灯背景，雨夜深巷',
                '20岁帅气亚裔男孩，机能风穿搭(Techwear)，黑色口罩，身后是东京涩谷街头，高对比度',
                '极具未来感的年轻偶像，半透明发光夹克，背景是巨大的LED屏幕和飞行汽车，8k高清',
                '暗黑机甲风格年轻女性，神秘冷酷，脸部有微妙的发光纹路，身处废弃太空站',
                '赛博朋克风格，霓虹灯街道，未来感服装，发光配饰，高科技城市背景'
            ]
        },
        anime: {
            name: '动漫风格',
            prompts: [
                '日本动漫风格，20岁美少女，粉色长发，校园制服，樱花飘落背景',
                '动漫风格少年，蓝色眼睛，帅气造型，魔法学院背景，奇幻风格',
                '萌系动漫女孩，猫耳发型，可爱表情，梦幻云朵背景',
                '热血动漫男主角，坚毅眼神，战斗服装，火焰背景效果',
                '动漫风格偶像，舞台服装，闪光效果，粉丝荧光棒背景'
            ]
        },
        realistic: {
            name: '写实风格',
            prompts: [
                '写实摄影风格，20岁专业模特，自然光，工作室拍摄，高清肖像',
                '自然生活照，阳光明媚的咖啡馆， casual穿搭，微笑表情',
                '商务风格，职业套装，办公室背景，专业形象照',
                '户外运动风格，运动装，阳光海滩，活力四射',
                '艺术写真，柔光效果，优雅姿态，白色背景'
            ]
        },
        fantasy: {
            name: '奇幻风格',
            prompts: [
                '奇幻精灵公主，尖耳朵，金色长发，森林背景，魔法光效',
                '龙骑士，银色铠甲，手持魔法剑，巨龙背景，史诗感',
                '魔法师，星空长袍，手持法杖，宇宙星空背景',
                '天使神祇，白色羽翼，圣光效果，云端天堂背景',
                '暗夜刺客，黑色紧身衣，神秘面纱，月光森林背景'
            ]
        }
    };

    // ==================== 初始化 ====================
    function init() {
        createParticles();
        updateHistoryList();
        applyTheme();
    }

    // ==================== 粒子效果 ====================
    function createParticles() {
        const particlesContainer = document.getElementById('particles');
        const particleCount = 50;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'particle';
            particle.style.left = Math.random() * 100 + '%';
            particle.style.top = Math.random() * 100 + '%';
            particle.style.animationDelay = Math.random() * 15 + 's';
            particle.style.animationDuration = (Math.random() * 10 + 10) + 's';
            particlesContainer.appendChild(particle);
        }
    }

    // ==================== 风格选择 ====================
    styleTabs.addEventListener('click', (e) => {
        if (e.target.classList.contains('style-tab')) {
            // 移除所有激活状态
            document.querySelectorAll('.style-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            // 激活当前标签
            e.target.classList.add('active');
            currentStyle = e.target.dataset.style;
        }
    });

    // ==================== 随机灵感（OpenRouter 大模型） ====================
    async function fetchRandomInspire() {
        const response = await fetch('/api/inspire', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ style: currentStyle })
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || '灵感生成失败');
        }
        const text = (data.prompt || '').trim();
        if (!text) {
            throw new Error('模型未返回有效描述');
        }
        return text;
    }

    btnRandom.addEventListener('click', async () => {
        const prevLabel = btnRandom.querySelector('.btn-text')?.textContent;
        btnRandom.disabled = true;
        btnGenerate.disabled = true;
        const textEl = btnRandom.querySelector('.btn-text');
        if (textEl) textEl.textContent = '生成中…';

        try {
            promptInput.value = await fetchRandomInspire();

            promptInput.style.animation = 'none';
            setTimeout(() => {
                promptInput.style.animation = 'shake 0.4s ease';
            }, 10);

            showSuccess('AI 已生成新的灵感描述');
        } catch (e) {
            console.error(e);
            showError(e.message || '灵感生成失败');
        } finally {
            btnRandom.disabled = false;
            btnGenerate.disabled = false;
            if (textEl && prevLabel) textEl.textContent = prevLabel;
        }
    });

    // ==================== 生成图片 ====================
    async function generateImage() {
        const prompt = promptInput.value.trim();
        const stylePrompt = stylePresets[currentStyle].prompts[0];
        const finalPrompt = prompt || stylePrompt;

        // UI 状态更新
        errorMessage.classList.add('hidden');
        successMessage.classList.add('hidden');
        placeholder.classList.add('hidden');
        generatedImage.classList.add('hidden');
        imageActions.classList.add('hidden');
        loader.classList.remove('hidden');
        btnGenerate.disabled = true;
        btnRandom.disabled = true;

        try {
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt: finalPrompt })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || '生成失败');
            }

            if (data.status === 'completed' && data.image_url) {
                // 立即返回图片
                await loadImage(data.image_url);
                currentImageURL = data.image_url;
                addToHistory(data.image_url, finalPrompt);
                showSuccess('图片生成成功！');
            } else if (data.task_id) {
                // 开始轮询
                await pollForResult(data.task_id, finalPrompt);
            } else {
                throw new Error('无效的响应格式');
            }

        } catch (error) {
            console.error('Generation error:', error);
            loader.classList.add('hidden');
            placeholder.classList.remove('hidden');
            showError(error.message);
        } finally {
            btnGenerate.disabled = false;
            btnRandom.disabled = false;
        }
    }

    // ==================== 轮询图片生成状态 ====================
    async function pollForResult(taskId, prompt) {
        const maxAttempts = 120;
        let attempts = 0;
        const pollInterval = 5000;

        updateProgress(0);

        while (attempts < maxAttempts) {
            try {
                const response = await fetch(`/api/status/${taskId}`);
                const data = await response.json();

                if (data.status === 'completed' && data.image_url) {
                    await loadImage(data.image_url);
                    currentImageURL = data.image_url;
                    addToHistory(data.image_url, prompt);
                    showSuccess('图片生成成功！');
                    loader.classList.add('hidden');
                    return;
                } else if (data.status === 'failed') {
                    throw new Error(data.error || '图片生成失败');
                }

                const progress = Math.min((attempts * pollInterval / 200000) * 100, 95);
                updateProgress(progress);

                attempts++;
                await sleep(pollInterval);

            } catch (error) {
                console.error('Polling error:', error);
                loader.classList.add('hidden');
                placeholder.classList.remove('hidden');
                showError(error.message);
                return;
            }
        }

        loader.classList.add('hidden');
        placeholder.classList.remove('hidden');
        showError('图片生成超时，请稍后重试');
    }

    function updateProgress(percent) {
        const progressFill = document.querySelector('.progress-fill');
        if (progressFill) {
            progressFill.style.width = percent + '%';
        }
    }

    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    function loadImage(url) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                generatedImage.src = url;
                loader.classList.add('hidden');
                generatedImage.classList.remove('hidden');
                imageActions.classList.remove('hidden');
                resolve();
            };
            img.onerror = () => {
                reject(new Error('图片加载失败'));
            };
            img.src = url;
        });
    }

    btnGenerate.addEventListener('click', generateImage);

    // ==================== 图片操作 ====================
    // 下载
    downloadBtn.addEventListener('click', async () => {
        try {
            const response = await fetch(currentImageURL);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `synth-avatar-${Date.now()}.png`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
            showSuccess('图片已下载');
        } catch (error) {
            showError('下载失败，请右键保存图片');
        }
    });

    // 重新生成
    regenerateBtn.addEventListener('click', generateImage);

    // 分享
    shareBtn.addEventListener('click', async () => {
        if (navigator.share) {
            try {
                await navigator.share({
                    title: 'SYNTH - 虚拟身份生成器',
                    text: '我刚刚用 SYNTH 生成了一个很酷的虚拟形象！',
                    url: currentImageURL
                });
                showSuccess('分享成功！');
            } catch (error) {
                console.log('Share canceled');
            }
        } else {
            // 复制链接
            navigator.clipboard.writeText(currentImageURL).then(() => {
                showSuccess('图片链接已复制到剪贴板');
            }).catch(() => {
                showError('复制失败，请手动复制图片链接');
            });
        }
    });

    // ==================== 历史记录 ====================
    function addToHistory(imageUrl, prompt) {
        const item = {
            id: Date.now(),
            url: imageUrl,
            prompt: prompt,
            time: new Date().toLocaleString('zh-CN')
        };

        history.unshift(item);
        if (history.length > 20) {
            history = history.slice(0, 20);
        }

        localStorage.setItem('synth_history', JSON.stringify(history));
        updateHistoryList();
    }

    function updateHistoryList() {
        if (history.length === 0) {
            historyList.innerHTML = '<div class="empty-state">暂无历史记录</div>';
            return;
        }

        historyList.innerHTML = history.map(item => `
            <div class="history-item" data-id="${item.id}">
                <img src="${item.url}" alt="Generated image">
                <div class="history-item-info">
                    <div class="history-item-prompt">${item.prompt}</div>
                    <div class="history-item-time">${item.time}</div>
                </div>
            </div>
        `).join('');

        // 添加点击事件
        document.querySelectorAll('.history-item').forEach(item => {
            item.addEventListener('click', () => {
                const id = parseInt(item.dataset.id);
                const historyItem = history.find(h => h.id === id);
                if (historyItem) {
                    currentImageURL = historyItem.url;
                    promptInput.value = historyItem.prompt;
                    loadImage(historyItem.url);
                    closeSidebar();
                }
            });
        });
    }

    // 打开历史记录侧边栏
    historyBtn.addEventListener('click', () => {
        historySidebar.classList.add('active');
        overlay.classList.add('active');
    });

    // 关闭侧边栏
    function closeSidebar() {
        historySidebar.classList.remove('active');
        overlay.classList.remove('active');
    }

    closeHistory.addEventListener('click', closeSidebar);
    overlay.addEventListener('click', closeSidebar);

    // 清空历史
    clearHistory.addEventListener('click', () => {
        if (confirm('确定要清空所有历史记录吗？')) {
            history = [];
            localStorage.removeItem('synth_history');
            updateHistoryList();
            showSuccess('历史记录已清空');
        }
    });

    // ==================== 主题切换 ====================
    themeBtn.addEventListener('click', () => {
        isDarkTheme = !isDarkTheme;
        applyTheme();
    });

    function applyTheme() {
        if (isDarkTheme) {
            document.documentElement.style.setProperty('--bg-color', '#0A0A0A');
            document.documentElement.style.setProperty('--text-main', '#FFFFFF');
        } else {
            document.documentElement.style.setProperty('--bg-color', '#F5F5F5');
            document.documentElement.style.setProperty('--text-main', '#1A1A1A');
        }
    }

    // ==================== 消息提示 ====================
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.classList.remove('hidden');
        setTimeout(() => {
            errorMessage.classList.add('hidden');
        }, 5000);
    }

    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.classList.remove('hidden');
        setTimeout(() => {
            successMessage.classList.add('hidden');
        }, 3000);
    }

    // ==================== 键盘快捷键 ====================
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + Enter 生成
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            generateImage();
        }

        // ESC 关闭侧边栏
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // ==================== 初始化 ====================
    init();
});
