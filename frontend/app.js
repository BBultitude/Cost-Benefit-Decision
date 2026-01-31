const API_BASE = '/api';

async function fetchItems() {
  const res = await fetch(`${API_BASE}/items`);
  if (!res.ok) {
    console.error('Failed to fetch items');
    return [];
  }
  return await res.json();
}

async function addItem(payload) {
  const res = await fetch(`${API_BASE}/items`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error('Failed to add item');
  }
  return await res.json();
}

async function deleteItem(id) {
  const res = await fetch(`${API_BASE}/items/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) {
    throw new Error('Failed to delete item');
  }
}

function renderItems(items) {
  const tbody = document.getElementById('items-body');
  tbody.innerHTML = '';
  for (const item of items) {
    const tr = document.createElement('tr');

    const cells = [
      item.description,
      `$${item.cost}`,
      item.severity,
      item.frequency,
      item.benefit_score,
      item.cost_score,
      item.net_score,
    ];

    for (const value of cells) {
      const td = document.createElement('td');
      td.textContent = value;
      tr.appendChild(td);
    }

    const actionTd = document.createElement('td');
    const btn = document.createElement('button');
    btn.textContent = 'Done';
    btn.className = 'action-btn';
    btn.addEventListener('click', async () => {
      try {
        await deleteItem(item.id);
        loadAndRender();
      } catch (e) {
        console.error(e);
      }
    });
    actionTd.appendChild(btn);
    tr.appendChild(actionTd);

    tbody.appendChild(tr);
  }
}

async function loadAndRender() {
  const items = await fetchItems();
  renderItems(items);
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('item-form');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const description = document.getElementById('description').value.trim();
    const cost = parseFloat(document.getElementById('cost').value);
    const severity = parseInt(document.getElementById('severity').value, 10);
    const frequency = parseInt(document.getElementById('frequency').value, 10);

    if (!description || isNaN(cost) || isNaN(severity) || isNaN(frequency)) {
      return;
    }

    try {
      await addItem({ description, cost, severity, frequency });
      form.reset();
      loadAndRender();
    } catch (e) {
      console.error(e);
    }
  });

  loadAndRender();

  const helpToggle = document.getElementById('help-toggle');
  const helpPanel = document.getElementById('help-panel');
  const helpClose = document.getElementById('help-close');

  if (helpToggle && helpPanel && helpClose) {
    helpToggle.addEventListener('click', () => {
      helpPanel.style.display = 'flex';
    });

    helpClose.addEventListener('click', () => {
      helpPanel.style.display = 'none';
    });

    helpPanel.addEventListener('click', (e) => {
      if (e.target === helpPanel) {
        helpPanel.style.display = 'none';
      }
    });
  }


});
