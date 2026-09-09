/* Filter existing cards without network requests or removing their links. */
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-crop-search-root]').forEach(root => {
    const input = root.querySelector('[data-crop-search]');
    const cards = [...root.querySelectorAll('[data-crop-search-item]')];
    const count = root.querySelector('[data-crop-count]');
    const empty = root.querySelector('[data-crop-empty]');
    if (!input || !count || !empty) return;
    const normalize = value => value.normalize('NFKC').toLocaleLowerCase().trim();
    const entries = cards.map(card => ({card, text: normalize(card.dataset.cropSearchItem)}));
    const filter = () => {
      const words = normalize(input.value).split(/\s+/).filter(Boolean);
      let visible = 0;
      entries.forEach(({card, text}) => {
        card.hidden = !words.every(word => text.includes(word));
        if (!card.hidden) visible++;
      });
      count.textContent = `${visible} / ${cards.length} ${count.dataset.label}`;
      empty.hidden = visible !== 0;
    };
    input.addEventListener('input', filter);
    root.querySelector('[data-crop-clear]').addEventListener('click', () => {
      input.value = ''; filter(); input.focus();
    });
    filter();
  });
});
