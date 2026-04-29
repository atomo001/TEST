let currentTask = null;
let recoveredFiles = [];

async function startScan() {
  const source = document.getElementById('source').value;
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
  if (task.status === 'running' || task.status === 'pending') {
    setTimeout(pollTask, 500);
  }
}

function renderFiles(files) {
  const ul = document.getElementById('fileList');
  ul.innerHTML = '';
  files.forEach(f => {
    const li = document.createElement('li');
    li.innerText = `${f.name} (${f.ext || 'unknown'}, ${f.size} bytes)`;
    ul.appendChild(li);
  });
}

function applyFilter() {
  const filterText = document.getElementById('filter').value.trim().toLowerCase();
  if (!filterText) return renderFiles(recoveredFiles);
  const allowed = new Set(filterText.split(',').map(x => x.trim()));
  renderFiles(recoveredFiles.filter(f => allowed.has(f.ext)));
}

async function recover() {
  if (!currentTask) return;
  const outputDir = document.getElementById('outputDir').value;
  const res = await fetch('/api/recover', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({task_id: currentTask, output_dir: outputDir, file_types: []})
  });
  const data = await res.json();
  if (data.need_confirmation) {
    alert('High-risk action requires explicit confirmation in full version.');
  }
}
