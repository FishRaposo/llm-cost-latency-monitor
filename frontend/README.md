# LLM Monitor — Dashboard

A polished Next.js dashboard for the **LLM Cost & Latency Monitor** FastAPI
backend. It surfaces token usage, cost, latency percentiles, error rates, daily
reports, model/prompt-version breakdowns, and budget alerts — and ships with a
**demo mode** so the whole UI is explorable with no backend running.

## Stack

- **Next.js 14** (App Router) + **React 18** + **TypeScript**
- **Tailwind CSS** for styling, **lucide-react** for icons
- **recharts** for the cost/latency/model charts
- **Vitest** + **@testing-library/react** (jsdom) for component tests
- **Playwright** for the smoke E2E

## Getting started

```bash
cd frontend
npm install
npm run dev          # http://localhost:3000
```

The dashboard talks to the backend at `NEXT_PUBLIC_API_URL`
(default `http://localhost:8000`). To run the backend locally:

```bash
# from the repo root
pip install -e .
python -m llm_monitor.main   # serves on :8000, offline-first (no DB needed)
```

## Demo mode (works with no backend)

Every read endpoint is wrapped in a **live-first, demo-fallback** client
(`src/lib/api.ts`). On any fetch error (backend down, timeout, non-2xx) it
returns bundled sample data from `src/lib/mockData.ts`, tagged
`source: "demo"`. The UI then shows a visible **"Demo mode"** badge and banner.

This means:

- `npm run dev` with **no backend** → fully populated, navigable dashboard.
- The Vitest and Playwright suites run **offline**.

The only write action, **Log a call** (`POST /log`), is not faked: if the
backend is unreachable the form shows a friendly "Demo mode — nothing was
persisted" notice instead of a false success.

## Pages & endpoints

| Page          | Route        | Backend endpoints consumed                |
| ------------- | ------------ | ----------------------------------------- |
| Overview      | `/`          | `GET /metrics`, `GET /reports/daily`, `GET /budgets/alerts` |
| Models        | `/models`    | `GET /metrics`                            |
| Daily report  | `/reports`   | `GET /reports/daily` (+ `?day=` filter)   |
| Budgets       | `/budgets`   | `GET /budgets/alerts` (tunable thresholds)|
| Log a call    | `/log`       | `POST /log`, `GET /metrics`               |

Every data view has **loading skeletons**, **empty states**, and **error
states**, and the app is wrapped in an **ErrorBoundary**.

## Environment variables

| Variable              | Default                 | Purpose                          |
| --------------------- | ----------------------- | -------------------------------- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | Base URL of the FastAPI backend  |

Copy `.env.example` to `.env.local` to override.

## Scripts

```bash
npm run dev        # dev server
npm run build      # production build
npm start          # serve the production build
npm test           # Vitest component tests (no backend needed)
npm run test:e2e   # Playwright smoke E2E (starts the dev server)
npx tsc --noEmit   # type-check
```

## Docker

The repo's root `docker-compose.yml` includes a `web` service:

```bash
docker compose up web
```

It builds this directory and serves the dashboard on
[http://localhost:3000](http://localhost:3000), pointed at the `api` service.
