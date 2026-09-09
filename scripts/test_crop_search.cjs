/* Dependency-free regression tests for the actual crop filtering script. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
function element(dataset = {}) {
  return {dataset, value: '', hidden: false, events: {}, addEventListener(name, fn) {this.events[name] = fn;}, focus() {this.focused = true;}};
}
const input = element(), clear = element(), count = element({label:'crops found'}), empty = element();
const cards = ['Potato आलू Solanum tuberosum', 'Tomato टमाटर Solanum lycopersicum', 'Rice धान Oryza sativa'].map(cropSearchItem => element({cropSearchItem}));
const root = {querySelector(s) {return {'[data-crop-search]':input,'[data-crop-count]':count,'[data-crop-empty]':empty,'[data-crop-clear]':clear}[s];},querySelectorAll() {return cards;}};
const document = {addEventListener(_, fn) {fn();}, querySelectorAll() {return [root];}};
vm.runInNewContext(fs.readFileSync(path.join(__dirname, '../static/js/crop-search.js'),'utf8'),{document});
const search = query => {input.value=query;input.events.input();return cards.filter(c=>!c.hidden).length;};
assert.equal(search('  POTATO '),1);
assert.equal(search('आलू'),1);
assert.equal(search('Solanum'),2);
assert.equal(search('solanum tuberosum'),1);
assert.equal(search('no-such-crop'),0);
assert.equal(empty.hidden,false);
assert.equal(search('<script>'),0);
clear.events.click();
assert.equal(input.value,'');assert.equal(input.focused,true);
assert.equal(cards.filter(c=>!c.hidden).length,3);
assert.equal(empty.hidden,true);
assert.equal(count.textContent,'3 / 3 crops found');
console.log('Crop search: English, Hindi, scientific names, case/space, no-match and clear tests passed.');
