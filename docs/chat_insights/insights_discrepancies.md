# Chat ↔ Sheet Discrepancies (2024–2026 overlap)

*Cross-references concrete numbers in `ojash_joshi_chat.txt` against `_sheet_reference.md`. The **chat timestamps are treated as ground truth**; the sheet's dates are approximate (reconstructed from week order, no real dates) and it only spans ~Mar 2024 → mid-2026. Chat quotes are short evidence with day-first dates.*

---

## TL;DR

- **Competitions match well** where both cover them (NYFC Dec 2024, Ox Classic Apr 2025) — same attempts, same totals, same placings. ✅
- **The sheet's headline "Total 630.0" was never lifted on one day.** It's the sum of each lift's best week (S220 + B135 + D275), which occurred on three *different* days across *different* years. Best real same-day total: **615 kg (training, 07/10/2025)** and **605 kg (meet, Ox Classic Apr 2025)**. ⚠️
- **A whole competition is missing from the sheet's comp list: the Iconic Clash deadlift meet, 07/02/2026, where he hit 275 kg.** The sheet's D275 shows up only as a training week ("Pull time"), dated ~2 weeks early. ⚠️
- **The 2022 first meet** (Park Village Resort, ~12/02/2022) predates the sheet entirely.
- Two big **injury-driven crashes** in the sheet's numbers (Jan 2025, Jun 2026) are fully explained by the chat. ✅ good corroboration.

---

## 1. Competitions

### NYFC Classic — chat 08/12/2024 vs sheet 2024-12-09
| | Squat | Bench | Deadlift | Total | Result |
|---|---|---|---|---|---|
| **Chat** | 195 / 210 / **220 (PR)** | 112.5 / 122.5 / 130 ✗ | 225 / 240 / **250 (raw PR)** | 592.5 | 8/9, 4th |
| **Sheet** | 220.0 | 122.5 | 250.0 | 592.5 | 8/9, 4th |
✅ **Match.** Sheet's counted bench (122.5) correctly reflects the failed 130 third attempt (3 reds). Date off by 1 day (approximate). Note he competed with a **103.6°F fever** (chat 08/12/2024) — context the sheet can't show.

### Ox Classic Summerslam — chat 26–27/04/2025 vs sheet 2025-04-27
| | Squat | Bench | Deadlift | Total | Result |
|---|---|---|---|---|---|
| **Chat** | 200 / 215 / **220** | 120 / 127.5 / **130** | 235 / 245 / **255 (PR)** | 605 | 9/9, 3rd |
| **Sheet** | 220.0 | 130.0 | 255.0 | 605.0 | 9/9, 3rd |
✅ **Match.** Chat adds that he **played it safe for the podium** — "went for plan B on every lift... I feel fresh", believed 225–230 / 132.5 / 270 were in the tank.

### ⚠️ Iconic Clash deadlift meet — chat 07/02/2026 — MISSING from sheet's competition list
- Chat (07/02/2026): a **deadlift-only competition**, attempts **245 / 262.5 / 275 kg**, hit 275. *"Peaking for this comp went great. I have more in the tank!"* Planned since 17/12/2025 ("Ironzilla... deadlift barbell... target 275–280").
- The sheet's competition section hardcodes **only two** meets (Dec 2024, Apr 2025). This meet is absent.
- The sheet *does* carry a D275 in week 85 ("Pull time", dated **2026-01-26**), which is almost certainly this comp's lift logged as a training week — and dated **~2 weeks early** vs the actual 07/02/2026.
- 👉 **Action:** add the 07/02/2026 Iconic Clash deadlift meet (275 kg) to the dashboard's competition list, and correct its date.

### 2022 first meet — outside sheet coverage
Chat: meet at Park Village Resort, Budhanilkantha, ~**12/02/2022** (prep derailed by COVID + double eye haemorrhage). **No meet-day result is in the chat** — he went quiet afterward and paused coaching (27/02/2022). Sheet begins Mar 2024, so no conflict, just a gap to be aware of.

---

## 2. The "630 total" is synthetic
The sheet reports **Computed PRs: Squat 220 · Bench 135 · Deadlift 275 · Total 630**. Each *individual* PR is real and chat-confirmed:
- **Squat 220:** competition Dec 2024, matched in training 05/10/2025 ("220 KG RPE 8-9 🚀 PR").
- **Bench 135:** training 05/10/2025 ("135 KG RPE 10, hips uthyo") and 29/12/2025.
- **Deadlift 275:** Iconic Clash meet 07/02/2026.

But **630 never happened as a single total** — the three bests are from Oct 2025, Oct 2025, and Feb 2026 respectively. Highest *actual* same-day totals:
- **615 kg training** (07/10/2025): S220 + B135 + D260. *"615 KG Total secured."*
- **605 kg meet** (Ox Classic, Apr 2025).
- **592.5 kg meet** (NYFC, Dec 2024).
👉 **Flag:** if the dashboard shows "Total 630" as an achievement, label it clearly as a *theoretical max* (sum of best lifts), not a competed/hit total. Add a separate "best actual total" metric.

---

## 3. Injury-driven dips in the sheet — corroborated by chat ✅
These are *not* errors — they're the sheet faithfully recording crashes the chat explains:
- **Sheet week 37 (2025-01-06): S125 / B120 / D135** — a dramatic squat/DL collapse. Chat: **lower-back injury** from 16/12/2024, physio 07/01/2025 (swelling above left lumbar spine). The tiny squat/DL numbers = injury rehab loads. ✅
- **Sheet weeks 103–105 (Jun 2026): S165→180, D180→200** — big drop. Chat: **lower-back flare 02/06/2026**, physio, **block reset** (06/06). ✅
These are good examples of the two datasets agreeing — the sheet shows *what load*, the chat shows *why*.

## 4. Travel & illness gaps the chat implies
Chat documents layoffs that should appear as gaps/dips in the sheet's week sequence:
- **~mid-Jun 2024** ~3-week trip (sheet jumps week 11 `2024-05-27` → week 12 `2024-07-01`). Roughly consistent.
- **14–29/10/2024 China trip** (detrained; sheet gap week 29 `2024-10-28` → week 30 `2024-11-18`). Consistent.
- **22 May–05 Jun 2025 Spain trip** (2 weeks; chat 08/06 "not as rusty as I thought"). Sheet has irregular spacing around weeks 58–60 here.
- **28 Jun–04 Jul 2025 gastritis layoff** (~2 gym days missed, lost ~2 kg BW). Hard to see at weekly granularity.
👉 These confirm the sheet's approximate dates drift by up to a couple of weeks in places; trust chat dates when they conflict.

## 5. Bench data missing from the sheet, Apr–Jun 2026
Sheet weeks 95–105 (2026-04-06 onward) show **Bench = "-"** (no data). But the chat shows bench was still trained in this window — e.g. **07/06/2026: long-pause bench 135 attempt (failed, retried at RPE 10)**, plus regular bench through Apr–May. 👉 **Flag:** a logging gap in the sheet, not an actual training gap. Bench numbers exist in the chat if you want to backfill.

## 6. Minor date drift notes
- Sheet dates run **~1–2 weeks early** in the Jan–Feb 2026 region (e.g. "Pull time" D275 at 2026-01-26 vs the real 07/02/2026 meet).
- NYFC off by 1 day. Ox Classic exact.
- General rule confirmed: **the sheet's week *order* is reliable; its absolute dates are approximate.**

---

## Suggested reconciliations for the dashboard
1. Add the **07/02/2026 Iconic Clash deadlift meet (275)** to the competition list; fix its date.
2. Relabel **"Total 630"** as *theoretical best* and add a **best-actual-total** stat (615 training / 605 meet).
3. **Backfill bench** for Apr–Jun 2026 from the chat.
4. Optionally overlay **chat-derived competition dates** to auto-correct the sheet's approximate week dates.
5. Overlay the **injury windows** (Jan 2025, Jun 2026) so the dips read as injuries, not deloads.
