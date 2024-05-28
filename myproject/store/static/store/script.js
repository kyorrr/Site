document.addEventListener("DOMContentLoaded", function() {
    // Обработка корзины
    const cartLink = document.getElementById("cart-link");
    const cartDropdown = document.getElementById("cart-dropdown");
    const loadingScreen = document.getElementById("loading-screen");
    const customAlert = document.getElementById("custom-alert");
    const buyButton = document.getElementById("buy-button");

    function showLoadingScreen() {
        loadingScreen.classList.add('active');
    }

    function hideLoadingScreen() {
        setTimeout(() => {
            loadingScreen.classList.remove('active');
        }, 2000); // Задержка 2 секунды
    }

    function showCustomAlert(message) {
        customAlert.querySelector('p').textContent = message;
        customAlert.classList.remove('hide');
        customAlert.classList.add('show');
        setTimeout(() => {
            customAlert.classList.remove('show');
            customAlert.classList.add('hide');
        }, 3000); // Показать на 3 секунды
    }

    if (cartLink && cartDropdown) {
        cartLink.addEventListener("click", function(event) {
            event.preventDefault();
            cartDropdown.classList.toggle("show");
            fetchCart();
        });

        window.addEventListener("click", function(event) {
            if (!event.target.matches('#cart-link') && !cartDropdown.contains(event.target)) {
                if (cartDropdown.classList.contains('show')) {
                    cartDropdown.classList.remove('show');
                }
            }
        });
    }

    const buyButtons = document.querySelectorAll(".buy-button");

    buyButtons.forEach(button => {
        button.addEventListener("click", function() {
            if (!document.body.classList.contains('authenticated')) {
                showCustomAlert('Пожалуйста, войдите или зарегистрируйтесь, чтобы добавлять товары в корзину.');
                return;
            }

            const productId = this.closest(".product").dataset.productId;
            fetch(`/add_to_cart/${productId}/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showCustomAlert("Товар добавлен в корзину");
                    fetchCart();
                } else {
                    showCustomAlert("Ошибка при добавлении товара в корзину");
                }
            });
        });
    });

    function fetchCart() {
        fetch(`/get_cart/`)
            .then(response => response.json())
            .then(data => {
                const cartItemsContainer = document.getElementById("cart-items");
                const cartTotalPriceContainer = document.getElementById("cart-total-price");
                cartItemsContainer.innerHTML = "";
                if (data.items.length > 0) {
                    data.items.forEach(item => {
                        cartItemsContainer.innerHTML += `
                            <div class="cart-item">
                                <img src="${item.image_url}" alt="${item.name}">
                                <div class="details">
                                    <p class="product-name">${item.name}</p>
                                    <input type="number" class="quantity-input" value="${item.quantity}" min="1" max="${item.stock}" data-item-id="${item.id}">
                                    <p>${item.price} руб.</p>
                                    <button class="remove-item" data-item-id="${item.id}">×</button> <!-- Кнопка удаления -->
                                </div>
                            </div>
                        `;
                    });
                    cartTotalPriceContainer.innerHTML = `Общая стоимость: ${data.total_price} руб.`;
                    document.getElementById("buy-button").style.display = "block";
                } else {
                    cartItemsContainer.innerHTML = "<p>Здесь будут отображаться товары, которые вы добавили в корзину.</p>";
                    cartTotalPriceContainer.innerHTML = "";
                    document.getElementById("buy-button").style.display = "none";
                }

                // Обработчик изменения количества товаров
                const quantityInputs = document.querySelectorAll(".quantity-input");
                quantityInputs.forEach(input => {
                    input.addEventListener("change", function() {
                        updateCartItem(this.dataset.itemId, this.value);
                    });
                });

                // Обработчик удаления товаров
                const removeButtons = document.querySelectorAll(".remove-item");
                removeButtons.forEach(button => {
                    button.addEventListener("click", function() {
                        removeCartItem(this.dataset.itemId);
                    });
                });
            });
    }

    function updateCartItem(itemId, quantity) {
        fetch(`/update_cart_item/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ quantity })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fetchCart(); // Обновляем корзину после изменения количества
            } else {
                showCustomAlert("Ошибка при обновлении количества товара в корзине");
            }
        });
    }

    function removeCartItem(itemId) {
        fetch(`/remove_cart_item/${itemId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                fetchCart(); // Обновляем корзину после удаления товара
            } else {
                showCustomAlert("Ошибка при удалении товара из корзины");
            }
        });
    }

    if (buyButton) {
        buyButton.addEventListener("click", function() {
            fetch(`/purchase/`, {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCookie("csrftoken"),
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    fetchCart();
                    showCustomAlert("Покупка успешно завершена");
                } else {
                    showCustomAlert(data.message || "Ошибка при покупке");
                }
            });
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Обработка для якорных ссылок
    const headerHeight = document.querySelector("header").offsetHeight;
    const links = document.querySelectorAll("nav a, .back-link, .form-container a, .logout-link");

    links.forEach(link => {
        link.addEventListener("click", function(event) {
            if (this.hash !== "") {
                event.preventDefault();
                const hash = this.hash;
                const targetElement = document.querySelector(hash);

                const elementPosition = targetElement.getBoundingClientRect().top + window.pageYOffset;
                const offsetPosition = elementPosition - headerHeight;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
            } else if (!this.href.includes('#') && !this.href.includes('cart')) {
                event.preventDefault();
                showLoadingScreen();
                const targetUrl = this.href;

                setTimeout(() => {
                    window.location.href = targetUrl;
                }, 500); // Задержка перед переходом на новую страницу 0.5 секунды
            }
        });
    });

    // Скрытие экрана загрузки после загрузки страницы
    window.addEventListener("load", hideLoadingScreen);
});
