/**
 * Интерактивная 2D-схема автомобиля.
 * Подсветка зон и клики для загрузки компонентов.
 */
document.addEventListener('DOMContentLoaded', function() {
    const svg = document.getElementById('car-svg');
    if (!svg) return;

    const zones = svg.querySelectorAll('.car-zone');
    const hitboxes = svg.querySelectorAll('.connection-hitbox');
    const visualLines = svg.querySelectorAll('.connection-line');
    const popup = document.getElementById('component-popup');
    const popupTitle = document.getElementById('popup-title');
    const popupList = document.getElementById('popup-list');
    const vehicleId = svg.dataset.vehicleId;

    // Подсветка связей при наведении на компонент
    zones.forEach(zone => {
        const componentType = zone.dataset.component;
        const partId = zone.dataset.partId;

        zone.addEventListener('mouseenter', () => {
            if (partId) {
                hitboxes.forEach(hb => {
                    if (hb.dataset.from === partId || hb.dataset.to === partId) {
                        // Подсветить соответствующую видимую линию
                        const visLine = hb.nextElementSibling;
                        if (visLine) visLine.classList.add('highlight');
                    }
                });
            }
            zone.style.cursor = 'pointer';
        });

        zone.addEventListener('mouseleave', () => {
            visualLines.forEach(line => line.classList.remove('highlight'));
        });

        zone.addEventListener('click', (e) => {
            e.stopPropagation();
            window.location.href = `/builder/select-component/${componentType}`;
        });
    });

    // Клик по связи
    hitboxes.forEach(hb => {
        hb.addEventListener('click', (e) => {
            e.stopPropagation();
            const label = hb.dataset.label || 'Связь';
            const type = hb.dataset.type || '';
            const from = hb.dataset.from || '';
            const to = hb.dataset.to || '';
            showConnectionPopup(label, type, from, to);
        });
    });

    function showConnectionPopup(label, type, from, to) {
        if (!popup || !popupTitle || !popupList) return;
        popupTitle.textContent = `🔗 ${label}`;
        popupList.innerHTML = `
            <li class="list-group-item bg-transparent text-light">
                <strong>Тип:</strong> ${type}
            </li>
            <li class="list-group-item bg-transparent text-light">
                <strong>Соединяет:</strong> ${from} → ${to}
            </li>
            <li class="list-group-item bg-transparent text-light">
                <small class="text-muted">Клик по компонентам на схеме открывает выбор деталей.</small>
            </li>
        `;
        popup.style.display = 'block';
    }

    // ... остальные функции showPopup, getComponentLabel — без изменений

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