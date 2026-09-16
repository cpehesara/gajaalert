const zone = document.querySelector('#zone');
const refresh = document.querySelector('#refresh');
const factors = document.querySelector('#factors');

async function assess() {
  document.querySelector('#status').textContent = 'Loading';
  const response = await fetch(`http://127.0.0.1:5000/api/fuzzy-risk`, {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({zone_id: zone.value})
  });
  const result = await response.json();
  document.querySelector('#level').textContent = result.risk_level;
  document.querySelector('#score').textContent = result.risk_score;
  document.querySelector('#status').textContent = 'Updated';
  factors.replaceChildren(...result.contributing_factors.map(factor => { const item = document.createElement('li'); item.textContent = factor; return item; }));
}
refresh.addEventListener('click', assess);