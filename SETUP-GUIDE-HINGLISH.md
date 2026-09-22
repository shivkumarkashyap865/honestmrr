# 🛠️ Setup Guide (Hinglish) — Zero Coding, Zero Paisa

Site already bani hui hai is folder me. Ab bas live karni hai. Total time: ~45 minutes.

## Step 1: GitHub account (free)

1. [github.com](https://github.com) par jao → Sign up (agar account nahi hai)
2. Verify karo email

## Step 2: Repo banao aur files upload karo

1. GitHub par **New repository** click karo
2. Name: `honestmrr` → Public → **Create repository**
3. "uploading an existing file" link par click karo
4. Is folder ki **saari files drag karke daalo** (`build.py`, `data/`, `.github/` — `site/` bhi daal sakte ho, koi dikkat nahi)
   - ⚠️ `.github` folder hidden hota hai — upload karna mat bhoolna (isi se auto-deploy hota hai)
5. **Commit changes** click karo

## Step 3: GitHub Pages on karo

1. Repo me **Settings** → left menu me **Pages**
2. "Build and deployment" → Source: **GitHub Actions** select karo
3. Bas. Repo me **Actions** tab kholo — "Build & Deploy Site" workflow chalega (~1 minute)
4. Green ✓ hone ke baad aapki site live hai:
   **`https://YOUR-USERNAME.github.io/honestmrr/`** 🎉

## Step 4: Google Sheet se data control karo (no-code database!)

Ab se listings add karne ke liye coding ki zaroorat nahi:

1. [sheets.google.com](https://sheets.google.com) → naya sheet banao, naam: `HonestMRR Data`
2. Pehli row me ye exact headers daalo (copy from `data/startups.csv` — usko Notepad me kholke headers copy kar lo):
   `name,slug,website,category,city,description,mrr_usd,growth_pct,for_sale,asking_price_usd,verification,source_url,submitted_date`
3. Sheet me rows daalo (ya CSV ka data paste kar do)
4. **File → Share → Publish to web** → Sheet select karo → format: **Comma-separated values (.csv)** → Publish
5. Jo link mile (`docs.google.com/spreadsheets/d/e/...`) usko copy karo
6. GitHub repo → **Settings → Secrets and variables → Actions → Variables** tab → **New repository variable**:
   - Name: `SHEET_CSV_URL`
   - Value: wo copied link
7. Done! Ab **roz subah 7:30 IST site automatically Sheet se data kheench kar update ho jayegi.**
   (Turant update chahiye to Actions tab → workflow → "Run workflow" click karo)

**Slug kya hota hai?** URL ka naam — `Zoho` ka slug `zoho`, `My Cool App` ka slug `my-cool-app` (lowercase, spaces ki jagah dash).

## Step 5: Submission form (founders apne aap listing bhejenge)

1. [tally.so](https://tally.so) (free) ya Google Forms par form banao:
   - Startup name, Website, Category, City, Description
   - Monthly revenue (USD), Growth %, For sale? Asking price?
   - **Revenue proof upload** (screenshot/export) — ye zaroori field hai
   - Founder email/X handle
2. Form ka link `data/config.json` ke `submit_form_url` me daalo (Sheet wale flow me `config.json` repo me hi rehta hai — GitHub par edit kar sakte ho directly, pencil icon)
3. Responses Google Sheet me connect karo → aap review karke approved rows main data sheet me daalo

## Step 6: Google Search Console (SEO ke liye zaroori)

1. [search.google.com/search-console](https://search.google.com/search-console) → property add karo (URL prefix wala option) → HTML tag verification
2. Meta tag ko site me daalna padega — GitHub par `site/index.html` edit karke `<head>` me paste kar do (ya mujhe bolo, main build me add kar dunga)
3. Sitemaps section me `sitemap.xml` submit karo
4. Free analytics: [cloudflare.com/web-analytics](https://www.cloudflare.com/web-analytics/) ya [plausible.io](https://plausible.io) (trial)

## Step 7 (baad me, jab traffic aaye): Custom domain

1. Hostinger/GoDaddy/Namecheap se `honestmrr.in` kharido (~₹700-900/saal)
2. GitHub Pages → Settings → Pages → Custom domain → domain daalo
3. DNS settings domain provider me add karo (GitHub instructions dega)
4. `data/config.json` me `site_url` update karo → rebuild (Actions → Run workflow)

---

## Roz ka routine (site chalane ke liye)

- **Data add karna** = sirf Google Sheet me row daalna. Kuch aur nahi.
- **Design change** = mujhe yahan chat me bolna ("header ka color badal do") — main build.py update kar dunga
- **Demo rows hatana** = Sheet me se `DemoInvoice`, `DemoNotes`, `DemoFit` wali rows delete kar do launch se pehle

## Files ka map

```
honestmrr/
├── build.py                  ← Site generator (isko chhedna nahi, mujhe bolna)
├── data/
│   ├── startups.csv          ← Seed data (Sheet setup ke baad Sheet hi source of truth hai)
│   └── config.json           ← Naam, links, form URL (GitHub par directly edit kar sakte ho)
├── site/                     ← Generated website (deploy yahi hoti hai)
└── .github/workflows/
    └── deploy.yml            ← Roz auto-update + deploy (GitHub Actions)
```
