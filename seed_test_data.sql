-- Скрипт для заполнения базы тестовыми данными
--Пользователи login:password - admin@example.com:1234567q, user@example.com:1234567q

-- Очистка существующих тестовых данных
DELETE FROM posts WHERE slug IN (
    'introduction-to-python',
    'modern-web-design',
    'seo-basics',
    'databases-for-developers',
    'social-media-marketing'
);

DELETE FROM categories WHERE slug IN ('programming', 'design', 'marketing');
DELETE FROM user_roles WHERE user_id IN (SELECT id FROM users WHERE email IN ('admin@example.com', 'user@example.com'));
DELETE FROM users WHERE email IN ('admin@example.com', 'user@example.com');

-- Добавление тестовых пользователей
INSERT INTO users (email, password_hash, first_name, last_name, is_verified, created_at, is_active)
VALUES
('admin@example.com', '$2b$12$4zSnC2pbZuF6meqrJx9yZ.pNsZG94TrvXjVcOODv2ZI/0x6xDn5yS', 'Admin', 'User', true, NOW(), true),
('user@example.com', '$2b$12$4zSnC2pbZuF6meqrJx9yZ.pNsZG94TrvXjVcOODv2ZI/0x6xDn5yS', 'Regular', 'User', true, NOW(), true);

-- Назначение ролей пользователям
INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r WHERE u.email = 'admin@example.com' AND r.name = 'admin';

INSERT INTO user_roles (user_id, role_id)
SELECT u.id, r.id FROM users u, roles r WHERE u.email = 'user@example.com' AND r.name = 'user';

-- Добавление категорий
INSERT INTO categories (name, slug, description, created_at, is_active)
VALUES
('Программирование', 'programming', 'Статьи о программировании и разработке ПО', NOW(), true),
('Дизайн', 'design', 'Статьи о дизайне и UX/UI', NOW(), true),
('Маркетинг', 'marketing', 'Статьи о маркетинге и продвижении', NOW(), true);

-- Добавление постов
INSERT INTO posts (title, slug, excerpt, content, is_published, category_id, author_id, created_at, is_active)
VALUES
('Введение в Python', 'introduction-to-python', 'Основы программирования на Python для начинающих', 'Python - это мощный и простой в изучении язык программирования.', true, (SELECT id FROM categories WHERE slug = 'programming'), (SELECT id FROM users WHERE email = 'admin@example.com'), NOW(), true),
('Современный веб-дизайн', 'modern-web-design', 'Тренды и принципы современного веб-дизайна', 'Веб-дизайн постоянно развивается.', true, (SELECT id FROM categories WHERE slug = 'design'), (SELECT id FROM users WHERE email = 'admin@example.com'), NOW() - INTERVAL '1 day', true),
('Основы SEO', 'seo-basics', 'Поисковая оптимизация для начинающих', 'SEO - это комплекс мер по оптимизации сайта.', true, (SELECT id FROM categories WHERE slug = 'marketing'), (SELECT id FROM users WHERE email = 'user@example.com'), NOW() - INTERVAL '2 days', true),
('Базы данных для разработчиков', 'databases-for-developers', 'Обзор современных систем управления базами данных', 'В этой статье рассмотрим различные типы баз данных.', false, (SELECT id FROM categories WHERE slug = 'programming'), (SELECT id FROM users WHERE email = 'user@example.com'), NOW() - INTERVAL '3 days', true),
('Социальные медиа маркетинг', 'social-media-marketing', 'Как эффективно использовать социальные сети для продвижения', 'Социальные медиа предоставляют уникальные возможности.', true, (SELECT id FROM categories WHERE slug = 'marketing'), (SELECT id FROM users WHERE email = 'admin@example.com'), NOW() - INTERVAL '4 days', true);