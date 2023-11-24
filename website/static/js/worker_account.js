var items = [];
var total_price = 0;

// Функция для добавления товара в корзину
function addToCart(name, price) {
  flag = true;
  for (var i = 0; i < items.length; i++) {
    if (items[i][0] == name) {
      flag = false;
    }
  }

  if (flag) {
    // Добавление товара в массив items корзины
    items.push([name, price, 1]);

    // Обновление общей стоимости
    total_price += price;
  }
}

function toggleCartPopup() {
  const cartPopup = document.getElementById("cart-popup");
  cartPopup.style.display =
    cartPopup.style.display === "none" || cartPopup.style.display === ""
      ? "block"
      : "none";

  // Получение ссылки на элемент, в который вы хотите вывести массив
  var outputElement = document.getElementById("cart-info");

  // Создание HTML-разметки на основе массива
  var htmlContent = "<table>";

  for (var i = 0; i < items.length; i++) {
    var item = items[i][0] + " " + items[i][1];
    htmlContent +=
      "<tr>" + "<td>" + items[i][0] + "</td>" + "<td>" + items[i][1] + "</td>";
    htmlContent +=
      "<td>" +
      "<input type='text' value='" +
      items[i][2] +
      "' min='1' max='100'><button id='plusButton' onclick='plusButton(" +
      i +
      ")'>+</button><button id='minusButton' onclick='minusButton(" +
      i +
      ")'>-</button>";
    htmlContent +=
      "<td>" +
      "<button onclick='deleteItem(" +
      i +
      ")'>Удалить</button>" +
      "</td>" +
      "</tr>";
  }

  htmlContent += "</table>";

  // Вставка HTML-разметки в элемент
  outputElement.innerHTML = htmlContent;
}

function clearCartPopup() {
  items = [];
  const cartPopup = document.getElementById("cart-popup");
  cartPopup.style.display =
    cartPopup.style.display === "none" || cartPopup.style.display === ""
      ? "block"
      : "none";
}

function deleteItem(item_id) {
  items.splice(item_id, 1);
  toggleCartPopup();
  toggleCartPopup();
}

function plusButton(item_id) {
  items[item_id][2] += 1;
  toggleCartPopup();
  toggleCartPopup();
  console.log(items);
}

function minusButton(item_id) {
  items[item_id][2] -= 1;
  toggleCartPopup();
  toggleCartPopup();
  console.log(items);
}
