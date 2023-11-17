$(document).ready(function () {
  var panelOne = $('.form').height(),
    panelTwo = $('.form-panel.two')[0].scrollHeight;

  // Используйте делегирование событий для обработки динамически создаваемых элементов
  $(document).on('click', '.form-panel.two:not(.active)', function (e) {
    e.preventDefault();

    $('.form-toggle').addClass('visible');
    $('.form-panel.one').addClass('hidden');
    $('.form-panel.two').addClass('active');
    $('.form').animate({
      'height': panelTwo
    }, 200);
  });

  $(document).on('click', '.form-toggle', function (e) {
    e.preventDefault();

    $(this).removeClass('visible');
    $('.form-panel.one').removeClass('hidden');
    $('.form-panel.two').removeClass('active');
    $('.form').animate({
      'height': panelOne
    }, 200);
  });
});