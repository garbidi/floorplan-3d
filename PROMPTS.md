# Промпты для 3D-визуализации планировок (вид сверху)

## 0. Рабочий процесс

1. Подготовить исходник: подать на вход **чистый план** (PNG, ≥2000 px по длинной стороне).
   Желательно заранее стереть золотую плашку с №квартиры и жилой площадью — по ТЗ её быть не должно.
2. Сгенерировать рендер по промпту (img2img / image editing с планом как референсом).
3. Проверить по чек-листу ТЗ (см. §4).
4. **Цифры площадей и плашку комнатности накладывать вектором в Figma поверх рендера** —
   так они всегда читаемы, одинаковы во всём каталоге и гарантированно без опечаток.
   В промпте цифры оставлены на случай, если постобработки не будет.

⚠️ Планы 44 и 45 повёрнуты на 180° (вход внизу — это правильно, но **цифры в исходнике вверх ногами**).
Планы НЕ разворачивать, а в промпте явно требовать рисовать цифры горизонтально и читаемо.

---

## 1. Базовый блок (одинаковый для всех планировок)

```
Photorealistic 3D top-down (bird's-eye) cutaway render of a furnished apartment, ceiling and roof removed.
Camera almost straight overhead with only a slight 5-10 degree tilt so that wall thickness and a little
volume are visible. No wide-angle lens, no fisheye, no strong perspective, no distortion — the layout must
stay as readable as the original floor plan. The apartment entrance door is at the BOTTOM edge of the image.

STRICT GEOMETRY — this is the most important rule:
Reproduce the attached floor plan 1:1. Identical outer contour, identical wall positions, identical wall
thickness, identical room proportions and relative sizes, identical position and width of every window and
every door opening. Do not add, remove, merge, move or resize any wall, room, window or door. Do not invent
extra rooms, niches, balconies or corridors. Every room must keep the exact shape and area shown on the plan.

FURNITURE RULE:
Place only the furniture listed below, in exactly the positions shown on the plan. No additional furniture,
no additional decor, no extra plants, no rugs, no paintings, no clutter, no random objects. Furniture must be
logically oriented for its room and must not block doors or windows.

MATERIALS:
- Floor: ONE single light warm oak wood-look laminate through the entire apartment — living rooms, bedrooms,
  kitchen, hallway, loggia — same tone, same plank width, same plank direction everywhere.
- Only the bathroom / WC has a different floor: light beige large-format ceramic tile. Nothing else is tiled.
- Walls: light warm white / soft beige plaster. Wall tops (the cut) are a flat matte near-black charcoal cap.
- All windows are modern white plastic (PVC) windows with white frames, light sheer curtains only.

KITCHEN RULE — base units only:
The kitchen consists ONLY of floor-standing lower cabinets with a continuous worktop. There are NO wall
cabinets, NO upper cabinets, NO overhead cupboards, NO open wall shelves, NO floating shelves and NO shelf
units of any kind above the worktop. The wall above the worktop is bare, finished with a plain backsplash
only. Nothing is mounted on the kitchen wall. A discreet warm LED strip runs along the underside of the
worktop edge.

WASHING MACHINE — critical:
The washing machine stands upright on the floor. Seen from above it is a plain rectangular box with a flat
white top panel facing the camera and nothing on it. Its round glass door is on the vertical front face,
facing sideways into the room, and is therefore NOT visible from above. Never draw a circle, a porthole, a
round door or control dials on the top surface. The machine is never lying on its back or tipped over.

WARDROBES AND STORAGE:
Every wardrobe, closet and built-in storage unit is shown with a TRANSPARENT glass top so the interior is
fully visible from above: hanging rails with clothes hanging HORIZONTALLY along the rail (never flat against
the wall, never vertical), folded linen on shelves, shoes on the lower shelf, warm LED strip inside.

LIGHTING:
Soft, bright, even daylight plus warm local light sources: floor lamp, table lamps, bedside lamps, LED strips
under the kitchen worktop edge and inside wardrobes. Light, comfortable, airy colour scheme — warm beige, soft grey,
natural wood, white. No dark or moody interior.

CLEAN OUTPUT — remove all 2D drafting symbols:
No hatching, no door swing arcs, no dashed lines, no dimension lines or arrows, no hanger pictograms, no
socket / plug / snowflake / glass icons, no room names, no apartment number, no living-area figure, no
north arrow, no logo, no watermark, no captions, no random text or lettering anywhere in the image.

In the bathroom, the wall segments reserved for plumbing risers and communications must be closed and
finished in the same colour as the wall — no open shafts, no visible pipes, no black slots.

LABELS (the only text allowed):
Small white rounded rectangular plates with dark grey digits, placed in the centre of each room, always
upright and horizontal, easy to read on top of floor and furniture. Plus one badge in the free area of the
plan: a gold square with the number of rooms and, next to it on a white field, the total area.
```

**Negative prompt** (для Flux / SD / ComfyUI):

```
extra rooms, extra walls, moved walls, changed layout, added furniture, duplicate furniture, clutter, rugs,
carpets, paintings, extra plants, people, pets, text, letters, labels, captions, watermark, logo, signature,
room names, apartment number, hatching, door swing arcs, dashed lines, dimension arrows, hanger icons,
socket icons, wall cabinets, upper kitchen cabinets, overhead cupboards, wall shelves, floating shelves,
range hood, tiles in hallway, tiles in kitchen, mixed flooring, different floor tones, dark interior,
moody lighting, wooden windows, fisheye, wide angle, strong perspective, tilted horizon, isometric game art,
cartoon, low detail, blurry
```

---

## 2. Промпт для плана 42 (2-комнатная, 53,8 м²)

Базовый блок + ниже.

```
This apartment is a 2-room flat, total area 53.8 m2. Entrance door at the bottom of the image.

ROOM BY ROOM (top row, left to right):

1. BEDROOM / CHILD'S ROOM 11.7 m2 — top-left corner. One window in the top wall.
   Against the left wall, near the window: a writing desk with a desk lamp and a swivel chair.
   Below it, along the same left wall: a single bed with a headboard, bedding and one pillow.
   A bedside table next to the bed. Against the right wall of this room: a built-in wardrobe with a
   transparent glass top, clothes hanging horizontally on the rail, shelves with folded clothes.
   Floor lamp in the free corner.

2. MASTER BEDROOM 11.9 m2 — top-middle. One window in the top wall.
   A double bed centred against the top wall under the window, two pillows, throw blanket,
   one bedside table on each side with a warm table lamp.
   Along the whole bottom wall of this room: a long built-in wardrobe with a transparent glass top,
   clothes on a horizontal rail, folded linen and boxes on shelves, LED strip inside.
   One potted plant in the top-left corner of the room. A slim wall-mounted TV panel on the left wall.

3. LOGGIA / BALCONY 3.8 m2 — top-right corner, glazed along the top wall.
   Only: one soft armchair, one small round side table, one large potted plant. Nothing else.
   Same wood floor as the rest of the apartment.

RIGHT SIDE:

4. KITCHEN-LIVING 13.5 m2 — occupies the whole right side from the loggia down to the bottom wall.
   Kitchen units run along the right wall: tall fridge at the bottom, sink with mixer tap under the
   window-side, 4-burner hob with cooktop, worktop. Base cabinets only — no wall cabinets, no shelves above the worktop.
   In the upper part of the room: a rectangular dining table with 4 chairs, set with plates and a
   small centrepiece. A door from this room to the loggia. A slim TV panel on the left wall.

BOTTOM ROW (left to right):

5. BATHROOM 3.8 m2 — bottom-left corner. Light beige ceramic tile floor (the only tiled area,
   together with the WC). A bathtub along the bottom wall with a wall mixer and a glass screen,
   a washbasin with mirror on the left wall, a front-loading washing machine in the top-left corner
   with its round door facing sideways (never upwards), folded towels.

6. WC 2.1 m2 — small room next to the bathroom. Light beige ceramic tile floor.
   Only a wall-hung toilet and a small corner washbasin. Plumbing wall closed and painted like the wall.

7. HALLWAY 7.0 m2 — centre-bottom, with the entrance door in the bottom wall.
   A built-in wardrobe along its right side with a transparent glass top — coats hanging horizontally
   on the rail, shoes on the lower shelf, boxes on the upper shelf. A small bench and a mirror.

LABELS: 11,7 / 11,9 / 3,8 / 13,5 / 3,8 / 2,1 / 7,0 on white plates in the centre of the matching rooms.
Badge: gold square with "2" and, on white, "53,8". No apartment number, no room names, no living area.
```

---

## 3. Промпт для плана 44 (1-комнатная, 38,8 м²)

Базовый блок + ниже.
Исходник повёрнут на 180°: **вход внизу — так и оставляем, но все цифры рисуем горизонтально и читаемо**.

```
This apartment is a 1-room flat, total area 38.8 m2. Entrance door at the bottom of the image.
The area numbers printed on the source plan are upside down — in the render all digits must be
upright, horizontal and readable.

ROOM BY ROOM:

1. LOGGIA 3.8 m2 — top-left corner, glazed along the top wall.
   Only: one soft armchair, one small round side table, one large potted plant. Same wood floor.

2. BEDROOM / LIVING ROOM 14.0 m2 — the whole left side below the loggia.
   A double bed centred in the upper part of the room, headboard against the left wall, two pillows,
   a bedside table with a warm lamp on each side.
   Along the bottom wall of this room: a built-in wardrobe with a transparent glass top — clothes
   hanging horizontally on the rail, folded linen on shelves, LED strip inside.
   A door in the top wall leading to the loggia. A slim wall-mounted TV panel opposite the bed.
   A floor lamp in the corner.

3. KITCHEN-LIVING 12.5 m2 — top-right. One large window in the top wall.
   Kitchen units along the right wall: 4-burner hob, worktop, sink with mixer tap, fridge,
   Base cabinets only — no wall cabinets, no shelves above the worktop.
   In the left part of the room: a dining table with 2 chairs set with plates, glasses and a small
   centrepiece; a bench or an extra chair at the end.

4. HALLWAY 4.4 m2 — centre-bottom, entrance door in the bottom wall.
   A narrow shoe cabinet and a mirror only, plus a built-in wardrobe with a transparent glass top
   on the left side of the hallway with coats on a horizontal rail and shoes below.

5. BATHROOM 4.1 m2 — bottom-right. Light beige ceramic tile floor — the only tiled room.
   A corner shower cabin with a glass enclosure and a round shower tray in the bottom-right corner,
   a wall-hung toilet on the right wall, a washbasin with a mirror on the bottom wall,
   a front-loading washing machine in the top-right corner with its round door facing sideways,
   never upwards. The plumbing riser wall is closed and finished in the wall colour.

LABELS: 3,8 / 14,0 / 12,5 / 4,4 / 4,1 on white plates in the centre of the matching rooms, upright.
Badge: gold square with "1" and, on white, "38,8". No apartment number, no room names, no living area.
```

---

## 4. Промпт для плана 45 (1-комнатная, 39,1 м²)

Базовый блок + ниже. Исходник тоже повёрнут на 180°.

```
This apartment is a 1-room flat, total area 39.1 m2. Entrance door at the bottom of the image.
The area numbers printed on the source plan are upside down — in the render all digits must be
upright, horizontal and readable.

ROOM BY ROOM:

1. BEDROOM 12.5 m2 — top-left. One window in the top wall.
   A double bed centred against the left wall, headboard to the left, two pillows and a throw blanket,
   one bedside table with a warm table lamp on each side.
   Along the bottom wall of this room: a built-in wardrobe with a transparent glass top — clothes
   hanging horizontally on the rail, folded linen on shelves, warm LED strip inside.
   A slim wall-mounted TV panel on the right wall opposite the bed.

2. LOGGIA 3.8 m2 — top-right corner, glazed along the top wall.
   Only: one soft armchair, one small round side table, one large potted plant. Same wood floor.

3. KITCHEN-LIVING ROOM 14.7 m2 — the whole right side below the loggia.
   In the upper-left part: a three-seat sofa against the left wall with two cushions, facing a slim
   wall-mounted TV panel on the opposite wall. A door in the top wall to the loggia.
   Lower part: a dining table with 2 chairs, set with plates and glasses.
   Kitchen units along the right wall: 4-burner hob, worktop, sink with mixer tap, fridge,
   Base cabinets only — no wall cabinets, no shelves above the worktop.

4. BATHROOM 4.2 m2 — bottom-left. Light beige ceramic tile floor — the only tiled room.
   A corner shower cabin with a glass enclosure in the bottom-left corner, a wall-hung toilet on the
   left wall, a washbasin with a mirror on the bottom wall, a front-loading washing machine in the
   top-right corner of the room with its round door facing sideways, never upwards.
   The plumbing riser wall is closed and finished in the wall colour.

5. HALLWAY 3.9 m2 — centre-bottom, entrance door in the bottom wall.
   A built-in wardrobe with a transparent glass top along its right side — coats hanging horizontally
   on the rail, shoes on the lower shelf. A mirror and a small bench. Nothing else.

LABELS: 12,5 / 3,8 / 14,7 / 4,2 / 3,9 on white plates in the centre of the matching rooms, upright.
Badge: gold square with "1" and, on white, "39,1". No apartment number, no room names, no living area.
```

---

## 5. Чек-лист приёмки (по ТЗ)

- [ ] Вход в квартиру снизу
- [ ] Лёгкий наклон камеры, без искажения планировки
- [ ] Светлая, комфортная гамма
- [ ] Окна пластиковые белые
- [ ] Короба коммуникаций в санузле закрыты и закрашены в цвет стены
- [ ] Есть локальная подсветка (торшеры, настольные лампы, LED)
- [ ] Одежда в шкафах висит горизонтально вдоль штанги, шкафы прозрачны сверху
- [ ] Стиральная машина с фронтальной загрузкой, люк не сверху
- [ ] Керамогранит только в санузле; коридор и кухня — то же дерево, что и комнаты
- [ ] Нет лишней мебели и предметов, нет чайника вне кухни
- [ ] Нет символов, названий комнат, № квартиры, жилой площади
- [ ] Плашки площадей читаемы, цифры совпадают с планом
- [ ] Плашка: комнатность + общая площадь

---

## 6. Запуск в Nano Banana Pro (Gemini 3 Pro Image)

### Главный приём: подавать ДВА изображения
Nano Banana Pro принимает несколько референсов в одном запросе. Используйте это:

1. **Изображение 1 — план** (`42 (1).png` / `44.png` / `45.png`) — источник геометрии.
2. **Изображение 2 — согласованный менеджером рендер** из ТЗ (правая половина картинки
   «Пример, который согласовал менеджер») — источник стиля.

И добавьте в начало промпта строку:

```
IMAGE 1 is the floor plan — copy its geometry exactly: walls, room shapes, proportions, window and
door positions. IMAGE 2 is the style reference — copy its rendering style, camera angle, colour
palette, lighting, materials and the look of the white area plates. Do not copy the layout, the
rooms or the furniture from IMAGE 2.
```

### Параметры генерации
- Resolution: **2K** (для каталога хватает; 4K дороже почти вдвое и не нужен)
- Aspect ratio: подобрать под пропорции плана — 42 ≈ **4:3**, 44 и 45 ≈ **3:4**
- Temperature: пониже (0.4–0.6), чтобы меньше фантазировала с планировкой
- Генерировать по 4 варианта на план, отбирать лучший

### Итеративная правка вместо перегенерации
Nano Banana хорошо правит собственный результат. Если 90% устраивает — не перегенерируйте,
а пришлите результат обратно с точечной командой, например:

```
Keep everything exactly as it is. Only change: the floor in the hallway must be the same wood
laminate as in the rooms, not tile. Do not change anything else.
```

```
Keep the image identical. Remove the text label above the kitchen counter and remove the extra
stool near the window. Do not change the layout, furniture or lighting.
```

---

## 7. Библиотека промптов-правок

Отправлять вместе с готовым рендером, temperature 0.15–0.25, по одной-две правки за раз.
Каждый начинать с фиксирующей фразы и заканчивать `Do not change anything else in the image.`

**Стиральная машина лежит на спине**
```
The washing machine in the bathroom is lying on its back with its round porthole facing up. Stand it
upright against the wall. Seen from above it must be a plain rectangular box with a flat white top panel
and nothing on it — no circle, no porthole, no dials. The round door is on the vertical front face and is
not visible from above.
```

**Плитка на кухне или в коридоре**
```
Replace the kitchen (hallway) floor with exactly the same light warm oak wood-look laminate used in the
rest of the apartment — identical tone, plank width and direction. The planks run continuously across the
doorway with no threshold strip and no visible boundary. The only tiled room is the bathroom.
```

**Навесные шкафы на кухне**
```
Remove the overhead wall cabinets above the kitchen worktop — the dark horizontal band along the kitchen
wall. No wall cabinets, no upper cupboards, no shelves above the worktop. The worktop, sink and hob must
be fully visible from above. The wall above the worktop is bare with a plain light backsplash only.
```

**Лишние предметы на столе / мебель не по плану**
```
Remove the plant (objects) from the dining table — the table top must be completely empty.
Remove the extra <object> near <place> — it is not on the floor plan.
```

**Одежда в шкафу висит неправильно**
```
In the wardrobe the clothes are hanging flat against the back wall. Rehang them HORIZONTALLY along the
rail, so from above you see a row of shoulders side by side along the length of the wardrobe.
```

**Открытые короба коммуникаций в санузле**
```
Close the plumbing riser recess in the bathroom wall and finish it in the same colour as the wall — no
open shaft, no visible pipes, no dark slot.
```

**Тёмный или контрастный интерьер**
```
Make the whole apartment lighter and warmer: light warm oak floor, soft beige walls, light furniture.
Keep the layout, furniture and labels exactly as they are.
```
