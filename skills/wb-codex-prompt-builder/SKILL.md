---
name: wb-codex-prompt-builder
description: Use this skill when creating ultra-detailed prompts for Codex to edit jewelry product images, including strict requirements, protected zones, local edit logic, visual acceptance tests, and iterative correction loops.
---

# WB Codex Prompt Builder

## Purpose

This skill creates strict, copy-paste-ready prompts for Codex when editing marketplace jewelry images.

The prompt must:
- be actionable;
- be strict;
- prevent unnecessary regeneration;
- protect good areas;
- include acceptance criteria;
- include autotests;
- include iteration logic;
- be concise enough for repeated use.

---

## Prompt style

Use Russian by default unless user requests otherwise.

Tone:
- formal;
- strict;
- engineering-like;
- no vague beauty language without criteria;
- no unnecessary explanations.

The output should be copy-paste-ready.

---

## Mandatory prompt sections

Every generated Codex prompt should include:

1. Role
2. Goal
3. Source materials
4. What to preserve
5. What to change
6. What is forbidden
7. Local edit strategy
8. Visual style
9. Technical requirements
10. Autotests
11. Iteration loop
12. Final report format
13. Acceptance criteria

---

## Standard prompt template

Use this structure:

```text
ЗАДАЧА ДЛЯ CODEX

Роль:
Ты работаешь как image-editing агент для маркетплейс-фото украшений Wildberries.

Цель:
[описать цель: улучшить CTR / показать браслет / снизить отвлечение лицом / сохранить предмет]

Исходники:
- Используй приложенное изображение как главный источник формы товара.
- Не выдумывай новые элементы.
- Если есть референсы конкурентов, используй только стиль подачи, но не меняй сам товар.

Что обязательно сохранить:
1. [элемент 1]
2. [элемент 2]
3. [элемент 3]

Что нужно изменить:
1. [правка 1]
2. [правка 2]

Что запрещено:
1. Полная перегенерация без необходимости.
2. Изменение формы украшения.
3. Замена товара на похожий.
4. Добавление лишних предметов.
5. Ухудшение уже удачных зон.
6. Изменение удачных колье/серег/браслета, если они не входят в задачу правки.

Стратегия редактирования:
- Сначала зафиксируй protected zones.
- Затем внеси только локальные изменения.
- После каждой правки проверь, что защищенные зоны не изменились.
- Если проблема не решена, делай следующий цикл.
- Максимум циклов: 5.

Визуальный стиль:
- Премиальный editorial.
- Темный/нейтральный фон.
- Спокойный тон кожи.
- Украшение должно быть главным объектом.
- Лицо не должно отвлекать.
- Фото должно работать в мобильной выдаче WB.

Автотесты после каждой итерации:
1. Сохранена форма товара.
2. Сохранено количество предметов.
3. Колье не изменено.
4. Серьги не изменены.
5. Браслет/кольцо не изменены, если есть.
6. Исправлена конкретная проблема.
7. Нет новых AI-артефактов.
8. Нет сломанной анатомии.
9. Товар читается в маленькой превью WB.
10. Фото выглядит дороже и чище.
11. Лицо не перетягивает внимание.
12. Нет лишних предметов.
13. Нет текстовых/визуальных пересечений с украшением.
14. Фон помогает, а не отвлекает.
15. Итоговая оценка не ниже 9/10.

Формат отчета:
- Что изменено:
- Что сохранено:
- Результаты автотестов:
- Оценка:
- Что еще требует правки:
- Решение: финализировать / продолжить цикл.
