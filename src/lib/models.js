function uid(prefix = 'id') {
  return `${prefix}_${Math.random().toString(36).slice(2, 10)}`;
}

function emptyCharacter() {
  return {
    id: uid('char'),
    type: 'PC',
    tags: ['party'],
    archived: false,
    identity: {
      name: 'New Character',
      player: '',
      race: '',
      classLevels: [{ classId: 'fighter', level: 1 }],
      alignment: '',
      deity: '',
      size: 'Medium',
      age: '',
      gender: '',
      heightWeight: '',
      appearance: '',
      homeland: '',
      languages: [],
    },
    abilities: {
      STR: baseAbility(), DEX: baseAbility(), CON: baseAbility(),
      INT: baseAbility(), WIS: baseAbility(), CHA: baseAbility(),
    },
    hp: {
      max: 10,
      current: 10,
      temp: 0,
      nonlethal: 0,
      damageReduction: '',
      energyResistances: [],
      immunities: [],
      fastHealing: 0,
      regeneration: 0,
      stableAtNegative: true,
      log: [],
    },
    combat: {
      baseAttackBonus: 1,
      grappleMisc: 0,
      speed: { land: 30, fly: 0, swim: 0, climb: 0, burrow: 0 },
      ac: { armor: 0, shield: 0, size: 0, natural: 0, deflection: 0, dodge: 0, misc: 0, dexCap: null },
      initiativeMisc: 0,
      attacks: [],
      initiativeScore: 0,
    },
    saves: { Fort: { base: 2, misc: 0 }, Ref: { base: 0, misc: 0 }, Will: { base: 0, misc: 0 }, conditional: [] },
    skills: [],
    feats: [],
    featChoices: [],
    spells: {
      classes: [],
      prepared: {},
      expended: {},
      known: {},
      spontaneous: false,
      notes: '',
    },
    equipment: { inventory: [], currency: { cp: 0, sp: 0, gp: 0, pp: 0 } },
    specialAbilities: [],
    effects: [],
    notes: { persistent: '', session: '' },
    modifiers: [],
    initiative: 0,
  };
}

function baseAbility() {
  return {
    base: 10,
    racial: 0,
    level: 0,
    enhancement: 0,
    morale: 0,
    circumstance: 0,
    misc: 0,
  };
}

function createDefaultCampaign() {
  return {
    schemaVersion: 1,
    id: uid('camp'),
    name: 'New Campaign',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    globalNotes: '',
    sessionNotes: '',
    currentRound: 1,
    currentTurnCharacterId: null,
    initiativeOrder: [],
    filePath: null,
    libraries: {
      feats: [],
      spells: [],
      conditions: [],
      items: [],
      imports: { sourceFiles: [], featRows: [], mappings: [] },
    },
    characters: [emptyCharacter()],
  };
}

function migrateCampaign(campaign) {
  if (!campaign || typeof campaign !== 'object') return createDefaultCampaign();
  const out = { ...createDefaultCampaign(), ...campaign };
  out.schemaVersion = 1;
  out.characters = (campaign.characters || []).map((c) => ({ ...emptyCharacter(), ...c }));
  return out;
}

module.exports = { uid, emptyCharacter, createDefaultCampaign, migrateCampaign };
