# Промпт: 2D-план → 3D-визуализация квартиры (вид сверху)

## 0. Как подавать (важнее самого текста)

1. **Модель:** лучше всего с этим справляются модели, которые принимают несколько входных изображений и хорошо рисуют текст:
   Nano Banana Pro (Gemini 3 Pro Image), затем GPT Image (в ChatGPT), затем Flux Kontext Pro/Max.
   Midjourney и SDXL без ControlNet планировку не соблюдают, их лучше не брать.
2. **Входные изображения, всегда в этом порядке:**
   - IMAGE 1 — ваш 2D-план (обрезанный по контуру квартиры, без шапки и логотипов застройщика).
   - IMAGE 2 — эталонный рендер (правая половина вашего примера, **без** левой половины с планом).
   - (опционально) IMAGE 3 — первый удачный рендер из вашей серии. Так стиль всех 30 визуализаций будет одинаковым.
3. **Соотношение сторон** выставляйте такое же, как у плана. Разрешение 2K или 4K: на 1K вешалки и мелочи превращаются в кашу.
4. **Промпт состоит из двух частей:** блок A (стиль) одинаковый для всех 30 планов, блок B (опись конкретного плана) пишется под каждый план.
   Именно блок B даёт точность: модель теряет объекты, которые не названы словами.
5. **Генерируйте в два захода:** сначала общий рендер, затем точечные правки (раздел 4).
   Даже на эталонном уровне с первого раза получается редко.

---

## 1. БЛОК A — мастер-промпт (копировать без изменений)

```
TASK
Convert the 2D architectural floor plan in IMAGE 1 into a photorealistic top-down 3D interior
visualization of the SAME apartment. Render it in exactly the same visual style, materials,
lighting mood, color palette and level of detail as the style reference in IMAGE 2.
IMAGE 1 is the single source of truth for geometry, room layout, openings and furniture positions.
IMAGE 2 is a STYLE reference only — never copy its room shapes, layout or furniture placement.
MANDATORY GRAPHIC STYLE copied from IMAGE 2: all walls solid flat matte BLACK (never grey or beige);
every area number inside a small white rectangle with a thin grey outline; the apartment badge a
white rectangle split vertically into two cells. Output 4K with every object seen strictly from above.

1. GEOMETRY — ABSOLUTE PRIORITY
- Strict orthographic top-down view, camera exactly 90° straight down. No perspective, no tilt,
  no isometric angle. Walls are seen only as their cut top section.
- Trace IMAGE 1 one-to-one: identical outer contour, proportions, wall thicknesses, room sizes,
  niches, shafts, columns, window and door openings. Do not add, remove, move, merge or resize
  any wall or room. Output framing and aspect ratio identical to IMAGE 1.
- Never invent rooms, enclosures, partitions or doors that are not drawn: no extra dressing
  rooms or walk-in closets, no extra walls. A dashed line in the plan = open passage, no wall.
- If a LAYOUT MAP with percentages is given below, it is binding: room boundaries must land at
  those percentages of the apartment's width and height.
- Walls: solid flat matte black (#111111) section fill with crisp sharp edges, same thickness as
  in the plan. Everything outside the apartment is pure white (#FFFFFF), no shadows outside.
- Loggia / balcony glazing is drawn as WINDOWS (light frames, glass, white sill) — never as doors
  with handles or dark door frames. Ventilation shafts / technical shafts are filled solid black like
  the walls (never open, hollow or transparent boxes).
- Windows exactly where and as wide as in the plan: light grey PVC frames with glass panes seen
  from above, white window sill on the inside, sheer white tulle curtains / light linen roller
  blinds gathered at both sides of each window.
- Doors: every door is a thin door leaf (dark graphite or warm walnut, entrance door dark metal)
  standing OPEN at the same hinge side and the same angle as the swing arc in the plan.
  The swing arcs themselves are NOT drawn. Doorways without a door stay open passages.
- Every symbol in the plan becomes a realistic 3D object of the same size, position and
  orientation. Symbol legend: bed outline = double bed; small squares beside bed = nightstands;
  4 circles in a rectangle = cooktop; square with a small circle = sink; asterisk * = refrigerator;
  wine-glass icon = dishwasher; circle inside a square = front-loading washing machine;
  oval with tank = toilet; long rounded rectangle = bathtub; dotted area with a shower head =
  walk-in shower tray (NOT a bathtub); sofa outline = sofa; hanger icon = open wardrobe / closet
  with hanging clothes; thin rectangle along a wall = TV / console; narrow rectangle with two small crosses × × = rectangular upholstered pouf / bench (NOT a
  cabinet or electrical panel); small square with a narrow bar inside, next to a wardrobe = basket /
  shelves with FOLDED clothes (part of an L-shaped wardrobe); plant drawing = large potted
  plant; table with chairs = dining set with the same number of chairs; small black-walled box with
  a circle = enclosed technical shaft: filled SOLID BLACK like the walls (no visible pipe, never
  shelves, storage or an open box).

2. STYLE
- High-end photorealistic architectural visualization (Corona / V-Ray quality), real-estate
  marketing plan render, warm cozy modern Scandinavian / Japandi interior.
- Palette: warm beige, greige, taupe, cream, warm white, natural light oak, dark graphite accents,
  muted olive-green plants. No saturated colors.
- Floors: warm light-medium natural oak laminate with visible grain and plank joints, one
  continuous floor through all living rooms, kitchen, hallway and loggia.
  Bathroom: large-format warm beige stone-look porcelain tiles with thin grout lines.
- Materials: linen and cotton bedding with natural wrinkles, bouclé and wool upholstery, matte
  wood, matte ceramic, brushed metal, glass. Real textures, real surface imperfections.

3. LIGHTING — CRITICAL
- Evening atmosphere, warm light 2700–3000 K. ONLY visible practical light sources:
  table lamps on nightstands (glowing fabric shades seen from above as bright warm round discs
  with a soft halo), floor lamps, a small pendant or candle glow above the dining table,
  warm LED strips inside wardrobes and closets, a warm backlit mirror in the bathroom.
- Each lamp casts a soft visible pool of warm light on the floor, furniture and textiles around it.
- ABSOLUTELY NO ceiling lights: no downlights, no spotlights, no chandeliers, no ceiling lamps,
  no light panels, no ceiling visible at all.
- Soft global illumination, gentle contact shadows under every piece of furniture, subtle ambient
  occlusion in corners and along walls. No harsh sunlight, no overexposure, no blown highlights.

4. DETAIL LEVEL — CRITICAL (this is what makes or breaks the render)
- EVERY object is seen strictly from ABOVE, never its front face: the washing machine shows its
  top lid (not the round door), the refrigerator and cabinets show their tops, closets and
  wardrobes show the tops of hangers, shoulders of garments and folded stacks from above —
  never a front (elevation) view of hanging clothes.
- Wardrobes and closets are shown OPEN from above (no top panel), lit by warm LED strips:
  a clothes rail with 10–15 individually readable hangers, each holding a DIFFERENT garment
  (shirts, knit sweaters, blazers, coats, dresses) in beige, white, grey, camel, taupe and black;
  shelf sections with neat stacks of folded sweaters and towels; pairs of shoes or shoe boxes on
  the bottom. Every hanger, every garment and every fold must be crisp, sharp and separable —
  never a blurry mass of fabric.
- Bedroom: double bed with upholstered headboard, rumpled linen duvet with realistic folds,
  4 pillows, folded knitted throw at the foot, nightstands with glowing lamps and a book or cup.
- Kitchen: ONLY base (floor-standing) cabinets and appliances. NO upper wall cabinets, NO wall
  shelves, NO rails, NO open niches, NO tall pantry columns, NO hood cabinet — the walls above
  the countertop are completely bare. Light stone or wood countertop; black glass induction cooktop with
  visible cooking zones; sink with faucet; kettle, cutting board, small utensils, a bowl of fruit.
  Refrigerator and dishwasher exactly where the plan marks them. Dining table or bar counter
  with plates, glasses and exactly as many chairs as drawn.
- Bathroom: bathtub OR shower exactly as drawn in the plan (never swap one for the other), with
  chrome mixer; wall-hung toilet with a narrow shelf / installation ledge
  on the wall BEHIND it holding toiletries and a small plant; washbasin on a vanity with a round
  backlit mirror; washing machine where the plan marks it; heated towel rail with towels; bath mat.
- Hallway: built-in closet where marked, open from above: a rail with 5–8 separate hangers, each
  with a different coat or jacket, pairs of shoes below, LED strip; small rug.
- Loggia / balcony: exactly the objects drawn in the plan.
- No potted plants on the bathroom floor.
- Small decor allowed (plants, books, vases, rugs, cushions), but it must never cover, replace or
  move any object defined in the plan.

5. LABELS
- Place each room area number at the same position as in IMAGE 1, inside a small white rectangle
  with a thin light-grey outline, dark grey clean thin sans-serif font (Montserrat Light style),
  comma as decimal separator. Copy the digits EXACTLY as written in the plan.
- Apartment badge in the same position as in the plan: white rectangle split by a thin vertical
  line into two cells SIDE BY SIDE (never stacked like a fraction) — large number of rooms in the
  left cell, total area in the right cell.
- No other text anywhere: no logos, no watermarks, no dimensions, no apartment code, no symbols.

DO NOT: change the layout; add or remove walls, doors, windows or rooms; tilt the camera; show
ceilings or ceiling lamps; add upper kitchen cabinets; draw door swing arcs or plan icons;
produce cartoon, flat, sketch or CGI-plastic look; blur small objects; invent extra text.
```

---

## 2. БЛОК B — шаблон описи плана (заполняется под каждый план)

Вставляется **сразу после** блока A. Обязательно начинать с EXACT OVERLAY RULE и SIZE MAP
(координаты каждой комнаты и каждого предмета в % от внешнего контура квартиры), как в `45_message.txt`:
без этого модель «плывёт» по пропорциям. Геометрию проверять `tools/overlay.py` (план красным поверх рендера).
Правила описи:
- называйте положение каждого объекта (top-left / right wall / along bottom wall…) и его ориентацию;
- считайте всё поштучно: стулья, подушки, конфорки;
- называйте, с какой стороны петли у двери и куда она открывается;
- отдельно перечислите, чего в комнате быть НЕ должно.

```
PLAN-SPECIFIC CONTENT (apartment: <N> rooms, total <XX,X> m²). Orientation: top of image = top of plan.

<ROOM NAME> (<area>, <position in plan>):
- <object> — <where>, <orientation>, <count/size>
- ...
- Light sources: <which lamps, where>
- Must NOT contain: <...>

Labels: "<area>" in <room>, ...; badge "<rooms> | <total>" at <position>.
```

---

## 3. БЛОК B — заполненный пример для эталонного плана №138

```
PLAN-SPECIFIC CONTENT (apartment: 1 room, total 35,8 m²). Orientation: top of image = top of plan.

LOGGIA 3,8 (top-left strip, full-width window along the top wall):
- Beige bouclé lounge armchair in the left part, rotated ~45°.
- Small round wooden side table to the right of the armchair.
- Floor lamp with a round glowing linen shade next to the armchair.
- Large potted monstera / tropical plant in the right part near the window.
- Sheer tulle curtains at the window.
- Separated from the bedroom by a partition with a glazed section on the left and a door on the
  right; the door leaf opens into the bedroom, hinged on the right.

BEDROOM 13,5 (left, below the loggia):
- Double bed with its headboard against the LEFT wall, bed centered vertically on that wall,
  pointing to the right.
- Two nightstands on the left wall, one above and one below the bed, each with a glowing table lamp.
- Thin dark TV console / wall TV on the RIGHT wall, opposite the bed.
- Full-width open wardrobe along the ENTIRE BOTTOM wall: section with folded clothes on shelves on
  the left, then 3–4 hanging sections with 10–15 distinct garments on hangers, warm LED strip glow.
- Door from the hallway in the lower part of the right wall, leaf open into the bedroom.
- Light sources: 2 bedside lamps only.

KITCHEN-DINING 10,0 (top-right, window along the top wall):
- Rectangular dining table in the upper-left area near the window with EXACTLY 3 chairs
  (top, bottom, right side of the table), 3 plates, glasses, a small candle glow.
- Floor-standing kitchen run along the RIGHT wall, top to bottom: narrow base cabinet in the top
  corner, black induction cooktop with 4 zones, countertop with kettle, sink with faucet.
- The kitchen turns into an L along the bottom: refrigerator (left) and base cabinet with
  built-in dishwasher (right), countertop continuous.
- NO upper wall cabinets, NO hood cabinet, NO wall shelves.
- Door from the hallway at the bottom-left corner, leaf open into the kitchen.

HALLWAY 4,4 (bottom-center, vertical corridor):
- Entrance door at the bottom wall, dark metal leaf opening OUTWARD, hinged on the left.
- Built-in closet niche on the LEFT (bottom-left of the hallway, marked with hanger): open, with
  hanging coats and jackets on hangers, folded items on a shelf, shoes below, LED glow.
- Narrow console / shoe cabinet and mirror on the right wall above the bathroom door.
- Doors: to kitchen (top), to bedroom (left), to bathroom (right).

BATHROOM 4,1 (bottom-right):
- Bathtub along the entire BOTTOM wall, mixer on its left end.
- Front-loading washing machine in the TOP-LEFT corner.
- Built-in low cabinets / shelves along the top wall.
- Wall-hung toilet on the RIGHT wall (upper half) with a narrow shelf ledge BEHIND it holding
  toiletries.
- Washbasin on a vanity on the RIGHT wall below the toilet, round backlit mirror above it.
- Small round riser pipe in the bottom-left corner near the bathtub.
- Door from the hallway on the left wall, leaf open into the bathroom.
- Beige stone-look tile floor.

Labels: "3,8" loggia, "13,5" bedroom, "10,0" kitchen, "4,4" hallway, "4,1" bathroom.
Badge "1 | 35,8" in the lower part of the bedroom, left of center (omit "№138" and "13,5" from the badge).
```

---

## 4. Промпты для второго захода (редактирование уже готового рендера)

Подаются вместе с готовым рендером. Каждый начинается с фиксации:
`Keep everything in this image exactly the same — layout, camera, walls, colors, lighting — and change ONLY the following:`

- **Гардероб:** `Make the wardrobe in the <room> open from above and highly detailed: 12–15 individual wooden hangers on a rail, each with a different garment (shirts, knit sweaters, coats, dresses) in beige, white, grey, camel and black; stacks of folded clothes on shelves; shoes at the bottom; warm LED strip light inside. Every hanger must be clearly visible and separate.`
- **Свет:** `Remove all ceiling lights. Make the table lamps and floor lamps visibly glow with warm 2700K light and cast soft pools of light on the surrounding floor and furniture.`
- **Кухня:** `Remove all upper wall cabinets and wall shelves from the kitchen. Keep only floor-standing base cabinets, countertop and appliances.`
- **Санузел:** `Add a narrow shelf ledge on the wall directly behind the toilet with toiletries, a small plant and a folded towel.`
- **Цифры:** `Fix the area labels: text must read exactly "<…>", "<…>" in white boxes with thin grey outlines, clean thin sans-serif.`
- **Геометрия:** `The wall between <room A> and <room B> must match the plan in IMAGE 1 exactly; move it to <…>.` (в этом случае план тоже подайте на вход)

---

## 5. Мета-промпт для автоматической описи (блок B) через LLM

Подайте LLM (Claude / GPT / Gemini) один план с этим текстом, и вы получите готовый блок B:

```
Ты — архитектор-визуализатор. Проанализируй план квартиры на изображении и составь на английском
поштучную опись для генератора изображений в формате:

PLAN-SPECIFIC CONTENT (apartment: <N> rooms, total <XX,X> m²). Orientation: top of image = top of plan.
<ROOM NAME> (<area>, <position>):
- <object> — <точное положение: какая стена / угол>, <ориентация>, <количество>
- Doors: <откуда, с какой стороны петли, куда открывается>
- Windows: <какая стена, ширина относительно стены>
- Light sources: <только лампы/торшеры/LED в шкафах>
- Must NOT contain: <…>
Labels: ...; Badge: ...

Правила: не пропускай ни одного условного знака плана (включая стояки, шахты, ниши, стиралку,
посудомойку, вешалки). Считай стулья и конфорки. Кухня всегда без верхних шкафов. Если символ
неоднозначен, опиши самый вероятный вариант и пометь его [?].
```
