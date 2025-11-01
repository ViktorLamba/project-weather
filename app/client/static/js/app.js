// frontend/static/js/app.js
function searchWeather() {
    const cityInput = document.getElementById('city-input');
    const city = cityInput.value.trim();
    
    if (!city) {
        alert('Пожалуйста, введите название города');
        return;
    }
    
    const weatherResult = document.getElementById('weather-result');
    weatherResult.innerHTML = `
        <div class="loading">Загрузка данных для ${city}...</div>
    `;
    
    setTimeout(() => {
        weatherResult.innerHTML = `
            <div class="weather-card">
                <h2>🌤️ Погода в ${city}</h2>
                <p>🌡️ Температура: +20°C</p>
                <p>💨 Ветер: 5 м/с</p>
                <p>☀️ Ясно</p>
            </div>
        `;
    }, 1000);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    console.log('Weather App frontend loaded');
});