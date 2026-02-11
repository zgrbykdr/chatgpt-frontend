const STACKING_RULES = {
  default: 'max',
  dodge: 'stack',
  circumstance: 'stack',
  untyped: 'stack',
  penalty: 'stack',
};

function abilityTotal(block) {
  return Object.values(block).reduce((a, b) => a + (Number(b) || 0), 0);
}

function abilityMod(score) {
  return Math.floor((score - 10) / 2);
}

function applyStacking(mods, rules = STACKING_RULES) {
  const buckets = new Map();
  for (const mod of mods.filter((m) => m.active !== false)) {
    const type = (mod.bonusType || 'untyped').toLowerCase();
    const key = `${mod.target}|${type}`;
    if (!buckets.has(key)) buckets.set(key, []);
    buckets.get(key).push(mod);
  }
  const resolved = [];
  for (const [key, list] of buckets.entries()) {
    const type = key.split('|')[1];
    const mode = rules[type] || rules.default;
    if (mode === 'stack') {
      resolved.push(...list);
    } else {
      const best = list.reduce((bestItem, cur) => (Number(cur.value) > Number(bestItem.value) ? cur : bestItem), list[0]);
      resolved.push(best);
    }
  }
  return resolved;
}

function collectCharacterModifiers(character) {
  const fromEffects = (character.effects || [])
    .filter((e) => e.active !== false)
    .flatMap((e) => (e.modifiers || []).map((m) => ({ ...m, source: e.name })));
  const fromFeats = (character.featChoices || [])
    .filter((f) => f.active !== false)
    .flatMap((f) => (f.modifiers || []).map((m) => ({ ...m, source: f.name })));
  const base = character.modifiers || [];
  return [...base, ...fromEffects, ...fromFeats];
}

function sumTarget(mods, target) {
  return mods.filter((m) => m.target === target).reduce((sum, m) => sum + Number(m.value || 0), 0);
}

function recalcCharacter(character) {
  const mods = applyStacking(collectCharacterModifiers(character));
  const ab = {};
  for (const k of ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']) {
    const score = abilityTotal(character.abilities[k]) + sumTarget(mods, `ability.${k}`);
    ab[k] = { score, mod: abilityMod(score) };
  }

  const dexForAc = character.combat.ac.dexCap == null ? ab.DEX.mod : Math.min(ab.DEX.mod, character.combat.ac.dexCap);
  const initiative = ab.DEX.mod + Number(character.combat.initiativeMisc || 0) + sumTarget(mods, 'initiative');
  const ac =
    10 +
    Number(character.combat.ac.armor || 0) +
    Number(character.combat.ac.shield || 0) +
    dexForAc +
    Number(character.combat.ac.size || 0) +
    Number(character.combat.ac.natural || 0) +
    Number(character.combat.ac.deflection || 0) +
    Number(character.combat.ac.dodge || 0) +
    Number(character.combat.ac.misc || 0) +
    sumTarget(mods, 'ac.total');

  const touch = 10 + dexForAc + Number(character.combat.ac.size || 0) + Number(character.combat.ac.deflection || 0) + Number(character.combat.ac.dodge || 0) + sumTarget(mods, 'ac.touch');
  const flatFooted = ac - dexForAc - Number(character.combat.ac.dodge || 0);

  const saves = {
    Fort: Number(character.saves.Fort.base || 0) + ab.CON.mod + Number(character.saves.Fort.misc || 0) + sumTarget(mods, 'save.Fort'),
    Ref: Number(character.saves.Ref.base || 0) + ab.DEX.mod + Number(character.saves.Ref.misc || 0) + sumTarget(mods, 'save.Ref'),
    Will: Number(character.saves.Will.base || 0) + ab.WIS.mod + Number(character.saves.Will.misc || 0) + sumTarget(mods, 'save.Will'),
  };

  return {
    ...character,
    derived: {
      abilities: ab,
      initiative,
      armorClass: { total: ac, touch, flatFooted },
      saves,
    },
  };
}

module.exports = {
  STACKING_RULES,
  abilityMod,
  applyStacking,
  recalcCharacter,
};
