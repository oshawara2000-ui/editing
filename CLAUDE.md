# CLAUDE.md: دستور شغل الريلز والمونتاج (Fekra Craft) — v0.2

> اقرأ الملف ده قبل أي مهمة فيديو. أي حاجة مكتوبة هنا تتنفذ من غير ما تتسأل عنها تاني.
> المستخدم: عمر (Fekra Craft). المحتوى: طباعة 3D، منتجات، ديكور، نحت، شروحات، كواليس، وريلز Talking-Head لعملاء (زي دكتور إسلام).
> اللغة: رد بالمصري، مختصر وعملي. في آخر كل مهمة اكتب 3 سطور بس: اتعمل إيه، الملفات فين، إيه اللي ناقص.

---

## ⚡ أمر "start reel" / "start video editing" (السيكونس الأوتوماتيك)

لما عمر يقول **start reel** أو **start video editing** ويدي فولدر، امشي بالترتيب ده **بالظبط**.
القاعدة الذهبية: **الشغل التقيل يتعمل على جهاز عمر** (GPU + RAM) بالسكريبتات اللي في `scripts\`.
كلود يقرا بس ملفات صغيرة (JSON / txt). **ممنوع رفع فيديو أو صوت لـ Gemini أو أي مكان**، Gemini بياخد **نص بس**.

### الخطوة 0: أسئلة البداية (كلها في رسالة واحدة، باختصار)
1. المونتاج: **DaVinci Resolve** ولا **ffmpeg**؟
2. نوع الشغل: **reel** (ريل Fekra: مسموح hook من نص الفيديو يتحط في الأول + شيل التكرار والغلطات بين الجمل) ولا **locked** (عميل Talking-Head: قاعدة 1.3 بالحرف)؟
3. لو لقيت **clean plate / studio background** في الفولدر: نعزل الشخص **بالكرسي** (Magic Mask) ونحطه في الاستوديو؟ أنهي نسخة (`clean plate` / `classic` / `gold`)؟
4. الطول المطلوب؟ (افتراضي 30–60 ثانية)
5. ترجمة؟ (عربي افتراضي، إنجليزي؟) موسيقى؟ (بس لو فيه تراك مرخّص)
6. فيه جملة لازم تفضل أو تتشال أكيد؟
> أي حاجة مش متجاوب عليها: خد الافتراضي وقول إنك خدته.

### الخطوات 1–6 (أوامر جاهزة)
| # | الخطوة | الأمر (من فولدر الأتمتة) | المخرج |
|---|---|---|---|
| 1 | فحص الفيديو | `python scripts\probe.py "<folder>"` | `_claude_preview\probe.json` |
| 2 | كاش الترجمة | تلقائي جوه الخطوة 3: لو `srt\<name>.srt` أو `.words.json` موجود **ما يتعادش** | — |
| 3a | تفريغ محلي (توقيت دقيق) | `python scripts\transcribe.py "<folder>"` (بيشغّل `transcribe.bat`) | `srt\<name>.srt` + `.words.json` |
| 3b | تصحيح الكلام بـ Gemini Pro (نص بس) | `python scripts\gemini_fix.py "<folder>"` | `srt\<name>.fixed.srt` + `.fixes.txt` |
| 4 | الـ hook + خطة القص (Gemini) | `python scripts\gemini_plan.py "<folder>" --target 45 --mode reel` | `_claude_preview\plan.json` |
| 5 | **اعرض الخطة واستنى الموافقة** | جدول: الـ hook + الأجزاء + الطول | — |
| 6a | ffmpeg: Draft ثم Final | `python scripts\render_ffmpeg.py "<folder>" --draft` ← بعد الموافقة من غير `--draft` | `_claude_preview\draft_720p_30fps.mp4` / `export\edited_video_4k_30fps.mp4` |
| 6b | DaVinci | ابني التايم لاين من `plan.json` عن طريق DaVinci MCP بإعدادات 2.3/2.4، والـ Magic Mask حسب المرحلة 4 | `.drp` في `project\` |

- أو كله مرة واحدة لحد الـ draft: `start_reel.bat "<folder>" 45 reel`
- الـ Whisper (transcribe.bat) = **التوقيت**، و Gemini = **صحة الكلام**. التوقيتات ما تتغيرش أبداً من Gemini.
- راجع `.fixes.txt` بسرعة قبل ما تكمل (لو Gemini غيّر معنى، ارجع لنسخة Whisper).
- مفتاح Gemini في `.env` (`GEMINI_API_KEY` من Google AI Studio، أو `OPENROUTER_API_KEY`). **ممنوع** يتكتب في أي ملف تاني أو يترفع.

---

## 0. المراجع الأساسية (اقراها من مكانها، ما تنزلش حاجة تاني)

| المرجع | المسار | الاستخدام |
|---|---|---|
| Fekra Motion Kit | `C:\Users\amrsh\Desktop\skills and textures and fonts\Fekra Motion Kit\` | الهوية، الخطوط، SFX، سكريبتات الموشن |
| الهوية البصرية | `...\Fekra Motion Kit\motion-kit\references\brand-identity.md` | **تتقري في كل شغل موشن** |
| مكتبة الحركات | `...\motion-kit\references\motion-library.md` و `style-analysis.md` | مرة واحدة لكل مشروع موشن |
| مكتبة AE | `...\motion-kit\scripts\motion_kit.jsx` | بناء الموشن بـ keyframes حقيقية |
| خلفيات الورق | `...\motion-kit\scripts\make_paper_assets.py` | ورق + grid + قصاصات + فولدرات |
| خطوط | `...\Fekra Motion Kit\fonts\` (Helvetica + Lyon Arabic Display) | إنجليزي / عربي |
| SFX الكيت | `...\Fekra Motion Kit\sfx\` | highlighter / paper / shutter / typewriter / whoosh |
| SFX KMeGa 2026 | `C:\Users\amrsh\Desktop\skills and textures and fonts\SFX KMeGa 2026\` (+ `Plus\HITS, RISERS, WHOOSHES, SLOW MOTION`) | clicks, pops, risers, hits, cash, gears |
| Presets Khaled MeGa V4 | `...\Presets Khaled MeGa V4\Presets Khaled MeGa V4 2026.prfpset` | بريسيتات Premiere (مش DaVinci) |
| أداة التفريغ | `C:\Users\amrsh\Desktop\skills and textures and fonts\transcribe-tool\transcribe.bat` | فيديو ← `.srt` + `.words.json` |
| مرجع الاستوديو | `C:\Users\amrsh\Desktop\dr eslam\` (`studio_clean_plate.jfif`، `4th try\clean plate.png / classic.png / gold.png`، `2nd try\compose_reel.py`، `studio_reel_compositor.jsx`) | خلفية الاستوديو والقيم المعتمدة |
| DaVinci MCP | `C:\Users\amrsh\AppData\Local\davinci-resolve-mcp\` | التحكم في Resolve أوتوماتيك |
| سكريبتات الأتمتة | `C:\Users\amrsh\Desktop\فكرة automation\scripts\` | probe / transcribe / gemini_fix / gemini_plan / render |
| Skills | `pro-reels-editor-ultimate`، `reels-motion-editor`، `reel-studio-ffmpeg` | اتبعها، والملف ده بيكملها |

> خط Lyon Arabic Display تجاري (اقرأ `LICENSE_NOTE.txt`). شغل العملاء يحتاج ترخيص، فنبّه عليها مرة واحدة.

---

## 1. القواعد العامة (لتوفير الاستهلاك وحماية الشغل)

### 1.1 ما تعيدش شغل اتعمل
- قبل أي خطوة، دوّر في فولدر المشروع: لو `.srt` أو `.words.json` أو draft أو proxy موجود **استخدمه**.
- **ممنوع** تعيد التفريغ لو فيه `.srt` أو `.words.json` لنفس الفيديو.
- **ممنوع** تحلل الفيديو كله. ابدأ بـ `ffprobe` (المدة، الدقة، الـ fps، الـ codec، الصوت).
- للمعاينة: فريمات محددة أو contact sheet (البداية، النهاية، كل انتقال). مش الفيديو كامل.
- اقرا كل مصدر **مرة واحدة**، واعمل **QC واحد منظم**، و**بحد أقصى محاولتين** لأي مشكلة. بعد كده وقف وقول السبب.
- ما تنزّلش موديلات أو مكتبات تقيلة عشان تحسين صغير. اتأكد إن الأداة موجودة الأول (ffmpeg / ffprobe / Python / GPU).

### 1.2 حماية الأصول
- **ممنوع** تكتب فوق أي ملف أصلي أو تعدّله. كل مخرج يتحفظ بشكل منفصل (`_v02`، `try2`...).
- المسودات في `_claude_preview\` جوه فولدر المشروع.
- أي مسح أو render طويل أو تحويل batch: اسأل الأول.

### 1.3 قفل الحوار (Locked Edit)
- **كل كلمة وترتيبها ووقفاتها وتكرارها وتزامنها تفضل زي ما هي.**
- ممنوع القص جوه الكلام، وممنوع إعادة الترتيب أو تغيير السرعة (ولا `atempo`)، وممنوع تعمل hook جديد من كلام متأخر.
- المسموح: تحسين الصورة والصوت بس. قص الـ dead air في البداية والنهاية مسموح لو المستخدم طلبه.
- **الاستثناء الوحيد: وضع `reel`** (ريلز Fekra Craft نفسها، لما عمر يختاره في سؤال البداية): مسموح hook من 2–4 ثواني من كلام متأخر يتحط في الأول، ومسموح شيل الصمت والتكرار والبدايات الغلط **بين الجمل بس**. برضه ممنوع: قص كلمة من النص، تغيير ترتيب الجمل، تغيير السرعة، أو hook بيوعد بحاجة مش في الفيديو.
- ممنوع تخترع كلام أو ادعاءات أو نتايج أو مميزات منتج. ممنوع وش لشخص حقيقي معمول بالـ AI، وممنوع مستند مزيف.

### 1.4 التسليم على مرحلتين (إجباري)
1. **Draft:** `draft_720p_30fps.mp4` (H.264 سريع، `-preset ultrafast -crf 28`) + ملاحظة قصيرة. **استنى الموافقة.**
2. **Final (بعد موافقة صريحة بس):** `edited_video_4k_30fps.mp4`، رأسي 2160×3840 (أو 3840×2160). H.264 CRF 16–19 + AAC. وقول هل الـ 4K native ولا upscaled.
3. مع التسليم: `edit_report.txt` (الاختيارات، الصوت، الـ SFX، الترجمة، التصدير، الـ QC، الحدود)، و`edit_timeline.json` لو ينفع.

### 1.5 هيكل فولدر المشروع
```
اسم-المشروع/
├── source/            ← الأصلي (لا يُلمس)
├── srt/               ← part_1_<topic>.srt / name_en.srt / name.words.json
├── assets/            ← clean plate، لوجو، صور، B-roll
├── _claude_preview/   ← المسودات والفريمات وcontact sheets
├── project/           ← .drp / .prproj / .aep / build scripts
└── export/            ← draft + final + edit_report.txt + edit_timeline.json
```
- أسماء الملفات بالإنجليزي، حروف صغيرة، `_` بدل المسافات، والتاريخ `YYYY-MM-DD`.

---

## 2. الهوية البصرية وإعدادات DaVinci Resolve

### 2.1 هوية Fekra (للموشن والجرافيكس والعناوين)
| العنصر | القيمة |
|---|---|
| الخلفية (موشن) | ورق أبيض بملمس ورق حقيقي ≈ `#FBFBF9` (ألياف، تبقيع، vignette خفيف). **أبداً مش لون سادة** |
| الـ Grid | أسود `#000000` بـ 4–7% opacity، Multiply، خانة ≈117px @1080، وخط 3–4px |
| الأحمر الأساسي | `#D82E2C`: كلام، خطوط، دواير، تمييز |
| الأحمر الفاتح | `#FA4A4A`: المساحات الكبيرة والكروت |
| الحبر | `#0A0A0A`: لوجو، labels، body |
| الصور والـ props | أبيض وأسود (B&W) عشان الأحمر يفضل اللون الوحيد. **فوتيج المنتج الحقيقي يفضل بألوانه** |
| الظلال | أسود 20–35%، ناعم (distance 8–15، softness 30–50) |
| خط إنجليزي | Helvetica (Bold + Light في نفس الكلمة للعناوين، Regular للنص) |
| خط عربي | Lyon Arabic Display (Bold + Regular) |
| الحركة | Bezier keyframes بـ ease. الافتراضي **expo-out** (out ≈12%، in ≈90%) والحركات الكبيرة **S-curve** (33/80). **ممنوع** linear أو bounce أو overshoot أو wiggle |

**قواعد اتصححت قبل كده (ما تتكررش):**
- أي كلام وهو ثابت يكون **مستوي 0°**. الميل مسموح للفولدرات والورق الفاضي بس.
- **ممنوع** كلام أو أشكال فوق صورة أو وش. الإطار الأحمر يبقى **حوالين** الصورة من بره.
- لو الكلام بيذكر حاجة عندنا صورتها، **اعرض الصورة** بدل النص.
- الـ Highlighter الأحمر يبقى **على الكلمات بالظبط ويتحرك مع الصوت** (من اليمين للشمال في العربي)، ومعاه `highlighter_N.wav`.
- لما يبقى فيه ريفرنس: **الستايل وقواعد الحركة أهم من الألوان.** نبني نفس العالم بألوان البراند.

### 2.2 لوك الاستوديو (ريلز الـ Talking-Head، المعتمد من مشروع dr eslam)
- الاسم: **Modern Warm Dark Studio**. الشخص معزول ومحطوط على clean plate للاستوديو (بالكرسي).
- مرجع الوقفة والكادر: `reference_pose`. حجم الشخص ومكان الراس لازم يطابقوا الريفرنس.
- القيم المعتمدة:
  - خلفية الاستوديو: Blur خفيف ≈ **2.5**، crop مطابق للريفرنس.
  - حواف الماسك: **Shrink 1–2px** (choke) + **Blur ≈1.2** (feather). تنعيم زمني على 3 فريمات (من غير ما يرعش).
  - **Contact shadow** تحت الشخص على الكرسي: offset ≈ (−14, +26) px، blur ≈ 28، opacity ≈ **0.45**.
  - توحيد اللون: **Warm ≈ 3000K** على الشخص عشان يطابق إضاءة الاستوديو.
  - الكرسي الدهبي في الفوتيج الأصلي **يتشال من الماسك** (subtract). المفروض يبان كرسي الـ clean plate بس.
- نسخ الخلفية المتاحة: `clean plate.png` / `classic.png` / `gold.png` / `studio_clean_plate.jfif`. اسأل مرة واحدة أنهي نسخة لو مش متحددة.

### 2.3 إعدادات المشروع والتايم لاين
| الإعداد | القيمة |
|---|---|
| Timeline Resolution | **1080 × 1920** للمونتاج. التصدير النهائي 2160 × 3840 بعد الموافقة |
| Timeline Frame Rate | **نفس الـ fps بتاع المصدر** (كاميرا DSC = 29.97، الموبايل غالباً 30). يتحدد قبل أول كليب وما يتغيرش |
| Color Science | DaVinci YRGB |
| Timeline / Output Color Space | Rec.709 Gamma 2.4 |
| Mismatched Resolution | Scale full frame with crop. **ممنوع stretch** |
| Proxy | للمصادر 4K: Proxy بنص الدقة (DNxHR LB أو H.264) |
| Safe Zones (9:16) | **فوق ~200px وتحت ~350px** فاضيين من الكلام والعناصر المهمة |

### 2.4 توزيع الـ Tracks (ثابت في كل ريل)
**فيديو (من تحت لفوق):**
| Track | الاسم | المحتوى |
|---|---|---|
| V1 | `BG_STUDIO` | الـ clean plate بتاع الاستوديو + Blur ≈2.5 |
| V2 | `SUBJECT` | الفيديو الأصلي + Magic Mask (Alpha) + contact shadow + 3000K |
| V3 | `B_ROLL` | لقطات مساعدة، close-ups للمنتج، screen recordings |
| V4 | `GFX` | عناوين، labels، أسهم، دواير، highlight (هوية Fekra) |
| V5 | `BRAND` | لوجو / CTA في الآخر |
| V6 | `ADJ` | Adjustment Clip للوك النهائي (اختياري) |

**ترجمة (Subtitle Tracks، منفصلة دايماً عن الفيديو):**
| Track | المحتوى |
|---|---|
| ST1 | `SUB_AR`: من `part_N_<topic>.srt` أو `<name>.srt` |
| ST2 | `SUB_EN`: من `<name>_en.srt` (لو مطلوب) |

**صوت:**
| Track | المحتوى |
|---|---|
| A1 | `VOICE`: الصوت الأصلي (مقفول، تحسين بس) |
| A2 | `SFX`: من الكيت / KMeGa |
| A3 | `MUSIC`: بس لو المستخدم بعت تراك مرخّص، ومعموله ducking تحت الصوت |
| A4 | `VOICE_RAW`: نسخة نضيفة من الأصلي، muted، backup |

### 2.5 الترجمة (SRT)
- النص **مطابق للكلام بالحرف**: مصري، مصطلحات إنجليزي، أسماء، أرقام، وحدات. ممنوع إعادة صياغة.
- **جملة واحدة في كل cue**، ومدته ≈ 4–6.5 ثانية، ومن غير overlap.
- الملف UTF-8. لو الفيديو فيه أكتر من موضوع، **افصله لملفات**: `part_1_<topic>.srt`، `part_2_<topic>.srt`...
- الـ Style: الخط Lyon Arabic Display (عربي) / Helvetica (إنجليزي)، أبيض بـ stroke أسود ≈2px، والكلمة المهمة بس بالأحمر `#D82E2C`.
- مكانها: lower third جوه الـ safe zone، ما تغطيش البق ولا العين ولا المنتج.
- قبل أي render كامل: **اختبار سطر** فيه عربي + إنجليزي + أرقام + علامات ترقيم، وتأكد من الاتجاه والتشكيل. **ممنوع تسليم عربي مكسور.**
- برّه DaVinci (ffmpeg): استخدم `.ass` + libass، و`fontsdir` على فولدر `fonts\` بتاع الكيت.

### 2.6 الصوت
- Voice: denoise خفيف، high-pass ≈ 90Hz، EQ هادي، de-ess، compression معتدل. **من غير** صوت معدني ولا pumping.
- الـ SFX باليت مش checklist: كل صوت مربوط بحركة أو كلمة، والـ hit الفعلي على الحدث (مش بداية الملف). نوّع النسخ (`highlighter_1..5`). ممنوع whoosh على كل cut.
- مرجع الكثافة والمستويات: `sfx\Sound Design - Sequence.xml` و`Preview - Sound Design.mp4`.
- Loudness: **≈ −16 LUFS integrated / −1.5 dBTP** كنقطة بداية (−14 مقبول لإنستجرام). الودن أهم من الرقم.

---

## 3. خطوات التنفيذ بالتفصيل

### المرحلة 1: الاستلام والجرد
1. `ffprobe` لكل ملف، واعمل جدول صغير: المسار، المدة، الدقة، الـ fps، الصوت، والدور (main / B-roll / plate / logo).
2. دوّر على `.srt` و`.words.json` و drafts قديمة. **لو موجودة استخدمها.**
3. لو فيه حاجة واحدة ناقصة وبتوقف الشغل، اسأل **سؤال واحد**. غير كده خد قرار ينفع يترجع فيه وكمّل.

### المرحلة 2: التفريغ والسكريبت
4. مافيش SRT؟ `python scripts\transcribe.py "<folder>"` (بيشغّل `transcribe.bat`: عربي، large-v3 على GPU أو medium على CPU) وهيطلع `.srt` + `.words.json`.
5. `python scripts\gemini_fix.py "<folder>"`: Gemini Pro يصحح الغلط في السمع بس (نص، من غير صوت). النتيجة في `.fixed.srt`، والأصل بتاع Whisper ما يتلمسش. ما تعيدش صياغة.
6. قسّم لجمل، كل جملة في cue، ولو فيه أكتر من موضوع افصل لـ `part_N_<topic>.srt`.
7. لو مطلوب إنجليزي: `<name>_en.srt` بنفس التوقيتات بالظبط.

### المرحلة 3: إعداد DaVinci
8. مشروع جديد بإعدادات 2.3، والـ fps = المصدر.
9. اعمل الـ Tracks بالأسامي والترتيب اللي في 2.4.
10. V1 = الـ clean plate (Zoom/Position يطابق الريفرنس + Blur ≈2.5). V2 = الفيديو الأصلي (Scale بحيث الراس والحجم يطابقوا `reference_pose`).
11. استورد الـ SRT على ST1/ST2 (File › Import › Subtitle).

### المرحلة 4: Magic Mask وعزل الشخص (صفحة Color)
12. على كليب V2: Node `MASK_PERSON` › Magic Mask › **Person** › Quality: **Better**.
13. ارسم stroke على الشخص، و**subtract stroke على الكرسي الدهبي**، واعمل Track ↔ (الاتجاهين).
14. Matte Finesse: **Shrink 1–2px**، **Blur ≈1.2**، Clean Black/White خفيف. اتأكد من الشعر والإيدين ومافيش رعشة.
15. وصّل الماسك لـ **Alpha Output** عشان V1 يبان من وراه.
16. Contact shadow (صفحة Fusion على V2): Shadow على الـ alpha، offset ≈ (−14, +26)، softness ≈ 28، opacity ≈ 0.45.

### المرحلة 5: الألوان (Node Tree ثابت)
| Node | الاسم | الشغل |
|---|---|---|
| 01 | `BALANCE` | White balance + exposure |
| 02 | `CONTRAST` | contrast و saturation معتدلين |
| 03 | `SKIN` | حماية لون البشرة الطبيعي |
| 04 | `MASK_PERSON` | Magic Mask ← Alpha Output |
| 05 | `WARM_3000K` | دفا ≈3000K يطابق إضاءة الاستوديو |
| 06 | `LOOK` | لمسة نهائية خفيفة (ممنوع over-saturation و sharpening) |
- الخلفية (V1): Node واحد يطابق تعريضها ولونها مع الشخص.
- المنتجات تفضل بألوانها الحقيقية.

### المرحلة 6: الجرافيكس والموشن
17. خطة قصيرة لكل لحظة مهمة: الوقت، الكلام، الهدف، المعالجة، والسبب. **باقي الفيديو يفضل نضيف.**
18. معالجة واحدة لكل beat (punch-in، label، سهم، دايرة حمرا، PiP، close-up). أقصى 3–4 عناصر جديدة في كل beat.
19. Labels من 1–3 كلمات، و body ≤ 8 كلمات، والعناوين Bold + Light.
20. الموشن الكبير يتبني في AE بـ `motion_kit.jsx` (keyframes حقيقية قابلة للتعديل، وكل layer باسمه). في DaVinci: Fusion / Text+ بنفس الـ eases.
21. الانتقالات: Hard cut في الكلام. Punch-in / match cut بس لما يبقى ليها سبب.

### المرحلة 7: الصوت (Fairlight)
22. A1: سلسلة تنضيف الصوت (2.6) من غير ما الطول أو التزامن يتغيروا.
23. A2: SFX متربطة بالأحداث، مستواها تحت الكلام. A3: موسيقى + ducking.
24. اقيس الـ loudness (`ebur128`) وظبط على −16 LUFS / −1.5 dBTP.

### المرحلة 8: الـ QC (مرة واحدة منظمة)
- **القصة:** الـ hook صادق، كل إضافة ليها لازمة، ومافيش حاجة اتنقلت من مكانها.
- **الصوت:** كل الكلمات والوقفات والتزامن سليمين. مافيش clipping ولا pumping ولا clicks.
- **الماسك:** حواف نضيفة، مافيش رعشة، الكرسي الدهبي مختفي، والظل مقنع.
- **الترجمة:** مطابقة للكلام، عربي سليم، جوه الـ safe zone، ومتزامنة.
- **الموشن:** ألوان البراند بس، الـ graph ناعم، الكلام مستوي، ومافيش حاجة فوق صورة.
- **التصدير:** المدة، الأبعاد، الـ fps، الـ codecs، الـ streams، وdecode كامل. Contact sheet للبداية والنهاية وكل انتقال.
- قول بوضوح إيه اللي اتراجع فعلاً وإيه اللي ما اتراجعش.

### المرحلة 9: التصدير والتسليم
25. Draft: `draft_720p_30fps.mp4`، وبعدين **وقف واستنى الموافقة.**
26. Final بعد الموافقة: `edited_video_4k_30fps.mp4` (H.264 High، yuv420p، CRF 16–19، AAC 48k، `+faststart`). الترجمة ترندر جوه الفيديو أو تتصدر `.srt` منفصل حسب الطلب.
27. `edit_report.txt` + `edit_timeline.json` في `export\`، ورسالة من 3 سطور بالمصري.

---

## 4. قرار أخير
بين effect مبهرج ومونتاج أوضح وأشيك، **اختار الأوضح.** استخدم أقوى effect الأدوات تقدر تنفذه بنضافة، مش أكبر عدد من الـ effects. واتأكد من الملف النهائي بنفسك وقول الحدود بصراحة.
