document.addEventListener('DOMContentLoaded', () => {
    const priceFilterForm = document.querySelector('.price-filter-form');
    if (priceFilterForm) {
        priceFilterForm.addEventListener('submit', (e) => {
            const priceMin = document.getElementById('price_min').value;
            const priceMax = document.getElementById('price_max').value;
            if (priceMin && priceMax && Number(priceMin) > Number(priceMax)) {
                e.preventDefault();
                alert('Мінімальна ціна не може бути більшою за максимальну!');
            }
            if (priceMin && Number(priceMin) < 0 || priceMax && Number(priceMax) < 0) {
                e.preventDefault();
                alert('Ціни не можуть бути від’ємними!');
            }
        });
    }
});