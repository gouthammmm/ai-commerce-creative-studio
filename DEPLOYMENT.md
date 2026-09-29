# Publish the portfolio demo on Render

This project is prepared for a free Render web service. It runs the Flask app with Gunicorn and checks `/api/health` after deployment.

## Publish

1. Create a GitHub repository for this project. Upload the **contents** of this folder so `render.yaml`, `app.py`, and `requirements.txt` are at the repository root.
2. Keep `.env`, `.venv`, `studio.db`, and personal credentials out of GitHub. The included `.gitignore` excludes these local files.
3. Sign in to Render and create a **Blueprint** from that GitHub repository. Render reads `render.yaml`; review the service and choose **Apply** to deploy it.
4. When deployment finishes, open the `onrender.com` address shown in the Render dashboard. Check that `/api/health` returns JSON with `"ok": true`.
5. Share the public service URL as the portfolio link.

## Free service notes

- Render's free web service can spin down after 15 minutes without requests, so the first visit after idle time may take longer to load.
- The free instance has an ephemeral filesystem. SQLite data such as demo orders, saved designs, and campaign edits may reset when the service restarts or redeploys. Do not collect real customer information or use this demo for real orders.
- No payment is taken and no emails or campaigns are sent by this project. The optional AI API key is not needed for demo mode. If you later configure one, add it as a secret environment variable in Render; never commit it to GitHub.
- Persistent SQLite storage requires a paid Render web service with a persistent disk. Check current pricing before enabling paid hosting.

## After deployment

Open the portfolio, test the storefront and case-study links, and confirm the health endpoint. Add the Render URL to your CV or applications only after you have reviewed the public page yourself.

Render references: [Blueprints](https://render.com/docs/blueprint-spec), [free services](https://render.com/docs/free), [persistent disks](https://render.com/docs/disks).
