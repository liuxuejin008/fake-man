# SYNTH - AI 虚拟身份生成器

<div align="center">

![Version](https://img.shields.io/badge/version-1.0.0-purple.svg)
![Flask](https://img.shields.io/badge/Flask-3.1.3-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

一个基于 AI 技术的虚拟形象生成器，支持多种风格和自定义描述

[功能特性](#功能特性) • [快速开始](#快速开始) • [使用说明](#使用说明) • [部署](#部署)

</div>

---

## ✨ 功能特性

### 🎨 多样化风格
- **赛博朋克** - 未来感十足的科技风格
- **动漫风格** - 日系动漫角色生成
- **写实风格** - 真实的摄影质感
- **奇幻风格** - 梦幻的魔法世界

### 🚀 核心功能
- ✅ **AI 生成** - 使用最新 AI 技术生成高质量虚拟形象
- ✅ **自定义描述** - 支持自定义描述来生成理想形象
- ✅ **随机灵感** - 一键获取随机创意描述
- ✅ **图片下载** - 支持高清图片下载
- ✅ **历史记录** - 本地保存生成历史，随时查看
- ✅ **分享功能** - 轻松分享你的作品
- ✅ **主题切换** - 支持亮色/暗色主题

### 🎯 用户体验
- 📱 **响应式设计** - 完美适配手机、平板和桌面设备
- ⚡ **即时加载** - 优化的加载体验
- 🎭 **精美动画** - 流畅的过渡和微交互
- 💫 **粒子特效** - 动态背景营造沉浸感
- 🎨 **玻璃拟态** - 现代 UI 设计风格

---

## 📦 快速开始

### 环境要求

- Python 3.9+
- pip 包管理器

### 安装步骤

1. **克隆项目**
```bash
git clone <your-repo-url>
cd fake-man
```

2. **创建虚拟环境**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. **安装依赖**
```bash
pip install -r requirements.txt
pip install beautifulsoup4 lxml  # 测试依赖
```

4. **配置环境变量**

创建 `.env` 文件：
```env
BANANA_API_KEY=your_api_key_here
BANANA_API_URL=https://api.acedata.cloud/nano-banana/images
```

5. **启动服务器**
```bash
python -m flask --app api/index.py run --port=5000
```

6. **访问应用**

打开浏览器访问 `http://localhost:5000`

---

## 📖 使用说明

### 基础用法

1. **选择风格**
   - 在顶部选择你喜欢的风格标签
   - 每种风格都有独特的预设描述

2. **生成图片**
   - 点击"随机灵感"获取随机描述
   - 或在输入框中输入自定义描述
   - 点击"立即生成"按钮开始生成

3. **操作图片**
   - 生成后可以下载、分享或重新生成
   - 点击历史记录按钮查看之前的生成

### 快捷键

- `Ctrl/Cmd + Enter` - 快速生成
- `ESC` - 关闭侧边栏

---

## 🧪 测试

运行前端测试：
```bash
python test_frontend.py
```

运行 API 测试：
```bash
python test_api.py
```

---

## 🚀 部署

### Vercel 部署

1. 安装 Vercel CLI：
```bash
npm install -g vercel
```

2. 部署项目：
```bash
vercel
```

3. 配置环境变量：
```bash
vercel env add BANANA_API_KEY
```

### 其他平台

项目支持部署到任何支持 Flask 的平台：
- Heroku
- Railway
- Render
- AWS Lambda
- Google Cloud Run

---

## 📁 项目结构

```
fake-man/
├── api/
│   └── index.py          # Flask 后端 API
├── static/
│   ├── style.css         # 样式文件
│   └── main.js           # 前端逻辑
├── templates/
│   └── index.html        # 页面模板
├── venv/                 # 虚拟环境
├── .env                  # 环境变量
├── requirements.txt      # Python 依赖
├── vercel.json          # Vercel 配置
├── test_api.py          # API 测试
├── test_frontend.py     # 前端测试
└── README.md            # 项目文档
```

---

## 🎨 技术栈

### 后端
- **Flask** - Python Web 框架
- **Requests** - HTTP 库
- **python-dotenv** - 环境变量管理

### 前端
- **原生 JavaScript** - 无框架依赖
- **CSS3** - 现代样式和动画
- **HTML5** - 语义化标签

### 设计
- **玻璃拟态 (Glassmorphism)** - 现代 UI 风格
- **渐变色彩** - 紫色到粉色的渐变
- **粒子动画** - 动态背景效果
- **响应式设计** - 移动优先

---

## 🔧 配置选项

### API 配置

在 `.env` 文件中配置：

```env
# Banana API 密钥（必需）
BANANA_API_KEY=your_api_key_here

# API 端点（可选，有默认值）
BANANA_API_URL=https://api.acedata.cloud/nano-banana/images

# Flask 配置（可选）
FLASK_ENV=development
FLASK_DEBUG=True
```

### 样式自定义

编辑 `static/style.css` 中的 CSS 变量：

```css
:root {
    --bg-color: #0A0A0A;          /* 背景色 */
    --primary: #7C3AED;            /* 主色调 */
    --secondary: #EC4899;          /* 辅助色 */
    --accent: #06B6D4;             /* 强调色 */
}
```

---

## 🐛 故障排除

### 常见问题

**Q: 图片生成失败**
A: 检查 API 密钥是否正确配置

**Q: 样式加载异常**
A: 确保静态文件路径正确

**Q: 历史记录丢失**
A: 历史记录保存在浏览器本地存储中，清除浏览器数据会删除

---

## 📝 待办事项

- [ ] 添加更多风格预设
- [ ] 支持批量生成
- [ ] 添加图片编辑功能
- [ ] 支持导出为不同格式
- [ ] 添加用户系统
- [ ] 支持社交账号登录

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License - 详见 LICENSE 文件

---

## 🙏 致谢

- [Banana API](https://acedata.cloud/) - 提供 AI 图片生成服务
- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Google Fonts](https://fonts.google.com/) - 字体资源

---

<div align="center">

**Made with ❤️ by SYNTH Team**

</div>
