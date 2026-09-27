const API_BASE = '/api';
const el = (id) => document.getElementById(id);

function esc(value) {
  return String(value ?? '').replace(/[&<>'"]/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  }[char]));
}

function showStatus(target, message, kind = 'info') {
  target.innerHTML = `<div class="alert alert-${kind}">${esc(message)}</div>`;
}

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {'Content-Type': 'application/json', ...(options.headers || {})},
    ...options,
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(body?.detail?.message || body?.message || 'The request failed.');
  }
  return body;
}

function mistakeRow(data = {}) {
  const wrapper = document.createElement('div');
  wrapper.className = 'mistake-editor';
  wrapper.dataset.optionId = data.option_id || '';
  wrapper.innerHTML = `
    <div class="mistake-head">
      <strong>${data.option_id ? `Tagged misconception · Option ${esc(data.option_id)}` : 'Teacher-observed mistake'}</strong>
      <button class="btn btn-secondary btn-small" type="button" data-remove-mistake>Remove</button>
    </div>
    <div class="form-field">
      <label>Where do students typically go wrong?</label>
      <input data-mistake-description placeholder="e.g. Forgets to change the negative sign when transposing the constant" value="${esc(data.mistake_description || '')}">
    </div>
    ${data.generated_wrong_answer ? `<div class="generated-answer"><span>Generated wrong option</span><strong>${esc(data.generated_wrong_answer)}</strong></div>` : ''}
    <div data-mistake-status style="margin-top:10px"></div>
  `;
  wrapper.querySelector('[data-remove-mistake]').addEventListener('click', () => wrapper.remove());
  return wrapper;
}

function renderNewStep(step = {}, index) {
  const card = document.createElement('div');
  card.className = 'author-step card';
  card.dataset.stepNumber = index;
  card.innerHTML = `
    <div class="author-step-head">
      <div>
        <div class="eyebrow" style="margin-bottom:7px">Step ${index}</div>
        <strong>Correct solution step</strong>
      </div>
      ${index > 1 ? '<button class="btn btn-secondary btn-small" type="button" data-remove-step>Remove step</button>' : ''}
    </div>
    <div class="form-field">
      <label>Step text</label>
      <input data-step-text placeholder="e.g. 6x - 3x = 11 + 4" value="${esc(step.step_text || '')}">
    </div>
    <div class="mistakes-wrap"></div>
    <button class="btn btn-secondary btn-small" type="button" data-add-mistake>+ Add where students go wrong</button>
  `;

  const mistakesWrap = card.querySelector('.mistakes-wrap');
  for (const mistake of (step.mistakes || [])) mistakesWrap.appendChild(mistakeRow(mistake));
  card.querySelector('[data-add-mistake]').addEventListener('click', () => mistakesWrap.appendChild(mistakeRow()));
  const removeStep = card.querySelector('[data-remove-step]');
  if (removeStep) removeStep.addEventListener('click', () => {
    card.remove();
    [...el('steps').querySelectorAll('.author-step')].forEach((node, i) => {
      node.dataset.stepNumber = i + 1;
      node.querySelector('.eyebrow').textContent = `Step ${i + 1}`;
    });
  });
  return card;
}

function resetNewForm() {
  el('question-text').value = '';
  el('correct-answer').value = '';
  el('steps').innerHTML = '';
  el('generated-options').innerHTML = '';
  el('steps').appendChild(renderNewStep({}, 1));
}

function collectNewPayload() {
  const teacherValue = el('teacher-id').value.trim();
  return {
    question_text: el('question-text').value.trim(),
    correct_answer: el('correct-answer').value.trim(),
    steps: [...el('steps').querySelectorAll('.author-step')].map((card, index) => ({
      step_number: index + 1,
      step_text: card.querySelector('[data-step-text]').value.trim(),
      mistakes: [...card.querySelectorAll('.mistake-editor')].map((row) => ({
        mistake_description: row.querySelector('[data-mistake-description]').value.trim(),
      })),
    })),
    ...(teacherValue ? {teacher_id: Number(teacherValue)} : {}),
  };
}

function validateNewPayload(payload) {
  if (!payload.question_text) return 'Question text is required.';
  if (!payload.correct_answer) return 'Correct final answer is required.';
  if (!payload.steps.length) return 'Add at least one solution step.';
  let mistakeCount = 0;
  for (const step of payload.steps) {
    if (!step.step_text) return `Step ${step.step_number} is empty.`;
    for (const mistake of step.mistakes) {
      mistakeCount += 1;
      if (!mistake.mistake_description) return `Describe the mistake on Step ${step.step_number}.`;
    }
  }
  if (!mistakeCount) return 'Add at least one teacher-observed mistake so the wrong-option engine has something to model.';
  return null;
}

function renderGeneratedOptions(data) {
  const rows = [];
  for (const step of (data.steps || [])) {
    for (const mistake of (step.mistakes || [])) {
      rows.push(`<div class="generated-option-row"><div><strong>Step ${esc(step.step_number)}</strong><p>${esc(mistake.mistake_description)}</p></div><div><span>Generated MCQ option</span><strong>${esc(mistake.generated_wrong_answer || mistake.wrong_step_text || '')}</strong></div></div>`);
    }
  }
  if (!rows.length) return '';
  return `<div class="card generated-options-card"><div class="ai-label">Wrong-option engine</div><h3>Generated diagnostic options</h3><p class="muted">Each option is linked to the teacher-described misconception and the exact step where it occurs.</p>${rows.join('')}</div>`;
}

function renderExisting(data) {
  const root = el('existing');
  const q = data.question;
  root.innerHTML = `
    <div class="profile-summary">
      <div class="eyebrow">Loaded question</div>
      <div class="big">${esc(q.question_text)}</div>
      <div class="profile-line"><span>Concept</span><strong>${esc(q.concept_name)}</strong></div>
      <div class="profile-line"><span>Correct answer</span><strong>${esc(q.correct_answer)}</strong></div>
    </div>
    <div class="existing-steps">
      ${data.steps.map(step => `
        <div class="author-step card" data-step-number="${step.step_number}">
          <div class="author-step-head">
            <div>
              <div class="eyebrow" style="margin-bottom:7px">Step ${step.step_number}</div>
              <strong>Correct solution</strong>
            </div>
          </div>
          <div class="readonly-step">${esc(step.step_text)}</div>
          <div class="mistakes-wrap">
            ${step.mistakes.map(m => mistakeRow(m).outerHTML).join('')}
          </div>
          <button class="btn btn-secondary btn-small" type="button" data-add-mistake>+ Add where students go wrong</button>
        </div>
      `).join('')}
    </div>
  `;

  root.querySelectorAll('.author-step').forEach((card) => {
    const stepNumber = Number(card.dataset.stepNumber);
    const mistakesWrap = card.querySelector('.mistakes-wrap');
    card.querySelector('[data-add-mistake]').addEventListener('click', () => {
      const row = mistakeRow();
      const save = document.createElement('button');
      save.type = 'button';
      save.className = 'btn btn-primary btn-small';
      save.textContent = 'Generate & save mistake';
      save.style.marginTop = '10px';
      row.appendChild(save);
      save.addEventListener('click', () => saveExistingMistake(q.id, stepNumber, row, null));
      mistakesWrap.appendChild(row);
    });

    card.querySelectorAll('.mistake-editor').forEach((row) => {
      let save = row.querySelector('[data-save-existing]');
      if (!save) {
        save = document.createElement('button');
        save.type = 'button';
        save.className = 'btn btn-secondary btn-small';
        save.textContent = 'Regenerate option';
        save.style.marginTop = '10px';
        save.dataset.saveExisting = 'true';
        row.appendChild(save);
      }
      const optionId = Number(row.dataset.optionId || 0) || null;
      save.addEventListener('click', () => saveExistingMistake(q.id, stepNumber, row, optionId));
    });
  });
}

async function saveExistingMistake(questionId, stepNumber, row, optionId) {
  const description = row.querySelector('[data-mistake-description]').value.trim();
  const status = row.querySelector('[data-mistake-status]');
  if (!description) {
    showStatus(status, 'Describe the mistake before generating an option.', 'danger');
    return;
  }
  try {
    const body = {mistake_description: description};
    if (optionId) body.option_id = optionId;
    const result = await request(`/teacher/questions/${questionId}/steps/${stepNumber}/mistakes`, {
      method: 'PATCH',
      body: JSON.stringify(body),
    });
    row.dataset.optionId = result.mistake.option_id;
    let generated = row.querySelector('.generated-answer');
    if (!generated) {
      generated = document.createElement('div');
      generated.className = 'generated-answer';
      generated.innerHTML = '<span>Generated wrong option</span><strong></strong>';
      row.insertBefore(generated, row.querySelector('[data-mistake-status]'));
    }
    generated.querySelector('strong').textContent = result.mistake.generated_wrong_answer;
    showStatus(status, 'Generated and saved. The option is now linked to this misconception.', 'success');
  } catch (error) {
    showStatus(status, error.message, 'danger');
  }
}

el('add-step').addEventListener('click', () => {
  const count = el('steps').querySelectorAll('.author-step').length + 1;
  el('steps').appendChild(renderNewStep({}, count));
});

el('save-new').addEventListener('click', async () => {
  const status = el('new-status');
  const payload = collectNewPayload();
  const validation = validateNewPayload(payload);
  if (validation) {
    showStatus(status, validation, 'danger');
    return;
  }
  try {
    const result = await request('/teacher/questions', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
    showStatus(status, `Question ${result.question.id} saved to Class 8 → Algebra → Linear Equations.`, 'success');
    el('existing-id').value = result.question.id;
    el('generated-options').innerHTML = renderGeneratedOptions(result);
    resetNewForm();
  } catch (error) {
    showStatus(status, error.message, 'danger');
  }
});

el('load-existing').addEventListener('click', async () => {
  const id = Number(el('existing-id').value);
  if (!id) {
    showStatus(el('existing'), 'Enter a question ID first.', 'danger');
    return;
  }
  el('existing').innerHTML = '<div class="loading"><div class="spinner"></div><div>Loading question…</div></div>';
  try {
    const result = await request(`/teacher/questions/${id}`);
    renderExisting(result);
  } catch (error) {
    el('existing').innerHTML = `<div class="alert alert-danger">${esc(error.message)}</div>`;
  }
});

resetNewForm();
