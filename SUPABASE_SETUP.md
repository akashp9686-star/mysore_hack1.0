# Google Login with Supabase

The frontend is wired for Supabase Auth + Google OAuth. The browser uses only the Supabase project URL and publishable/anon key. Never put a Supabase service-role key in the frontend.

## 1. Create/configure Supabase Auth

In Supabase Dashboard:

1. Create or open your project.
2. Go to Authentication → Providers → Google.
3. Enable Google.
4. Create a Google OAuth Web client in Google Cloud and add the application's localhost origin.
5. Add the Supabase callback URL shown by the Google provider configuration.
6. In Authentication → URL Configuration, add your local site URL, for example:
   `http://localhost:8000`
   and allow the redirect URL used by this app:
   `http://localhost:8000/path.html`

Supabase's current browser flow uses `supabase.auth.signInWithOAuth({ provider: 'google', options: { redirectTo } })`.

## 2. Configure the project

Open:

`frontend/supabase-config.js`

Replace:

```js
window.SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL";
window.SUPABASE_PUBLISHABLE_KEY = "YOUR_SUPABASE_PUBLISHABLE_OR_ANON_KEY";
```

with your project's public URL and publishable/anon key.

Do not use a service-role key here.

## 3. Run through FastAPI

Do not open the HTML files directly with `file://`.

Run:

```powershell
uvicorn backend.main:app --reload
```

Then open:

`http://localhost:8000`

The Google button will redirect to Google when Supabase is configured. If it is not configured, the demo login still lets the hackathon MVP run locally.

## 4. Learning-profile mapping

For the MVP, the selected learner profile maps to the existing Class 8 Mathematics demo learner (`student_id=101`) so the real adaptive-learning loop remains connected to the existing database.

The broader categories are intentionally profile-selection UI only until corresponding backend content exists; the contract says not to invent fake functionality.
