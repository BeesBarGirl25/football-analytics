$(document).ready(function() {
    $('.searchable-dropdown').select2();

    $('.tab-btn').on('click', function () {
        $('.tab-btn').removeClass('active');
        $(this).addClass('active');

        const target = $(this).data('tab');
        $('.analysis-content').addClass('hidden');
        $('#' + target).removeClass('hidden');
    });
});