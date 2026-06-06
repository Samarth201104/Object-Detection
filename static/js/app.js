(function themeInit(){
  const root = document.documentElement;
  const key = 'odemo-theme';
  const saved = localStorage.getItem(key);
  if(saved){ root.setAttribute('data-theme', saved); }
  const toggle = document.getElementById('themeToggle');
  const setPressed = () => toggle?.setAttribute('aria-pressed', root.getAttribute('data-theme') === 'light');
  setPressed();
  toggle?.addEventListener('click', ()=>{
    const next = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next);
    localStorage.setItem(key, next);
    setPressed();
  });
})();

const $ = (sel, parent=document) => parent.querySelector(sel);
const $$ = (sel, parent=document) => Array.from(parent.querySelectorAll(sel));
const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v));

const canvas = $('#stage');
const ctx = canvas.getContext('2d');
const video = $('#videoEl');
const dropZone = $('#dropZone');
const fileInput = $('#fileInput');
const fpsLabel = $('#fps');
const errorEl = $('#error');
const detCountEl = $('#detCount');
const confRange = $('#confRange');
const confValue = $('#confValue');
const maxDets = $('#maxDets');
const toggleBoxes = $('#toggleBoxes');
const toggleLabels = $('#toggleLabels');
const chips = $$('.chip');
const progress = $('#progress');
const runBtn = $('#runBtn');
const btnDownloadPNG = $('#btnDownloadPNG');
const btnDownloadJSON = $('#btnDownloadJSON');
const btnCopy = $('#btnCopy');
const btnSnapshot = $('#btnSnapshot');
const year = $('#year');
const btnSummary = $('#btnSummary');
const demoBtn = $('#btnDemo');
const demoImg = $('#demoImg');

let currentMode = 'image';
let imageBitmap = null;
let detections = [];
let animRAF = null;
let fpsFake = 0;
let webcamStream = null;

year.textContent = new Date().getFullYear();

(function setDemo(){
  const svg = `<svg xmlns='http://www.w3.org/2000/svg' width='640' height='360'>
    <defs>
      <linearGradient id='g' x1='0' x2='1' y1='0' y2='1'>
        <stop offset='0' stop-color='#1f2a44'/>
        <stop offset='1' stop-color='#0d1222'/>
      </linearGradient>
    </defs>
    <rect width='100%' height='100%' fill='url(#g)'/>
    <circle cx='180' cy='160' r='60' fill='#6e8bff' opacity='0.8'/>
    <rect x='330' y='120' width='140' height='80' fill='#41d1b7' opacity='0.85' rx='10'/>
    <text x='320' y='260' fill='#e8ecf1' font-family='Poppins' font-size='20'>Sample Scene</text>
  </svg>`;
  const url = 'data:image/svg+xml;base64,' + btoa(svg);
  demoImg.src = url;
})();

function setMode(mode){
  currentMode = mode;
  $$('#panel .tab').forEach(t=>{
    t.classList.toggle('active', t.dataset.mode === mode);
    t.setAttribute('aria-selected', t.dataset.mode === mode ? 'true' : 'false');
  });
  fileInput.accept = mode==='image' ? 'image/*' : (mode==='video' ? 'video/*' : 'image/*,video/*');
  fpsLabel.textContent = 'FPS: —';
  stopLoops();
  if(mode==='webcam') startWebcam();
}

$('#tabImage')?.addEventListener('click', ()=> setMode('image'));
$('#tabVideo')?.addEventListener('click', ()=> setMode('video'));
$('#tabWebcam')?.addEventListener('click', ()=> setMode('webcam'));

$('#ctaImage')?.addEventListener('click', ()=>{ document.getElementById('panel').scrollIntoView({behavior:'smooth'}); setMode('image'); fileInput.click(); });
$('#ctaVideo')?.addEventListener('click', ()=>{ document.getElementById('panel').scrollIntoView({behavior:'smooth'}); setMode('video'); fileInput.click(); });
$('#ctaWebcam')?.addEventListener('click', ()=>{ document.getElementById('panel').scrollIntoView({behavior:'smooth'}); setMode('webcam'); });

async function handleFile(file){
  errorEl.hidden = true;
  if(!file) return;
  if(file.type.startsWith('image/')){
    const bmp = await createImageBitmap(file);
    imageBitmap = bmp; video.classList.add('hidden');
    drawImageToCanvas(bmp);
  } else if(file.type.startsWith('video/')){
    const url = URL.createObjectURL(file);
    video.src = url; video.classList.remove('hidden');
    imageBitmap = null; video.currentTime = 0; await video.play().catch(()=>{});
    startVideoLoop();
  } else {
    errorEl.textContent = 'Unsupported file type.';
    errorEl.hidden = false;
  }
}

const dropEvents = ['dragenter','dragover','dragleave','drop'];
dropEvents.forEach(ev => dropZone.addEventListener(ev, e => e.preventDefault()));
['dragenter','dragover'].forEach(ev=> dropZone.addEventListener(ev, ()=> dropZone.classList.add('surface','dragover')));
['dragleave','drop'].forEach(ev=> dropZone.addEventListener(ev, ()=> dropZone.classList.remove('dragover')));
dropZone.addEventListener('drop', (e)=>{
  const f = e.dataTransfer?.files?.[0];
  if(f) handleFile(f);
});
const fileInputEl = document.getElementById('fileInput');
fileInputEl.addEventListener('change', ()=> handleFile(fileInputEl.files?.[0]));

function drawImageToCanvas(bmp){
  const {width: cw, height: ch} = canvas;
  ctx.clearRect(0,0,cw,ch);
  ctx.fillStyle = '#0b0f1a';
  ctx.fillRect(0,0,cw,ch);
  const scale = Math.min(cw / bmp.width, ch / bmp.height);
  const w = bmp.width * scale; const h = bmp.height * scale;
  const x = (cw - w)/2; const y = (ch - h)/2;
  ctx.drawImage(bmp, x, y, w, h);
}

function startVideoLoop(){
  stopLoops();
  let last = performance.now(); let frames = 0; fpsFake = 0;
  const loop = () => {
    if(video.paused || video.ended){ fpsLabel.textContent = 'FPS: —'; return; }
    const now = performance.now(); frames++;
    if(now - last >= 1000){ fpsFake = frames; frames = 0; last = now; fpsLabel.textContent = `FPS: ${fpsFake}`; }
    try{ ctx.drawImage(video, 0, 0, canvas.width, canvas.height); }catch{}
    animRAF = requestAnimationFrame(loop);
  };
  animRAF = requestAnimationFrame(loop);
}

function stopLoops(){
  if(animRAF) cancelAnimationFrame(animRAF), animRAF = null;
  if(webcamStream){
    webcamStream.getTracks().forEach(t=>t.stop());
    webcamStream = null;
    video.classList.add('hidden');
  }
}

async function startWebcam(){
  try{
    webcamStream = await navigator.mediaDevices.getUserMedia({video:true, audio:false});
    video.srcObject = webcamStream; video.classList.remove('hidden');
    await video.play(); startVideoLoop();
  }catch(err){
    errorEl.textContent = 'Camera permission denied (simulated).';
    errorEl.hidden = false;
  }
}

btnSnapshot.addEventListener('click', ()=>{
  canvas.classList.add('flash'); setTimeout(()=> canvas.classList.remove('flash'), 120);
});

confRange.addEventListener('input', ()=>{
  const v = Number(confRange.value).toFixed(2);
  confValue.textContent = v; confRange.setAttribute('aria-valuenow', v);
});

chips.forEach(chip=>{
  chip.addEventListener('click', ()=>{
    chip.classList.toggle('selected');
    chip.setAttribute('aria-pressed', chip.classList.contains('selected')?'true':'false');
  })
});

function simulateDetections(){
  const classes = chips.filter(c=>c.classList.contains('selected')).map(c=>c.dataset.class);
  const conf = parseFloat(confRange.value);
  const max = clamp(parseInt(maxDets.value||'10',10), 1, 100);

  const count = Math.floor(Math.random()* (max - 2)) + 2;
  const dets = [];
  for(let i=0;i<count;i++){
    const w = 80 + Math.random()*260;
    const h = 50 + Math.random()*180;
    const x = Math.random()*(canvas.width - w);
    const y = Math.random()*(canvas.height - h);
    const cls = classes[Math.floor(Math.random()*classes.length)] || 'object';
    const score = (conf + Math.random()*(1-conf)).toFixed(2);
    dets.push({bbox:[x,y,w,h], class:cls, score: Number(score)});
  }
  return dets;
}

function drawDetections(){
  if(!toggleBoxes.checked && !toggleLabels.checked) return;
  detections.forEach((d, i)=>{
    const [x,y,w,h] = d.bbox;
    const hue = (i*47)%360;
    const color = `hsl(${hue} 80% 60%)`;
    if(toggleBoxes.checked){
      ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.strokeRect(x,y,w,h);
    }
    if(toggleLabels.checked){
      const text = `${d.class} ${(d.score*100|0)/100}`;
      ctx.font = 'bold 14px Inter, system-ui, sans-serif';
      ctx.fillStyle = '#000a';
      ctx.fillRect(x, y-20, ctx.measureText(text).width+10, 20);
      ctx.fillStyle = '#fff';
      ctx.fillText(text, x+6, y-6);
    }
  })
}

function runSimulate(){
  progress.hidden = false; runBtn.disabled = true;
  setTimeout(()=>{
    if(imageBitmap) drawImageToCanvas(imageBitmap);
    detections = simulateDetections();
    detCountEl.textContent = String(detections.length);
    drawDetections();
    progress.hidden = true; runBtn.disabled = false;
  }, 900 + Math.random()*700);
}
runBtn.addEventListener('click', runSimulate);

window.addEventListener('keydown', (e)=>{
  if(e.code==='Space'){ e.preventDefault(); runSimulate(); }
  if(e.key==='1') setMode('image');
  if(e.key==='2') setMode('video');
  if(e.key==='3') setMode('webcam');
});

function download(filename, blob){
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = filename; a.click();
  setTimeout(()=> URL.revokeObjectURL(a.href), 1000);
}
btnDownloadPNG.addEventListener('click', ()=>{ canvas.toBlob(b=> b && download('annotated.png', b)); });
btnDownloadJSON.addEventListener('click', ()=>{
  const payload = {model:'simulated', timestamp: Date.now(), detections};
  const blob = new Blob([JSON.stringify(payload,null,2)], {type:'application/json'});
  download('detections.json', blob);
});
btnCopy.addEventListener('click', async()=>{
  try{
    await navigator.clipboard.writeText(JSON.stringify({detections}, null, 2));
    toast('Results copied to clipboard');
  }catch{ toast('Copy failed'); }
});

btnSummary.addEventListener('click', ()=>{
  const txt = `Object Detection Demo (UI Only)

Author: Samarth More — Final Year CSE (AI & ML)
Tech: HTML, CSS, JavaScript (no frameworks)

Features:
• Hero with animated gradient, CTAs, smooth scroll
• Detection Panel: image/video/webcam (simulated), drag & drop, controls, chips
• Simulated detections with boxes/labels, FPS label, progress loader
• Export annotated PNG/JSON, copy to clipboard
• How it works, Demo section, About, Future Scope
• Light/Dark mode (localStorage), scroll reveal, responsive

Integration Hook:
Call runDetection(imageOrVideoOrCanvas) where noted to integrate an ML model later.`;
  download('project-summary.txt', new Blob([txt], {type:'text/plain'}));
});

if(demoBtn){
  demoBtn.addEventListener('click', async()=>{
    const img = new Image(); img.src = demoImg.src; await img.decode();
    imageBitmap = await createImageBitmap(img);
    drawImageToCanvas(imageBitmap);
    runSimulate();
    document.getElementById('panel').scrollIntoView({behavior:'smooth'});
  });
}

let toastTimer = null;
function toast(msg){
  let t = document.getElementById('toast');
  if(!t){
    t = document.createElement('div');
    t.id = 'toast';
    t.style.cssText = 'position:fixed;left:50%;bottom:24px;transform:translateX(-50%);padding:10px 14px;border-radius:999px;background:rgba(0,0,0,.6);backdrop-filter:blur(6px);color:#fff;border:1px solid #ffffff40;z-index:9999;opacity:0;transition:.3s';
    document.body.appendChild(t);
  }
  t.textContent = msg; t.style.opacity = '1';
  clearTimeout(toastTimer); toastTimer = setTimeout(()=> t.style.opacity = '0', 1600);
}

(function reveal(){
  const io = new IntersectionObserver((entries)=>{
    entries.forEach(e=>{ if(e.isIntersecting){ e.target.classList.add('show'); io.unobserve(e.target);} });
  }, {threshold:.1});
  $$('.reveal, .reveal-up, .reveal-left, .reveal-right').forEach(el=> io.observe(el));
})();

(function focusRings(){
  function setRing(e){ document.body.classList.add('kbd'); }
  function clearRing(e){ document.body.classList.remove('kbd'); }
  window.addEventListener('keydown', e=> e.key==='Tab' && setRing());
  window.addEventListener('mousedown', clearRing);
})();

