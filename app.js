const list = document.querySelector('#mod-list');
const statusText = document.querySelector('#status-text');
const playerPanel = document.querySelector('#player-panel');
const currentMod = document.querySelector('#current-mod');
const gameFrame = document.querySelector('#game-frame');
const openGame = document.querySelector('#open-game');

function prettyName(slug) {
  return slug.replace(/[-_]+/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());
}

function showEmpty(message) {
  list.innerHTML = `<div class="empty">${message}</div>`;
}

function playMod(mod) {
  const url = `/mods/${encodeURIComponent(mod.slug)}/index.html`;
  currentMod.textContent = mod.name;
  gameFrame.src = url;
  openGame.href = url;
  playerPanel.hidden = false;
  playerPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

async function loadMods() {
  statusText.textContent = 'Scanning mods…';
  try {
    const response = await fetch('/api/mods', { cache: 'no-store' });
    if (!response.ok) throw new Error('Unable to scan mods');
    const mods = await response.json();
    statusText.textContent = `${mods.length} mod${mods.length === 1 ? '' : 's'} ready`;
    if (!mods.length) {
      showEmpty('No browser builds found. Add an extracted mod containing <code>index.html</code> under <code>mods/&lt;mod-name&gt;/</code>, then click Refresh.');
      return;
    }
    list.innerHTML = '';
    for (const mod of mods) {
      const card = document.createElement('article');
      card.className = 'mod-card';
      card.innerHTML = `<div><strong>${mod.name}</strong><small>${mod.slug}/index.html</small></div>`;
      const button = document.createElement('button');
      button.className = 'button';
      button.type = 'button';
      button.textContent = 'Play';
      button.addEventListener('click', () => playMod(mod));
      card.append(button);
      list.append(card);
    }
  } catch (error) {
    statusText.textContent = 'Server error';
    showEmpty('The launcher could not reach the local server. Check that <code>./start.sh</code> is running on port 8080.');
  }
}

document.querySelector('#refresh').addEventListener('click', loadMods);
loadMods();
