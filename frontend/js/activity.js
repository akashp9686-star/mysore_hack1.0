const params = new URLSearchParams(location.search);
const type = params.get('type') || 'communication';
let grade = Number(params.get('grade') || localStorage.getItem('selectedGrade') || 5);
let level = Math.max(1, Math.min(20, Number(params.get('level') || 1)));

const $ = id => document.getElementById(id);
const names = { communication: 'Communication Skills', spell_talk: 'Spell Talk', brainstorm: 'Brainstorm' };
const S = { data: null, a: null, attempts: 0, selected: {}, cube: null, history: [] };

const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[c]));
const words = value => String(value || '').trim().split(/\s+/).filter(Boolean);
const attemptKey = () => `attempts:${grade}:${type}:${level}`;
const completeKey = () => `completed:${grade}:${type}:${level}`;
const coins = () => Number(localStorage.getItem('learningCoins') || 10);
const completed = () => localStorage.getItem(completeKey()) === '1';
const saveAttempts = n => { S.attempts = n; localStorage.setItem(attemptKey(), String(n)); };
const setCoins = n => { localStorage.setItem('learningCoins', String(Math.max(0, n))); $('coinBalance').textContent = coins(); };
const rewardFor = (base, n) => n === 1 ? base : n === 2 ? Math.max(2, Math.round(base * .75)) : Math.max(1, Math.round(base * .5));

function updateAttemptBar() {
  $('attemptCount').textContent = `${S.attempts} / 3 attempts used`;
  $('attemptNote').textContent = S.attempts ? 'Use the guidance to improve your next attempt.' : 'First try earns the full coin reward.';
  document.querySelectorAll('.attempt-pip').forEach((p, i) => p.classList.toggle('used', i < S.attempts));
}

function renderQuestionSet(questions) {
  return `<div class="question-set">${questions.map((q, i) => `
    <section class="question-block">
      <div class="question-number">QUESTION ${i + 1}</div>
      <h3>${esc(q.prompt)}</h3>
      <div class="option-grid">${q.options.map((o, j) => `<button type="button" class="option-button" data-q="${i}" data-o="${j}">${esc(o)}</button>`).join('')}</div>
      <div id="explain-${i}" class="question-explain hidden"></div>
    </section>`).join('')}</div>`;
}

function bindQuestions() {
  document.querySelectorAll('.option-button').forEach(button => button.addEventListener('click', () => {
    const q = Number(button.dataset.q), o = Number(button.dataset.o);
    S.selected[q] = o;
    document.querySelectorAll(`.option-button[data-q="${q}"]`).forEach(x => x.classList.remove('selected'));
    button.classList.add('selected');
  }));
}

function renderCommunication() {
  if (S.a.format === 'essay') {
    $('activityBody').innerHTML = `
      <div class="response-card">
        <label class="response-label">YOUR RESPONSE</label>
        <textarea id="response" rows="12" placeholder="Write your answer here..."></textarea>
        <div class="criteria-box"><strong>Medium-level checklist</strong><p>Clear opening · relevant ideas · class-appropriate language · organised ending · complete sentences.</p></div>
      </div>`;
    $('submitButton').textContent = 'Check Response';
    return;
  }
  $('activityBody').innerHTML = (S.a.paragraph ? `<div class="paragraph-box"><span class="mini-label">READ THIS</span><p>${esc(S.a.paragraph)}</p></div>` : '') + renderQuestionSet(S.a.questions || S.a.scenarios || []);
  bindQuestions();
  $('submitButton').textContent = 'Check Answers';
}

function renderSpell() {
  if (S.a.format === 'lesson') {
    $('activityBody').innerHTML = `
      <div class="lesson-banner">
        <div><span class="mini-label">SPELLING LEARNING CLASS</span><h3>Study the words before you test yourself.</h3><p>No attempt is used while you learn. Read the spelling, meaning and memory clue.</p></div>
        <button id="startTest" class="primary-button">Finish Class →</button>
      </div>
      <div class="lesson-grid">${S.a.word_cards.map(w => `<article class="word-card"><div class="word-tag">WORD</div><h3>${esc(w.word)}</h3><p><strong>Meaning:</strong> ${esc(w.meaning)}</p><p class="clue">Memory clue: ${esc(w.clue)}</p></article>`).join('')}</div>`;
    $('submitButton').classList.add('hidden'); $('resetButton').classList.add('hidden');
    $('startTest').onclick = () => completeLearningLesson();
    return;
  }
  $('activityBody').innerHTML = renderQuestionSet(S.a.questions || []);
  bindQuestions();
  $('submitButton').textContent = 'Check Test';
}

/* ---------- Rubik's Cube ---------- */
function solvedCube() { return { U:Array(9).fill('W'), R:Array(9).fill('R'), F:Array(9).fill('G'), D:Array(9).fill('Y'), L:Array(9).fill('O'), B:Array(9).fill('B') }; }
function cloneCube(c) { return Object.fromEntries(Object.entries(c).map(([k,v]) => [k, v.slice()])); }
function rotateFace(a) { return [a[6],a[3],a[0],a[7],a[4],a[1],a[8],a[5],a[2]]; }
function turnFace(c, f) {
  c[f] = rotateFace(c[f]);
  let t;
  if (f==='U') { t=c.F.slice(0,3); c.F.splice(0,3,...c.R.slice(0,3)); c.R.splice(0,3,...c.B.slice(0,3)); c.B.splice(0,3,...c.L.slice(0,3)); c.L.splice(0,3,...t); }
  if (f==='D') { t=c.F.slice(6,9); c.F.splice(6,3,...c.L.slice(6,9)); c.L.splice(6,3,...c.B.slice(6,9)); c.B.splice(6,3,...c.R.slice(6,9)); c.R.splice(6,3,...t); }
  if (f==='F') { t=[c.U[6],c.U[7],c.U[8]]; [c.U[6],c.U[7],c.U[8]]=[c.L[8],c.L[5],c.L[2]]; [c.L[2],c.L[5],c.L[8]]=[c.D[0],c.D[1],c.D[2]]; [c.D[0],c.D[1],c.D[2]]=[c.R[6],c.R[3],c.R[0]]; [c.R[0],c.R[3],c.R[6]]=t; }
  if (f==='B') { t=[c.U[0],c.U[1],c.U[2]]; [c.U[0],c.U[1],c.U[2]]=[c.R[2],c.R[5],c.R[8]]; [c.R[2],c.R[5],c.R[8]]=[c.D[8],c.D[7],c.D[6]]; [c.D[6],c.D[7],c.D[8]]=[c.L[0],c.L[3],c.L[6]]; [c.L[0],c.L[3],c.L[6]]=t; }
  if (f==='R') { t=[c.U[2],c.U[5],c.U[8]]; [c.U[2],c.U[5],c.U[8]]=[c.F[2],c.F[5],c.F[8]]; [c.F[2],c.F[5],c.F[8]]=[c.D[2],c.D[5],c.D[8]]; [c.D[2],c.D[5],c.D[8]]=[c.B[6],c.B[3],c.B[0]]; [c.B[0],c.B[3],c.B[6]]=t; }
  if (f==='L') { t=[c.U[0],c.U[3],c.U[6]]; [c.U[0],c.U[3],c.U[6]]=[c.B[8],c.B[5],c.B[2]]; [c.B[2],c.B[5],c.B[8]]=[c.D[6],c.D[3],c.D[0]]; [c.D[0],c.D[3],c.D[6]]=[c.F[0],c.F[3],c.F[6]]; [c.F[0],c.F[3],c.F[6]]=t; }
}
function applyMove(c, notation) { const face=notation[0]; const times=notation.endsWith("'")?3:notation.endsWith('2')?2:1; for(let i=0;i<times;i++) turnFace(c,face); }
function isSolved(c) { return Object.values(c).every(face => face.every(v => v === face[4])); }
function cubeNotation(m) { return m.replace("'",'′'); }
function paintCube() {
  const map={W:'white',Y:'yellow',R:'red',O:'orange',G:'green',B:'blue'};
  ['U','F','R'].forEach(face => document.querySelectorAll(`#face-${face} span`).forEach((s,i)=>s.className=map[S.cube[face][i]]));
  $('cubeMoveCount').textContent = `${S.history.length} move${S.history.length===1?'':'s'}`;
}
function cubeHTML() {
  const faces=['U','F','R'];
  return `<div class="cube-guide">
    <div class="cube-heading"><div><span class="mini-label">RUBIK'S CUBE LAB</span><h3>Follow the method — do not turn randomly.</h3></div><span id="cubeMoveCount" class="level-chip">0 moves</span></div>
    <div class="cube-stage"><div class="cube" id="cubeVisual">${faces.map(f=>`<div class="cube-face ${f==='U'?'top':f==='F'?'front':'right'}" id="face-${f}">${'<span></span>'.repeat(9)}</div>`).join('')}</div></div>
    <div class="cube-help"><strong>How to use the controls</strong><p><b>U/R/F/D/L/B</b> = turn that face clockwise. <b>′</b> = turn it backwards. <b>2</b> = turn it twice. Use <b>Undo</b> to reverse your last move and <b>Reset</b> to return to the solved cube. Keep the white face on top when the lesson asks for the white cross or corners.</p></div>
    <div class="cube-notation"><span>U = Up</span><span>R = Right</span><span>F = Front</span><span>D = Down</span><span>L = Left</span><span>B = Back</span></div>
    <div class="cube-controls"><button data-m="U">U</button><button data-m="U'">U′</button><button data-m="U2">U2</button><button data-m="R">R</button><button data-m="R'">R′</button><button data-m="R2">R2</button><button data-m="F">F</button><button data-m="F'">F′</button><button data-m="F2">F2</button><button data-m="D">D</button><button data-m="D'">D′</button><button data-m="L">L</button><button data-m="L'">L′</button><button data-m="B">B</button><button data-m="B'">B′</button><button data-m="Undo">↶ Undo</button><button data-m="Reset">Reset</button></div>
    <p class="cube-sequence"><b>Lesson focus:</b> ${esc(S.a.stage_tip)}</p>
    <div id="cubeStatus" class="sim-status">Ready — use the controls above and follow the highlighted lesson.</div>
  </div>`;
}
function renderBrain() {
  if(!S.cube) S.cube=solvedCube();
  $('activityBody').innerHTML = `<div class="brain-guide"><span class="mini-label">GUIDED CUBE PATH</span><h3>${esc(S.a.stage || 'Cube Fundamentals')}</h3><p>${esc(S.a.stage_tip)}</p><div class="cube-stages"><span class="${S.a.level<=5?'current':''}">1–5 White Plus</span><span class="${S.a.level>=6&&S.a.level<=10?'current':''}">6–10 Corners</span><span class="${S.a.level>=11&&S.a.level<=14?'current':''}">11–14 Middle</span><span class="${S.a.level>=15&&S.a.level<=17?'current':''}">15–17 Yellow Plus</span><span class="${S.a.level>=18&&S.a.level<=19?'current':''}">18–19 Last Layer</span><span class="${S.a.level===20?'current':''}">20 Full Cube</span></div></div>${cubeHTML()}${renderQuestionSet(S.a.questions || [])}`;
  document.querySelectorAll('.cube-controls button').forEach(button => button.addEventListener('click',()=>{
    const move=button.dataset.m;
    if(move==='Reset'){ S.cube=solvedCube(); S.history=[]; $('cubeStatus').textContent='Reset — the cube is solved again.'; }
    else if(move==='Undo'){ const last=S.history.pop(); if(last) applyMove(S.cube,last.endsWith("'")?last[0]:last.endsWith('2')?'2':last[0]+"'"); else $('cubeStatus').textContent='Nothing to undo yet.'; if(last) $('cubeStatus').textContent=`Undid ${cubeNotation(last)}.`; }
    else { S.history.push(move); applyMove(S.cube,move); $('cubeStatus').textContent=`${cubeNotation(move)} applied. Check the stickers against the lesson goal.`; }
    paintCube();
  }));
  bindQuestions();
  $('submitButton').textContent='Check Mission';
  paintCube();
}

function essayCheck(text) {
  const n=words(text).length, sentences=(text.match(/[.!?]+/g)||[]).length, c=S.a.criteria||{};
  const min=c.minWords||50, max=c.maxWords||180, minSentences=c.minSentences||3;
  const checks=[];
  if(n<min) checks.push(`Write at least ${min} words; you currently have about ${n}.`);
  if(sentences<minSentences) checks.push(`Use at least ${minSentences} complete sentences.`);
  if(!/[.!?]$/.test(text.trim())) checks.push('Finish the final sentence with punctuation.');
  return {ok:n>=min && n<=max+30 && sentences>=minSentences && /[.!?]$/.test(text.trim()), checks:checks.length?checks:['Your response meets the basic structure.']};
}
function questionCheck() {
  const qs=S.a.questions||S.a.scenarios||[], wrong=[];
  qs.forEach((q,i)=>{
    const box=$(`explain-${i}`);
    if(S.selected[i]===undefined) wrong.push(`Answer question ${i+1}.`);
    else if(Number(S.selected[i])!==Number(q.answer)) { wrong.push(q.explanation || `Review question ${i+1}.`); if(box){box.textContent='✗ '+(q.explanation||'Review this answer.');box.className='question-explain bad';} }
    else if(box){box.textContent='✓ Correct. '+(q.explanation||'Good choice.');box.className='question-explain good';}
  });
  return {ok:wrong.length===0,checks:wrong.length?wrong:['All answers are correct.']};
}

function completeLearningLesson(){
  if(completed()) return;
  localStorage.setItem(completeKey(),'1');
  const reward=S.a.coins||10;
  setCoins(coins()+reward);
  $('coinBalance').textContent=coins();
  $('feedback').className='feedback success';
  $('feedback').innerHTML=`<strong>🎉 Learning class complete!</strong><p>You finished the study lesson and earned <b>+${reward} coins</b>. Level 2 is now ready.</p>`;
  $('startTest').disabled=true;
  $('startTest').textContent='Completed ✓';
}

function showMistake(messages){
  $('feedback').className='feedback error';
  $('feedback').innerHTML=`<strong>Not quite yet — here is how to improve.</strong><ul class="review-list">${messages.map(m=>`<li>${esc(m)}</li>`).join('')}</ul><p class="guide-line">Fix one issue at a time and submit again. You have up to 3 attempts.</p>`;
}
function showSuccess(reward,message){
  $('feedback').className='feedback success';
  $('feedback').innerHTML=`<strong>🎉 Excellent work!</strong><p>${esc(message)}</p><div class="coin-pop">+${reward} 🪙 coins added · New balance: ${coins()} coins</div>`;
  $('submitButton').classList.add('hidden'); $('resetButton').classList.add('hidden'); $('completion').className='completion';
  $('coinsAwarded').textContent=reward;
  $('progressFeedback').textContent=level<20?`Level ${level+1} is unlocked on your roadmap.`:'You completed the final level in this skill.';
}
function showFailure(){
  $('failureBox').className='failure-box';
  $('failureBox').innerHTML=`<div><div class="failure-label">LEVEL FAILED</div><h2>Use the feedback and try the level again.</h2><p>Three attempts were used. No completion reward was added for this failed run. Redo the level whenever you are ready.</p></div><button id="redo" class="primary-button">Redo Level</button>`;
  $('submitButton').classList.add('hidden'); $('resetButton').classList.add('hidden');
  $('redo').onclick=()=>{localStorage.removeItem(attemptKey());location.reload();};
}
function submit(){
  if(completed()){ showSuccess(0,'This level is already complete.'); return; }
  let result;
  if(type==='communication' && S.a.format==='essay') result=essayCheck($('response').value);
  else result=questionCheck();
  const attempt=S.attempts+1;
  saveAttempts(attempt);
  if(result.ok){
    localStorage.setItem(completeKey(),'1');
    const reward=rewardFor(S.a.coins||10,attempt);
    setCoins(coins()+reward);
    showSuccess(reward,`Level ${level} cleared on attempt ${attempt}.`);
  } else {
    updateAttemptBar(); showMistake(result.checks); if(attempt>=3) showFailure();
  }
}

async function load(){
  if(level>1 && localStorage.getItem(`completed:${grade}:${type}:${level-1}`)!=='1'){ location.href=`./roadmap.html?type=${type}&grade=${grade}`; return; }
  try{
    const response=await fetch('./data/learning-activities.json');
    if(!response.ok) throw new Error('Could not load activity content.');
    S.data=await response.json();
    S.a=S.data.grades[String(grade)].activities.find(a=>a.type===type&&a.level===level);
    if(!S.a) throw new Error('This level is not available.');
    S.attempts=Number(localStorage.getItem(attemptKey())||0);
    $('gradeSelect').value=String(grade); $('gradeLabel').textContent=grade;
    $('activityCounter').textContent=`GRADE ${grade} · ${names[type].toUpperCase()} · LEVEL ${level}`;
    $('levelTitle').textContent=S.a.title; $('levelSub').textContent=`Level ${level} of 20`;
    $('activityTitle').textContent=S.a.title; $('activityTheme').textContent=S.a.theme||`Grade ${grade} skill practice`;
    $('activityPrompt').textContent=S.a.prompt;
    $('stageLabel').textContent=type==='brainstorm' ? (S.a.stage||'CUBE STRATEGY') : 'MEDIUM SKILL PRACTICE';
    $('roadBack').href=`./roadmap.html?type=${type}&grade=${grade}`;
    $('coinBalance').textContent=coins(); updateAttemptBar();
    $('feedback').className='feedback hidden'; $('completion').className='completion hidden'; $('failureBox').className='failure-box hidden';
    $('submitButton').classList.remove('hidden'); $('resetButton').classList.remove('hidden');
    $('activityBody').innerHTML=''; S.selected={};
    if(type==='communication') renderCommunication();
    else if(type==='spell_talk') renderSpell();
    else renderBrain();
    if(completed()) showSuccess(0,'This level is already complete. You can review it or return to the roadmap.');
  }catch(error){
    $('activityTitle').textContent='Activity unavailable'; $('activityPrompt').textContent=error.message;
  }
}

$('submitButton').onclick=submit;
$('resetButton').onclick=()=>{S.selected={};S.cube=type==='brainstorm'?solvedCube():S.cube;S.history=[];load();};
$('reviewButton').onclick=()=>{$('completion').className='completion hidden';};
$('continueButton').onclick=()=>location.href=level<20?`./roadmap.html?type=${type}&grade=${grade}`:`./roadmap.html?type=${type}&grade=${grade}`;
$('gradeSelect').onchange=e=>{grade=Number(e.target.value);localStorage.setItem('selectedGrade',grade);location.href=`./roadmap.html?type=${type}&grade=${grade}`;};
load();
