(function () {
    const PAGE_SIZE = 24;
    const STYLE = 'alternate';

    const masonry = document.getElementById('masonry');
    const sentinel = document.getElementById('masonrySentinel');
    const statusEl = document.getElementById('galleryStatus');
    const lightbox = document.getElementById('lightbox');
    const lightboxImg = document.getElementById('lightboxImg');
    const lightboxCaption = document.getElementById('lightboxCaption');
    const lightboxClose = document.getElementById('lightboxClose');
    const lightboxBackdrop = document.getElementById('lightboxBackdrop');
    const themeBtn = document.getElementById('galleryThemeBtn');

    let offset = 0;
    let loading = false;
    let done = false;
    let isDarkTheme = true;

    function setStatus(text) {
        if (statusEl) statusEl.textContent = text || '';
    }

    function applyTheme() {
        if (isDarkTheme) {
            document.documentElement.style.setProperty('--bg-color', '#0A0A0A');
            document.documentElement.style.setProperty('--text-main', '#FFFFFF');
        } else {
            document.documentElement.style.setProperty('--bg-color', '#F5F5F5');
            document.documentElement.style.setProperty('--text-main', '#1A1A1A');
        }
    }

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            isDarkTheme = !isDarkTheme;
            applyTheme();
        });
    }
    applyTheme();

    function openLightbox(url, caption) {
        lightboxImg.src = url;
        lightboxCaption.textContent = caption || '';
        lightbox.classList.remove('hidden');
        document.body.style.overflow = 'hidden';
        lightboxClose.focus();
    }

    function closeLightbox() {
        lightbox.classList.add('hidden');
        lightboxImg.src = '';
        lightboxCaption.textContent = '';
        document.body.style.overflow = '';
    }

    lightboxClose.addEventListener('click', closeLightbox);
    lightboxBackdrop.addEventListener('click', closeLightbox);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !lightbox.classList.contains('hidden')) {
            closeLightbox();
        }
    });

    function appendBrick(item) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'masonry-brick';
        const hint = (item.prompt || '').slice(0, 160);
        btn.title = hint;
        const img = document.createElement('img');
        img.src = item.image_url;
        img.alt = '';
        img.loading = 'lazy';
        btn.appendChild(img);
        btn.addEventListener('click', () => {
            openLightbox(item.image_url, item.prompt || '');
        });
        masonry.appendChild(btn);
    }

    async function loadMore() {
        if (loading || done || !masonry) return;
        loading = true;
        if (offset === 0) setStatus('加载中…');
        try {
            const u = new URL('/api/gallery', window.location.origin);
            u.searchParams.set('style', STYLE);
            u.searchParams.set('limit', String(PAGE_SIZE));
            u.searchParams.set('offset', String(offset));
            const res = await fetch(u.toString());
            const data = await res.json();
            if (!res.ok) {
                setStatus('加载失败，请稍后重试');
                done = true;
                return;
            }
            const items = data.items || [];
            if (offset === 0 && !items.length) {
                setStatus('暂无伪人作品。请先在首页选择「伪人」风格并成功生成（需配置数据库）。');
                done = true;
                return;
            }
            setStatus('');
            items.forEach(appendBrick);
            offset += items.length;
            if (!data.has_more || items.length === 0) {
                done = true;
                if (offset > 0) setStatus('已加载全部');
            }
        } catch (e) {
            console.error(e);
            setStatus('网络错误');
            done = true;
        } finally {
            loading = false;
        }
    }

    const observer = new IntersectionObserver(
        (entries) => {
            if (entries.some((en) => en.isIntersecting)) {
                loadMore();
            }
        },
        { root: null, rootMargin: '400px', threshold: 0 }
    );

    if (sentinel) observer.observe(sentinel);
    loadMore();
})();
