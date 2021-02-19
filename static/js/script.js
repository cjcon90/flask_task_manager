$(document).ready(function () {
    $('.sidenav').sidenav({
        edge: 'right'
    });
});

$(document).ready(function () {
    $('.collapsible').collapsible();
});

$(document).ready(function () {
    $('.tooltipped').tooltip();
});

$(document).ready(function () {
    $('.datepicker').datepicker({
        format: "dd mmmm, yyyy",
        yearRange: 3,
        showClearBtn: true,
        i18n: {
            done: 'Select'
        }
    });
});