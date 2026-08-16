(() => {
  'use strict';

  const state = {
    data: null,
    voices: [],
    selectedVoice: null,
    selectedSection: 'abstract',
  };

  const $ = (selector) => document.querySelector(selector);
  const elements = {
    voiceGrid: $('#voice-grid'),
    voiceCount: $('#voice-count'),
    emptyState: $('#empty-state'),
    detail: $('#voice-detail'),
    detailMeta: $('#detail-meta'),
    detailTitle: $('#detail-title'),
    detailDisclaimer: $('#detail-disclaimer'),
    detailAccent: $('#detail-accent'),
    sectionTabs: $('#section-tabs'),
    readingIndex: $('#reading-index'),
    readingLabel: $('#reading-label'),
    readingText: $('#reading-text'),
    metricList: $('#metric-list'),
    copyButton: $('#copy-button'),
    copyStatus: $('#copy-status'),
    languageFilter: $('#language-filter'),
    eraFilter: $('#era-filter'),
    search: $('#voice-search'),
  };

  const escapeHTML = (value) => String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#039;');

  const metricRows = (voice) => {
    const metrics = voice.metrics || {};
    const rows = [
      ['语言', voice.language],
      ['句长 CV', metrics.cv ?? '待测'],
      ['AI 味', metrics.ai_flavor == null ? '待测' : `${metrics.ai_flavor}/100`],
      ['声纹相似', metrics.similarity == null ? '待测' : `${metrics.similarity}%`],
    ];
    return rows.map(([label, value]) => `<div class="metric"><span>${escapeHTML(label)}</span><span>${escapeHTML(value)}</span></div>`).join('');
  };

  const populateEraFilter = () => {
    const eras = [...new Set(state.data.voices.map((voice) => voice.era))];
    elements.eraFilter.innerHTML = '<option value="all">全部时代</option>' + eras.map((era) => `<option value="${escapeHTML(era)}">${escapeHTML(era)}</option>`).join('');
  };

  const matchesFilter = (voice) => {
    const language = elements.languageFilter.value;
    const era = elements.eraFilter.value;
    const needle = elements.search.value.trim().toLowerCase();
    const haystack = [voice.name, voice.register, voice.accent, voice.language, voice.era].join(' ').toLowerCase();
    return (language === 'all' || voice.language === language)
      && (era === 'all' || voice.era === era)
      && (!needle || haystack.includes(needle));
  };

  const renderVoiceGrid = () => {
    state.voices = state.data.voices.filter(matchesFilter);
    elements.voiceCount.textContent = `${state.voices.length} / ${state.data.voices.length} VOICES`;
    elements.emptyState.hidden = state.voices.length !== 0;
    elements.voiceGrid.innerHTML = state.voices.map((voice, index) => `
      <button class="voice-card ${state.selectedVoice === voice.id ? 'is-active' : ''}" data-voice-id="${escapeHTML(voice.id)}" data-index="${String(index + 1).padStart(2, '0')}" type="button">
        <h3>${escapeHTML(voice.name)}</h3>
        <p>${escapeHTML(voice.accent)}</p>
        <span class="card-meta"><span>${escapeHTML(voice.language)}</span><span>${escapeHTML(voice.register.split(' / ')[0])}</span></span>
      </button>`).join('');
    elements.voiceGrid.querySelectorAll('[data-voice-id]').forEach((card) => {
      card.addEventListener('click', () => selectVoice(card.dataset.voiceId));
    });
  };

  const renderSectionTabs = () => {
    elements.sectionTabs.innerHTML = Object.entries(state.data.units).map(([key, label], index) => `
      <button class="section-tab" data-section="${key}" aria-selected="${state.selectedSection === key}" type="button">
        ${String(index + 1).padStart(2, '0')} ${escapeHTML(label)}
      </button>`).join('');
    elements.sectionTabs.querySelectorAll('[data-section]').forEach((tab) => {
      tab.addEventListener('click', () => {
        state.selectedSection = tab.dataset.section;
        renderDetail();
      });
    });
  };

  const renderDetail = () => {
    const voice = state.data.voices.find((item) => item.id === state.selectedVoice);
    if (!voice) {
      elements.detail.hidden = true;
      return;
    }
    const sectionKeys = Object.keys(state.data.units);
    const sectionIndex = sectionKeys.indexOf(state.selectedSection);
    const sectionKey = sectionIndex >= 0 ? state.selectedSection : sectionKeys[0];
    state.selectedSection = sectionKey;
    elements.detail.hidden = false;
    elements.detailMeta.textContent = `${voice.language} / ${voice.era} / ${voice.register}`;
    elements.detailTitle.textContent = voice.name;
    elements.detailDisclaimer.textContent = voice.disclaimer;
    elements.detailAccent.textContent = voice.accent;
    elements.metricList.innerHTML = metricRows(voice);
    renderSectionTabs();
    elements.readingIndex.textContent = `${String(sectionIndex + 1).padStart(2, '0')} / 05`;
    elements.readingLabel.textContent = state.data.units[sectionKey];
    elements.readingText.textContent = voice.sections[sectionKey];
    elements.readingText.lang = voice.language === 'English' ? 'en' : 'zh-CN';
  };

  const selectVoice = (voiceId) => {
    state.selectedVoice = voiceId;
    renderVoiceGrid();
    renderDetail();
    elements.detail.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  const copyCurrent = async () => {
    const voice = state.data.voices.find((item) => item.id === state.selectedVoice);
    if (!voice) return;
    const text = voice.sections[state.selectedSection];
    try {
      await navigator.clipboard.writeText(text);
      elements.copyStatus.textContent = '已复制';
    } catch (error) {
      elements.copyStatus.textContent = '请手动选择';
    }
    window.setTimeout(() => { elements.copyStatus.textContent = ''; }, 1800);
  };

  const bindFilters = () => {
    [elements.languageFilter, elements.eraFilter].forEach((control) => control.addEventListener('change', renderVoiceGrid));
    elements.search.addEventListener('input', renderVoiceGrid);
    elements.copyButton.addEventListener('click', copyCurrent);
  };

  const boot = async () => {
    try {
      const response = await fetch('data/styles.json');
      if (!response.ok) throw new Error(`data request failed: ${response.status}`);
      state.data = await response.json();
      populateEraFilter();
      bindFilters();
      state.selectedVoice = state.data.voices[0].id;
      renderVoiceGrid();
      renderDetail();
    } catch (error) {
      elements.voiceCount.textContent = 'DATA UNAVAILABLE';
      elements.emptyState.hidden = false;
      elements.emptyState.textContent = '无法载入共享数据。请通过本地 HTTP 服务器打开此页面。';
      console.error(error);
    }
  };

  boot();
})();
