// Плавная анимация при загрузке (пример)
document.addEventListener('DOMContentLoaded', () => {
    console.log('AUTOMATCH frontend ready');
    // Здесь позже будут обработчики конструктора и интерактивных элементов
});
// Сохранение позиции прокрутки для списков
(function() {
    // Сохраняем текущую позицию перед уходом со страницы
    window.addEventListener('beforeunload', function() {
        var key = 'scrollPos_' + window.location.pathname;
        sessionStorage.setItem(key, window.scrollY);
    });

    // Восстанавливаем позицию при загрузке страницы
    window.addEventListener('load', function() {
        var key = 'scrollPos_' + window.location.pathname;
        var saved = sessionStorage.getItem(key);
        if (saved !== null && !isNaN(saved)) {
            window.scrollTo(0, parseInt(saved, 10));
        }
        // Удаляем сохранённую позицию, чтобы при следующем обновлении (не возврате) она не применялась снова?
        // Мы оставляем её, чтобы при возврате по кнопке "Назад" восстановилась. 
        // Если нужно, чтобы при обычном обновлении сбрасывалась к началу, можно удалить после восстановления, 
        // но тогда возврат назад не сработает. Оставляем.
    });
})();