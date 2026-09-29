# AI Commerce & Creative Studio

## Project Overview
An independent portfolio prototype combining a fictional AURA LIVING storefront, Shopify-style commerce practice, AI-assisted creative workflows and a professional creative portfolio. Other named brands are fictional/demo projects. No client relationship, professional outcomes, sales or conversion results are claimed.

## Features
- Responsive storefront, product pages, collections, search, filtering, sorting, variants, wishlist and cart.
- Cart → demo checkout → order confirmation → SQLite order record. No payment is taken.
- Campaign manager, local design library, editable poster canvas, export and campaign attachment.
- SQLite demo commerce APIs, Shopify Liquid theme practice, optional server-side Shopify Admin GraphQL product read, optional AI connections, demo-mode fallback, simulated insights and local automation history.
- Professional creative portfolio with category filters, case studies and reusable process/expertise sections.

## Professional Portfolio
All concepts below are fictional independent practice: [AURA LIVING](static/case-studies/aura-living.html), [NOVA TECH](static/case-studies/nova-tech.html), [VELORA](static/case-studies/velora.html), [ORBIT FITNESS](static/case-studies/orbit-fitness.html), [NORTHLINE](static/case-studies/northline.html), and [AI Creative Campaign Studio](static/case-studies/ai-creative-campaign-studio.html).

## Case Studies
- **AURA LIVING:** fictional commerce storefront and seasonal campaign.
- **NOVA TECH:** fictional connected-audio product launch; wordmark, product hero, product ad, Instagram post/story, Facebook and Google ads, email banner, video thumbnail, launch poster and feature graphic.
- **VELORA:** fictional premium lifestyle identity, visual direction, product presentation, social, web, advertising and email placements.
- **ORBIT FITNESS:** fictional fitness/wellness product campaign, product ads, social, banner, email and landing-page concept.
- **NORTHLINE:** fictional architecture studio identity, wordmark, type, business card, social profile, web header, ad, presentation and email signature.
- **AI Creative Campaign Studio:** brief → audience → product → platform → direction → prompt → draft → refinement → copy → variations.

## Creative Process
Brief → research → concept → design → adapt → deliver. Each case study describes audience, direction, process, campaign assets and limitations.

## Shopify Architecture
`shopify-theme/` contains Liquid layout, JSON templates, product/collection/cart sections and responsive theme assets. The product section uses Shopify’s native product form and updates variant price, availability and image. These are theme-conversion practice files, not a deployed theme. The local checkout is a simulation, not live Shopify checkout.

`shopify_admin.py` provides an optional server-side Admin GraphQL adapter using Shopify’s client-credentials grant for a store in the owner’s Shopify organization. It reads products only; it does not access orders or customer data. A public multi-merchant app would need OAuth and a proper installation flow. No Shopify store is connected in the current deployment.

## AI Workflow
The local Creative Studio creates draft product description, ad headline, social caption, CTA, SEO description, image prompt and creative variations. Deterministic output is labeled demo mode; server-side provider calls require valid credentials. Placeholder photography in portfolio SVGs is Unsplash imagery and is not described as generated.

## API Architecture
Flask serves the single-page storefront and JSON routes. The existing `/api/shopify/*` routes remain SQLite simulations. `/api/shopify/live/*` uses a real Admin GraphQL adapter only when server-side Shopify credentials are configured.

| Method | Route | Purpose |
|---|---|---|
| GET | `/api/shopify/live/status` | Report whether the optional live adapter is configured |
| GET | `/api/shopify/live/products` | Read storefront-safe product fields from Shopify Admin GraphQL |
| GET | `/api/shopify/products` | Search/filter/sort demo products |
| GET | `/api/shopify/collections` | List derived product categories |
| POST | `/api/shopify/orders` | Validate stock and save a simulated order |
| GET | `/api/shopify/orders` | List local demo orders |
| GET | `/api/shopify/inventory` | Read local stock |
| POST | `/api/creative/generate` | Generate copy/prompt; optional provider connection |
| POST | `/api/creative/image` | Optional image provider; unavailable without credentials |
| GET / POST | `/api/campaigns` | List/create/update campaigns |
| GET / POST | `/api/designs` | Read/save editable poster layouts |
| GET | `/api/analytics` | Local orders plus simulated metrics |
| POST | `/api/automations/run` | Record a local demo workflow step |
| GET | `/api/automations/history` | Read local workflow history |
| POST | `/api/contact` | Save a local-only contact note; sends no email |

## Database
SQLite stores seeded demo products, simulated orders, campaigns and attached creative IDs, designs, automation history and contact messages. Order creation and stock decrement occur in one database transaction. Checkout smoke tests should use a temporary database; local order totals are demo-only.

## Tech Stack
HTML · CSS · JavaScript · Python · Flask · SQLite · Shopify Liquid · REST-style APIs · optional OpenAI API · Docker.

## Installation
### Windows PowerShell

```powershell
cd path\to\ai-commerce-creative-studio
.\run.ps1
```

Or manually: `py -m venv .venv`, `.\.venv\Scripts\Activate.ps1`, `python -m pip install -r requirements.txt`, `Copy-Item .env.example .env`, then `python app.py`. Open <http://127.0.0.1:5000>.

### macOS / Linux

```bash
cd path/to/ai-commerce-creative-studio
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python app.py
```

Open <http://127.0.0.1:5000>. Python 3.10 or later is recommended.

## Public Portfolio Deployment

The project includes a Render Blueprint at `render.yaml` for a free Flask web service. Follow [DEPLOYMENT.md](DEPLOYMENT.md) to publish it from GitHub. The free service can sleep while idle and has temporary filesystem storage, so local SQLite demo data may reset after a restart or redeploy. This is a portfolio demo, not a production store. Persistent SQLite storage requires paid hosting; check current pricing before enabling it.

## Environment Variables
See `.env.example`. Provider and Shopify credentials are optional and must remain server-side. Without Shopify credentials, the live adapter remains disconnected and reports that status.

## Demo Mode
No payment is processed, no live Shopify order is created, campaign automations remain local, and analytics are simulated. Checkout confirmation explicitly says no payment was taken.

## Tests
There is no checked-in automated test suite. The revision smoke check covers server startup, storefront/product detail, collection filtering, add-to-cart, demo checkout and the SQLite order row.

## Screenshots
- Storefront: `static/screenshots/storefront.jpg`
- Creative Studio: `static/screenshots/creative-studio.jpg`
- Poster editor: `static/screenshots/poster-editor.jpg`

## Limitations
No live Shopify deployment, payment processing, publishing integration, connected Figma/Adobe workflow, or verified business metrics. Brand art is independent practice. Current campaign photography is licensed Unsplash imagery, not generated AI imagery. Optional AI image routes require a provider key; demo mode returns a prompt and does not fabricate images.

## Future Improvements
Connect an authenticated development-store adapter, add automated integration coverage and accessibility/performance review, and use owned/cleared campaign photography.
