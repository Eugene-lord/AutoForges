/**
 * Интерактивная 2D-схема автомобиля.
 * Подсветка зон и клики для загрузки компонентов.
 */
document.addEventListener('DOMContentLoaded', function() {
    const svg = document.getElementById('car-svg');
    if (!svg) return;

    const zones = svg.querySelectorAll('.car-zone');
    const popup = document.getElementById('component-popup');
    const popupTitle = document.getElementById('popup-title');
    const popupList = document.getElementById('popup-list');
    const vehicleId = svg.dataset.vehicleId;

    zones.forEach(zone => {
        const componentType = zone.dataset.component;

        // Подсветка при наведении
        zone.addEventListener('mouseenter', () => {
            zone.style.fill = 'rgba(255, 107, 107, 0.5)';
            zone.style.stroke = '#ff6b6b';
            zone.style.cursor = 'pointer';
        });
        zone.addEventListener('mouseleave', () => {
            zone.style.fill = 'rgba(255,255,255,0)';
            zone.style.stroke = 'rgba(255,255,255,0.2)';
        });

        // Клик
        zone.addEventListener('click', async (e) => {
            e.stopPropagation();
            if (!vehicleId) return;

            try {
                const response = await fetch(`/builder/api/components/${vehicleId}/${componentType}`);
                const data = await response.json();
                showPopup(componentType, data.components);
            } catch (err) {
                console.error('Ошибка загрузки компонентов:', err);
            }
        });
    });

    function showPopup(type, components) {
        if (!popup || !popupTitle || !popupList) return;
        popupTitle.textContent = getComponentLabel(type);
        popupList.innerHTML = '';
        if (components.length === 0) {
            popupList.innerHTML = '<li class="list-group-item bg-transparent text-light">Нет данных</li>';
        } else {
            components.forEach(comp => {
                const li = document.createElement('li');
                li.className = 'list-group-item bg-transparent text-light';
                li.innerHTML = `
                    <strong>${comp.name}</strong>
                    <span class="badge ms-2 ${comp.status === 'compatible' ? 'bg-success' : comp.status === 'warning' ? 'bg-warning text-dark' : 'bg-danger'}">
                        ${comp.status === 'compatible' ? '✅' : comp.status === 'warning' ? '⚠️' : '❌'}
                    </span>
                    <br><small>${comp.description || ''}</small>
                    <br><span class="text-info">Стоимость: $${comp.estimated_cost || 0}</span> | Сложность: ${comp.difficulty || 0}/10
                `;
                li.addEventListener('click', () => {
                    window.location.href = `/builder/select-component/${type}`;
                });
                li.style.cursor = 'pointer';
                popupList.appendChild(li);
            });
        }
        popup.style.display = 'block';
    }

    function getComponentLabel(type) {
        const labels = {
            'engine': 'Двигатель',
            'transmission': 'КПП',
            'differential': 'Редуктор',
            'suspension': 'Подвеска',
            'brakes': 'Тормоза',
            'cooling': 'Охлаждение',
            'electronics': 'Электроника',
            'ecu': 'ЭБУ',
            'turbo': 'Турбина',
            'intercooler': 'Интеркулер',
            'exhaust': 'Выхлоп',
            'electric_motor': 'Электромотор',
            'battery': 'Батарея',
            'inverter': 'Инвертор'
        };
        return labels[type] || type;
    }

    // Закрытие попапа при клике вне
    document.addEventListener('click', (e) => {
        if (popup && !popup.contains(e.target) && !e.target.classList.contains('car-zone')) {
            popup.style.display = 'none';
        }
    });
});