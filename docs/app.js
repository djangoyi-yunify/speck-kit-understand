// 文档对比查看器 - 主应用逻辑

// 文档映射表
const documentMap = {
    'djangoyi-yunify-tech-research-101-main': [
        { source: 'demo.md', target: 'demo.cn.md', name: 'Demo' }
    ],
    'github-spec-kit-main': [
        { source: '00-constitution/constitution.md', target: '00-constitution/constitution.cn.md', name: 'Constitution (宪法)' },
        { source: '00-constitution/constitution-template.md', target: '00-constitution/constitution-template.cn.md', name: 'Constitution Template' },
        { source: '01-specify/specify.md', target: '01-specify/specify.cn.md', name: 'Specify (规范说明)' },
        { source: '01-specify/spec-template.md', target: '01-specify/spec-template.cn.md', name: 'Spec Template' },
        { source: '02-plan/plan.md', target: '02-plan/plan.cn.md', name: 'Plan (计划)' },
        { source: '02-plan/plan-template.md', target: '02-plan/plan-template.cn.md', name: 'Plan Template' },
        { source: '03-tasks/tasks.md', target: '03-tasks/tasks.cn.md', name: 'Tasks (任务)' },
        { source: '03-tasks/tasks-template.md', target: '03-tasks/tasks-template.cn.md', name: 'Tasks Template' },
        { source: '04-implement/implement.md', target: '04-implement/implement.cn.md', name: 'Implement (实现)' },
        { source: '05-checklist/checklist.md', target: '05-checklist/checklist.cn.md', name: 'Checklist (检查清单)' },
        { source: '05-checklist/checklist-template.md', target: '05-checklist/checklist-template.cn.md', name: 'Checklist Template' },
        { source: '06-analyze/analyze.md', target: '06-analyze/analyze.cn.md', name: 'Analyze (分析)' },
        { source: '07-clarify/clarify.md', target: '07-clarify/clarify.cn.md', name: 'Clarify (澄清)' },
        { source: '08-taskstoissues/taskstoissues.md', target: '08-taskstoissues/taskstoissues.cn.md', name: 'Tasks to Issues' },
        { source: '09-agent-file/agent-file-template.md', target: '09-agent-file/agent-file-template.cn.md', name: 'Agent File Template' }
    ],
    'anthropics-skills-main': [
        { source: 'README.md', target: 'README.cn.md', name: 'README' },
        { source: 'skills/skill-creator/SKILL.md', target: 'skills/skill-creator/SKILL.cn.md', name: 'Skill Creator' },
        { source: 'skills/skill-creator/agents/analyzer.md', target: 'skills/skill-creator/agents/analyzer.cn.md', name: 'Analyzer Agent' },
        { source: 'skills/skill-creator/agents/comparator.md', target: 'skills/skill-creator/agents/comparator.cn.md', name: 'Comparator Agent' },
        { source: 'skills/skill-creator/agents/grader.md', target: 'skills/skill-creator/agents/grader.cn.md', name: 'Grader Agent' }
    ]
};

// 基础路径
const basePath = 'translated';

// DOM 元素
const repoSelect = document.getElementById('repo-select');
const docSelect = document.getElementById('doc-select');
const renderToggle = document.getElementById('render-toggle');
const sourceContent = document.getElementById('source-content');
const targetContent = document.getElementById('target-content');
const sourceName = document.getElementById('source-name');
const targetName = document.getElementById('target-name');

// 存储当前文档内容
let currentSourceContent = '';
let currentTargetContent = '';

// 初始化
function init() {
    repoSelect.addEventListener('change', handleRepoChange);
    docSelect.addEventListener('change', handleDocChange);
    renderToggle.addEventListener('change', renderContent);
}

// 处理仓库选择变化
function handleRepoChange() {
    const repo = repoSelect.value;

    // 重置文档选择器
    docSelect.innerHTML = '<option value="">选择文档...</option>';

    if (repo && documentMap[repo]) {
        // 填充文档列表
        documentMap[repo].forEach((doc, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = doc.name;
            docSelect.appendChild(option);
        });
        docSelect.disabled = false;
    } else {
        docSelect.disabled = true;
    }

    // 清空内容
    sourceContent.innerHTML = '<p class="placeholder">请选择要对比的文档</p>';
    targetContent.innerHTML = '<p class="placeholder">请选择要对比的文档</p>';
    sourceName.textContent = '-';
    targetName.textContent = '-';
    currentSourceContent = '';
    currentTargetContent = '';
}

// 处理文档选择变化
async function handleDocChange() {
    const repo = repoSelect.value;
    const docIndex = docSelect.value;

    if (!repo || docIndex === '') {
        sourceContent.innerHTML = '<p class="placeholder">请选择要对比的文档</p>';
        targetContent.innerHTML = '<p class="placeholder">请选择要对比的文档</p>';
        return;
    }

    const doc = documentMap[repo][docIndex];
    const sourcePath = `${basePath}/${repo}/${doc.source}`;
    const targetPath = `${basePath}/${repo}/${doc.target}`;

    // 显示加载状态
    sourceContent.innerHTML = '<div class="loading">加载中</div>';
    targetContent.innerHTML = '<div class="loading">加载中</div>';

    try {
        // 并行加载原文和译文
        const [sourceText, targetText] = await Promise.all([
            fetchFile(sourcePath),
            fetchFile(targetPath)
        ]);

        currentSourceContent = sourceText;
        currentTargetContent = targetText;

        sourceName.textContent = doc.source;
        targetName.textContent = doc.target;

        // 渲染内容
        renderContent();
    } catch (error) {
        console.error('加载文档失败:', error);
        sourceContent.innerHTML = `<p class="placeholder">加载失败: ${error.message}</p>`;
        targetContent.innerHTML = `<p class="placeholder">加载失败: ${error.message}</p>`;
    }
}

// 获取文件内容
async function fetchFile(path) {
    const response = await fetch(path);
    if (!response.ok) {
        throw new Error(`无法加载文件: ${path}`);
    }
    return await response.text();
}

// 渲染内容
function renderContent() {
    const shouldRender = renderToggle.checked;

    if (shouldRender) {
        // 渲染 Markdown
        sourceContent.innerHTML = marked.parse(currentSourceContent);
        targetContent.innerHTML = marked.parse(currentTargetContent);
        sourceContent.classList.remove('raw-text');
        targetContent.classList.remove('raw-text');
    } else {
        // 显示原始文本（转义 HTML 特殊字符）
        sourceContent.innerHTML = escapeHtml(currentSourceContent);
        targetContent.innerHTML = escapeHtml(currentTargetContent);
        sourceContent.classList.add('raw-text');
        targetContent.classList.add('raw-text');
    }
}

// 转义 HTML 特殊字符
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// 启动应用
init();