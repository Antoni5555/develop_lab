-- Учебная БД «магазин» (PostgreSQL 16). Описание — docs/shop-schema.md.
-- Порядок создания учитывает внешние ключи.

CREATE TABLE users (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email       text        NOT NULL UNIQUE,
    name        text        NOT NULL,
    city        text,                                   -- NULL: город не указан
    is_active   boolean     NOT NULL DEFAULT true,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE profiles (                                 -- 1:1 с users
    user_id     integer PRIMARY KEY REFERENCES users (id) ON DELETE CASCADE,
    phone       text UNIQUE,
    birth_date  date
);

CREATE TABLE categories (                               -- дерево: самосвязь
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        text    NOT NULL,
    parent_id   integer REFERENCES categories (id) ON DELETE RESTRICT
);

CREATE TABLE products (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_id integer       NOT NULL REFERENCES categories (id) ON DELETE RESTRICT,
    name        text          NOT NULL,
    price       numeric(10,2) NOT NULL CHECK (price >= 0),
    stock       integer       NOT NULL DEFAULT 0 CHECK (stock >= 0),
    attributes  jsonb         NOT NULL DEFAULT '{}',    -- {"color": "black", "size": "M"}
    created_at  timestamptz   NOT NULL DEFAULT now()
);

CREATE TABLE tags (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        text NOT NULL UNIQUE
);

CREATE TABLE product_tags (                             -- простое N:M без доп. полей
    product_id  integer NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    tag_id      integer NOT NULL REFERENCES tags (id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, tag_id)
);

CREATE TABLE promo_codes (
    id               integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code             text    NOT NULL UNIQUE,
    discount_percent integer NOT NULL CHECK (discount_percent BETWEEN 1 AND 90),
    valid_until      date    NOT NULL,
    is_active        boolean NOT NULL DEFAULT true
);

CREATE TABLE orders (
    id            integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id       integer     NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
    promo_code_id integer     REFERENCES promo_codes (id) ON DELETE SET NULL,
    status        text        NOT NULL DEFAULT 'new'
                  CHECK (status IN ('new', 'paid', 'shipped', 'cancelled')),
    created_at    timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_items (                              -- N:M orders ↔ products с доп. полями
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    order_id    integer       NOT NULL REFERENCES orders (id) ON DELETE CASCADE,
    product_id  integer       NOT NULL REFERENCES products (id) ON DELETE RESTRICT,
    quantity    integer       NOT NULL CHECK (quantity > 0),
    price       numeric(10,2) NOT NULL CHECK (price >= 0),  -- цена на момент покупки
    UNIQUE (order_id, product_id)
);

CREATE TABLE reviews (
    id          integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    user_id     integer     NOT NULL REFERENCES users (id) ON DELETE CASCADE,
    product_id  integer     NOT NULL REFERENCES products (id) ON DELETE CASCADE,
    rating      smallint    NOT NULL CHECK (rating BETWEEN 1 AND 5),
    text        text,                                   -- NULL: оценка без текста
    created_at  timestamptz NOT NULL DEFAULT now(),
    UNIQUE (user_id, product_id)
);
