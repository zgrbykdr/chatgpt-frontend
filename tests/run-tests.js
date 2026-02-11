const assert = require('assert');
const { recalcCharacter } = require('../src/lib/modifierEngine');
const { emptyCharacter } = require('../src/lib/models');
const { parseFeatTxt } = require('../src/lib/txtFeatParser');

function testAbilityAndInitiative() {
  const c = emptyCharacter();
  c.abilities.DEX.base = 14;
  c.featChoices.push({
    id: 'feat_improved_initiative_srd',
    name: 'Improved Initiative',
    modifiers: [{ target: 'initiative', value: 4, bonusType: 'untyped' }],
  });
  const out = recalcCharacter(c);
  assert.strictEqual(out.derived.abilities.DEX.mod, 2, 'DEX modifier should be +2');
  assert.strictEqual(out.derived.initiative, 6, 'Initiative should include +4 feat bonus');
}

function testFatiguedPenalties() {
  const c = emptyCharacter();
  c.abilities.STR.base = 14;
  c.abilities.DEX.base = 14;
  c.effects.push({
    name: 'Fatigued',
    active: true,
    modifiers: [
      { target: 'ability.STR', value: -2, bonusType: 'penalty' },
      { target: 'ability.DEX', value: -2, bonusType: 'penalty' },
    ],
  });
  const out = recalcCharacter(c);
  assert.strictEqual(out.derived.abilities.STR.score, 12, 'Fatigued should lower STR by 2');
  assert.strictEqual(out.derived.abilities.DEX.score, 12, 'Fatigued should lower DEX by 2');
}

function testTxtParser() {
  const txt = `Name\tSource\tDescription\nImproved Initiative\tPHB p.96\tMove faster in combat\nImproved Initiative\tPHB p.96\tDuplicate row\nAlertness\tMM 2003 p.12\tKeen senses`;
  const out = parseFeatTxt(txt, 'sample.txt');
  assert.strictEqual(out.rows.length, 2, 'Dedup by name+source should remove duplicate');
  assert.strictEqual(out.rows[0].source, 'PHB p.96', 'Source must be preserved exactly');
}

function run() {
  testAbilityAndInitiative();
  testFatiguedPenalties();
  testTxtParser();
  console.log('All tests passed');
}

run();
