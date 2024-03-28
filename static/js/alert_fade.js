document.addEventListener("DOMContentLoaded", function () {
    var alertElements = document.querySelectorAll('.alert');

    alertElements.forEach(function (alert) {
        setTimeout(function () {
            alert.classList.add('fade-out');
            setTimeout(function () {
                alert.style.display = 'none';
            }, 1000);
        }, 2000);
    });
});