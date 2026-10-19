> **ЧЕРНОВИК.** Стартовое предложение, не утверждено. Дорабатывается в сессии «Контент».

# Учебная БД «магазин»

Единая база для всех задач по SQL, Django ORM и SQLAlchemy. Задачи используют только эти таблицы и поля.
Если для задачи не хватает поля, сначала меняем схему здесь, а уже потом пишем задачу.

```
users        id PK, email UNIQUE, name, city NULL, is_active bool, created_at
categories   id PK, name, parent_id NULL → categories.id      -- дерево категорий
products     id PK, category_id → categories.id, name, price numeric(10,2), stock int, created_at
orders       id PK, user_id → users.id, status ('new'|'paid'|'shipped'|'cancelled'), created_at
order_items  id PK, order_id → orders.id, product_id → products.id, quantity int, price numeric(10,2)
             -- price = цена на момент покупки, может отличаться от products.price
reviews      id PK, user_id → users.id, product_id → products.id, rating 1..5, text NULL, created_at
             -- UNIQUE (user_id, product_id)
```

**Связи:**
- users 1—N orders, users 1—N reviews;
- orders 1—N order_items N—1 products, то есть orders M—N products через order_items;
- categories 1—N products;
- categories 1—N categories (самосвязь).

**В данные специально заложены:**
- пользователи без заказов;
- товары без отзывов;
- категории без товаров;
- NULL в `city`, `text` и `parent_id`;
- отменённые заказы;
- одинаковые цены (для RANK и DENSE_RANK);
- заказы на границах месяцев (для работы с датами).

Объём: 10–15 пользователей, 6–8 категорий в 2–3 уровнях, 20–25 товаров, 30–40 заказов.
Данных столько, чтобы результат любого запроса помещался на экран.
