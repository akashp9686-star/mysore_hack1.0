const stages=[['beginner','Beginner','Board control, checks, captures and simple tactics.'],['intermediate','Intermediate','Candidate moves, tactical patterns and short calculation.'],['advanced','Advanced','Deeper calculation, king safety and accurate conversion.']];
const key=(stage,l)=>`chess:${stage}:${l}`;
const done=(stage,l)=>localStorage.getItem(key(stage,l))==='1';
const count=stage=>{let n=0;for(let i=1;i<=25;i++)if(done(stage,i))n++;return n};
const stageComplete=stage=>count(stage)>=25;
function stageUnlocked(i){return i===0||stageComplete(stages[i-1][0]);}
function currentStageIndex(){for(let i=0;i<stages.length;i++)if(!stageComplete(stages[i][0]))return i;return 2;}
let selected=currentStageIndex();
function render(){
 document.getElementById('coins').textContent=localStorage.getItem('learningCoins')||10;
 const totalDone=stages.reduce((n,s)=>n+count(s[0]),0); document.getElementById('status').textContent=totalDone===75?'All 75 chess levels complete!':`Continue at ${stages[selected][1]} Level ${count(stages[selected][0])+1}`;
 document.getElementById('statusText').textContent=selected===0?'Build your foundation first. Intermediate unlocks only after all 25 Beginner levels are complete.':selected===1?'Beginner is complete. Now continue through the 25 Intermediate levels.':'Intermediate is complete. Advanced is now open.';
 const next=Math.min(25,count(stages[selected][0])+1); document.getElementById('continueLink').href=`../concepts/chess_problems/index.html?stage=${stages[selected][0]}&level=${next}`;
 const root=document.getElementById('stages');root.innerHTML='';
 stages.forEach((s,i)=>{const unlocked=stageUnlocked(i),n=count(s[0]);const card=document.createElement('article');card.className=`chess-stage ${unlocked?'':'locked'} ${i===selected?'selected-stage':''}`;card.innerHTML=`<span class="section-label">STAGE 0${i+1}</span><h2>${s[1]} · 25 levels</h2><p>${s[2]}</p><div class="stage-progress"><div style="width:${n*4}%"></div></div><small>${n}/25 complete</small><button class="start-button stage-select" ${unlocked?'':'disabled'}>${unlocked?'View roadmap →':'Locked until previous stage is complete'}</button>`;card.querySelector('.stage-select').onclick=()=>{if(unlocked){selected=i;render();}};root.appendChild(card);});
 document.getElementById('stageTitle').textContent=`${stages[selected][1]} · 25 levels`;
 const n=count(stages[selected][0]);document.getElementById('stageProgress').textContent=`${n} / 25`;document.getElementById('stageFill').style.width=`${n*4}%`;
 const levels=document.getElementById('levels');levels.innerHTML='';for(let i=1;i<=25;i++){const unlocked=i===1||done(stages[selected][0],i-1);const c=done(stages[selected][0],i);const a=document.createElement('a');a.className=`road-level ${unlocked?'unlocked':'locked'} ${c?'complete':''}`;a.href=unlocked?`../concepts/chess_problems/index.html?stage=${stages[selected][0]}&level=${i}`:'#';a.innerHTML=`<span class="road-number">${String(i).padStart(2,'0')}</span><span class="road-main"><b>Level ${i}</b><small>${c?'Completed':unlocked?(i===n+1?'Continue here':'Open level'):'Locked — clear Level '+(i-1)}</small></span><span class="road-state">${c?'✓':unlocked?'OPEN':'🔒'}</span>`;if(!unlocked)a.onclick=e=>e.preventDefault();levels.appendChild(a);}
}
render();
