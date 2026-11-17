<div dir="rtl">

# אתר גלריה לצימר

אתר של עמוד אחד: שם הצימר, גלריית תמונות גדולה ופרטי יצירת קשר (טלפון ווואטסאפ).
את כל הניהול השוטף עושים מתוך האתר עצמו, גם מהטלפון, בכתובת ‎`/admin`‎: מעלים תמונות, מוחקים, משנים סדר, כותבים כיתובים ומעדכנים את שם הצימר ואת מספרי הטלפון.

ההגדרה הראשונית נעשית **פעם אחת בלבד**, בלוח הבקרה של Cloudflare, לפי השלבים שבהמשך. אחריה אין צורך לגעת יותר ב-Cloudflare או בקוד.

---

## מה יש כאן, בקצרה

| רכיב | מה הוא עושה |
|---|---|
| Cloudflare Worker אחד בשם `zimmer-gallery` | מגיש את האתר, את דף הניהול ואת התמונות |
| דלי R2 אחד בשם `zimmer-gallery-photos` | שומר את כל התמונות וקובץ אחד, `site.json`, עם הסדר, הכיתובים והטקסטים |
| Secret אחד בשם `ADMIN_TOKEN` | קוד הגישה לדף הניהול |
| Workers Builds | כל שינוי שנכנס לענף `main` ב-GitHub עולה לאוויר לבד, תוך דקה-שתיים |

אין מסד נתונים, אין שירותים חיצוניים ואין שלב בנייה. הכול רץ על התוכנית החינמית של Cloudflare.

---

## הגדרה ראשונית (פעם אחת)

> **לפני שמתחילים:** צריך חשבון GitHub שבו נמצא המאגר הזה, וחשבון Cloudflare (ההרשמה ב-<span dir="ltr">dash.cloudflare.com/sign-up</span> חינמית).
>
> **שימו לב:** שמות הכפתורים בלוח הבקרה של Cloudflare מופיעים כאן באנגלית, בדיוק כפי שהם מופיעים במסך. Cloudflare משנה מדי פעם את עיצוב לוח הבקרה, כך שייתכן שכפתור יופיע במקום מעט אחר או בשם מעט שונה. המונחים החשובים (Workers & Pages,‏ R2,‏ Variables and Secrets) נשארים זהים.

### שלב 1: יצירת דלי התמונות (R2)

1. נכנסים אל <span dir="ltr">https://dash.cloudflare.com</span> ומתחברים.
2. בתפריט הצד בוחרים **<span dir="ltr">R2 Object Storage</span>** (לפעמים מופיע תחת **Storage & Databases**).
3. אם זו הפעם הראשונה שמשתמשים ב-R2, Cloudflare תבקש להפעיל אותו. לוחצים על כפתור ההפעלה ומאשרים. ייתכן שתתבקשו להזין אמצעי תשלום: זה תנאי של Cloudflare להפעלת R2, אבל אתר בגודל הזה (עד 50 תמונות) נשאר בתוך המכסה החינמית של R2 ולא אמור להיות מחויב.
4. לוחצים **<span dir="ltr">Create bucket</span>**.
5. ממלאים:

| שדה | ערך |
|---|---|
| <span dir="ltr">Bucket name</span> | <span dir="ltr">`zimmer-gallery-photos`</span> (בדיוק כך, באותיות קטנות ועם המקפים) |
| <span dir="ltr">Location</span> | <span dir="ltr">Automatic</span> (ברירת המחדל) |
| <span dir="ltr">Default Storage Class</span> | <span dir="ltr">Standard</span> (ברירת המחדל) |

6. לוחצים **<span dir="ltr">Create bucket</span>**. זהו, אין צורך לשנות שום הגדרה נוספת בדלי. **אין** להפעיל בו גישה ציבורית (<span dir="ltr">Public access</span>): התמונות מוגשות דרך ה-Worker.

> אם תדלגו על השלב הזה, ה-Worker ינסה ליצור את הדלי בעצמו בפריסה הראשונה. זה עובד רק אם R2 כבר הופעל בחשבון, ולכן עדיף ליצור אותו ידנית כמו שמתואר כאן.

### שלב 2: חיבור המאגר מ-GitHub ופריסה אוטומטית (Workers Builds)

1. בתפריט הצד בוחרים **<span dir="ltr">Workers & Pages</span>** (לפעמים תחת **Compute**).
2. לוחצים **<span dir="ltr">Create application</span>** (או **Create**).
3. בוחרים **<span dir="ltr">Import a repository</span>** (ייתכן שיופיע כ-<span dir="ltr">Continue with GitHub</span>).
4. אם החשבון עוד לא מחובר ל-GitHub: לוחצים **<span dir="ltr">Connect GitHub</span>**, מתחברים ל-GitHub, ומאשרים את ההתקנה של האפליקציה של Cloudflare. אפשר לתת לה גישה רק למאגר הזה (<span dir="ltr">Only select repositories</span>, ואז בוחרים את המאגר).
5. ברשימת המאגרים בוחרים את המאגר הזה ולוחצים **<span dir="ltr">Next</span>** (או **Begin setup**).
6. במסך ההגדרות ממלאים:

| שדה | ערך |
|---|---|
| <span dir="ltr">Project name</span> | <span dir="ltr">`zimmer-gallery`</span> (חייב להיות זהה לשם שבקובץ `wrangler.jsonc`) |
| <span dir="ltr">Production branch</span> (אם מופיע) | <span dir="ltr">`main`</span> |
| <span dir="ltr">Build command</span> | משאירים **ריק** |
| <span dir="ltr">Deploy command</span> | <span dir="ltr">`npx wrangler deploy`</span> (בדרך כלל כבר ממולא כך) |
| <span dir="ltr">Non-production branch deploy command</span> (תחת Advanced settings, אם מופיע) | <span dir="ltr">`npx wrangler versions upload`</span> (ברירת המחדל, לא משנים) |
| <span dir="ltr">Path</span> / <span dir="ltr">Root directory</span> (תחת Advanced settings) | <span dir="ltr">`/`</span> (ברירת המחדל, לא משנים) |
| <span dir="ltr">API token</span> | משאירים את האפשרות ליצור טוקן חדש אוטומטית (ברירת המחדל) |
| <span dir="ltr">Variables</span> / <span dir="ltr">Build variables</span> | **לא מוסיפים כלום** |

7. לוחצים **<span dir="ltr">Deploy</span>** (או **Save and Deploy**). הבנייה הראשונה לוקחת דקה-שתיים. אפשר לעקוב אחריה במסך שנפתח.
8. בסיום תופיע כתובת האתר, בצורה <span dir="ltr">`https://zimmer-gallery.<השם-שלכם>.workers.dev`</span>. אם זו הפעם הראשונה שאתם משתמשים ב-Workers, Cloudflare עשויה לבקש לבחור את <span dir="ltr">`<השם-שלכם>`</span> (תת-הדומיין של <span dir="ltr">workers.dev</span>); בוחרים שם קצר באנגלית.

עכשיו האתר באוויר. נכנסים לכתובת ורואים את שם הצימר הזמני ("שם הצימר") ושורה שאומרת שהתמונות יעלו בקרוב. דף הניהול (<span dir="ltr">`/admin`</span>) יציג הודעה שקוד הגישה עדיין לא הוגדר. זה תקין: מגדירים אותו בשלב הבא.

### שלב 3: הגדרת קוד הגישה (ADMIN_TOKEN)

קוד הגישה הוא הסיסמה לדף הניהול. בוחרים קוד ארוך שקשה לנחש:

- לפחות 24 תווים. אפשר לשלב כמה מילים אקראיות באנגלית עם ספרות, למשל בסגנון <span dir="ltr">`olive-river-7-candle-north-42`</span> (אל תשתמשו בדוגמה הזו עצמה).
- או לתת למנהל הסיסמאות של הטלפון או הדפדפן לייצר סיסמה ארוכה.
- שומרים את הקוד במקום בטוח (מנהל סיסמאות). תצטרכו להקליד אותו בכל טלפון או מחשב שממנו תנהלו את האתר, פעם ב-30 יום לכל היותר.

איך מגדירים:

1. בלוח הבקרה של Cloudflare: **<span dir="ltr">Workers & Pages</span>** ← לוחצים על **<span dir="ltr">zimmer-gallery</span>**.
2. עוברים ללשונית **<span dir="ltr">Settings</span>**.
3. באזור **<span dir="ltr">Variables and Secrets</span>** לוחצים **<span dir="ltr">+ Add</span>**.
4. ממלאים:

| שדה | ערך |
|---|---|
| <span dir="ltr">Type</span> | <span dir="ltr">Secret</span> (חשוב: לא <span dir="ltr">Text</span>) |
| <span dir="ltr">Variable name</span> | <span dir="ltr">`ADMIN_TOKEN`</span> (בדיוק כך, באותיות גדולות ועם קו תחתון) |
| <span dir="ltr">Value</span> | קוד הגישה שבחרתם |

5. לוחצים **<span dir="ltr">Deploy</span>** (הכפתור שומר את ה-Secret ומפעיל אותו). אחרי כחצי דקה נכנסים ל-<span dir="ltr">`/admin`</span>, מרעננים, ומתחברים עם הקוד.

ה-Secret נשמר ב-Cloudflare ולא בקוד. פריסות עתידיות (כל דחיפה ל-`main`) לא מוחקות ולא משנות אותו, כך שאין צורך להגדיר אותו שוב.

### שלב 4 (רשות): דומיין משלכם

אם יש לכם דומיין שמנוהל ב-Cloudflare: **<span dir="ltr">Workers & Pages</span>** ← **<span dir="ltr">zimmer-gallery</span>** ← **<span dir="ltr">Settings</span>** ← **<span dir="ltr">Domains & Routes</span>** ← **<span dir="ltr">+ Add</span>** ← **<span dir="ltr">Custom domain</span>**, ומקלידים את הדומיין (למשל <span dir="ltr">`www.example.co.il`</span>). Cloudflare מגדירה את השאר לבד.

---

## שימוש יומיומי (מהטלפון)

נכנסים ל-<span dir="ltr">`https://<כתובת-האתר>/admin`</span> ומתחברים עם קוד הגישה. ההתחברות נשמרת 30 יום באותו דפדפן.

| רוצים ל... | עושים כך |
|---|---|
| להוסיף תמונות | לוחצים **הוספת תמונות** ובוחרים כמה תמונות יחד מגלריית הטלפון. במחשב אפשר גם לגרור קבצים לדף. לכל תמונה מופיע פס התקדמות משלה. |
| לשנות סדר | גוררים את שני הפסים שבצד התמונה, או לוחצים **למעלה** / **למטה**. הסדר נשמר לבד. התמונה הראשונה מוצגת בגדול בראש האתר, ולכן כדאי שתהיה צילום לרוחב. |
| להוסיף כיתוב | כותבים בשדה שליד התמונה. הכיתוב נשמר כשיוצאים מהשדה או לוחצים אישור במקלדת. אפשר להשאיר ריק. |
| למחוק תמונה | לוחצים **מחיקה**, ואז שוב על **למחוק?** כדי לאשר. המחיקה סופית. |
| לעדכן שם, שורת משנה או טלפון | ממלאים בטופס **פרטי הצימר** ולוחצים **שמירת הפרטים**. השינוי מופיע באתר מיד. אם משאירים את שדה הוואטסאפ ריק, כפתור הוואטסאפ ישתמש במספר הטלפון. |

פרטים שכדאי לדעת:

- עד 50 תמונות. כל תמונה עד 30MB, בפורמט JPEG,‏ PNG או WebP.
- **התמונה המקורית נשמרת כמו שהיא**, בלי הקטנה ובלי דחיסה. בזמן ההעלאה הדפדפן מכין עוד שתי גרסאות WebP (ברוחב 800 ו-2000 פיקסלים) שמוצגות באתר כדי שייטען מהר. בתצוגה המוגדלת מוצגת הגרסה הגדולה.
- באייפון: בוחרים תמונות דרך כפתור **הוספת תמונות**, והאייפון ממיר אותן ל-JPEG לבד. קובצי HEIC שהועברו בדרך אחרת לא נתמכים, והדף יסביר מה לעשות.
- כדאי להשאיר את הדף פתוח עד שכל ההעלאות מסתיימות.

### החלפת קוד הגישה

חוזרים לשלב 3, ובאזור **<span dir="ltr">Variables and Secrets</span>** עורכים את <span dir="ltr">`ADMIN_TOKEN`</span> (סמל העריכה או <span dir="ltr">Edit</span>), מזינים קוד חדש ולוחצים **<span dir="ltr">Deploy</span>**. כל ההתחברויות הקיימות מתנתקות מיד, בכל המכשירים.

### אם משהו לא עובד

| מה רואים | מה עושים |
|---|---|
| בדף הניהול: "קוד הגישה עדיין לא הוגדר" | ה-Secret לא הוגדר, או שהשם שלו לא בדיוק <span dir="ltr">`ADMIN_TOKEN`</span>. חוזרים לשלב 3. |
| "יותר מדי ניסיונות כושלים" | אחרי 5 ניסיונות שגויים הכניסה נחסמת ל-15 דקות מאותה כתובת. מחכים ומנסים שוב. |
| "פג תוקף ההתחברות" | עברו 30 יום או שקוד הגישה הוחלף. מתחברים שוב. |
| הבנייה ב-Cloudflare נכשלת עם שגיאה על R2 או על <span dir="ltr">bucket</span> | בודקים שהדלי קיים ושהשם שלו בדיוק <span dir="ltr">`zimmer-gallery-photos`</span> (שלב 1). אחר כך ב-<span dir="ltr">Workers & Pages</span> ← <span dir="ltr">zimmer-gallery</span> ← <span dir="ltr">Deployments</span> (או <span dir="ltr">Builds</span>) לוחצים על הבנייה האחרונה ← <span dir="ltr">Retry build</span>. |
| רוצים לראות שגיאות מהשרת | <span dir="ltr">Workers & Pages</span> ← <span dir="ltr">zimmer-gallery</span> ← <span dir="ltr">Observability</span> (או <span dir="ltr">Logs</span>). |

---

## למפתחים

<div dir="ltr">

| Path | Purpose |
|---|---|
| `wrangler.jsonc` | Worker config: static assets (`public/`), R2 binding `BUCKET` → `zimmer-gallery-photos`. Validated against the schema bundled with wrangler 4.164. |
| `src/worker.js` | Routing, server-rendered home page, JSON API, auth, image serving. |
| `public/` | Static assets: `site.css`, `site.js`, fonts, `admin/` (admin page, its CSS/JS and the vendored libwebp encoder). `_headers` sets CSP and caching for static files. |

**Local development**

```sh
npm install
echo 'ADMIN_TOKEN="dev-token-change-me-0123456789"' > .dev.vars   # optional; omit to see the "not configured" state
npx wrangler dev
```

Local R2 data lives in `.wrangler/state` (git-ignored).

**API** (all writes need the session cookie and a same-origin request)

| Method | Path | Notes |
|---|---|---|
| GET | `/api/session` | `{configured, authenticated}` |
| GET | `/api/site` | current `site.json` |
| POST | `/api/login` | `{token}`; constant-time compare; 5 failures per 15 min per IP → 15 min lock (counter in R2 under `_system/`) |
| POST | `/api/logout` | clears the cookie |
| PUT | `/api/photos/:id/(original\|w800\|w2000)` | raw body streamed to R2 untouched; type checked by header and magic bytes; 30 MB cap |
| POST | `/api/photos` | commit an uploaded photo to `site.json` (checks all three objects exist; 50-photo cap) |
| PATCH / DELETE | `/api/photos/:id` | caption / delete |
| PUT | `/api/order` | `{ids}` must be a permutation of the current photos |
| PUT | `/api/texts` | name, subtitle, phone, whatsapp |
| GET | `/img/:id/:file` | `Cache-Control: public, max-age=31536000, immutable`, ETag, 304 on `If-None-Match` |

`site.json` writes use an R2 etag precondition with retries, so concurrent saves never overwrite each other.

Session cookie: `__Host-zimmer_session`, value `exp.HMAC-SHA256(exp)` keyed from `ADMIN_TOKEN`, `HttpOnly; Secure; SameSite=Strict`, 30 days. Rotating the token invalidates every session.

Fonts: Assistant and Bellefair (SIL OFL, licences in `public/fonts/`). WebP encoder: libwebp via `@jsquash/webp` 1.5.0 (Apache-2.0, `public/admin/vendor/webp/LICENSE.txt`), loaded only in browsers that cannot encode WebP on a canvas (Safari).

</div>
</div>
