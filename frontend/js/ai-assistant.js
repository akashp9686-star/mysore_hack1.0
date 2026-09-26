(function(){
  const existing=document.getElementById('learning-assistant-widget');
  if(existing) return;

  function readProfile(){try{return JSON.parse(localStorage.getItem('pl_profile')||'null')}catch(_){return null}}
  const profile=readProfile();
  if(!profile) return;

  const studentId=Number(new URLSearchParams(location.search).get('student_id')||profile.student_id||localStorage.getItem('hackmysore_student_id')||101);
  const displayName=(profile.name||'Learner').trim()||'Learner';
  const widget=document.createElement('div');
  widget.id='learning-assistant-widget';
  widget.innerHTML=`
    <button class="ai-fab" id="ai-fab" aria-label="Open Learning Assistant" title="Learning Assistant">
      <span class="ai-fab-pulse"></span><span class="ai-fab-icon">✦</span>
    </button>
    <section class="ai-panel" id="ai-panel" role="dialog" aria-modal="false" aria-label="Learning Assistant">
      <header class="ai-panel-head">
        <div class="ai-panel-title"><div class="ai-panel-logo">✦</div><div><strong>Learning Assistant</strong><span>Advisory · powered by your learning evidence</span></div></div>
        <button class="ai-close" id="ai-close" aria-label="Close">×</button>
      </header>
      <div class="ai-context" id="ai-context">Your learning data is ready.</div>
      <div class="ai-messages" id="ai-messages"><div class="ai-msg bot">Hi ${esc(displayName)}! How can I help you with your learning today?</div></div>
      <div class="ai-suggestions">
        <button class="ai-suggestion" data-q="What am I struggling with right now?">What am I struggling with?</button>
        <button class="ai-suggestion" data-q="Why was this recommended?">Why this recommendation?</button>
        <button class="ai-suggestion" data-q="What should I learn next?">What next?</button>
      </div>
      <form class="ai-form" id="ai-form"><input class="ai-input" id="ai-input" autocomplete="off" maxlength="600" placeholder="Ask about your learning…"><button class="ai-send" id="ai-send" type="submit" aria-label="Send">↑</button></form>
    </section>`;
  document.body.appendChild(widget);
  const fab=document.getElementById('ai-fab'), panel=document.getElementById('ai-panel'), close=document.getElementById('ai-close'), form=document.getElementById('ai-form'), input=document.getElementById('ai-input'), send=document.getElementById('ai-send'), messages=document.getElementById('ai-messages'), context=document.getElementById('ai-context');
  let contextLoaded=false;
  function addMessage(text,who,source){const d=document.createElement('div');d.className=`ai-msg ${who}`;d.textContent=text;if(source){const s=document.createElement('div');s.className='ai-source';s.textContent=source;d.appendChild(s)}messages.appendChild(d);messages.scrollTop=messages.scrollHeight;return d;}
  function toggle(open){panel.classList.toggle('open',open);if(open){input.focus();loadContext();}}
  fab.addEventListener('click',()=>toggle(!panel.classList.contains('open')));close.addEventListener('click',()=>toggle(false));
  document.addEventListener('keydown',e=>{if(e.key==='Escape')toggle(false)});
  async function loadContext(){
    if(contextLoaded) return; contextLoaded=true;
    try{
      if(typeof getStudentProgress==='function'){
        const p=await getStudentProgress(studentId); const weak=(p.weak_concepts&&p.weak_concepts[0])||null;
        context.innerHTML=weak?`Current focus: <strong>${esc(weak.name)}</strong> · ${Math.round(weak.accuracy||0)}% accuracy`:'Your learning data is ready. Ask me about your next step.';
      } else context.textContent='Your learning data is ready. Ask me about your next step.';
    }catch(_){context.textContent='Your learning path is available even if AI assistance is unavailable.';}
  }
  async function ask(question){
    if(!question.trim()) return;
    addMessage(question,'user'); input.value=''; send.disabled=true;
    const loadingMsg=addMessage('Thinking from your learning evidence…','bot');
    try{
      if(typeof apiFetch!=='function') throw new Error('Learning API is unavailable.');
      const result=await apiFetch('/ai/assistant',{method:'POST',body:JSON.stringify({student_id:studentId,message:question.trim(),display_name:displayName})});
      loadingMsg.remove(); addMessage(result.answer||'I could not generate an answer right now.', 'bot', result.source==='jai_ganesh_ai_agent'?'Jai Ganesh AI · advisory':'AI unavailable · adaptive engine still active');
    }catch(e){loadingMsg.remove();addMessage('AI assistance is currently unavailable. Your personalized learning path is still available through the adaptive engine.','bot','Adaptive engine remains active');}
    finally{send.disabled=false;input.focus();}
  }
  form.addEventListener('submit',e=>{e.preventDefault();ask(input.value)});
  document.querySelectorAll('.ai-suggestion').forEach(b=>b.addEventListener('click',()=>ask(b.dataset.q)));

  // Open once after a fresh login, then remain available from the corner.
  if(!sessionStorage.getItem('pl_ai_greeted_session')){
    sessionStorage.setItem('pl_ai_greeted_session','1');
    setTimeout(()=>toggle(true),420);
  }
})();