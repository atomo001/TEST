let currentTask = null;
let recoveredFiles = [];

function setTheme(theme, btn) {
  document.body.className = `theme-${theme}`;
  document.querySelectorAll('.chip').forEach(x => x.classList.remove('active'));
  btn.classList.add('active');
}

async function startScan() {
  const source = document.getElementById('source').value.trim();
  if (!source) return alert('请先输入磁盘/分区/镜像路径');

  const res = await fetch('/api/scan', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({source, mode: 'partition'})
  });
  const data = await res.json();
  currentTask = data.task_id;
  pollTask();
}

async function pollTask() {
  if (!currentTask) return;
  const res = await fetch(`/api/task/${currentTask}`);
  const task = await res.json();
  document.getElementById('bar').style.width = `${task.progress}%`;
  document.getElementById('status').innerText = `${task.status} ${task.progress}%`;
  document.getElementById('log').innerText = task.logs.join('\n');
  if (task.result && task.result.files) {
    recoveredFiles = task.result.files;
    renderFiles(recoveredFiles);
  }
  if (task.status === 'running' || task.status === 'pending') setTimeout(pollTask, 500);
}

function renderFiles(files) {
  const ul = document.getElementById('fileList');
  ul.innerHTML = '';
  files.forEach(f => {
    const li = document.createElement('li');
    li.innerText = `${f.name} · ${f.ext || 'unknown'} · ${f.size} bytes`;
    ul.appendChild(li);
  });
}

function applyFilter() {
  const filterText = document.getElementById('filter').value.trim().toLowerCase();
  if (!filterText) return renderFiles(recoveredFiles);
  const allowed = new Set(filterText.split(',').map(x => x.trim()).filter(Boolean));
  renderFiles(recoveredFiles.filter(f => allowed.has(f.ext)));
}

async function recover() {
  if (!currentTask) return alert('请先完成扫描');
  const outputDir = document.getElementById('outputDir').value.trim();
  const confirmRisk = document.getElementById('confirmRisk').checked;
  if (!outputDir) return alert('请设置恢复目录');

  const res = await fetch('/api/recover', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({task_id: currentTask, output_dir: outputDir, file_types: [], allow_overwrite: confirmRisk})
  });
  const data = await res.json();
  if (data.need_confirmation && !confirmRisk) {
    return alert('检测到潜在高风险操作，请先勾选风险确认后再执行。');
  }
  alert('恢复任务请求已提交（MVP）。');
}
