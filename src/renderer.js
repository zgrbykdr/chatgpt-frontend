const { recalcCharacter } = require('./lib/modifierEngine');
const { emptyCharacter, uid } = require('./lib/models');

const state = {
  campaign: null,
  selectedCharacterId: null,
  savePath: null,
  privateMappings: { mappings: [] },
};

const STARTER_FEATS = [
  {
    id: 'feat_improved_initiative_srd',
    name: 'Improved Initiative',
    source: 'SRD 3.5',
    summary: '+4 bonus on initiative checks.',
    mappingStatus: 'Mapped',
    prerequisites: [],
    modifiers: [{ target: 'initiative', value: 4, bonusType: 'untyped', notes: 'Improved Initiative' }],
  },
];

const STARTER_CONDITIONS = [
  {
    id: 'condition_fatigued',
    name: 'Fatigued',
    summary: '-2 Strength and -2 Dexterity; cannot run/charge.',
    type: 'condition',
    defaultDurationRounds: 10,
    modifiers: [
      { target: 'ability.STR', value: -2, bonusType: 'penalty' },
      { target: 'ability.DEX', value: -2, bonusType: 'penalty' },
    ],
  },
];

function byId(id) { return document.getElementById(id); }
function selectedChar() { return state.campaign.characters.find((c) => c.id === state.selectedCharacterId); }

async function initialize() {
  const campaign = await window.dmApp.newCampaign();
  campaign.libraries.feats = [...STARTER_FEATS];
  campaign.libraries.conditions = [...STARTER_CONDITIONS];
  state.campaign = campaign;
  state.selectedCharacterId = campaign.characters[0].id;
  rerender();
  wireEvents();
}

function rerender() {
  state.campaign.characters = state.campaign.characters.map((c) => recalcCharacter(c));
  renderCharacterList();
  renderCharacterDetails();
  renderFeatLibrary();
  renderEffects();
  renderCombat();
}

function renderCharacterList() {
  const q = byId('charSearch').value?.toLowerCase() || '';
  byId('characterList').innerHTML = state.campaign.characters
    .filter((c) => c.identity.name.toLowerCase().includes(q))
    .map((c) => `<li data-id="${c.id}" class="${state.selectedCharacterId === c.id ? 'active' : ''}">${c.identity.name} (${c.type})</li>`)
    .join('');
  [...byId('characterList').querySelectorAll('li')].forEach((li) => {
    li.onclick = () => { state.selectedCharacterId = li.dataset.id; rerender(); };
  });
}

function renderCharacterDetails() {
  const c = selectedChar();
  if (!c) return;
  byId('charName').value = c.identity.name;
  byId('charPlayer').value = c.identity.player;
  byId('charType').value = c.type;
  byId('charRace').value = c.identity.race;
  byId('hpMax').value = c.hp.max;
  byId('hpCurrent').value = c.hp.current;
  byId('hpTemp').value = c.hp.temp;
  byId('hpNonlethal').value = c.hp.nonlethal;
  byId('acArmor').value = c.combat.ac.armor;
  byId('acShield').value = c.combat.ac.shield;
  byId('acNatural').value = c.combat.ac.natural;
  byId('initMisc').value = c.combat.initiativeMisc;
  byId('charNotes').value = c.notes.persistent;
  byId('charSessionNotes').value = c.notes.session;
  byId('campaignGlobalNotes').value = state.campaign.globalNotes;

  byId('derivedLine').textContent =
    `Init ${c.derived.initiative} | AC ${c.derived.armorClass.total} (Touch ${c.derived.armorClass.touch}, Flat ${c.derived.armorClass.flatFooted}) | ` +
    `Fort ${c.derived.saves.Fort}, Ref ${c.derived.saves.Ref}, Will ${c.derived.saves.Will}`;

  byId('selectedFeats').innerHTML = (c.featChoices || []).map((f) => `<li>${f.name} <span class="status-${f.mappingStatus.toLowerCase()}">${f.mappingStatus}</span></li>`).join('');
}

function renderFeatLibrary() {
  const q = byId('featSearch').value?.toLowerCase() || '';
  const feats = state.campaign.libraries.feats.filter((f) => f.name.toLowerCase().includes(q));
  byId('featList').innerHTML = feats.map((f) =>
    `<li><strong>${f.name}</strong> — ${f.source} <span class="status-${f.mappingStatus.toLowerCase()}">${f.mappingStatus}</span><br/>` +
    `<small>${f.summary || ''}</small><br/><button data-feat="${f.id}">Select</button></li>`).join('');

  [...byId('featList').querySelectorAll('button')].forEach((btn) => {
    btn.onclick = () => {
      const feat = state.campaign.libraries.feats.find((f) => f.id === btn.dataset.feat);
      const c = selectedChar();
      if (!feat || !c) return;
      if (c.featChoices.some((x) => x.id === feat.id)) return;
      c.featChoices.push({ ...feat });
      if (feat.mappingStatus !== 'Mapped') alert('Warning: This feat is currently Unmapped and will not modify stats yet.');
      rerender();
    };
  });

  byId('mapperFeatSelect').innerHTML = feats.map((f) => `<option value="${f.id}">${f.name} (${f.source})</option>`).join('');
}

function renderEffects() {
  const c = selectedChar();
  byId('effectsList').innerHTML = (c?.effects || []).map((e, idx) =>
    `<li>${e.name} (${e.type}) - ${e.remainingRounds ?? 'Permanent'} rounds left <button data-idx="${idx}">Toggle</button></li>`).join('');
  [...byId('effectsList').querySelectorAll('button')].forEach((btn) => {
    btn.onclick = () => {
      const fx = c.effects[Number(btn.dataset.idx)];
      fx.active = fx.active === false;
      rerender();
    };
  });
}

function renderCombat() {
  const rows = [...state.campaign.characters]
    .map((c) => recalcCharacter(c))
    .sort((a, b) => b.derived.initiative - a.derived.initiative)
    .map((c) => `<tr>
      <td>${c.identity.name}</td>
      <td>${c.derived.initiative}</td>
      <td>${c.hp.current}/${c.hp.max} (+${c.hp.temp} temp)</td>
      <td>${c.derived.armorClass.total}</td>
      <td>F ${c.derived.saves.Fort} R ${c.derived.saves.Ref} W ${c.derived.saves.Will}</td>
      <td>${(c.effects || []).filter((e) => e.active !== false).map((e) => e.name).join(', ')}</td>
      <td><button data-dmg="${c.id}">-5</button><button data-heal="${c.id}">+5</button></td>
    </tr>`).join('');
  byId('combatRows').innerHTML = rows;
  [...byId('combatRows').querySelectorAll('button[data-dmg]')].forEach((b) => b.onclick = () => mutateHp(b.dataset.dmg, -5));
  [...byId('combatRows').querySelectorAll('button[data-heal]')].forEach((b) => b.onclick = () => mutateHp(b.dataset.heal, 5));
}

function mutateHp(charId, delta) {
  const c = state.campaign.characters.find((x) => x.id === charId);
  if (!c) return;
  c.hp.log.push({ time: new Date().toISOString(), delta, before: c.hp.current });
  c.hp.current = Math.max(-999, c.hp.current + delta);
  rerender();
}

function applyOverviewEdits() {
  const c = selectedChar();
  if (!c) return;
  c.identity.name = byId('charName').value;
  c.identity.player = byId('charPlayer').value;
  c.type = byId('charType').value;
  c.identity.race = byId('charRace').value;
  c.hp.max = Number(byId('hpMax').value || 0);
  c.hp.current = Number(byId('hpCurrent').value || 0);
  c.hp.temp = Number(byId('hpTemp').value || 0);
  c.hp.nonlethal = Number(byId('hpNonlethal').value || 0);
  c.combat.ac.armor = Number(byId('acArmor').value || 0);
  c.combat.ac.shield = Number(byId('acShield').value || 0);
  c.combat.ac.natural = Number(byId('acNatural').value || 0);
  c.combat.initiativeMisc = Number(byId('initMisc').value || 0);
  c.notes.persistent = byId('charNotes').value;
  c.notes.session = byId('charSessionNotes').value;
  state.campaign.globalNotes = byId('campaignGlobalNotes').value;
}

function applyFatigued() {
  const c = selectedChar();
  const base = state.campaign.libraries.conditions.find((x) => x.id === 'condition_fatigued');
  if (!c || !base) return;
  c.effects.push({
    id: uid('fx'),
    ...base,
    source: 'DM Quick Apply',
    startRound: state.campaign.currentRound,
    remainingRounds: 10,
    active: true,
  });
  rerender();
}

function endRound() {
  state.campaign.currentRound += 1;
  for (const c of state.campaign.characters) {
    c.effects = (c.effects || []).filter((e) => {
      if (e.remainingRounds == null || e.active === false) return true;
      e.remainingRounds -= 1;
      return e.remainingRounds > 0;
    });
  }
  rerender();
}

async function importFeatTxt() {
  const parsed = await window.dmApp.pickFeatTxt();
  if (!parsed) return;
  state.campaign.libraries.imports.sourceFiles.push({ filePath: parsed.sourceFile, importedAt: new Date().toISOString() });
  for (const row of parsed.rows) {
    state.campaign.libraries.imports.featRows.push(row);
    if (!state.campaign.libraries.feats.some((f) => f.name === row.name && f.source === row.source)) {
      state.campaign.libraries.feats.push(row);
    }
  }
  const improved = state.campaign.libraries.feats.find((f) => f.name.toLowerCase() === 'improved initiative');
  if (improved) {
    improved.mappingStatus = 'Mapped';
    improved.modifiers = [{ target: 'initiative', value: 4, bonusType: 'untyped', notes: 'Improved Initiative' }];
  }
  alert(`Imported ${parsed.rows.length} feats from TXT.`);
  rerender();
}

function saveMapping() {
  const featId = byId('mapperFeatSelect').value;
  const feat = state.campaign.libraries.feats.find((f) => f.id === featId);
  if (!feat) return;
  const mapping = {
    featId: feat.id,
    featName: feat.name,
    source: feat.source,
    modifiers: [{
      target: byId('mapTarget').value,
      value: Number(byId('mapValue').value || 0),
      bonusType: byId('mapType').value || 'untyped',
    }],
    prerequisites: [],
  };
  state.campaign.libraries.imports.mappings.push(mapping);
  feat.mappingStatus = 'Mapped';
  feat.modifiers = mapping.modifiers;
  alert('Mapping saved into local private feat mechanics pack (inside campaign data).');
  rerender();
}

async function importFeatMappingJson() {
  const payload = await window.dmApp.pickJson();
  if (!payload) return;
  const mappings = payload.json.mappings || [];
  for (const map of mappings) {
    const feat = state.campaign.libraries.feats.find((f) => f.id === map.featId || (f.name === map.featName && f.source === map.source));
    if (feat) {
      feat.mappingStatus = 'Mapped';
      feat.modifiers = map.modifiers || [];
      feat.prerequisites = map.prerequisites || [];
    }
  }
  alert(`Imported ${mappings.length} feat mappings.`);
  rerender();
}

async function saveCampaign(asNew = false) {
  applyOverviewEdits();
  if (asNew || !state.savePath) {
    const p = await window.dmApp.pickSavePath();
    if (!p) return;
    state.savePath = p;
  }
  const res = await window.dmApp.saveCampaign({ campaign: state.campaign, targetPath: state.savePath });
  state.savePath = res.finalPath;
  state.campaign = res.campaign;
  alert(`Saved to ${res.finalPath}`);
}

async function loadCampaign() {
  const loaded = await window.dmApp.loadCampaign();
  if (!loaded) return;
  state.campaign = loaded.campaign;
  state.savePath = loaded.filePath;
  state.selectedCharacterId = state.campaign.characters[0]?.id || null;
  rerender();
}

function wireEvents() {
  ['charName', 'charPlayer', 'charType', 'charRace', 'hpMax', 'hpCurrent', 'hpTemp', 'hpNonlethal', 'acArmor', 'acShield', 'acNatural', 'initMisc', 'charNotes', 'charSessionNotes', 'campaignGlobalNotes']
    .forEach((id) => byId(id).addEventListener('change', () => { applyOverviewEdits(); rerender(); }));

  byId('newCampaignBtn').onclick = async () => { state.campaign = await window.dmApp.newCampaign(); state.selectedCharacterId = state.campaign.characters[0].id; rerender(); };
  byId('loadCampaignBtn').onclick = loadCampaign;
  byId('saveCampaignBtn').onclick = () => saveCampaign(false);
  byId('saveAsCampaignBtn').onclick = () => saveCampaign(true);
  byId('exportCharsBtn').onclick = () => window.dmApp.exportCharacters({ characters: state.campaign.characters });
  byId('importFeatTxtBtn').onclick = importFeatTxt;
  byId('importFeatMappingBtn').onclick = importFeatMappingJson;

  byId('addCharacterBtn').onclick = () => { state.campaign.characters.push(emptyCharacter()); state.selectedCharacterId = state.campaign.characters.at(-1).id; rerender(); };
  byId('charSearch').oninput = renderCharacterList;
  byId('featSearch').oninput = renderFeatLibrary;

  byId('applyDamageBtn').onclick = () => mutateHp(state.selectedCharacterId, -Math.abs(Number(byId('hpDelta').value || 0)));
  byId('applyHealBtn').onclick = () => mutateHp(state.selectedCharacterId, Math.abs(Number(byId('hpDelta').value || 0)));
  byId('undoHpBtn').onclick = () => {
    const c = selectedChar();
    const last = c.hp.log.pop();
    if (last) c.hp.current = last.before;
    rerender();
  };
  byId('fatiguedBtn').onclick = applyFatigued;
  byId('saveMappingBtn').onclick = saveMapping;
  byId('endRoundBtn').onclick = endRound;

  window.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key.toLowerCase() === 'd') byId('applyDamageBtn').click();
    if (e.ctrlKey && e.key.toLowerCase() === 'h') byId('applyHealBtn').click();
    if (e.ctrlKey && e.key.toLowerCase() === 'e') byId('endRoundBtn').click();
    if (e.ctrlKey && e.key.toLowerCase() === 'f') byId('fatiguedBtn').click();
  });
}

initialize();
