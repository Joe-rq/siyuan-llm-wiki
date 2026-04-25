#!/usr/bin/env node

/**
 * LLM Wiki 初始化脚本
 * 一键创建知识库笔记本、目录结构、核心文档，并生成 wiki.config.json
 *
 * 用法：
 *   node wiki-init.js [--dry-run] [--notebook-name <name>] [--skill-path <path>] [--force]
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// ── 参数解析 ──

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = {
    dryRun: false,
    notebookName: 'LLM-Wiki',
    skillPath: '',
    force: false,
  };
  for (let i = 0; i < args.length; i++) {
    switch (args[i]) {
      case '--dry-run': opts.dryRun = true; break;
      case '--notebook-name': opts.notebookName = args[++i]; break;
      case '--skill-path': opts.skillPath = args[++i]; break;
      case '--force': opts.force = true; break;
      case '--help':
        console.log(`LLM Wiki 初始化脚本

用法: node wiki-init.js [选项]

选项:
  --dry-run            仅打印将执行的操作，不实际创建
  --notebook-name <n>  笔记本名称（默认 LLM-Wiki）
  --skill-path <p>     siyuan-skill/siyuan.js 的路径
  --force              覆盖已有的 wiki.config.json
  --help               显示帮助`);
        process.exit(0);
    }
  }
  return opts;
}

// ── 查找 siyuan-skill 路径 ──

function findSiyuanSkill(explicitPath) {
  // 优先级：命令行参数 > 环境变量 > 相对路径猜测
  if (explicitPath) {
    if (fs.existsSync(explicitPath)) return explicitPath;
    console.error(`❌ 指定的 siyuan-skill 路径不存在: ${explicitPath}`);
    process.exit(1);
  }
  const envPath = process.env.SIYUAN_SKILL_PATH;
  if (envPath && fs.existsSync(envPath)) return envPath;

  const candidates = [
    path.resolve(__dirname, '..', 'siyuan-skill', 'siyuan.js'),
    path.resolve(__dirname, 'node_modules', 'siyuan-skill', 'siyuan.js'),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  console.error(`❌ 找不到 siyuan-skill。请通过以下方式之一指定路径：
  --skill-path <path>
  环境变量 SIYUAN_SKILL_PATH
  或将 siyuan-skill 安装到 ../siyuan-skill/`);
  process.exit(1);
}

// ── 执行 siyuan 命令 ──

function runSiyuan(siyuanPath, cmd, opts = {}) {
  const fullCmd = `node "${siyuanPath}" ${cmd}`;
  try {
    const result = execSync(fullCmd, {
      encoding: 'utf-8',
      timeout: 30000,
      stdio: ['pipe', 'pipe', 'pipe'],
    });
    try {
      return JSON.parse(result);
    } catch {
      return { raw: result.trim() };
    }
  } catch (err) {
    return { error: err.stderr || err.message };
  }
}

// ── 提取 docId ──

function extractDocId(result) {
  if (result.error) return null;
  // siyuan.js create 返回 { success: true, data: { docId: "..." } }
  if (result.data?.docId) return result.data.docId;
  // ls 返回的目录结构中包含 id
  if (result.id) return result.id;
  // 尝试从原始输出中匹配思源 ID 格式
  const raw = typeof result.raw === 'string' ? result.raw : JSON.stringify(result);
  const match = raw.match(/20\d{12}-[a-z0-9]{5,7}/);
  return match ? match[0] : null;
}

// ── 主流程 ──

async function main() {
  const opts = parseArgs();
  const configPath = path.join(__dirname, 'wiki.config.json');

  // 检查已有配置
  if (fs.existsSync(configPath) && !opts.force) {
    console.log('⚠️  wiki.config.json 已存在。使用 --force 覆盖，或手动编辑该文件。');
    process.exit(1);
  }

  const siyuanPath = findSiyuanSkill(opts.skillPath);
  console.log(`✅ 找到 siyuan-skill: ${siyuanPath}`);

  // 检测思源 API 连通性
  const nbResult = runSiyuan(siyuanPath, 'notebooks');
  if (nbResult.error) {
    console.error('❌ 无法连接思源笔记 API。请确认思源笔记已启动。');
    console.error(`   错误: ${nbResult.error}`);
    process.exit(1);
  }
  console.log('✅ 思源笔记 API 连通');

  const config = {
    notebook: { id: '', name: opts.notebookName },
    docs: { index: '', log: '', schema: '' },
    dirs: { raw: '', wiki: '', wiki_entities: '', wiki_topics: '', wiki_sources: '', wiki_synthesis: '' },
    siyuanSkillPath: siyuanPath,
  };

  const dry = opts.dryRun;
  const prefix = dry ? '[DRY-RUN] ' : '';

  // ── 1. 检查同名笔记本 ──

  let notebookId = null;
  const notebooks = nbResult.data || nbResult;
  if (Array.isArray(notebooks)) {
    const existing = notebooks.find(nb => nb.name === opts.notebookName);
    if (existing) {
      notebookId = existing.id;
      console.log(`ℹ️  笔记本 "${opts.notebookName}" 已存在 (ID: ${notebookId})`);
    }
  }

  // ── 2. 创建笔记本（如不存在）──

  if (!notebookId) {
    console.log(`${prefix}创建笔记本 "${opts.notebookName}"`);
    if (!dry) {
      const result = runSiyuan(siyuanPath, `create --path "${opts.notebookName}" ""`);
      notebookId = extractDocId(result);
      if (!notebookId) {
        console.error('❌ 创建笔记本失败，无法提取 ID');
        console.error('   返回值:', JSON.stringify(result, null, 2));
        console.error('\n💡 你可以手动创建笔记本，然后编辑 wiki.config.json 填入 ID');
        process.exit(1);
      }
      console.log(`✅ 笔记本已创建: ${notebookId}`);
    } else {
      notebookId = '<NOTEBOOK_ID>';
    }
  }
  config.notebook.id = notebookId;

  // ── 3. 创建目录结构 ──

  const dirPaths = [
    ['raw', `${opts.notebookName}/raw`],
    ['wiki', `${opts.notebookName}/wiki`],
    ['wiki_entities', `${opts.notebookName}/wiki/entities`],
    ['wiki_topics', `${opts.notebookName}/wiki/topics`],
    ['wiki_sources', `${opts.notebookName}/wiki/sources`],
    ['wiki_synthesis', `${opts.notebookName}/wiki/synthesis`],
  ];

  for (const [key, p] of dirPaths) {
    console.log(`${prefix}创建目录: ${p}`);
    if (!dry) {
      // 用 ls 先检查是否已存在
      const lsResult = runSiyuan(siyuanPath, `search "${p.split('/').pop()}"`);
      let dirId = null;

      // 尝试创建
      const createResult = runSiyuan(siyuanPath, `create --path "${p}" ""`);
      dirId = extractDocId(createResult);

      if (!dirId && createResult.error) {
        // 可能已存在，尝试从搜索结果中获取
        console.log(`   ⚠️  创建返回错误，尝试搜索已有目录...`);
        if (lsResult.data && Array.isArray(lsResult.data)) {
          const found = lsResult.data.find(d => d.path && d.path.endsWith(p));
          if (found) dirId = found.id || found.docId;
        }
      }

      if (dirId) {
        config.dirs[key] = dirId;
        console.log(`   ✅ ${key}: ${dirId}`);
      } else {
        console.log(`   ⚠️  ${key}: 无法获取 ID，请手动填写`);
      }
    } else {
      config.dirs[key] = `<${key.toUpperCase()}_ID>`;
    }
  }

  // ── 4. 创建核心文档 ──

  const templateDir = path.join(__dirname, 'templates');

  const docs = [
    ['index', `${opts.notebookName}/index`, 'index.md'],
    ['log', `${opts.notebookName}/log`, 'log.md'],
    ['schema', `${opts.notebookName}/schema`, 'schema.md'],
  ];

  for (const [key, docPath, templateFile] of docs) {
    const templatePath = path.join(templateDir, templateFile);
    let content = '';
    if (fs.existsSync(templatePath)) {
      content = fs.readFileSync(templatePath, 'utf-8');
    }

    console.log(`${prefix}创建文档: ${docPath}`);
    if (!dry) {
      const result = runSiyuan(siyuanPath, `create --path "${docPath}" ${JSON.stringify(content)}`);
      const docId = extractDocId(result);
      if (docId) {
        config.docs[key] = docId;
        console.log(`   ✅ ${key}: ${docId}`);
      } else {
        console.log(`   ⚠️  ${key}: 无法获取 ID，请手动填写`);
      }
    } else {
      config.docs[key] = `<${key.toUpperCase()}_DOC_ID>`;
    }
  }

  // ── 5. 写入配置 ──

  console.log(`\n${prefix}写入 wiki.config.json`);
  if (!dry) {
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');
    console.log('✅ wiki.config.json 已生成');
  }

  // ── 6. 输出结果 ──

  console.log('\n' + '='.repeat(50));
  if (dry) {
    console.log('[DRY-RUN] 以上是将会执行的操作，未实际创建任何内容');
  } else {
    console.log('✅ 初始化完成！');
    console.log('\n下一步：');
    console.log('  1. 在 CLAUDE.md 中添加 LLM Wiki 配置（参考 README.md）');
    console.log('  2. 在思源笔记中验证笔记本结构');
    console.log('  3. 使用 /wiki <docId> 开始摄入文档');
    console.log(`\n配置文件: ${configPath}`);
    console.log('所有文档 ID 已记录在 wiki.config.json 中，脚本运行时自动读取。');
  }
}

main().catch(err => {
  console.error('❌ 初始化失败:', err.message);
  process.exit(1);
});
