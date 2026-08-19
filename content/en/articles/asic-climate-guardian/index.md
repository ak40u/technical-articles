---
title: "How AI Turned Five ASICs in a Country House Into a Self-Funding Climate System"
date: 2026-08-19
description: "How an autonomous AI agent solved the thermal heating challenge of a country house using five Jasminer X16-Q ASICs, balanced tiered electricity tariffs, and strictly maintained room temperatures between +10°C and +33°C across five zones."
author: "Pavel Volkov"
image: "og/sdd-in-production-hero-en.png"
translationKey: "asic-climate-guardian"
---

A friend of mine owns a country house where he spends time during the summer. By autumn, both the main house and the timber outbuilding begin to cool down. In total, there are five separate rooms: three in the main house and two in the outbuilding.

The heating requirement for autumn was straightforward but came with strict engineering constraints:
1. **Prevent freezing**: temperature in every room must strictly stay **above +10°C**.
2. **Prevent overheating**: temperature in any room must **not exceed +33°C**.
3. **Avoid penal electricity tariffs**. The local utility imposes a progressive tiered tariff structure:
   - **Tier 1 (up to 1,600 kWh/month)**: subsidized rate at `4.21 RUB / kWh`.
   - **Tier 2 (1,600 – 2,400 kWh/month)**: elevated rate at `6.07 RUB / kWh`.
   - **Tier 3 (above 2,400 kWh/month)**: penal rate at `8.74 RUB / kWh`.

Instead of purchasing five traditional space heaters drawing 1.5–2 kW each, he placed five quiet Jasminer X16-Q ASICs across the rooms. Each unit consumes exactly **630 W** from the wall and emits exactly **630 W of pure convective heat** (with thermal dissipation efficiency near 100%), while simultaneously mining ETC at a factory hashrate of **1,850 MH/s**.

He handed complete control of this infrastructure to an autonomous AI agent. Here is how the agent structured the mathematics and thermodynamics.

---

### Step 1. Tariff Economics: Why 3 ASICs Beat 5

The agent integrated live power consumption with utility brackets, network difficulty, and market coin prices:

- **1 ASIC** running 24/7 for 30 days consumes **453.6 kWh** (`1,909.66 RUB` at the Tier 1 rate of 4.21 RUB) and yields **3.68 ETC** (`1,915.52 RUB`). Break-even coin price is **$6.09**.
- **3 ASICs** running 24/7 consume **1,360.8 kWh** (`5,728.97 RUB`). This sits **100% inside Tier 1** (1,600 kWh limit). Mining output is **11.04 ETC** (`5,746.55 RUB`). 1.89 kW of thermal heating is entirely self-funded with a slight surplus of **+17.58 RUB**.
- **5 ASICs** running 24/7 consume **2,268.0 kWh** (`10,790.76 RUB`). 668 kWh of this total is billed at the elevated **6.07 RUB** rate. Mining output is **18.41 ETC** (`9,577.58 RUB`), resulting in a net monthly loss of **-1,213.18 RUB**, while the break-even price jumps to **$6.88**.

**Model conclusion:**
Running all 5 units simultaneously is economically counterproductive: the penal tariff on excess kilowatt-hours turns mining unprofitable. But running **exactly 3 units concurrently (1.89 kW of continuous heat)** keeps electricity inside the lowest tariff bracket, while mined coins fully offset the utility bill.

---

### Step 2. Two-Tiered Climate Supervisor

The remaining task was distributing these 3 power slots across 5 rooms. The timber outbuilding has thinner insulation than the main house and cools down faster.

The agent implemented an autonomous climate supervisor (`core/thermo_guardian.py`) operating under a strict decision contract:

```
                  ┌────────────────────────────────────────┐
                  │       Room Telemetry Poll Cycle        │
                  └──────────────────┬─────────────────────┘
                                     │
                    Any room with temp < 10°C?
                     ├── YES ──> PRIORITY 1: ANTI-FREEZE
                     │           Turn ON ASIC in cold room (630 W).
                     │           If all 3 slots are occupied, temporarily
                     │           turn off the ASIC in the warmest room.
                     │
                     └── NO ───> Any room with temp >= 33°C?
                                 ├── YES ──> OVERHEAT PROTECTION
                                 │           Mandatory shutdown of that unit.
                                 │
                                 └── NO ───> PRIORITY 2: BASELINE HEATING
                                             Keep exactly 3 units active.
                                             Consumption: 1,360.8 kWh (< 1,600 kWh).
```

---

### Real-World Operational Behavior

1. **Mild autumn day (all rooms between 18–22°C)**:
   3 ASICs remain active (two bedrooms in the house and one workshop in the outbuilding). Total heating power is 1.89 kW. The 1,600 kWh monthly ceiling is never breached.

2. **Night frost (unheated workshop drops to +8°C)**:
   The agent detects the drop below +10°C. Unit #4 in the workshop immediately powers on. To avoid exceeding the Tier 1 threshold, the agent temporarily cuts power to the living room in the main house, where the temperature is already comfortable (+21°C). Once the workshop warms to +13°C, the slot rotates back to the house.

3. **Sunny midday (bedroom warms to +33°C)**:
   The agent immediately shuts off the bedroom ASIC to prevent hardware and room overheating, reallocating thermal power to a cooler part of the property.

---

### Summary

Without purchasing dedicated electric heaters or commercial thermostats, the property gained a five-zone autonomous climate control system:
- No room ever drops below **+10°C**.
- No room ever exceeds **+33°C**.
- Total monthly electricity consumption never leaves the subsidized **4.21 RUB / kWh** tier.
- Heating expenses are completely offset by mined cryptocurrency.

The entire loop runs autonomously via local Home Assistant and Tailscale on scheduled triggers, requiring zero manual switch-toggling or human supervision.
