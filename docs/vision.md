# bloom-iot Vision & Roadmap

This document lays out where bloom-iot is headed and why, based on a deep-research
review of the competitive landscape, the feasibility of adaptive/"recursive"
learning on hobbyist hardware, and the focus-vs-scope trade-off for an
early-stage open-source project. See the full research summary at the bottom.

## Where we stand

bloom-iot's current architecture — MQTT sensor listening → normalization/threshold
alerting → CLI dashboard / JSON export — is a solid foundation, but it is **not
itself a differentiator**. Mature open-source tools already cover this ground:

- **Mycodo** runs full closed-loop control (sensor → actuator → measure → adjust,
  via PID/conditionals/triggers) on a Raspberry Pi today, across dozens of use cases.
- **GrowAssistant**, a self-contained microgreen/herb grow fixture, is assembled
  entirely from off-the-shelf ESPHome + Home Assistant + Node-RED — no custom
  framework required.

If bloom-iot only reimplements MQTT plumbing and closed-loop actuation, it has no
wedge. The path to a defensible product runs through **doing one thing better
than anyone else**, not through breadth.

## Strategic direction

**Go narrow. Build depth. Defer breadth.**

1. **Own microgreen / indoor plant monitoring deeply** — not "any sensor, any
   domain." Every comparable success story (Mycodo, Home Assistant, GrowAssistant)
   started narrow and only widened after building a real user base.
2. **Differentiate on adaptive per-plant baselines**, not static thresholds. This
   is the one piece of "recursive learning" that is genuinely feasible on the
   hardware we target today (see below) — and nobody in the current landscape
   ships it out of the box for plant monitoring.
3. **Defer automated actuation (watering, lighting).** Mycodo already does
   threshold/PID-based actuation; RL-based control is real but immature and
   carries genuine safety risk. Not a v1 priority.
4. **Win on reliability and documentation**, not feature count. Field reports
   show ESP32 grow-tent nodes routinely lose ~75% of readings to Wi-Fi dropouts.
   Rock-solid ingestion, honest error handling, and good docs are themselves a
   competitive edge in this space.

## What "recursive learning" means for bloom-iot

"Recursive learning" breaks into three tiers of feasibility. We're committing to
one now and explicitly deferring the other two.

| Tier | Feasibility | Decision |
|---|---|---|
| **(a) Adaptive baseline anomaly detection** — learn each tent/tray's own "normal" range over time and flag drift, instead of relying on hand-set thresholds | **Proven today.** An isolation forest trains directly on an ESP32 in 1.2–6.4s using ~80KB RAM and infers in <16ms, learning entirely from nominal (non-faulty) data — no need to simulate failure cases. | **Build this next.** It's our flagship differentiator. |
| **(b) Closed-loop actuation** (sensor → water pump / grow light → measure outcome → adjust), including RL/fuzzy control | Demonstrated in research (RL cut greenhouse irrigation water use; a fuzzy controller held soil moisture in range on a single ESP32) but based on single-study/simulation evidence, and automated watering has real safety failure modes (e.g. sensor spoofing triggering overwatering). | **Defer.** If/when built, gate behind hard-coded safety limits (max runtime, rest intervals, duty-cycle caps) — never let the learning algorithm alone control actuation. |
| **(c) Full on-device continual/online learning** | Technically demonstrated but memory-bound; peak RAM is the binding constraint on MCUs, and most real continual-learning work is pushed to more capable hardware than an ESP32. | **Not now.** Lightweight drift-tracking (tier a) on the ESP32; anything heavier belongs on the Raspberry Pi tier, later. |

### Why tier (a) is the right bet

- Runs today, on the hardware we already target (ESP32 sensor nodes, Raspberry Pi hub).
- Trains unsupervised, on-device, from data the system is already collecting —
  no labeled fault data, no cloud dependency.
- Turns "is this reading bad?" from a static, hand-tuned threshold (today's
  `warn_low` / `warn_high` config) into something that adapts per plant, per
  tent, per season — genuinely useful and not something the incumbents offer
  out of the box for this use case.

## Roadmap

**Phase 0 — Harden the foundation (current)**
- Reliable MQTT ingestion, normalization, threshold alerting, dashboard/JSON
  output. ✅ Done (see `bloom_iot/`).
- Improve resilience to the connectivity failure modes seen in the field
  (reconnect/backoff, buffering during Wi-Fi dropouts, clear stale-data
  indicators in the dashboard).

**Phase 1 — Adaptive baselines (the differentiator)**
- Add an on-device (or Pi-side, for v1 simplicity) unsupervised baseline model
  per sensor/tent, trained on nominal data.
- Surface drift as a new alert tier distinct from static thresholds
  (`ok` / `warn` / `critical` / `drift-detected`).
- Document the feature clearly — this is the headline reason to choose
  bloom-iot over Mycodo or a bare ESPHome/HA setup.

**Phase 2 — Community and documentation**
- Treat docs, setup ease, and reliability as first-class deliverables, not
  afterthoughts — this is what the research shows actually drives adoption in
  open-source hardware/software projects, not feature breadth.
- Get real users running Phase 1 before touching actuation or broader scope.

**Phase 3 — Actuation (only after Phase 1/2 traction)**
- Threshold- and rule-based actuation first (matching what Mycodo already
  does), always behind explicit hard safety limits.
- RL/fuzzy closed-loop control only as an explicitly experimental, opt-in mode,
  informed by further validation on real plant data (not just industrial/motor
  analogs).

**Not now: general IoT platform breadth**
- Keep internal module boundaries (`listener` / `adapter` / `emitter`) clean
  enough that widening to other domains later is possible, but do not build
  generic "any sensor, any domain" support before the microgreen use case is
  proven.

## Open questions

These weren't resolved by research and need real-world validation:

1. **Monetization mechanics.** Kit sales (cf. SparkFun's open-source OpenScale
   IoT board), a hosted tier, paid pro features, or sponsorship — which
   actually works for a project like this? Success *factors* are well
   evidenced; concrete revenue *mechanics* are not.
2. **Does isolation-forest/K-means anomaly detection hold up on real plant
   sensor data?** The feasibility numbers above come mostly from industrial
   motor/vibration monitoring — validated as a hardware-feasibility analogy,
   not yet proven on slow-drift temperature/humidity/soil-moisture/light
   streams.
3. **Alert fatigue.** What false-positive rate do per-unit adaptive baselines
   produce in practice, and how much clean "normal" data is needed before a
   baseline can be trusted?
4. **Is the wedge big enough?** Given Mycodo and the ESPHome/Home Assistant
   stack already cover monitoring and closed-loop control, is "adaptive
   per-plant baseline + zero-config setup" enough of a reason to switch —
   and is there validated demand for it among early adopters?

---

## Research summary

*Produced via a deep-research pass (6 search angles, 26 sources fetched, 25
claims adversarially verified — 23 confirmed, 2 refuted) on 2026-09-15.*

**Product path:** bloom-iot's architecture is not novel — Mycodo already does
on-device closed-loop control, and DIY grow rigs like GrowAssistant are built
entirely from off-the-shelf tools. Open-source project success is driven by
value creation, documentation quality, and community process, not feature
count (Cambridge Design Science practitioner survey, 2022; Home Assistant's
own account of its early years).

**Recursive learning feasibility:** Adaptive per-unit baseline anomaly
detection is proven and practical today — an isolation forest trains on an
ESP32 in seconds using ~80KB RAM, from nominal data alone. Full continual
learning is memory-bound and mostly impractical on microcontrollers today.
RL/fuzzy closed-loop watering is demonstrated in research but rests on
single-study/simulation evidence and carries real safety risk; it should be
gated by hard-coded actuation limits, not the learning algorithm itself.

**Focus vs. scope:** Every relevant precedent (Mycodo, Home Assistant,
GrowAssistant) succeeded by starting narrow and expanding only after building
a community. No evidence supports a wide-first approach for a solo/small team
at the pre-adoption stage.

**Caveats:** the competitor landscape moves fast and "not novel" judgments
should be periodically re-checked; most edge-ML feasibility evidence comes
from non-plant (industrial) domains and is used here only as a hardware
analogy; the RL/fuzzy-irrigation findings rest on limited (single-study or
n=1) evidence.
