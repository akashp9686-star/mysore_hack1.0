const params = new URLSearchParams(location.search);
const type = params.get('type') || 'communication';
let grade = Number(params.get('grade') || localStorage.getItem('selectedGrade') || 5);

const names = {
  communication: 'Communication Skills',
  spell_talk: 'Spell Talk',
  brainstorm: 'Brainstorm'
};

const key = level => `completed:${grade}:${type}:${level}`;
const done = level => localStorage.getItem(key(level)) === '1';
const unlocked = level => level === 1 || done(level - 1);

function completedCount() {
  let count = 0;
  for (let i = 1; i <= 20; i++) if (done(i)) count++;
  return count;
}

function render() {
  const count = completedCount();
  const next = Math.min(20, count + 1);

  document.getElementById('gradeSelect').value = String(grade);
  document.getElementById('coinBalance').textContent = localStorage.getItem('learningCoins') || '10';
  document.getElementById('roadmapEyebrow').textContent = `${names[type].toUpperCase()} · GRADE ${grade}`;
  document.getElementById('roadmapTitle').textContent = `${names[type]} road map.`;
  document.getElementById('progressTitle').textContent = `${count} of 20 levels completed`;
  document.getElementById('progressChip').textContent = `${count} / 20`;
  document.getElementById('roadmapFill').style.width = `${count * 5}%`;

  const continueButton = document.getElementById('continueLevel');
  const continueText = document.getElementById('continueText');
  continueText.textContent = count >= 20 ? 'All 20 levels complete' : `Continue from Level ${next}`;
  continueButton.href = count >= 20 ? `./activity.html?type=${type}&grade=${grade}&level=20` : `./activity.html?type=${type}&grade=${grade}&level=${next}`;

  const root = document.getElementById('levels');
  root.innerHTML = '';

  for (let i = 1; i <= 20; i++) {
    const a = document.createElement('a');
    const isUnlocked = unlocked(i);
    const isComplete = done(i);
    a.className = `road-level ${isUnlocked ? 'unlocked' : 'locked'} ${isComplete ? 'complete' : ''}`;
    a.href = isUnlocked ? `./activity.html?type=${type}&grade=${grade}&level=${i}` : '#';
    a.innerHTML = `
      <span class="road-number">${String(i).padStart(2, '0')}</span>
      <span class="road-main">
        <b>Level ${i}</b>
        <small>${isComplete ? 'Completed' : isUnlocked ? (i === next ? 'Continue here' : 'Open level') : 'Locked — complete the previous level'}</small>
      </span>
      <span class="road-state">${isComplete ? '✓' : isUnlocked ? 'OPEN' : '🔒'}</span>`;
    if (!isUnlocked) a.onclick = e => e.preventDefault();
    root.appendChild(a);
  }
}

document.getElementById('gradeSelect').onchange = e => {
  grade = Number(e.target.value);
  localStorage.setItem('selectedGrade', grade);
  render();
};

render();
