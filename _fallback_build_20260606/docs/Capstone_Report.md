<!--
DRAFTING CONVENTIONS (remove before final):
  [VERIFY: x]   = a fact/number to confirm against a notebook or CSV before submission.
  [CITE: src]   = a citation slot keyed to a KNOWN source; full reference to be filled by author
                  from her own library. Agent does NOT manufacture references.
  [TEMPLATE]    = institutional boilerplate (declarations) to be pasted by author.
Honest-framing thread runs throughout: ex-ante headline (~6% pooled / ~9-10% single-country,
negative single-country R2); conditional ~4-5% is REFERENCE only; intervals are LOWER bounds;
Ridge coefficients are NOT elasticities; 2040 figures are CONDITIONAL scenario projections.
Voice choice: no first-person "we"; confident impersonal subject ("This report...", "The
forecast...") per established house style. Flag to author if "we" is preferred.
-->

# Uzbekistan's Power Sector to 2040
### Forecasting Demand, Bounding Uncertainty, and Locating Advisory Opportunity

**Author:** Farangiz Jurakhonova
**Programme:** MSc in Business Analytics, Central European University
**Capstone client:** ILF Consulting Engineers Austria GmbH [VERIFY: confirm full legal entity name and a one-line descriptor for the title page, e.g. "an international engineering and advisory firm" — the "GmbH" form is attested in the project's EDA notebook header]
**Date:** June 2026

---

## Abstract

This report builds a demand-anchored forecast of Uzbekistan's electricity system to 2040 and reads it for the advisory opportunities the country's energy transition creates. The motivating question is practical rather than academic: for an engineering-advisory firm, where and when does a gas-dominated system in transition generate decisions — new transmission, plant replacement, renewable integration, efficiency reform — that call for outside expertise? Answering it requires a forecast, and the forecast is hard for one reason that organises the whole analysis: Uzbekistan has only about thirty years of usable annual data. Every methodological choice follows from that constraint. Demand is modelled with shrinkage regression on a small set of structurally screened drivers — income, industry, services and cooling demand — and is scored honestly out-of-sample: each driver is itself forecast and the demand lag is propagated recursively, so the model is never handed its own inputs. On that ex-ante basis the deployed single-country model achieves roughly 9–10% error with a *negative* hold-out R² against the deliberate post-2018 structural break, while a pooled four-country Central-Asian panel reaches about 6% with a positive R², validating the common structure even though Uzbekistan remains among the hardest cases to predict from its neighbours. The deployed model projects demand from about 74 TWh in 2024 to 86 TWh in 2030 and roughly 124 TWh in 2040, within a band that is explicitly a lower bound on true uncertainty. Three supply scenarios sharing that single demand path bracket the 2040 renewable share between 36% and 80% and grid carbon intensity between roughly 436 and 90 gCO₂/kWh, depending only on build-out ambition. Throughout, the report holds a hard line between what thirty observations can predict and what they can only bound, and maps each structural finding to a concrete investment signal — chronic ~16% grid losses, recurring supply-deficit windows, gas-import exposure, and a staged capital programme — that an advisory practice can act on.

**Keywords:** Uzbekistan; electricity demand forecasting; energy transition; small-sample econometrics; pooled panel regression; renewable energy; carbon intensity; investment signalling

## Declarations

**Use of generative AI.** Generative AI tools — specifically Anthropic's Claude, used through the Claude Code command-line environment — assisted in the preparation of this report. Their role was confined to drafting and editing prose, generating and styling figures from the author's own data and code, assembling and typesetting the document, and serving as a programming aid within the analysis notebooks. All data, modelling choices, analytical decisions, interpretations and conclusions are the author's own; every figure, statistic and reference produced or formatted with AI assistance was verified by the author against the underlying notebooks and source data, and the author takes full responsibility for the content of this report.

**Authorship and originality.** This report is the author's own work, prepared as the capstone project for the MSc in Business Analytics at Central European University. Except where explicit attribution is given, the analysis, code and writing are original; all external data, literature and policy sources are acknowledged in the References, and the work has not been submitted, in whole or in part, for any other degree or qualification.

## Table of contents

[Auto-generated at typeset stage. Chapters: 1 Introduction · 2 The Uzbek power system · 3 Data · 4 Methodology · 5 Forecasts and scenarios to 2040 · 6 Investment signals and advisory opportunity · 7 Limitations · 8 Conclusion · References · Appendices.]

---

# 1 — Introduction

## 1.1 The question

Uzbekistan is rebuilding the machine that powers it. A fleet of Soviet-era gas plants is aging toward retirement, the government has committed to a large renewable build-out, and electricity demand climbs each year behind a young, urbanising population. For an energy-advisory firm — the client this work was scoped for, ILF — the question is not whether the transition happens. It is *where* and *when* the transition creates decisions that call for outside expertise: which corridors will need new transmission, which plants will need replacing, and where a supply gap will force an investment choice. Answering that requires a forecast of where the system is heading. This report builds one, and then reads it for the opportunities it implies.

## 1.2 Why Uzbekistan, and why the forecast is hard

Two features make Uzbekistan an unusually tractable case, and one feature makes it genuinely hard.

The first feature is concentration. The country runs overwhelmingly on natural gas, so the questions that matter for the next two decades are few and sharp: how fast gas gives way to renewables, how much fossil generation remains, and what that does to the carbon intensity of the grid. A system with a dozen balanced fuels would blur those questions; Uzbekistan's does not.

The second feature is direction. The government has legislated a large renewable build-out: a 2024 amendment to the energy law sets a target of roughly 27 GW of renewable capacity and a 40 percent renewable share of generation by 2030, raised from an earlier goal of a 25 percent share and 12 GW of solar and wind [CITE: Enerdata, Uzbekistan country energy profile; 2024 amendment to the Law on the Use of Renewable Energy Sources]. The presidency has since signalled a still more ambitious path — a 54 percent renewable share and roughly 51.6 GW of renewable capacity by 2030 — so a visible gap now separates what the law requires from what the executive aspires to [CITE: Enerdata, Uzbekistan country energy profile]. The build-out is backed by a sequence of reforms that unbundled the state monopoly and opened the market to independent power producers [CITE: NB02 §E sources — World Bank / IFC programme record]. The direction of travel is set by policy; what is uncertain is the pace, and pace is exactly what a forecast can put numbers on.

The hard feature is data. Uzbekistan has only about three decades of usable annual statistics — on the order of thirty observations per series, spanning 1990 to 2023. That is far too few for the data-hungry methods a richer evidence base would invite, and it is the single fact that shapes every modelling decision that follows. This report treats the small sample not as a caveat tucked into a footnote but as the organizing logic of the whole analysis: the methods are chosen *because* the data are thin, and the claims are sized to match.

## 1.3 What this report does

The report does three things, in sequence.

It forecasts electricity demand to 2040 from the drivers that actually move it — income, population, climate, and price. It then translates that demand into the supply system that must meet it, projecting renewable share, fossil generation, and grid carbon intensity under three build-out scenarios. Finally, it reads those projections for opportunity, connecting each structural finding to a decision the sector will have to make.

The link from system structure to opportunity is direct, and it is what makes the analysis useful rather than merely descriptive. A gas-dominated system raises questions of combustion efficiency and gas-supply security. A thin renewable share beneath a large project pipeline turns grid evacuation and balancing into pressing problems. A demand centre in the east, paired with the best renewable resource in the west, sets up a transmission-corridor challenge that will not resolve itself. Each structural finding in the chapters that follow connects to one of these, and the closing chapters make the mapping explicit.

## 1.4 What this report does not claim

A forecast built on thirty observations earns trust by being exact about its own limits. Four claims this report deliberately does not make are worth stating at the outset, because each one disciplines how its results should be read.

Point precision is not on offer. The demand path is a central estimate wrapped in an interval, and that interval is a *lower* bound on the true uncertainty — it captures the model's own noise but not the deeper uncertainty in the drivers being fed into it (Chapter 5).

The scenarios are not predictions. The three supply pathways share a single demand trajectory and differ only in how quickly renewables are built; they are conditional "if-then" projections, not competing forecasts of what will occur.

The coefficients are not elasticities. Income, population, and demand all trend upward together, so the model's coefficients are shrunken, correlated quantities tuned for prediction — not causal measures of how a one-percent change in income moves demand (Chapter 4).

And the report does not assert a long-run equilibrium it cannot test. With thirty years of data, the standard test for a stable long-run demand–income relationship has too little statistical power to settle the question; the report says so plainly rather than building a model on an assumption it cannot defend (Chapter 4).

## 1.5 How the report is organised

The argument runs across eight chapters. Chapter 2 describes the power system as it stands — its fuel mix, its physical fleet, and the regional geography of its resources — and shows why each structural fact points to a distinct kind of opportunity. Chapter 3 documents the data: how four sources were reconciled into one master series, and where their conventions disagree. Chapter 4, the methodological core, shows how the diagnostics force the modelling choices, builds the forecasting bench from naïve baselines up to a pooled cross-country panel, and sets out the honest out-of-sample test by which every model is judged. Chapter 5 presents the demand forecast and the three supply scenarios to 2040, with renewable share, fossil generation, and carbon intensity. Chapter 6 turns those projections into investment signals, maps them to the areas where advisory engagement is most likely to arise, and describes the dashboard through which the tracker is delivered. Chapter 7 consolidates the limitations into a single honest accounting, and Chapter 8 concludes with what the client should act on now and what it should monitor.

---

# 2 — The Uzbek power system

## 2.1 From Soviet grid to gas monopoly: a brief history

Uzbekistan's power system did not choose to run on gas; it inherited the choice. The shape it has today — a gas-thermal backbone, a grid centred on Tashkent, a single state operator — was set in the Soviet decades, and a short history makes the rest of the chapter easier to read (Figure 2.1).

Electrification began under early Soviet industrialisation, when the first generating stations were built around Tashkent and output grew rapidly off a near-zero base [CITE: inlibrary.uz electrification paper]. The mid-century build-out was hydropower: the Farhad plant (126 MW) was started in 1943 and commissioned around 1953 [CITE: Farhad — Eurasian Research hydropower programme (date-supporting source)], and the Charvak cascade (~600 MW) followed between 1963 and 1972 [CITE: Charvak — power-technology / orexca; JRC country report]. Then the scale of the system changed with gas. Construction of the Syrdarya thermal power plant began in 1960 and its first 150 MW unit came online in 1963; built out through the 1970s and completed in 1981 at roughly 3,215 MW, it became — and remains — the country's largest station [CITE: Syrdarya TPP — tep.uz / Wikipedia]. Gas-fired thermal, not water, became the backbone, and that is the direct root of the gas dominance the next section measures.

Two structural inheritances followed. The Central Asian Power System, built in the 1970s, tied the grids of all five republics together and ran them from a single dispatch centre in Tashkent — by one account Uzbekistan generated about half of the bloc's electricity, the largest share [CITE: ADB — Central Asia Power System]. When the Soviet Union dissolved in 1991, that centrally planned system passed intact to the new state and was consolidated into a vertically integrated monopoly, JSC Uzbekenergo, spanning generation, transmission and distribution [CITE: JRC / Minnebo country report]. The system then turned inward: around 2009 Uzbekistan withdrew from the regional pool and leaned on its own thermal fleet and new internal lines [CITE: Jamestown — 2009 CAPS exit]. Only in 2018–2019 did the pattern break — the Renewable Energy Law and the unbundling of Uzbekenergo into separate generation, transmission and distribution companies opened the market to independent power producers [CITE: Uzbekistan PP-3981 (2018); PP-4249 (2019)] and began the transition the rest of this report analyses. The present system, in short, is a gas-heavy, Tashkent-centred grid built for central planning — which is exactly why decarbonising it is a structural problem, not a switch to flip.

![Figure 2.1](../outputs/history_timeline_uzbekistan.png)

*Figure 2.1. A milestone history of Uzbekistan's power sector, 1920s → 2026, grouped into six eras. Marker size is proportional to nameplate capacity at commissioning (hydropower in blue, gas-thermal in brown), showing the mid-century shift from hydro to gas. Historical context compiled from secondary sources; pre-1990 milestones are not part of the project dataset, and pre-1950 figures are qualitative. Sources: [CITE: inlibrary.uz; Eurasian Research; power-technology / orexca; tep.uz; ADB; JRC / Minnebo; Jamestown].*

## 2.2 A system built on gas

Uzbekistan makes most of its electricity by burning natural gas. In 2023, the last fully confirmed year, gas supplied 78.1% of generation — comfortably above the 60% mark the IEA uses to call a system "gas-dominated" [CITE: IEA Uzbekistan Energy Profile 2024]. Coal and hydropower cover most of the remainder; solar and wind together still rounded to under one percent. One fuel carries the system, which means one risk carries it too: a gas-price or gas-supply shock passes almost undiluted into the cost of power.

That dominance is structural, not a recent accident. Across the confirmed record gas grew faster than any other large source — about 2.5% a year since 2010 — while hydropower flatlined, with no new large dams since 2010 and only turbine modernisation since [CITE: REF asset dataset]. Demand growth has been met by burning more gas, not by diversifying. The consequence for the next two decades is sharp: any gain in renewable share has to come from newly built solar and wind, because the water is already fully used.

That new build has begun, and it is moving fast off a tiny base. Total generation jumped to roughly 82 TWh in 2024 — a 10% rise in a single year, the largest step in the record [CITE: StatSUZ preliminary 2024]. Within that jump, solar output rose more than six-fold against 2023 and wind more than a hundred-fold (Figure 2.2). But level matters more than growth rate here: even after the surge, non-hydro renewables supplied under 6% of generation. The transition is real, and it is a construction story — not a re-dispatch of plant that already exists.

![Figure 2.2](../outputs/energy_mix_evolution.png)

*Figure 2.2. Generation by fuel. Left: the long-run mix, 1990–2023, fully decomposed into gas, coal, oil & other fossil, hydropower, solar and wind — the six bands sum to total generation, and gas holds about three-quarters of output in every year while the solar-and-wind sliver stays under 1% even at the end of the confirmed record. Right: the recent split, 2022–2024; 2022 and 2023 are shown fuel-by-fuel, while the 2024 total (82.0 TWh, StatSUZ preliminary) carries only its known solar and wind on top and leaves the thermal-and-hydro remainder hatched, because that split is not yet published by the IEA and is not fabricated into shares. Solar output rose 6.4× and wind ≈110× against 2023, yet non-hydro renewables still supplied under 6% of generation. Source: master_dataset_core.csv (per-fuel to 2023; StatSUZ preliminary 2024); UzStat national series.*

## 2.3 Where Uzbekistan sits among its neighbours

"Central Asia" is not one electricity market, and the difference decides which comparisons are fair. Renewable share across the five systems splits them cleanly in two (2024): Kyrgyzstan (89%) and Tajikistan (95%) run on hydropower and face a problem of seasonality and flexibility; Uzbekistan (16%), Kazakhstan (15%) and Turkmenistan (near zero) run on fossil fuels and face a problem of decarbonisation [CITE: OWID/Ember; World Bank WDI]. Uzbekistan belongs firmly to the second group.

This matters beyond description. A forecast for a country with thirty observations gains power by borrowing strength from similar systems (Chapter 4), but "similar" has to mean structurally alike: a model pooled with the hydro states would be learning from a different transition, while one pooled with the fossil-heavy peers is defensible. Which neighbours actually enter the pool, and on what rationale, is settled in the methodology. [VERIFY: NB02 frames the credible pool as the fossil-heavy peers (KAZ, TKM); the implemented pool in NB07 is a four-country Central-Asia panel — reconcile the membership and the stated rationale in Chapter 4.]

## 2.4 The physical fleet

Behind the fuel shares sits a fleet of named assets, and reading it the way an investor does — what runs today, what is contracted, what is still a target — is more informative than any single headline number. A curated catalogue of 46 major plants [CITE: REF asset dataset] records 34 operational assets totalling about 19 GW of capacity, six under construction adding 4.2 GW, and six more planned at 2.65 GW. Thermal plant dominates what runs today (13.7 GW across seven stations), with hydro (1.9 GW), solar (2.0 GW) and wind (1.5 GW) far behind, and the country's first nuclear plant — a 2.1 GW integrated station at Jizzakh, pairing two large VVER-1000 reactors with two RITM-200N small modular units — now under construction [CITE: Rosatom / Uzatom Jizzakh project record, 2025]. (The asset catalogue logs this entry as a small modular reactor, a label that predates the project's September 2025 reconfiguration into the larger mixed design; the 2.1 GW total reflects the current scope.)

The fleet's history runs at two speeds (Figure 2.3). For nearly three decades after 1990 almost nothing new was built: capacity crept from 12.7 GW (1990) to 15.4 GW (2010) to 19.1 GW (2025), and the additions were mostly gas. Then the pace broke. The 2018 Renewable Energy Law and the 2019 unbundling of the state utility opened the market to independent power producers [CITE: Uzbekistan PP-3981 (2018); PP-4249 (2019)], and from 2021 new solar, wind and storage projects appear almost every year. The forward pipeline carries the next turn of the story: from 2027 the new entries are dominated by storage and nuclear rather than generation, a sign that the binding constraint is shifting from raw megawatts to grid flexibility and dispatch [CITE: IEA Uzbekistan Energy Profile 2024].

![Figure 2.3](../outputs/fleet_evolution_4panel.png)

*Figure 2.3. The generation fleet, 1990 → 2040, by technology and status (REF catalogue, 46 named assets; markers sized by capacity). Operational capacity grows from 12.7 GW in 1990 to 19.1 GW in 2025; the 2040 panel adds the contracted and planned pipeline to reach 26.2 GW. The post-2021 solar and wind build-out (yellow, green) lands in the west, away from the eastern thermal core. Source: REF asset dataset (uzbekistan_energy_projects.json).*

## 2.5 The geography of supply and demand

Where the assets sit is the headline of the chapter, because supply and demand pull in opposite directions on the map. The legacy thermal core and the hydro cascades sit in the east — in and around the Tashkent corridor and the Fergana valley — which is also where most of the load is. The best renewable resource sits in the west and southwest (Figure 2.4). Karakalpakstan, Navoi and Bukhara hold roughly 84% of the country's technical wind potential, with hub-height wind speeds above 7.5 m/s [CITE: CAREC 2024]; the strongest solar irradiance, above 1,820 kWh/m² a year, runs through Bukhara, Kashkadarya and Surkhandarya [CITE: Global Solar Atlas; IEA Solar Roadmap 2024]. Hydro stays in the east, concentrated about 75% in the Charvak cascade and the Andijan reservoir, and is being modernised rather than expanded.

This east–west split is the single most consequential fact in the chapter. A demand centre in the east paired with the best generation resource in the west cannot work without long-distance transmission, and that gap becomes one of the clearest opportunities the forecast points to (Chapter 6). The first nuclear plant, sited at Jizzakh inside the eastern demand centre, reads partly as a counterweight — firm capacity close to the load that reduces how much western power has to be wheeled across the country.

![Figure 2.4](../outputs/oblast_resource_map.png)

*Figure 2.4. Oblast renewable-resource atlas. Left: solar irradiance (colour, kWh/m²/yr) and total renewable capacity (bubble size) by region. Right: the dominant renewable technology in each oblast. Wind concentrates in the northwest (Karakalpakstan), the highest solar irradiance in the south-centre (Bukhara, Kashkadarya, Surkhandarya), and hydro in the eastern valleys. Source: oblast_atlas.csv (CAREC 2024; Global Solar Atlas).*

## 2.6 An aging fleet and a tight grid

Two further facts complete the picture, and both create work. The thermal fleet is old, and retiring it has barely begun: no Soviet- or transition-era plant has closed outright, and decommissioning has so far happened unit by unit inside still-running stations. About 1.04 GW has been retired against a national target of roughly 6.4 GW of obsolete thermal capacity [CITE: EBRD / ADB project documents; Global Energy Monitor], leaving more than five gigawatts still to replace. The grid, meanwhile, runs tight. Transmission-and-distribution losses sit near 16% of supply and reached 17.8% in 2023 — high by international standards, and a signal the report returns to in Chapter 6. (The 2023 figure is the Eurasian Development Bank's; the World Bank's loss series is unreliable for 2018–2022 and is corrected as §3.6 describes.) [CITE: Eurasian Development Bank, Central Asia Energy Outlook 2026] Cross-border trade absorbs the seasonal extremes: Uzbekistan is a net exporter across the year but a net importer in winter, when heating demand pushes the thermal fleet to as much as 93% of its capacity [CITE: IEA; Times of Central Asia].

## 2.7 The stakes for the forecast

Put together, these facts define what the rest of the report has to quantify. Uzbekistan runs on gas, demand is rising, and the only way to lower the carbon intensity of the grid is to build solar and wind faster than load grows — while replacing an aging thermal fleet and moving power from a windy, sunny west to a power-hungry east across a grid that already loses a sixth of what it carries. The pace of that build-out is uncertain, and pace is what a forecast can bound. Chapter 5 turns these stakes into numbers — a demand path to 2040 and three supply scenarios for renewable share, fossil generation and carbon intensity — and Chapter 6 turns the numbers into the specific opportunities each structural fact implies.

---

# 3 — Data

## 3.1 The binding constraint: thirty years of record

Every modelling choice in this report follows from one fact: Uzbekistan's electricity record is short. The confirmed national series — generation, demand, the fuel split, carbon intensity — runs annually from 1990 to 2023, thirty-four observations, and the most recent year is provisional (Figure 3.1). The early-1990s values, recorded during the post-Soviet contraction, sit so far outside the modern regime that they inform a forecast only weakly; after holding out the provisional years and accounting for that break, the effective sample a model can learn from is about thirty points. Thirty is not enough to estimate a rich model; it is barely enough to estimate a simple one. This is why the methodology that follows leans on regularisation and on borrowing strength from neighbouring countries rather than on adding variables — and why the report stays careful, throughout, about the line between what thirty points can predict and what they can only bound.

![Figure 3.1](../outputs/data_coverage_provenance.png)

*Figure 3.1. Data coverage and provenance, 1990 → 2026. Each bar shows the years over which a source supplies a given series; colour marks the source. The IEA reference balance ends in 2023 (dashed line); the 2024 demand and generation points are filled by ratio-scaling StatSUZ onto the IEA basis (hatched caps), and 2024–2026 are flagged preliminary (amber band). The confirmed electricity record spans 1990–2023 — about thirty modelling years. Source: master_dataset.csv (IEA, StatSUZ, IRENA, World Bank); central_asia_panel.csv (OWID + World Bank); imf_weo_uzb.csv (IMF WEO, April 2026 vintage).*

The shortness is not the only constraint. The record is also assembled from sources that do not agree by construction — different boundaries, different latest years, different conventions. Reconciling them without quietly inventing data at the seams is the work of this chapter, and it is where the project's data-provenance honesty is tested.

## 3.2 Four sources, four definitional boundaries

Four primary datasets feed the project, and naming what each is for — and where each stops — is the first step in trusting the combined record. The International Energy Agency's balance [CITE: IEA Uzbekistan Energy Profile 2024] is the reference: it supplies generation by fuel, electricity consumption, gas flows and the power-sector carbon-intensity series on an internationally consistent boundary, but it stops at 2023, a one-year publication lag. The National Statistics Committee of Uzbekistan (StatSUZ) [CITE: StatSUZ] is the only source that publishes 2024, so it carries the burden of extending every series to the most recent year; it also reports installed capacity and renewable generation by technology at a granularity the IEA does not. IRENA [CITE: IRENA Renewable Capacity Statistics 2024] supplies the canonical renewable-capacity and renewable-share series as an independent cross-check. The World Bank's World Development Indicators [CITE: World Bank WDI] supply the macroeconomic covariates the demand model needs — real GDP, population, urbanisation, industrial value added.

These four do not measure the same thing the same way, and the difference that matters most is the accounting boundary. The IEA reports electricity on the consumption boundary — energy delivered to end users, net of transmission-and-distribution (T&D) losses. StatSUZ reports on the supply boundary — energy dispatched into the grid, gross of those losses. Both are correct, and they sit about eight percent apart, because roughly eight percent of what enters the Uzbek grid never reaches a meter. Any analysis that mixed them without accounting for that gap would read a definitional difference as a real change in demand. The bridge in §3.4 exists precisely to prevent that error.

Three further feeds enter downstream, and Figure 3.1 shows where each sits on the timeline. A five-country Central Asian panel, built from Our World in Data and World Bank series [CITE: OWID Energy; World Bank WDI], lets the demand model borrow strength from Uzbekistan's neighbours (Chapter 4). The IMF's World Economic Outlook [CITE: IMF WEO April 2026] supplies the forward GDP and population path that drives the post-2024 scenarios. A curated dataset of 46 named power assets [CITE: REF asset dataset] underpins the fleet and spatial analysis of Chapter 2.

## 3.3 Harmonisation: one spine, one unit system

Before anything is compared, everything is placed on one spine and one set of units. The spine is a continuous annual index from 1990 to 2026; every series is left-joined onto it, so a gap appears as a missing value rather than a missing row, and no single source can silently shorten the record. Units are converted once, through named constants rather than inline arithmetic: electricity to terawatt-hours, gas to terajoules at the net calorific value adopted for the domestic blend, 38.1 MJ/m³ — modestly above IRENA's generic 36 MJ/m³. That choice moves no headline number: the converted gas series enters the dataset only as the two sides of a self-sufficiency ratio, where the calorific factor cancels, and the carbon series is read directly from the IEA and World Bank rather than reconstructed from gas volumes. Pinning the conversions in one place is still not housekeeping; it removes the most common class of late-stage error in a multi-source pipeline — the column silently read in the wrong unit.

## 3.4 The bridge: extending the record to 2024 without contaminating it

The most recent year is also the most decision-relevant, and it is the one the reference source does not yet cover. Closing that gap is a genuine methodological choice, and the report makes it explicitly rather than by default. Two alternatives were rejected. Replacing the IEA series with StatSUZ would have changed the level of the demand series — swapping a consumption-boundary number for a supply-boundary one — and contaminated every per-capita and intensity ratio built on it. Truncating at 2023 would have discarded the year the dashboard and the forecasting splits most need.

The pipeline uses ratio scaling instead. For each IEA–StatSUZ pair it computes the average ratio of the two over their common years (2010–2023), then multiplies the StatSUZ 2024 value by that ratio to infer the missing IEA-basis 2024 point. The level basis stays the IEA's; only the most recent observation is mechanically carried in from StatSUZ. The scale factor is itself informative. For consumption it is about 0.92 over the most recent five years — StatSUZ supply runs roughly eight percent above IEA consumption in the recent window the bridge relies on (over the full overlap the gap is wider, near thirteen percent; §3.5 reconciles the two). For generation it is close to 0.99 — the two sources agree on physical production to within one percent. That near-agreement on generation is what makes the bridge defensible: where the sources measure the same quantity on the same boundary they match, so the one place a scale factor is applied is the one place a known boundary difference explains the gap. The confirmed 2023 demand of 73.4 TWh extends to a bridged 2024 figure of about 77.7 TWh on this basis. The bridged values serve as trend lines and as the forecast's most recent anchor; they are not used for absolute cross-source level claims, and the report marks them as bridged wherever they appear.

## 3.5 Where the sources disagree — and why the disagreement is information

A multi-source dataset is only trustworthy if its disagreements are understood rather than averaged away. Two disagreements in this record deserve stating plainly, because both are convention differences that can masquerade as trends.

The first is the consumption-versus-supply gap already named. In principle it is the wedge of total grid losses and own-use that separates energy dispatched into the network from energy delivered to a meter, and across the earlier overlap it ran in the mid-teens — roughly thirteen to seventeen percent — the order of magnitude independent sources report for total losses on Uzbekistan's aging grid [CITE: IEA Uzbekistan Energy Profile, energy-security section; World Bank Electricity Distribution Improvement Project (P504630), 2025]. Over recent years the measured gap narrows to about eight percent, but this is not evidence that losses fell: independent figures still place technical distribution losses alone near twelve to thirteen percent through the early 2020s, so the narrowing most likely reflects the two series' boundaries partly realigning after the 2017–2019 statistical and structural reforms rather than a real improvement in the grid. The disagreement is therefore read as an order-of-magnitude indicator of how lossy the system is rather than a precise meter — and the broad mid-teens figure, anchored at the EDB's 17.8 percent for 2023, is the loss rate Chapter 6 returns to as an advisory signal.

The second is subtler and more dangerous, because it produces an apparent collapse that is entirely an artefact. The IEA balance reports oil as a single "oil and oil products" line — crude bundled with all refined products — which came to 11.4 percent of total primary energy supply in 2023. The StatSUZ balance reports crude and condensate (5.1 percent) separately from refined products (1.7 percent), a bundled 6.8 percent. Splice the two and oil appears to fall by almost half between 2023 and 2024; in reality nothing fell — the two balances simply draw the boundary of "oil" in different places [CITE: IEA Uzbekistan Energy Profile 2024; StatSUZ fuel-energy balance 2024]. The project refuses the splice: the 2024 composition is re-bucketed to StatSUZ's own convention and shown beside the IEA series rather than continuing it, and the two are flagged comparable only for gas and coal. The one fact robust to either convention is the one that matters most — gas supplies between 79 and 84 percent of primary energy whichever balance is used. The discipline here is general: where two sources disagree because they define a quantity differently, the report shows both and names the convention rather than letting the seam manufacture a trend.

A third source closes the anchor year. The Eurasian Development Bank's 2026 Central Asia Energy Outlook [CITE: EDB Central Asia Energy Outlook 2026] reads the same 2024 independently: its figures for demand, generation and installed capacity all sit within two percent of the StatSUZ-driven values used here. Three sources agreeing on the anchor year is the strongest external check this record allows.

## 3.6 What is provisional, and what the data permits

The record is explicit about what it does not yet know for certain. The years 2024 to 2026 are stamped preliminary — first-release or projected values the next statistical vintage may revise by several percent. The flag is not cosmetic: the forecasting models in Chapter 4 drop these years from their training folds, so that no model fits noise a later revision will erase, while the dashboard still displays them, labelled provisional. One series is corrected by hand, with the correction recorded in the open: the World Bank T&D-loss figures for 2018–2022 dip to physically implausible values (3.4 percent in one year, against a historical band of 13–17 percent), so those years are masked and 2023 is set to the EDB's 17.8 percent rather than carried from a number the source itself appears to have mis-stated [CITE: World Bank WDI; EDB Central Asia Energy Outlook 2026]. The same series also changes basis at its other end, and the change is sharp enough to be unmistakable: from 1990 to 2000 the recorded loss rate sits near 9% (9.4% in 1990, 9.3% in 2000), then steps to 15.3% in 2001 and stays in the 13–18% band every year through 2023 (17.8% that year). A loss rate does not nearly double in a single year; the 2000→2001 jump is a change in accounting basis — the earlier figures rest on a narrower definition — not a real collapse in grid performance. The like-for-like loss history therefore begins in 2001, and the pre-2001 ~9% figures are set aside [VERIFY: confirm whether the pre-2001 narrow basis is a documented WDI methodology change versus a reporting-coverage artefact]. This matters beyond bookkeeping: the ~9% that surfaces elsewhere in the project — in an early-series caption, in the forward loss-reduction target — is precisely *not* the realized modern loss rate, which is the ~16% the post-2001 record shows and which Chapter 6 treats as an advisory signal.

What all of this permits is a narrow but honest forecast. The data is short, it is assembled from boundaries that differ by construction, and its most recent year is provisional — so the methodology that follows forecasts on the confirmed IEA-basis series, treats the bridged year as a trend anchor rather than a hard fact, holds the provisional years out of training, and, because thirty points cannot carry a rich model alone, borrows structure from the cross-country panel. How those choices are made — and why a single-country model is deployed for the headline demand path while a pooled model is used to validate it — is the subject of Chapter 4.

---

# 4 — Methodology

## 4.1 The binding constraint, and the shape it forces

One number governs every modelling decision in this report: the usable sample is about thirty annual points. Chapter 3 established why — the confirmed record runs 1990–2023, the provisional years are held out, and the early-1990s contraction sits outside the modern regime. With a sample that small the binding constraint is not which model is cleverest but how little the data can support, and the entire method is built around that fact rather than against it. Specifications are kept parsimonious; coefficients are shrunk rather than freely estimated; model selection is confined to the training years; every model is scored as a genuine forecast rather than a fitted curve; and uncertainty is reported beside every point estimate instead of after it. The target is electricity demand — the spine of the system — from which renewable share, residual fossil generation and carbon intensity are then derived. Setting the method up this way is what lets the report draw the line it promised: a demand path it can predict with bounded confidence, and supply trajectories it can only bound.

## 4.2 From the data to the model: which drivers, and which model class

The driver set is inherited from the exploratory analysis, not chosen for convenience, and that inheritance is load-bearing. Each candidate was screened on its correlation with demand in levels and — the harder test — after first-differencing, which strips out the shared trend that makes almost any two growing series look related. Four drivers survive that screen and are kept: industrial value-added (the strongest detrended link, *r* ≈ 0.41 on differences), GDP per capita (*r* ≈ 0.42), services value-added (*r* ≈ 0.46), and cooling degree-days, a genuine summer-load signal and one of the few series that is stationary in its own right (*r* ≈ 0.42) [CITE: project EDA, Notebook 05]. A lagged demand term is added to absorb the series' unit root. Three candidates are deliberately excluded: population (collinear with GDP, no short-run signal), urbanisation (weak, retained only as a slow structural control where a near-zero weight is the expected result), and electricity tariffs (no continuous real-price series exists for the period — flagged as future work, not silently dropped).

Two findings from that same analysis decide the *model class*, not merely the feature list. First, GDP, industry and services move almost in lockstep — mutually collinear at *r* ≈ 0.99 — so ordinary least squares would produce unstable, sign-flipping coefficients. This is the formal justification for the ridge and Bayesian-ridge shrinkage used throughout: shrinkage trades a little bias for the stability an over-determined small sample needs [CITE: Tipping 2001; Hoerl & Kennard 1970]. Second, Granger tests find no significant short-run causality from income growth to demand growth (*p* ≈ 0.46), so these fits are read as associational-structural, not causal. That reading has a direct consequence for what the report puts forward as its headline: a predictive interval, not a single point path. It also fixes the status of the fitted weights — because the models are estimated in levels with shrinkage, the coefficients are regularised partial associations, **not elasticities**; reading them as the percent response of demand to a percent change in a driver would claim a causal precision the data cannot support.

## 4.3 Baselines, the order of integration, and why there is no error-correction model

The advanced models are required to beat an honest bench, so a ladder of baselines is fitted first: a naïve last-value carry-forward, a linear trend, a first-differenced regression, an AICc-selected ARIMA, Prophet, and a frequentist ridge [CITE: project Notebook 06]. The naïve model floors the bench at about 13.9% error and the linear trend is worst at about 30.6% — predictably, because it ignores the series' integration order. The decision to difference once — rather than twice, or not at all — rests on three converging lines rather than the single test reported above: the unambiguous unit root in the levels; an AICc grid that, left free to choose, independently selects one order of differencing; and the parsimony argument that a second difference would over-smooth a thirty-point macro series and inflate forecast variance. The post-differencing diagnostics are genuinely mixed — at twenty-eight points the differenced ADF still does not reject and KPSS now flips the other way — and that ambiguity is reported rather than hidden, because it is the textbook small-sample artefact of a low-power test on a series dominated by one large 2017–18 jump [CITE: Box, Jenkins & Reinsel 2015].

The same short sample is the reason this report stops short of an error-correction model, the standard tool for linking demand to its economic drivers in the long run. An error-correction model requires a cointegrating relationship estimated from the levels, and the test for one is badly underpowered at thirty observations; fitting it anyway would manufacture a long-run equilibrium the data cannot actually evidence. First-differencing and a lagged-demand term capture what the sample can genuinely support, and the report declines the false precision of the richer specification.

## 4.4 The honest scoring rule: ex-ante, not backcast

A driver-based model can be scored on the 2019–2023 hold-out in two very different ways, and the difference is the most important methodological choice in the report. The flattering way — a conditional backcast — feeds the model the *observed* values of its drivers over the hold-out, so it is never asked to forecast its own inputs; this yields an impressive error of roughly 4–4.6%. The honest way — *ex-ante* scoring — forecasts each driver in turn (macro drivers as a log random walk with drift, climate from its recent climatology) and feeds the lagged-demand term recursively from the model's own predictions, exactly as a real forecast must. On that basis the single-country models' error rises to about 9–10%. The gap between the two numbers is precisely the advantage a backcast quietly grants itself, and this report headlines the ex-ante figure and keeps the conditional one only as a labelled optimistic bound (Table 4.1, Figure 4.1). The earlier interim figures in the low single digits were conditional backcasts; they are not the headline.

The hold-out is, by design, a hard one. The 2019–2023 window contains the post-2018 demand surge — roughly a 27% jump over the 2018 level — so any model trained only on 1990–2018 under-predicts it, and most post a **negative** hold-out R². The same five-year window also straddles the COVID-19 shock: Uzbek electricity consumption fell about 1.8% in 2020 — a contraction with no parallel in the surrounding 2015–2023 demand run-up — before rebounding roughly 23% in 2021. The hold-out therefore superimposes a transient pandemic dip on the post-2018 structural surge, two disturbances of opposite sign, neither of which a parsimonious model trained on the smooth pre-2019 record can anticipate; the pandemic distortion deepens the out-of-sample difficulty rather than relieving it, and is one more reason the headline ~9–10% ex-ante error is a hard-won figure rather than a pessimistic one. That negative score is the finding, not a flaw in the model: it measures how far the recent, policy-driven regime departs from any smooth extrapolation of the prior three decades, and demonstrates that no parsimonious model anticipates a structural break it was never shown. To keep the test clean, the ridge penalty is selected by expanding-window one-step-ahead cross-validation on the training years alone, never on the hold-out — tuning a model on the data used to judge it would invalidate the comparison — and standardisation is likewise fit on the training window only.

![Figure 4.1](../outputs/forecast_scoreboard_exante.png)

*Figure 4.1. The demand-model scoreboard on the single 2019–2023 hold-out. Bars show the ex-ante error each model incurs when it must forecast its own drivers and propagate the demand lag recursively; hollow markers show the conditional backcast on observed drivers, kept only as the optimistic reference. Single-country models cluster near 9–10% with negative hold-out R² against the deliberate post-2018 structural break; the pooled Central-Asia models lead at about 6% and turn R² positive. Source: forecast_scoreboard_advanced.csv (project Notebook 07).*

**Table 4.1. Demand models on the 2019–2023 hold-out (single test window).** Ex-ante is the headline; the conditional backcast is reported for reference only.

| Model | Family | Ex-ante MAPE | Ex-ante R² | Conditional MAPE *(ref.)* |
|---|---|---:|---:|---:|
| ARIMA(1,1,0) | time-series baseline | 9.2% | −0.27 | — |
| Ridge — Uzbekistan (minimal) | single-country driver | 9.7% | −0.66 | 4.6% |
| Ridge — Uzbekistan (extended) | single-country driver | 9.0% | −0.37 | 4.0% |
| Bayesian Ridge — Uzbekistan (minimal) | single-country driver | 9.0% | −0.39 | 4.4% |
| **Bayesian Ridge — Uzbekistan (extended) — deployed** | single-country driver | 10.1% | −0.84 | 4.3% |
| Pooled Ridge — 4 Central-Asia + fixed effects | pooled *(validation)* | 6.1% | +0.10 | 4.6% |
| Pooled Bayesian Ridge — 4 Central-Asia + fixed effects | pooled *(validation)* | 6.2% | +0.06 | 4.6% |

*The ARIMA(1,1,0) — a purely extrapolative model that uses no drivers, hence no conditional-backcast column — posts the best ex-ante error in the table and edges the deployed driver model (9.2% versus 10.1%); on a five-point hold-out the two are statistically indistinguishable. It is nonetheless not the deployed model, for the reason §4.5 sets out: a univariate time-series model cannot generate the driver-conditioned demand fan of Chapter 5 or the supply scenarios of Chapters 5–6 on which the advisory product rests. Exact figures: ARIMA 9.221% / R² −0.266; deployed Bayesian ridge 10.138% / R² −0.838 (project Notebook 06/07).*

## 4.5 Borrowing strength, and why the deployed model is the single-country one

A negative hold-out R² is the problem the rest of the method has to answer: thirty Uzbek points simply cannot span a regime they never contained. The answer is to widen the sample sideways. A pooled model is fitted across the four Central-Asian countries with complete driver coverage — Kazakhstan, Kyrgyzstan, Tajikistan and Uzbekistan — giving roughly ninety-five country-years against Uzbekistan's thirty-four, with Kazakhstan as the fixed-effect reference [CITE: Hsiao 2014; IEA Central Asia Energy Outlook 2024]. Turkmenistan, a structurally similar gas economy and in principle a useful peer, drops out because its macroeconomic series are incomplete — a credible neighbour lost to data rather than excluded by choice, and named as such. Pooling rests on an explicit assumption: that the *response structure* linking income, industry and climate to demand is broadly common across the region, while persistent *level* differences between countries are absorbed by the country fixed effects. The payoff is decisive in the one place it matters — the pooled models reach about 6% ex-ante error with **positive** hold-out R² (+0.06 to +0.10), because the borrowed country-years let the model observe income-driven demand growth that Uzbekistan's own history could not show it. The roughly ninety-five country-years available become about seventy-two once the hold-out is withheld, so the pool is wider than Uzbekistan's record but is itself still a small sample.

Pooling earns its keep, but a leave-one-country-out test shows precisely how far that keep extends — and where it stops. Refitting the panel with one country wholly withheld and then predicting it from the other three turns the held-out error into a direct measure of how transferable the shared structure is. The results are uneven and instructive: the small hydro systems are predicted well from their neighbours (Tajikistan 8.1%, Kyrgyzstan 11.7% MAPE), while the large fossil systems transfer worst (Kazakhstan 23.4%, Uzbekistan 19.6%) [CITE: project Notebook 07, leave-one-country-out cell]. The reading is two-sided, and the report keeps both sides. Pooling validates the *structure* — a common income–industry–climate response does generalise across the region, which is what turns the pooled hold-out R² positive — but Uzbekistan is among the hardest countries in the panel to predict *from the others*, so the pooled 6% is a panel average that flatters the Uzbek-specific case rather than a promise that Uzbekistan has become easy to forecast. The pooled model corroborates the single-country one; it does not supersede it.

That the regularised-linear class is the right one is itself tested, not assumed. A gradient-boosted regression-tree ensemble (XGBoost) — the one machine-learning model tested against the regularised-linear class — scores far worse on the same pooled panel, about 13% MAPE, because a high-variance learner cannot exploit ninety-odd country-years and over-reacts to Tajikistan's small, volatile system; and a SHAP decomposition of that tree independently reproduces the exploratory screen, attributing almost all explained demand to GDP per capita and industrial value-added and almost none to urbanisation, population or the country dummies [CITE: Lundberg & Lee 2017]. The chain from the correlation analysis through feature selection to the fitted model is therefore internally consistent rather than merely asserted.

Why, then, is the deployed model a *driver* model at all, when the best ex-ante score in Table 4.1 belongs to the ARIMA(1,1,0) — 9.2% against the deployed model's 10.1%? The concession is granted plainly: on the five-point hold-out the ARIMA edges every driver specification, and the gap between it and the regressions is statistically meaningless on so short a window. Accuracy on the demand line is simply not the binding requirement. The advisory product is not a single demand number; it is the driver-conditioned predictive fan of Chapter 5 and the supply scenarios of Chapters 5 and 6, and **only a driver model can generate either.** A univariate ARIMA extrapolates demand from its own past and offers no channel through which income, climate, or a renewable build-out path can enter; it cannot be widened into a fan conditioned on macroeconomic scenarios, and it cannot be turned into a generation mix and a carbon-intensity path. The ARIMA wins the narrow contest and loses the deployable one — it is reported as the honest extrapolative benchmark, and then set aside.

Among the driver models, the *single-country* specification is deployed rather than the lower-error pooled one, for a reason of target rather than skill. The single-country models forecast the project's own reported series — the bridged IEA–StatSUZ consumption path of Chapter 3 — whereas the pooled models forecast the harmonised cross-country series, comparable across the four countries but defined on a different basis. The pooled model's 6% is therefore earned on a different target; the cross-family comparison is indicative rather than exact, and a pooled number could not be reported as the Uzbek consumption path without reintroducing the boundary mismatch Chapter 3 worked to remove. So the single-country model is deployed because it forecasts exactly the series the report and dashboard carry, and the pooled model **validates** it — its positive R² and 6% error are the external evidence, which the single-country hold-out cannot itself supply, that the structural relationship survives once the sample is widened. Among the four single-country specifications, all post negative R² and cluster within a point of one another, so the break-dominated window cannot rank them; the extended Bayesian ridge is chosen because its drivers are the ones the analysis validated as structural and because it returns the predictive standard deviation the Chapter 5 fan is built from — not because it won a contest the hold-out is too short to decide.

## 4.6 From demand to supply, and what the method can and cannot deliver

The advisory question is finally about supply — renewable share, residual fossil generation and carbon intensity — so the method closes the chain from the demand forecast through the generation mix to emissions, regenerated from the live model rather than from a retired snapshot. The supply scenarios are pinned to the deployed Bayesian-ridge baseline demand path: total generation is set to demand grossed up for grid losses, and the three scenarios then differ **only** in renewable build-out ambition, leaving demand uncertainty to the separate predictive fan. The capacity figures behind each scenario are taken from published targets or reported actuals, none invented. Two assumptions in this step are stated plainly because they shape the result. The forward grid-loss rate used to gross demand up into required generation is held at about 9% — a loss-*reduction target*, well below the realized ~16% band (17.8% in 2023) Chapter 3 documented; the two are not in conflict, but the gap between today's losses and the assumed target is itself an advisory signal, and Chapter 6 opens by reconciling the two and quantifying that gap as the system's modernization prize. And because the IMF World Economic Outlook drivers end in 2031, the 2032–2040 tail holds the terminal growth rate flat — a transparent, growth-optimistic choice that lifts 2040 demand toward roughly 124 TWh and, by raising the denominator, makes the renewable-share targets *harder* to reach. The three supply paths are therefore read as demanding policy envelopes, not point forecasts.

This is also where the limits of the method must be stated, not deferred. The probabilistic fan around the demand path combines the model's predictive standard deviation — which captures parameter and residual uncertainty — with three calibrated macro scenarios. It does **not** capture the error in forecasting the drivers themselves, the uncertainty of having chosen one model class over another, or the structural-break risk the hold-out so clearly exposed. The reported intervals are therefore best understood as **lower bounds** on the true uncertainty, not its full width. With that honestly marked, the division of labour for the rest of the report is set: the method can predict a demand path and attach a defensible, if conservative, band to it; it can only *bound* the supply trajectories, which turn on policy and investment choices no statistical model can foresee. Chapter 5 turns this machinery on the data and reports what it produces.

---

# 5 — Forecasts and scenarios to 2040

## 5.1 How to read this chapter

This chapter reports four things: a demand path to 2040, the probabilistic fan around it, and three supply scenarios that turn that demand into a renewable share, a residual fossil-generation path, and a grid carbon-intensity path. Each is presented the same way — first what the exploratory analysis led the report to expect, then what the model actually produced, then whether the two agree. That ordering is deliberate. A forecast that merely confirms the descriptive chapters adds little; a forecast that contradicts them is either a discovery or a bug, and saying in advance what was expected is what makes the difference legible. Every result carries its caveat inline, where the number is, rather than in a footnote the reader can skip.

One framing point governs everything that follows. The demand path is a *forecast* — predicted, with a band. The three supply scenarios are *not* forecasts; they are conditional projections that share the single demand path and differ only in how fast renewables are built (§4.6). They are named for their build-out ambition — **BAU**, **Government**, and **Accelerated** — so that "Accelerated" never doubles as a demand-side label. Reading the scenario spread as a probability distribution over outcomes would misread it: it is a set of "if-then" envelopes, and the policy choice, not the data, decides which one the country lands on.

## 5.2 The demand path

The exploratory analysis predicted that electricity demand would keep climbing and that income would be the engine: demand, GDP per capita, industrial and services value-added all trend upward almost in lockstep (mutually correlated at *r* ≈ 0.99, §4.2), and cooling demand adds a genuine summer-load signal on top. Nothing in the data suggested demand was near saturation. The forecast bears this out without surprise (Figure 5.1). The deployed extended Bayesian-ridge model projects demand rising from **73.98 TWh in 2024 to 86.01 TWh in 2030** — about 2.5% a year, accelerating across the window as the income drivers compound — and then, on the held-flat terminal-growth tail that begins where the IMF driver path ends in 2031 (§4.6), continuing to roughly **123.9 TWh by 2040** [CITE: deployed BayesianRidge demand path, project Notebook 07 §8; IMF WEO April 2026 driver path]. These figures match the dataset's own most recent anchor: the bridged 2024 demand of about 77.7 TWh on the IEA-consumption basis of §3.4 and the model's 73.98 TWh starting value are the same quantity read on two boundaries, and the report does not blur them.

The 2040 figure should be read as the deliberately growth-optimistic end of a plausible range, not a central expectation. Holding the terminal growth rate flat across 2032–2040 is a transparent assumption that lifts demand rather than letting it taper, and it has a specific consequence the next sections rely on: a higher demand denominator makes every renewable-*share* target harder to reach, so the scenarios are tested against a demanding load, not a flattering one.

![Figure 5.1](../data/processed/forecast_demand_bayes_ridge.png)

*Figure 5.1. Deployed demand forecast, 2024–2030, from the extended Bayesian-ridge model, with the 90% predictive band. Demand rises from 73.98 TWh (2024) to 86.01 TWh (2030); the 90% band widens from [66.4, 81.6] to [76.7, 95.3] TWh. The band is the model's own predictive standard deviation and is a lower bound on true uncertainty (§5.3). The shaded 2020–21 band marks the COVID-19 demand shock — a ~1.8% dip in 2020 followed by a sharp 2021 rebound, retained rather than smoothed because it is part of why the 2019–2023 hold-out is hard (§4.4). Source: forecast_demand_bayes_ridge.csv (project Notebook 07 §8).*

## 5.3 The fan, and why it is a lower bound

The exploratory work gave no reason to expect a tight forecast — thirty observations, a structural break in 2017–18, and drivers that must themselves be projected all argue for a wide band — and the fan is correspondingly wide. At 2030 the model's 90% predictive band runs from **76.7 to 95.3 TWh** around the 86.0 central value (roughly ±11%); extended to 2040 the published fan reaches **[110, 137] TWh at 80% and [103, 145] TWh at 95%** confidence [CITE: forecast_demand.csv, project Notebook 07 §8]. 

What matters more than the width is what the width does *not* include, and this is stated wherever the fan appears. The band is built from the model's predictive standard deviation — parameter and residual uncertainty — combined with the macro scenarios. It does not propagate the error in forecasting the drivers themselves, the recursive-lag error that compounds as each year's prediction feeds the next, or the model-choice and structural-break risk the negative hold-out R² exposed (§4.4). The reported intervals are therefore **lower bounds** on the true uncertainty. A reader who treats the 95% band as a genuine 95% interval will be overconfident; the honest claim is narrower — that the true uncertainty is *at least* this wide.

## 5.4 From demand to generation: one path, three mixes

The supply scenarios begin by converting demand into the generation that must be dispatched to meet it. That conversion grosses demand up for grid losses at the forward target rate of about 9% (the loss-reconciliation Chapter 6 opens with), so total generation runs from **80.6 TWh in 2024 to 93.8 TWh in 2030 and 135.1 TWh in 2040** — and this single generation path is **identical across all three scenarios** [CITE: forecast_scenarios.csv, project Notebook 07 §8]. The scenarios diverge only in how that fixed total is split among thermal, hydro, solar, and wind. Holding the total constant is what isolates the one variable of interest — build-out ambition — from demand uncertainty, which lives entirely in the separate fan of §5.3. It also means the scenario spread says nothing about whether demand is high or low; it speaks only to the mix.

## 5.5 Renewable share

Chapter 2 predicted that the renewable share could rise only as fast as new solar and wind are built, because hydropower is already fully used and gas cannot decarbonise itself — decarbonisation here is a construction story, not a re-dispatch. The scenarios make that prediction quantitative, and they bear it out with one important nuance (Figure 5.2). From a 2024 base, the renewable share by 2030 reaches **43.1% under BAU, 58.4% under Government, and 70.8% under Accelerated**; by 2040 the three diverge sharply — **36.5%, 60.0%, and 80.0%** respectively [CITE: forecast_scenarios.csv]. The nuance is the BAU trajectory: its share *peaks* near 2030 and then *declines*, because in BAU the contracted solar-and-wind pipeline is completed but not extended, so once demand keeps climbing after 2030 the system meets the increment by burning more gas, and the renewable share slides backward. A build-out that is not sustained does not merely stall the transition; it reverses it.

A caution on the base year belongs here, inline — and it resolves cleanly once the construction is understood. The scenario engine does not start from a 2024 share and add increments; it builds each year's renewable share from that year's *capacity targets multiplied by a technology capacity factor*. The 2024 value this produces — about 22.6% total renewables (10.3% non-hydro) — runs *higher* than the independently sourced figure Chapter 2 reports for the same year (about 16% total, under 6% non-hydro, OWID/Ember basis), because the reconstruction credits newly commissioned 2024 plant with a full year of output it did not physically run. That makes the 2024 base a partial-year artifact. Crucially, because every later share is computed forward from the 2030 capacity targets rather than carried up from 2024, the artifact **does not propagate**: the 2030 and 2040 shares — and the §5.8 verdicts that rest on them — are unaffected (BAU, for instance, clears the 40% generation target down to a solar capacity factor of about 0.145, so its margin is structural, not an artefact of the base). The absolute 2024 base is the one number not to quote on its own; the trajectories and the inter-scenario spread are sound [VERIFY: optional — re-seed the scenario 2024 solar/wind from metered rather than capacity-implied generation to remove the partial-year discontinuity at the historical/scenario join; not required for the 2030/2040 conclusions].

![Figure 5.2](../data/processed/forecast_scenarios.png)

*Figure 5.2. Generation mix and renewable share under the three supply scenarios, 2024–2040. All three share one total-generation path (80.6 → 135.1 TWh) and differ only in build-out. The renewable share reaches 43.1% / 58.4% / 70.8% by 2030 (BAU / Government / Accelerated) and 36.5% / 60.0% / 80.0% by 2040; note the BAU share peaks near 2030 and then declines as unsustained build-out cedes the demand increment back to gas. Source: forecast_scenarios.csv (project Notebook 07 §8).*

## 5.6 Residual fossil generation

The same logic, read on the fossil side, produces the sharpest single number in the chapter. Chapter 2 observed that demand growth had historically been met by burning more gas, with thermal output growing about 2.5% a year while hydro flatlined. The scenarios show that pattern either breaking or continuing, depending entirely on build-out. Thermal generation, **62.4 TWh in 2024**, falls under every scenario to 2030 (to 53.3, 39.0, and 27.4 TWh under BAU, Government, and Accelerated) — but then the paths split violently. By 2040 thermal generation is **85.8 TWh under BAU — higher than today** — against 54.0 TWh under Government and a flat **27.0 TWh under Accelerated** [CITE: forecast_scenarios.csv]. The BAU result is the one to dwell on: it is not that decarbonisation merely stalls, but that absolute fossil generation in 2040 *exceeds* the 2024 level, because a rising demand denominator with a frozen renewable build forces more gas through the system than runs through it today. The transition is not self-sustaining; left to the completed pipeline alone, the fossil fleet grows.

## 5.7 Carbon intensity

Grid carbon intensity follows mechanically from the mix. The exploratory analysis measured the historical grid at about **668 gCO₂/kWh in 2023** — within a 590–825 gCO₂/kWh range across the record, settling to roughly 590–680 from 2018 onward as the fuel mix held steady [CITE: project Notebook 03 §8]. The scenario engine, however, reconstructs a 2024 starting intensity of about **520–530 gCO₂/kWh** — some 140 g below the EDA's own 2023 measurement, a one-year drop of roughly a fifth that the physical system did not undergo. The seam has the same origin as the renewable-share base discussed in §5.5: the scenario's 2024 mix is implied from capacity figures rather than read from the metered generation series, so it understates the gas share in the partial-year base. The scenario *paths* are nonetheless sound, because each later year's intensity is built forward from that year's generation mix — and from 2030 onward the mix is set by published capacity targets, not by the 2024 base — so the artifact is a base-year seam that does not propagate into the 2030 and 2040 figures [VERIFY: optionally re-anchor the scenario's 2024 carbon intensity to the metered ~590–668 gCO₂/kWh EDA value for internal consistency; the 2030/2040 results are unaffected]. Read forward from that reconstructed base, the scenarios drive intensity in three directions (Figure 5.3). By 2030 carbon intensity falls to **390 gCO₂/kWh under BAU, 245 under Government, and 172 under Accelerated**; by 2040 the spread is enormous — **436, 179, and 90 gCO₂/kWh** respectively [CITE: forecast_co2.csv, project Notebook 07 §8]. The BAU path again bends the wrong way after 2030: intensity *rises* from 390 back to 436 gCO₂/kWh as thermal generation regrows, so the business-as-usual grid in 2040 is dirtier per kilowatt-hour than it was in 2030. In absolute terms, annual power-sector CO₂ runs from about 42–43 Mt in 2024 to **58.9 Mt (BAU), 24.2 Mt (Government), and 12.1 Mt (Accelerated) in 2040** [CITE: forecast_co2.csv]. The gap between the BAU and Accelerated endpoints — a factor of nearly five in carbon intensity — is the whole stake of the transition expressed in one comparison, and it is decided by build-out policy, not by anything the demand forecast can settle.

![Figure 5.3](../data/processed/forecast_co2.png)

*Figure 5.3. Power-sector carbon intensity (gCO₂/kWh) under the three scenarios, 2024–2040. From a reconstructed 2024 base of ~520–530 gCO₂/kWh — below the ~668 gCO₂/kWh the exploratory analysis metered for 2023 (§5.7) — intensity reaches 390 / 245 / 172 by 2030 and 436 / 179 / 90 by 2040 (BAU / Government / Accelerated). BAU intensity rises after 2030 as thermal regrows. Source: forecast_co2.csv (project Notebook 07 §8).*

## 5.8 The scenarios against the legislated targets

Set beside Uzbekistan's own targets, the scenarios reveal which commitments are easy and which are binding. The legislated goal is a 40% renewable *generation* share and roughly 27 GW of renewable *capacity* by 2030, with the presidency aspiring to a 54% share (§1.2). On the generation-share test, the results are almost anticlimactic: **all three scenarios clear 40% by 2030** — even BAU, at 43.1% — so the headline share target is not, on these projections, the demanding constraint. The harder tests are two. First, the *capacity* target: total renewable capacity at 2030 reaches about **18 GW under BAU, 24.7 GW under Government, and 30.2 GW under Accelerated**, so only the Accelerated build meets the 27 GW commitment, and the Government path falls modestly short [CITE: forecast_scenarios.csv capacity columns]. Second, and more revealing, *sustaining* the share past 2030: only the Government and Accelerated paths hold or extend it, while BAU surrenders it. The presidential 54% aspiration, for its part, is reached by 2030 only under the Government and Accelerated builds, not BAU. The advisory reading is clean: the 2030 share headline will likely be met on momentum, but the capacity target and the post-2030 trajectory are where ambition actually has to be financed — and that is precisely where Chapter 6 locates the opportunity.

---

# 6 — Investment signals and advisory opportunity

## 6.1 The loss-rate reconciliation, and the prize it defines

One number must be reconciled before any signal in this chapter can be read, because two very different versions of it circulate through the project. Uzbekistan's realized transmission-and-distribution losses are chronic and high: the post-2001 record sits in a 13–18% band every year, the five-year rolling mean stands at **16.3%**, and the most recent confirmed figure is **17.8% in 2023** (§3.6) [CITE: World Bank WDI; EDB Central Asia Energy Outlook 2026]. The competing **~9%** figure that appears in the project's forward conversion and in some early captions is *not* a measurement of today's grid — it is two different things wearing the same digits: the pre-2001 narrow-basis loss series (§3.6), and the government's forward loss-*reduction target* used to gross demand up into generation (§4.6 and §5.4). Holding these apart is the whole point. The realized rate is ~16%; the target is ~9%; and **the gap between them is the modernization prize.** Roughly seven percentage points of the energy entering Uzbekistan's grid is lost above what a modernised network would lose — energy that is generated, often by burning imported-grade gas, and then never billed. Closing that gap is simultaneously a decarbonisation lever, a cost recovery, and a deferral of new generation, and it is the single largest efficiency opportunity the data points to (Figure 6.1).

![Figure 6.1](../data/processed/eda_td_losses.png)

*Figure 6.1. Transmission-and-distribution losses, 1990–2023. The series steps from ~9% before 2001 to a 13–18% band thereafter — a change in accounting basis, not a real doubling (§3.6) — and the modern record stays chronically near 16%, reaching 17.8% in 2023. The forward conversion target of ~9% (§5.4) is a policy goal, not the realized rate; the gap is the modernization opportunity of §6.5. Source: investment_signal_td.csv (project Notebook 08).*

## 6.2 Signal 1 — Reserve headroom, not a forecast deficit

The first signal must be stated carefully, because its construction invites an overclaim the report declines to make. The deficit analysis compares required generation (demand grossed up for losses) against planned supply — but planned supply is *set equal* to the central required generation, so at the central demand path the system balances by construction and the point deficit is zero in every year [CITE: investment_signal_deficit.csv, project Notebook 08]. There is therefore no forecast "supply gap" along the central path, and the report does not claim one. The genuine signal is the **reserve headroom the demand uncertainty implies**: at the upper-80% demand band, required generation exceeds the central plan by about **6.5 TWh in 2024, widening to 14.8 TWh by 2040** [CITE: investment_signal_deficit.csv]. That is the capacity margin the build-out must carry to stay adequate against a plausibly higher load — a reserve-planning quantity, identical across the three scenarios because it is driven by the shared demand fan rather than by build-out ambition. The year-by-year "deficit/stress" flags in the underlying table alternate on rounding noise around a zero point estimate and should not be read as a calendar of shortfalls; the substantive number is the widening reserve requirement.

## 6.3 Signal 2 — Gas-import exposure

The second signal makes Chapter 2's gas-dependence concrete and forward-looking. Gas burned for power generation stands at about **17.7 bcm in 2024**, and its 2040 value is a direct function of build-out: it **rises to 24.3 bcm under BAU**, falls to **15.3 bcm under Government**, and falls sharply to about **7.7 bcm under Accelerated**, where it plateaus from 2030 (gas is assumed to supply 88% of thermal output) [CITE: investment_signal_gas.csv, project Notebook 08]. The exposure this measures is both fiscal and strategic: Uzbekistan is a net gas exporter that turns net importer in winter (§2.6), so every bcm burned for domestic power is a bcm not exported and, at the winter margin, a bcm imported. The BAU path therefore does not merely emit more carbon; it deepens the country's exposure to gas-price and gas-supply shocks at exactly the season the grid is tightest, while the Accelerated path more than halves gas-for-power and insulates the system. Renewable build-out reads, in this signal, as energy-security policy as much as climate policy.

## 6.4 Signal 3 — The persistence of grid losses

The third signal is the loss rate of §6.1 read as a *trend* rather than a level: losses have not merely been high, they have been stubbornly stable near 16% for two decades, with no downward trajectory in the confirmed record (Figure 6.1) [CITE: investment_signal_td.csv]. Persistence is itself the signal. A loss rate that drifted down would suggest the problem is being solved by incremental maintenance; a loss rate pinned at 16% across twenty years of rising demand indicates chronic underinvestment in transmission and distribution that ordinary operations will not fix. This is the demand-side complement to the supply-side opportunity: the same network that loses a sixth of its throughput is the network that must absorb a west-to-east renewable build and a five-fold swing in possible 2040 carbon intensity. The persistence finding is what turns grid modernization from a maintenance line item into a structural advisory engagement.

## 6.5 Capital envelopes, mapped to the advisory categories

The signals above imply capital, and the model sizes it — with a caveat that must travel with every figure. The capex numbers are **undiscounted, constant-cost upper-bound envelopes**: unit costs multiplied by capacity added, with no discounting, no learning-curve cost decline, and no financing structure. They bound the capital mobilised; they are not net-present-value estimates, and they should be read as the high end of a range [CITE: investment_signals.csv, project Notebook 08]. On that basis the total 2024–2040 build-out envelope is about **$27.3 bn under BAU, $56.9 bn under Government, and $79.3 bn under Accelerated**, with wind and solar the largest line items in every scenario (Government: wind $16.0 bn, solar $13.1 bn, thermal $12.1 bn, hydro $8.4 bn, transmission $6.2 bn, storage $1.1 bn) [CITE: investment_signals.csv] (Figure 6.2).

![Figure 6.2](../data/processed/forecast_investment.png)

*Figure 6.2. Capital envelope by technology and scenario, 2024–2040 (undiscounted, constant-cost upper bounds). Total build-out runs ~$27.3 bn (BAU), ~$56.9 bn (Government), ~$79.3 bn (Accelerated); wind and solar dominate. Source: investment_signals.csv (project Notebook 08).*

Mapped to the five categories through which an engineering-advisory practice would engage, the Government-path programme falls out as follows [CITE: ILF opportunity table, project Notebook 08 §15]:

| # | Advisory category | What it covers | Indicative envelope |
|---|---|---|---:|
| 1 | **Generation build** | ~25 GW of new renewable capacity to the government target | ~$28 bn |
| 2 | **Grid modernization** | ~6,000 km of HV lines plus a ~1,450 km wind-corridor evacuation, and the loss-reduction programme of §6.1 | ~$3.0 bn |
| 3 | **Renewable integration** | balancing and storage (~5 GWh BESS) to absorb a ≥40% variable share | ~$2.0 bn |
| 4 | **Energy efficiency (NEEA)** | tariff reform and demand-side efficiency | ~$1.5 bn |
| 5 | **PPP / IFI advisory** | structuring the EBRD / ADB / IFC project pipeline | advisory fees |

*The category figures are NB08's curated advisory cut and rest on a slightly different basis than the technology envelope above (for instance, the ~$28 bn generation line is close to, but not identical with, the scenario's combined solar-and-wind capex); both are upper-bound envelopes and the two cuts are not meant to reconcile to the dollar [VERIFY: confirm the exact basis of the NB08 §15 category figures against investment_signals.csv].*

The mapping is the chapter's payoff. Generation build is the largest envelope but also the most contested commercially; grid modernization and renewable integration are smaller in dollars but are where the loss-persistence and reserve-headroom signals make engagement close to unavoidable; and the efficiency and PPP-structuring categories are where advisory fees, rather than capital, accrue. The opportunity is not uniform across the programme — it concentrates exactly where the structural signals are sharpest.

## 6.6 Plan B — firm low-carbon capacity at Jizzakh

One contingency sits outside the three renewable scenarios and is modelled as a parametric overlay rather than folded into the baseline, because its construction has only just begun and Central Asia has no commissioning precedent. The Jizzakh nuclear plant — a 2.1 GW integrated station pairing two VVER-1000 reactors with two RITM-200N small modular units (§2.4) — would add firm, dispatchable low-carbon capacity inside the eastern demand centre, close to load and reducing how much western renewable power must be wheeled across a lossy grid [CITE: Rosatom / Uzatom Jizzakh project record, 2025; World Nuclear News]. The notebook tests nuclear parametrically across a **1.2–3.6 GW** range commissioning in 2030–2034, and the real 2.1 GW plant sits squarely inside that tested range (Figure 6.3). At the 1.2 GW grid point, nuclear adds about 8.9 TWh a year and lifts the Government scenario's combined renewable-plus-nuclear share at 2040 from 60.0% to **66.6%**; at 2.4 GW it reaches 73.3% [CITE: forecast_scenarios_with_nuclear.csv, project Notebook 08]. The real plant, at 2.1 GW, would fall between these — on the order of 15–16 TWh of firm output. As an undiscounted envelope the nuclear option carries a **$6–18 bn** cost across the parametric range [CITE: project Notebook 08]. The honest framing is that Jizzakh is neither in nor out of the central projection: it is a firm-capacity hedge whose value rises precisely if the renewable build-out underperforms, which is why the report carries it as Plan B rather than as a scenario assumption.

![Figure 6.3](../data/processed/signal_planb_nuclear.png)

*Figure 6.3. Nuclear sensitivity overlay (Plan B). Combined renewable-plus-nuclear share at 2040 under the Government build for nuclear capacities of 0 / 1.2 / 2.4 / 3.6 GW: 60.0% / 66.6% / 73.3% / 79.9%. The actual Jizzakh plant (2.1 GW integrated VVER-1000 + RITM-200N) sits inside the tested 1.2–3.6 GW range. Source: forecast_scenarios_with_nuclear.csv (project Notebook 08). Note: NB08's parametric default is labelled 1.2 GW and predates the project's 2.1 GW integrated scope (§2.4); the figure brackets rather than fixes the plant.*

## 6.7 Delivery: the transition tracker dashboard

The signals above are delivered to the client through an interactive dashboard (project Notebook 10), and its surfaced numbers now mirror the deployed model exactly. The dashboard organises the analysis into four areas — an overview (country snapshot and electricity demand), a by-source view (gas, hydro, solar, wind, coal, installed capacity), a transition-signals view (CO₂ and the investment outlook), and a resources view (documents, news, methodology, glossary) — and renders the historical 1990–2023 record alongside the 2024–2040 projection [CITE: project Notebook 10]. Its hero panel reports the deployed Bayesian-ridge demand path — 86.0 TWh in 2030 rising toward 124 TWh in 2040 — names the extended Bayesian ridge as the deployed model, and carries the realized loss rate of ~16% (17.8% in 2023) of §6.1 rather than the 9% forward target. The renewable-share, carbon and capital panels read from the same scenario files as Chapter 5, so the Government-scenario figures on the landing page — a 58.4% renewable share, 22.9 Mt of power-sector CO₂ and a $56.9 bn capital programme by 2030 — are the Chapter 5 and Chapter 6 numbers rather than a separate calculation. The provisional years are displayed but labelled as such, and the methodology and glossary panels describe the deployed shrinkage-regression approach rather than the earlier forecasting bench. The tracker is the mechanism through which the client monitors each signal as new annual data arrives, and its surfaced numbers are reconciled to the deployed model.

---

# 7 — Limitations and future work

The limitations of this analysis have been stated inline throughout, where each result appears; this chapter consolidates them so they can be weighed together, and then points to the work that would relax them.

**The sample is small, and one break dominates it.** About thirty usable annual observations underlie every estimate, and the 2017–18 demand surge is large enough that the 2019–2023 hold-out is effectively a test of whether a model can predict a structural break it was never shown; the same window also contains the 2020 COVID-19 demand dip, a second, opposite-sign shock that the pre-2019 record gave the model no way to anticipate. It cannot, which is why the single-country hold-out R² is negative (§4.4). This is not a defect to be engineered away at *n* ≈ 30; it is the honest ceiling on what the data can support, and it is the reason the report headlines an ex-ante ~9–10% error rather than the flattering conditional ~4–5% (§4.4).

**The intervals are lower bounds.** The predictive fan captures the model's parameter and residual uncertainty but not the error in projecting the drivers, the compounding of the recursive demand lag, or model-choice risk (§5.3). Reported bands are therefore narrower than the truth, and should be read as a floor on uncertainty.

**The coefficients are not elasticities.** Because the drivers are mutually collinear at *r* ≈ 0.99 and the model is estimated with shrinkage, the fitted weights are regularised partial associations tuned for prediction; reading them as causal income or price elasticities would claim a precision the data cannot bear (§4.2). The appendix tables that report them are labelled accordingly.

**There is no error-correction model, by choice not omission.** A long-run cointegrating demand–income relationship cannot be reliably estimated at thirty observations — the test is badly underpowered — so the report declines to fit an ECM rather than manufacture a long-run equilibrium it cannot evidence (§4.3). The first-differenced specification with a lagged-demand term captures what the sample genuinely supports.

**Pooling validates structure but does not make Uzbekistan easy.** The leave-one-country-out test shows that the large fossil systems transfer worst (Uzbekistan 19.6%, Kazakhstan 23.4% MAPE), so the pooled 6% is a panel average that flatters the Uzbek-specific case; pooling corroborates the common response structure without promising that Uzbekistan itself is now easy to forecast (§4.5).

**The scenario base year is unreconciled.** The supply scenarios begin from a 2024 renewable share (≈22.6%) higher than Chapter 2's independently sourced figure (≈16%), most likely a metered-versus-capacity difference; the trajectories and spread are robust, the absolute base is flagged for reconciliation (§5.5).

Three lines of future work would each lift a specific constraint. First, a continuous real electricity-price series — constructible from the tariff schedules published on lex.uz — would let demand be estimated with a genuine price term and would turn the excluded tariff variable (§4.2) into an estimated price elasticity, the single most valuable addition the data environment permits. Second, an oblast-level or monthly panel would multiply the effective sample and let the spatial east–west mismatch (§2.5) and the summer cooling-load signal be modelled directly rather than nationally and annually. Third, broadening the cross-country pool beyond Central Asia to a wider set of transition economies — and recovering Turkmenistan once its macro series fill in — would test whether the response structure that the LOCO analysis found only partly transferable within the region holds across a larger, more varied panel.

These same extensions would also widen the set of model classes the data can bear. At about thirty observations the analysis cannot support a high-capacity learner — the gradient-boosted tree (XGBoost) of §4.5 was tested and lost to the regularised-linear models for exactly this reason, over-fitting a sample too small to discipline it. Higher-variance methods, including neural networks, were not tested here and would fail for the same want of data; their absence reflects the sample size, not an oversight. They become a genuine option only once the data environment changes: an oblast-level or monthly panel, or a broadened multi-country sample, would multiply the effective observations to the point where neural and other machine-learning models could be trained and fairly evaluated against the linear baseline — making them a natural line of future work rather than a present alternative.

---

# 8 — Conclusion

This report set out to do three things, and it is worth returning to them in order. It explored the power sector and found a system whose structure is its destiny: gas carries 78% of generation, hydropower is fully used, the best renewable resource sits in a west that the load in the east cannot reach without new transmission, and a grid that loses a sixth of its throughput must absorb whatever transition is built. It then bounded the 2040 trajectory honestly — predicting demand at about 86 TWh in 2030 and roughly 124 TWh in 2040 within a band marked plainly as a lower bound, and projecting, under three build-out scenarios that share that one demand path, a 2040 renewable share between 36% and 80% and a grid carbon intensity between 436 and 90 gCO₂/kWh. The distance between those endpoints is not a forecast error; it is the policy choice, and the report's refusal to collapse it into a single number is the most important thing it does.

Finally, it located where the transition creates advisory opportunity. The structural facts and the projections converge on a small number of decisions the sector cannot avoid: a generation build-out that only the Accelerated path carries to the legislated capacity target; a grid whose chronic ~16% losses, set against a ~9% target, define a modernization prize that is simultaneously a decarbonisation lever and a cost recovery; a west-to-east evacuation problem that new transmission must solve; a gas-import exposure that renewable build-out converts into energy security; and a firm-capacity hedge at Jizzakh whose value rises precisely if the renewables underperform. What the client should act on now is the modernization-and-integration layer, where the signals are sharpest and engagement is close to unavoidable; what it should monitor is the build-out pace, because the BAU trajectory shows that an unsustained transition does not merely stall but reverses. A forecast built on thirty observations cannot tell anyone the future of Uzbekistan's grid. It can, done honestly, tell them where to look — and that is what this report has tried to do.

---

# References

*The list below is keyed to the sources cited in the text and is to be completed by the author from her own library; full bibliographic detail is the author's to supply, and is deliberately not manufactured here. Each entry names the source and what it is cited for.*

## Data sources

- **International Energy Agency** — *Uzbekistan Energy Profile* (2024) and the IEA reference energy balance. Cited for: generation by fuel, electricity consumption, gas flows, power-sector carbon intensity (the project's reference balance, to 2023); gas-dominance threshold; winter capacity utilisation. [CITE-COMPLETE]
- **International Energy Agency** — *Solar PV / renewable roadmap* material (2024). Cited for: solar resource and deployment context. [CITE-COMPLETE]
- **National Statistics Committee of the Republic of Uzbekistan (StatSUZ)** — national electricity and fuel-energy balance, 2024 release. Cited for: the only 2024 observation; installed capacity and renewable generation by technology; the 2024 fuel-balance re-bucketing of §3.5. [CITE-COMPLETE]
- **IRENA** — *Renewable Capacity Statistics 2024*. Cited for: renewable-capacity and renewable-share cross-check. [CITE-COMPLETE]
- **World Bank** — *World Development Indicators*. Cited for: GDP, population, urbanisation, industrial and services value-added, and the T&D-loss series (with the pre-2001 basis change and 2018–2022 correction of §3.6). [CITE-COMPLETE]
- **World Bank** — *Electricity Distribution Improvement Project (P504630)*, 2025. Cited for: distribution-loss magnitude and grid-modernization context. [CITE-COMPLETE]
- **Eurasian Development Bank** — *Central Asia Energy Outlook 2026*. Cited for: the 17.8% (2023) loss anchor; independent 2024 demand/generation/capacity cross-check. [CITE-COMPLETE]
- **International Monetary Fund** — *World Economic Outlook*, April 2026 vintage. Cited for: forward GDP and population driver path (to 2031) behind the post-2024 scenarios. [CITE-COMPLETE]
- **Our World in Data / Ember** — electricity and renewable-share series. Cited for: the five-country Central-Asian comparison and the pooled panel. [CITE-COMPLETE]
- **Enerdata** — *Uzbekistan country energy profile*. Cited for: the 27 GW / 40% (2024 amendment) and 54% / 51.6 GW renewable targets. [CITE-COMPLETE]
- **CAREC (2024); Global Solar Atlas** — oblast wind and solar resource. Cited for: the §2.5 resource atlas. [CITE-COMPLETE]
- **REF asset dataset** (uzbekistan_energy_projects.json) — curated catalogue of 46 named power assets. Cited for: the fleet and spatial analysis of Chapter 2. [CITE-COMPLETE]

## Methods and literature

- **Lewis, C. D. (1982)** — MAPE interpretation bands. Cited for: forecast-accuracy scoring. [CITE-COMPLETE]
- **Hyndman, R. J., & Athanasopoulos, G.** — *Forecasting: Principles and Practice*. Cited for: baseline forecasting methods, differencing, and evaluation. [CITE-COMPLETE]
- **Hsiao, C. (2014)** — *Analysis of Panel Data*. Cited for: pooled fixed-effects panel and the common-response assumption (§4.5). [CITE-COMPLETE]
- **Tipping, M. E. (2001)** — sparse Bayesian / relevance-vector learning. Cited for: the Bayesian-ridge shrinkage rationale (§4.2). [CITE-COMPLETE]
- **Granger, C. W. J., & Newbold, P.** — spurious regression in time series. Cited for: the detrending screen and the associational reading of coefficients (§4.2). [CITE-COMPLETE]
- **Hoerl, A. E., & Kennard, R. W. (1970)** — ridge regression. Cited for: the collinearity/shrinkage justification (§4.2). [CITE-COMPLETE]
- **Box, G. E. P., Jenkins, G. M., & Reinsel, G. C. (2015)** — *Time Series Analysis*. Cited for: ARIMA, unit-root and small-sample diagnostics (§4.3). [CITE-COMPLETE]
- **Lundberg, S. M., & Lee, S.-I. (2017)** — SHAP. Cited for: the tree-model interpretability check (§4.5). [CITE-COMPLETE]

## Policy, history, and secondary sources

- **World Nuclear News** — Jizzakh nuclear project. Cited for: the 2.1 GW integrated VVER-1000 + RITM-200N scope (§2.4, §6.6). [CITE-COMPLETE]
- **Rosatom / Uzatom** — Jizzakh project record, 2025. Cited for: nuclear plant scope and siting. [CITE-COMPLETE]
- **Government of Uzbekistan** — Renewable Energy Law (2018, PP-3981); unbundling of Uzbekenergo (2019, PP-4249); 2024 amendment to the Law on the Use of Renewable Energy Sources. Cited for: the reform sequence and renewable targets (§1.2, §2.1, §2.4). [CITE-COMPLETE]
- **ADB; JRC / Minnebo country report; Jamestown Foundation; inlibrary.uz; Eurasian Research; power-technology / orexca; tep.uz** — Central Asia Power System history and individual plant histories. Cited for: the §2.1 historical timeline. [CITE-COMPLETE]
- **EBRD / ADB project documents; Global Energy Monitor** — thermal retirement and decommissioning. Cited for: the §2.6 retirement figures. [CITE-COMPLETE]
- **Times of Central Asia** — winter import and capacity-utilisation reporting. Cited for: §2.6. [CITE-COMPLETE]

---

# Appendices

## Appendix A — Full forecasting scoreboard

Ex-ante is the headline; the conditional backcast is reference only (§4.4). Single test window 2019–2023; *n*_train = 28 (single-country), 72 (pooled). Source: forecast_scoreboard_advanced.csv (project Notebook 07).

| Model | Basis | Ex-ante MAPE | Ex-ante R² | Conditional MAPE *(ref.)* |
|---|---|---:|---:|---:|
| ARIMA(1,1,0) | time-series baseline | 9.22% | −0.27 | — |
| Ridge CV-α (UZB, minimal) | single-country | 9.71% | −0.66 | 4.62% |
| Ridge CV-α (UZB, extended + UzStat) | single-country | 8.97% | −0.37 | 4.04% |
| BayesianRidge (UZB, minimal) | single-country | 9.03% | −0.39 | 4.39% |
| **BayesianRidge (UZB, extended) — deployed** | single-country | 10.14% | −0.84 | 4.30% |
| Pooled Ridge CV-α (4 CA + FE) | pooled *(validation)* | 6.08% | +0.10 | 4.58% |
| Pooled BayesianRidge (4 CA + FE) | pooled *(validation)* | 6.20% | +0.06 | 4.62% |

*The full baseline bench (naïve last-value 13.9%, linear trend 30.6%, first-differenced OLS 10.8%, Prophet 18.6%, and the interim 1990–2023 bench) is recorded in forecast_scoreboard.csv. A pooled gradient-boosted tree on the same panel scores ~13.4%, confirming the regularised-linear class is the right one (§4.5).*

## Appendix B — Leave-one-country-out (LOCO) transfer test

Each country withheld in turn and predicted from the other three; held-out MAPE measures transferability of the pooled structure (§4.5). Source: project Notebook 07 (LOCO cell).

| Held-out country | System type | LOCO MAPE |
|---|---|---:|
| Tajikistan | small hydro | 8.1% |
| Kyrgyzstan | small hydro | 11.7% |
| Uzbekistan | large fossil | 19.6% |
| Kazakhstan | large fossil | 23.4% |

*Reading: the large fossil systems transfer worst. Pooling validates the common response structure, but Uzbekistan is among the hardest cases to predict from its neighbours — so the pooled 6% is a panel average, not a promise of Uzbek-specific ease.*

## Appendix C — Coefficient tables (non-interpretable)

The fitted weights below are **regularised partial associations, not elasticities** (§4.2). They are reported for transparency only; their signs and magnitudes should not be read causally. Note in particular that the income term carries a *negative* point estimate and that *no* driver is individually significant (all *p* > 0.27) — both are expected artefacts of collinearity (*r* ≈ 0.99) and a thirty-point sample, and both are exactly why the coefficients are not interpreted. Source: forecast_drivers_v2_coefs.csv (first-differenced log specification).

| Term | Coefficient | Std. error | *p*-value |
|---|---:|---:|---:|
| const | −0.076 | 0.204 | 0.71 |
| Δln GDP per capita | −4.816 | 5.638 | 0.39 |
| Δln industry VA | 1.106 | 3.568 | 0.76 |
| Δln services VA | 2.789 | 2.553 | 0.27 |
| Δln agriculture VA | 1.403 | 2.676 | 0.60 |
| Δ cooling degree-days | 0.00011 | 0.00024 | 0.64 |
| Δ heating degree-days | −0.000035 | 0.00010 | 0.74 |
| Δ industry share | 0.0166 | 0.0244 | 0.50 |
| Δ urbanisation | −0.0412 | 0.1288 | 0.75 |
| Δ energy efficiency | −0.0758 | 0.0724 | 0.30 |

*The deployed Bayesian-ridge model is estimated in standardised levels with shrinkage and reports a predictive standard deviation rather than per-coefficient significance; its weights are likewise non-interpretable [VERIFY: if a per-coefficient table for the deployed standardised-levels Bayesian ridge is wanted alongside this differenced-log diagnostic table, export it from NB07 §3].*

## Appendix D — Sensitivity grids

**D.1 Capital envelope by technology and scenario, 2024–2040** (undiscounted, constant-cost upper bounds; USD bn / MW added). Source: investment_signals.csv.

| Technology | BAU $bn (MW) | Government $bn (MW) | Accelerated $bn (MW) |
|---|---:|---:|---:|
| Solar | 6.59 (6,933) | 13.11 (13,798) | 19.44 (20,468) |
| Wind | 7.82 (5,396) | 16.03 (11,052) | 22.47 (15,499) |
| Hydro | 4.14 (1,882) | 8.41 (3,823) | 11.74 (5,336) |
| Thermal | 5.38 (4,887) | 12.06 (10,960) | 15.00 (13,636) |
| Storage | 0.28 (693) | 1.10 (2,759) | 1.64 (4,093) |
| Transmission | 3.08 (6,164) | 6.21 (12,425) | 8.99 (17,983) |
| **Total** | **~27.3** | **~56.9** | **~79.3** |

**D.2 Nuclear Plan-B sensitivity** (combined renewable-plus-nuclear share at 2040, Government build; nuclear at capacity factor 0.85). Source: forecast_scenarios_with_nuclear.csv.

| Nuclear capacity | Nuclear output (2040) | RE+nuclear share (2040) |
|---|---:|---:|
| 0 GW | 0 TWh | 60.0% |
| 1.2 GW | 8.9 TWh | 66.6% |
| 2.4 GW | 17.9 TWh | 73.3% |
| 3.6 GW | 26.8 TWh | 79.9% |

*The actual Jizzakh plant (2.1 GW) lies between the 1.2 and 2.4 GW rows. Commissioning was tested at 2030 / 2032 / 2034; cost envelope $6–18 bn across the range.*

**D.3 Scenario endpoints** (shared demand/generation; differing mix). Source: forecast_scenarios.csv, forecast_co2.csv.

| Quantity (2040) | BAU | Government | Accelerated |
|---|---:|---:|---:|
| Renewable share | 36.5% | 60.0% | 80.0% |
| Thermal generation | 85.8 TWh | 54.0 TWh | 27.0 TWh |
| Gas for power | 24.3 bcm | 15.3 bcm | 7.7 bcm |
| Carbon intensity | 436 gCO₂/kWh | 179 gCO₂/kWh | 90 gCO₂/kWh |
| Power-sector CO₂ | 58.9 Mt | 24.2 Mt | 12.1 Mt |

## Appendix E — Dashboard description and reconciliation status

The transition-tracker dashboard (project Notebook 10) renders the analysis interactively across four areas — overview, by-source, transition-signals, and resources (§6.7). Its surfaced KPIs are reconciled to the deployed model: the hero panel shows a 2030 demand of 86.0 TWh on the extended Bayesian-ridge path (≈124 TWh by 2040), names that model as deployed, reports the realized loss rate of ~16% / 17.8% (2023), and reads its renewable-share (58.4%), carbon (22.9 Mt) and capital ($56.9 bn, Government scenario) figures for 2030 directly from the Chapter 5–6 scenario files. The notebook was re-executed against the current forecast outputs and writes to the canonical project output path (`outputs/uzbekistan_power_tracker.html`).

## Appendix F — Data vintage and provenance

- **Confirmed electricity record:** 1990–2023, IEA-consumption basis; ~30 effective modelling years after holding out provisional years and the early-1990s contraction (§3.1).
- **Bridged year:** 2024, ratio-scaled from StatSUZ onto the IEA basis (consumption factor ≈ 0.92 recent; generation factor ≈ 0.99); ~77.7 TWh bridged demand; used as trend anchor only (§3.4).
- **Provisional:** 2024–2026 flagged preliminary; dropped from training folds, displayed (labelled) on the dashboard (§3.6).
- **Hand-corrected series:** World Bank T&D losses — 2018–2022 masked as implausible; 2023 set to EDB 17.8%; pre-2001 narrow basis set aside (§3.6).
- **Driver path:** IMF WEO April 2026 to 2031; terminal growth held flat 2032–2040 (§4.6).
- **Pooled panel:** four Central-Asian countries (KAZ, KGZ, TJK, UZB), ~95 country-years (~72 training); Turkmenistan excluded for incomplete macro series (§4.5).
- **Key output files:** forecast_demand_bayes_ridge.csv, forecast_demand.csv, forecast_scenarios.csv, forecast_co2.csv, forecast_scenarios_with_nuclear.csv, forecast_scoreboard_advanced.csv, investment_signals.csv, investment_signal_{deficit,gas,td}.csv (all project Notebooks 07–08).
