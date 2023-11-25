var items = [];
var total_price = 0;

// Функция для добавления товара в корзину
function addToCart(name, price, b64, structure) {
  price = parseInt(price);
  flag = true;
  for (var i = 0; i < items.length; i++) {
    if (items[i][0] == name) {
      flag = false;
    }
  }

  if (flag) {
    // Добавление товара в массив items корзины
    items.push([name, parseInt(price), 1, b64, structure]);

    // Обновление общей стоимости
    total_price += price;
  }
}

function toggleCartPopup() {
  const cartPopup = document.getElementsByClassName("cart-popup")[0];
  cartPopup.style.display = 'block';

  document.getElementsByClassName('mute')[0].style.display = 'block';

  var htmlCode = '<button class="close_btn" onclick="closeCartPopup()"><img src="../static/images/remove.png"></button>' +
                '<div class="cart-header">' +
                  '<h3>Корзина</h3>' +
                  '<button class="clear_btn" onclick="clearCartPopup()"><img src="../static/images/clear_cart_icon.png"></button>' +
                '</div>';

  for (var i = 0; i < items.length; i++) {
    var item = items[i];

    htmlCode += '<div class="cart-info">' +
                  '<div class="image-box">' +
                    '<img src="data:image/jpeg;base64,' + item[3] + '" style="height: 120px;"/>' +
                  '</div>' +
                  '<div class="about">' +
                    '<h1 class="title">' + item[0] + '</h1>' +
                    '<h3 class="subtitle">' + item[4] + ' каллорий</h3>' +
                  '</div>' +
                  '<div class="counter">' +
                    '<div class="btn" onclick="minusButton(' + i + ')">-</div>' +
                    '<div class="count">' + item[2] + '</div>' +
                    '<div class="btn plus" onclick="plusButton(' + i + ')">+</div>' +
                  '</div>' + 
                  '<div class="prices">' +
                    '<div class="amount">' + item[1] * item[2] + '₽</div>' +
                    '<div class="remove"><u><button onclick="deleteItem(' + i + ')"><img src="../static/images/delete_icon_red.png"></button></u></div>' +
                  '</div>' +
                '</div>';
  }

  htmlCode += '<hr>' +
              '<div class="checkout">' +
                '<div class="total">' +
                  '<div>' +
                    '<div class="with_delivery">' +
                      '<h5>С доставкой:</h5>' +
                      '<label class="switch">' +
                        '<input id="is_delivery" class="is_delivery" type="checkbox">' +
                        '<span class="slider round"></span>' +
                      '</label>' +
                    '</div>' +
                    '<input id="officeFloor" type="text" placeholder="Этаж">' +
                    '<input id="officeNumber" type="text" placeholder="Офис">' +
                    '<input id="placeNumber" type="text" placeholder="Место">' +
                    '<div class="subtotal">Стоимость: ' + total_price + '₽</div>' +
                    '<div class="items"></div>' +
                  '</div>' + 
                  '<div class="total-amount"></div>' +
                '</div>' +
                '<button class="button" onclick="makeOrder()">Заказать</button>' +
              '</div>';
  
  cartPopup.innerHTML = htmlCode;
}

function clearCartPopup() {
  items = [];
  total_price = 0;
  toggleCartPopup();
}

function deleteItem(item_id) {
  item = items[item_id];
  total_price -= item[1] * item[2]
  items.splice(item_id, 1);
  toggleCartPopup();
  toggleCartPopup();
}

function plusButton(item_id) {
  items[item_id][2] += 1;
  total_price += items[item_id][1];
  toggleCartPopup();
  toggleCartPopup();
}

function minusButton(item_id) {
  if (items[item_id][2] > 1) {
    items[item_id][2] -= 1;
    total_price -= items[item_id][1];
    toggleCartPopup();
    toggleCartPopup();
  }
}

function closeCartPopup() {
  const cartPopup = document.getElementsByClassName("cart-popup")[0];
  cartPopup.style.display = 'none';
  document.getElementsByClassName('mute')[0].style.display = 'none';
}

function makeOrder() {
  var is_delivery = document.getElementById('is_delivery').checked;
  var officeFloor = document.getElementById('officeFloor').value;
  var officeNumber = document.getElementById('officeNumber').value;
  var placeNumber = document.getElementById('placeNumber').value;

  if (is_delivery) {
    var orderData = {is_delivery: is_delivery, address: {officeFloor: officeFloor, officeNumber: officeNumber, placeNumber: placeNumber}, dishes: []}
  }
  else {
    var orderData = {is_delivery: is_delivery, address: {officeFloor: null, officeNumber: null, placeNumber: null}, dishes: []}
  }

  for (var i = 0; i < items.length; i++) {
    var item = items[i];
    orderData["dishes"].push({title: item[0], quantity: item[2], price: item[1]})
  }

  // Отправляем AJAX-запрос на сервер Flask
  fetch('/make_order', {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
      },
      body: JSON.stringify(orderData),
  })
      .then(response => response.json())
      .then(data => {
          console.log('Ответ от сервера:', data);
          // Обработка ответа от сервера, если необходимо
      })
      .catch(error => {
          console.error('Ошибка при отправке запроса:', error);
      });
  clearCartPopup();
}

document.addEventListener('DOMContentLoaded', function() {
  var checkbox = document.getElementsByClassName('is_delivery')[0];

  checkbox.addEventListener('change', function(checkbox) {

    if (checkbox.checked) {
      console.log('Checkbox выбран');
    } else {
      console.log('Checkbox не выбран');
    }
  });
});
