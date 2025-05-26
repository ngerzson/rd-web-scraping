const rows = document.querySelectorAll('#value .chartlist li'); 
const data = [];

rows.forEach(row => {
  const name = row.querySelector('.prdname')?.textContent.trim() || '-';
  const price = row.querySelector('.price-neww')?.textContent.trim() || '-';
  const score = row.querySelector('.count')?.textContent.trim() || '-';

  data.push({ name, price, score });
});

console.log(JSON.stringify(data, null, 2));