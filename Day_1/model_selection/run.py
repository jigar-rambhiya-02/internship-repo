# """
# Model Selection Benchmark: Document Summarization
# Compares Gemini 3.1 Pro Preview, Gemini 3 Flash Preview, and Gemini 3.1 Flash-Lite
# Task: Summarize a 1-page document into 3 bullet points
# """

# import os
# import time
# import csv
# import json
# import re
# from datetime import datetime
# import google.generativeai as genai

# from dotenv import load_env

# # ── Configuration ──────────────────────────────────────────────────────────────

# load_env()

# API_KEY = os.getenv("GROQ_API_KEY")
# genai.configure(api_key=API_KEY)

# # Model identifiers (current as of June 2026)
# # Line ~18 — model identifiers
# MODELS = {
#     "llama3-70b": "llama3-70b-8192",
#     "mixtral-8x7b": "mixtral-8x7b-32768",
#     "gemma2-9b": "gemma2-9b-it",
# }

# # Line ~24 — pricing (2.5 series, paid tier)
# PRICING = {
#     "gemini-2.5-pro":        {"input": 1.25,  "output": 10.00},
#     "gemini-2.5-flash":      {"input": 0.30,  "output": 2.50},
#     "gemini-2.5-flash-lite": {"input": 0.10,  "output": 0.40},
# }

# # Line ~109 — judge model
# JUDGE_MODEL = "gemini-2.5-pro"
# OUTPUT_CSV  = "results.csv"

# # ── Summarization Prompt ───────────────────────────────────────────────────────

# SYSTEM_PROMPT = (
#     "You are a professional summarizer. Read the document and return EXACTLY "
#     "3 concise bullet points that capture the most important information. "
#     "Each bullet must start with '• ' and be one sentence. "
#     "Return only the 3 bullets — no preamble, no headings, no extra text."
# )

# def build_user_prompt(document: str) -> str:
#     return f"Document:\n\n{document}\n\nSummarize into 3 bullet points."

# # ── Judge Prompt ───────────────────────────────────────────────────────────────

# JUDGE_SYSTEM = (
#     "You are an objective evaluator. Score the quality of an AI-generated "
#     "3-bullet summary on a scale of 1–5.\n\n"
#     "Scoring rubric:\n"
#     "5 = All 3 bullets are accurate, distinct, and capture the most important points\n"
#     "4 = Mostly good, minor omissions or slight redundancy\n"
#     "3 = Acceptable, but misses a key point or has vague wording\n"
#     "2 = Weak — inaccurate, repetitive, or only 1 good bullet\n"
#     "1 = Poor — wrong, irrelevant, or format not followed\n\n"
#     "Respond with ONLY a JSON object: {\"score\": <1-5>, \"reason\": \"<one sentence>\"}"
# )

# def build_judge_prompt(document: str, summary: str) -> str:
#     return (
#         f"Original document:\n{document}\n\n"
#         f"Generated summary:\n{summary}\n\n"
#         "Score the summary quality."
#     )

# # ── 20 Sample Documents ────────────────────────────────────────────────────────
# # Mix of news-style and Wikipedia-style paragraphs, each ~200-300 words

# DOCUMENTS = [
#     # 1
#     """The Amazon rainforest, often described as the "lungs of the Earth," covers over 5.5 million
# square kilometres across nine countries, with Brazil holding the largest share at about 60%.
# It produces roughly 20% of the world's oxygen through photosynthesis and absorbs vast amounts
# of carbon dioxide, playing a critical role in regulating the global climate. The forest is home
# to an estimated 10% of all species on Earth, including 40,000 plant species, 1,300 bird species,
# and 3,000 types of fish. Despite its importance, the Amazon has lost about 17% of its original
# cover over the past 50 years, primarily due to agricultural expansion, illegal logging, and
# infrastructure development. Scientists warn that if deforestation reaches 20–25%, the forest
# could cross a tipping point and begin to self-destruct, transitioning to savannah. In recent
# years, Brazil's deforestation rate has fluctuated significantly with changes in government
# policy. International pressure, indigenous land rights campaigns, and sustainable agriculture
# initiatives are among the forces working to slow destruction. The Amazon also holds enormous
# economic value through ecosystem services — water cycling, climate stabilisation, and
# biodiversity — estimated by some researchers at trillions of dollars annually.""",

#     # 2
#     """SpaceX successfully launched its Starship rocket on its fourth integrated flight test on
# June 6, 2024, achieving a major milestone in the company's ambitions to develop a fully
# reusable launch system capable of carrying humans to the Moon and Mars. The test saw both
# the Super Heavy booster and the Starship upper stage complete controlled splashdowns for the
# first time, with the booster executing a precise flip maneuver before touching the Gulf of Mexico
# and the Starship surviving re-entry heating before splashing down in the Indian Ocean. The flight
# lasted approximately 65 minutes. Elon Musk called the test a tremendous success, noting that
# the heat shield tiles performed better than expected. NASA, which has contracted SpaceX to use
# a version of Starship as the Human Landing System for the Artemis lunar missions, praised the
# progress. The next phase of testing will focus on catching the booster with the launch tower's
# mechanical arms, known internally as "Mechazilla," and eventually achieving a full catch of both
# vehicle stages on the launch pad.""",

#     # 3
#     """Artificial intelligence is rapidly transforming the healthcare industry, offering new tools
# for disease diagnosis, drug discovery, and personalised treatment. Machine learning algorithms
# trained on millions of medical images can now detect cancers, diabetic retinopathy, and other
# conditions with accuracy comparable to or exceeding specialist physicians. In drug discovery,
# AI systems like AlphaFold have solved the long-standing problem of protein structure prediction,
# potentially accelerating development of new medicines by years. Hospitals are deploying AI to
# predict patient deterioration, optimise scheduling, and reduce administrative burdens on
# clinicians. However, the technology also raises significant concerns around data privacy,
# algorithmic bias, and the risk that AI tools trained on non-representative datasets may perform
# poorly for certain demographic groups. Regulatory agencies in the US, EU, and UK are developing
# frameworks to evaluate and approve AI medical devices. Proponents argue that, properly validated
# and deployed, AI could democratise access to expert-level diagnosis in low-resource settings
# and save millions of lives globally over the coming decades.""",

#     # 4
#     """The global semiconductor shortage that began in 2020 exposed deep vulnerabilities in modern
# supply chains and the extreme geographic concentration of chip manufacturing. Taiwan
# Semiconductor Manufacturing Company (TSMC) alone produces over 90% of the world's most
# advanced chips, creating a single point of failure that has alarmed governments worldwide.
# The shortage forced automotive manufacturers to idle factories, delayed consumer electronics
# releases, and highlighted how a disruption in a small island nation could ripple across every
# sector of the global economy. In response, the United States passed the CHIPS and Science Act
# in 2022, committing $52 billion to domestic semiconductor manufacturing. The European Union
# launched its own Chips Act, and countries from Japan to India have announced incentives to
# attract semiconductor investment. TSMC, Intel, and Samsung are all building new fabrication
# plants outside their traditional hubs. Analysts warn, however, that building competitive chip
# fabs takes 5–10 years and that diversification will not happen quickly enough to prevent
# future shocks from geopolitical tensions over Taiwan.""",

#     # 5
#     """Climate change is altering ocean ecosystems at an unprecedented rate, with rising sea
# temperatures, ocean acidification, and deoxygenation combining to create what scientists call
# the triple threat to marine life. Coral reefs, which support about 25% of all marine species
# despite covering less than 1% of the ocean floor, have experienced mass bleaching events of
# increasing frequency and severity. The Great Barrier Reef suffered its most widespread bleaching
# on record in 2024, with over 73% of surveyed reefs showing signs of bleaching. Fish populations
# are shifting poleward as they follow cooler water, disrupting fisheries that millions of people
# depend on for food and income. Ocean acidification — caused by the sea absorbing excess
# atmospheric CO2 — threatens shell-forming organisms at the base of marine food webs.
# Researchers are exploring interventions such as assisted evolution of heat-tolerant coral,
# shading reefs with floating screens, and marine protected areas. Without significant reductions
# in greenhouse gas emissions, scientists project that coral reefs could functionally disappear
# by the end of the century.""",

#     # 6
#     """The European Union's General Data Protection Regulation (GDPR), which came into force in
# May 2018, fundamentally changed how organisations around the world handle personal data.
# The regulation grants EU citizens broad rights including the right to access their data, the
# right to have it deleted, and the right to know how it is being used. It imposes strict
# obligations on companies, requiring them to obtain explicit consent for data collection,
# appoint data protection officers, and report breaches within 72 hours. Penalties for
# non-compliance can reach €20 million or 4% of global annual turnover, whichever is higher.
# Since its introduction, regulators have levied billions of euros in fines against major
# technology companies including Meta, Google, and Amazon. The GDPR has also had a global
# influence, inspiring similar legislation in California (CCPA), Brazil (LGPD), and other
# jurisdictions. Critics argue that the regulation disproportionately burdens smaller businesses
# and has not prevented the dominance of large tech platforms that have the resources to absorb
# compliance costs. Supporters contend that it has meaningfully raised privacy standards and
# given citizens greater control over their digital lives.""",

#     # 7
#     """Quantum computing promises to solve certain categories of problems exponentially faster
# than classical computers, with potential applications in cryptography, materials science,
# drug discovery, and optimisation. Unlike classical bits, which represent either 0 or 1,
# quantum bits (qubits) can exist in superpositions of both states simultaneously, and
# entangled qubits can be correlated across distances, enabling computations that would
# take classical machines longer than the age of the universe. IBM, Google, Microsoft, and
# a growing ecosystem of startups are racing to build fault-tolerant quantum computers.
# In 2019, Google claimed "quantum supremacy," completing a specific calculation in 200
# seconds that it said would take the best classical supercomputer 10,000 years. IBM
# disputed the claim. Practical, fault-tolerant quantum computers remain years or decades
# away because current "noisy intermediate-scale quantum" (NISQ) devices are too error-prone
# for most real-world applications. A major concern is that sufficiently powerful quantum
# computers could break current RSA and elliptic-curve encryption, motivating global efforts
# to develop post-quantum cryptographic standards.""",

#     # 8
#     """Urbanisation is one of the most significant demographic trends of the 21st century. By
# 2050, approximately 68% of the world's population is expected to live in cities, up from
# about 55% today. This rapid growth is placing enormous pressure on infrastructure, housing,
# transportation, and public services, particularly in developing nations. Megacities — urban
# areas with more than 10 million inhabitants — are proliferating, with new additions expected
# in Africa and Asia. Smart city technologies, including IoT sensors, AI-driven traffic
# management, and data analytics platforms, are being deployed to improve urban efficiency
# and quality of life. However, urbanisation also drives inequality: informal settlements and
# slums house over a billion people globally and often lack clean water, sanitation, and secure
# land tenure. Climate change compounds the challenge, as many of the fastest-growing cities
# are in coastal regions or areas vulnerable to extreme heat. Urban planners are increasingly
# focused on "15-minute city" concepts that reduce car dependence and ensure residents can
# access essential services on foot or by bicycle.""",

#     # 9
#     """The global mental health crisis has worsened significantly since the COVID-19 pandemic,
# with rates of depression, anxiety, and loneliness rising across all age groups. The World
# Health Organization estimates that depression alone affects more than 280 million people
# worldwide and is among the leading causes of disability. Mental health conditions account
# for a significant portion of the global burden of disease yet receive historically
# underfunded and understaffed care systems. In high-income countries, people with severe
# mental illness die on average 10–20 years earlier than the general population, largely
# due to preventable physical health conditions and barriers to care. Digital mental health
# tools — apps, online therapy platforms, and AI chatbots — have expanded access for some
# populations but raise concerns about evidence quality, data privacy, and the risk of
# replacing rather than supplementing human therapeutic relationships. Workplace mental
# health programmes have grown in prominence, with employers recognising that poor mental
# health costs billions in lost productivity annually. Advocates are pushing for parity of
# mental and physical health care in insurance coverage and public investment.""",

#     # 10
#     """The history of the internet dates to the late 1960s, when ARPANET, funded by the US
# Department of Defense, first connected computers at universities and research institutions.
# The development of TCP/IP protocols in the 1970s and 80s created the technical foundation
# for a global network. Tim Berners-Lee invented the World Wide Web in 1989 while working
# at CERN, introducing the concepts of URLs, HTML, and HTTP that made information on the
# internet easily navigable by ordinary users. The commercialisation of the internet
# accelerated through the 1990s with the rise of dial-up providers, search engines, and
# e-commerce platforms. The dot-com bubble of the late 1990s saw massive speculation
# followed by a crash in 2000-2001, but the underlying infrastructure and user base
# continued to grow. The 2010s brought mobile internet, social media platforms, and cloud
# computing, fundamentally changing how billions of people communicate, work, shop, and
# access information. Today, more than 5 billion people are connected to the internet,
# and it underpins virtually every sector of the modern economy.""",

#     # 11
#     """Electric vehicles are reshaping the global automotive industry at an accelerating pace.
# Global EV sales surpassed 10 million units in 2022 and have continued to grow, with China
# accounting for the largest share of sales. Battery costs have fallen by over 90% since 2010,
# making EVs increasingly cost-competitive with internal combustion engine vehicles on a
# total cost of ownership basis. Governments worldwide are setting targets to phase out petrol
# and diesel car sales, with the UK, EU, and several US states targeting 2035. The transition
# brings both opportunities and challenges. While EVs produce zero tailpipe emissions, the
# environmental benefit depends heavily on the electricity grid mix. Mining lithium, cobalt,
# nickel, and other battery materials raises environmental and human rights concerns.
# Charging infrastructure, particularly in rural areas and apartment buildings, remains a
# barrier to adoption. The shift threatens jobs in traditional combustion engine supply chains
# while creating new roles in battery manufacturing, software development, and EV servicing.
# Tesla, BYD, and legacy automakers are investing hundreds of billions in the transition.""",

#     # 12
#     """Antibiotic resistance is one of the greatest public health threats of the 21st century.
# Bacteria evolve rapidly in response to antibiotic use, and overuse in human medicine and
# agriculture has accelerated the spread of resistant strains. The World Health Organization
# has identified antimicrobial resistance (AMR) as a global priority, estimating it currently
# causes at least 1.27 million deaths directly each year and contributes to millions more.
# Without action, AMR could kill 10 million people annually by 2050 — more than cancer.
# The pipeline of new antibiotics is alarmingly thin; developing a new antibiotic takes
# 10–15 years and offers limited financial returns compared to drugs for chronic conditions,
# so pharmaceutical companies have largely exited the field. Stewardship programmes that
# promote appropriate prescribing, investment in diagnostics, and international agreements
# on surveillance are seen as critical near-term interventions. Longer-term, phage therapy,
# AI-assisted drug discovery, and vaccines against bacterial pathogens offer hope but
# remain largely unproven at scale.""",

#     # 13
#     """The James Webb Space Telescope, launched on December 25, 2021, represents the most
# powerful space telescope ever built and has already transformed our understanding of
# the early universe, exoplanet atmospheres, and galaxy formation. Operating primarily in
# the infrared spectrum, Webb can peer through dust clouds that obscured Hubble's view,
# allowing scientists to observe the first galaxies that formed after the Big Bang, some
# just 300 million years after the universe began. Its instruments detected water vapour,
# carbon dioxide, and methane in the atmospheres of exoplanets, advancing the search for
# potentially habitable worlds. Webb's images have revealed previously unknown structures
# in nearby galaxies and provided unprecedented detail of star-forming regions. The
# telescope resides at the second Lagrange point (L2), about 1.5 million kilometres from
# Earth, where its sunshield keeps it cool enough to detect faint infrared signals.
# It carries enough fuel for a 20-year mission. Scientists have described its early results
# as consistently exceeding expectations, with some discoveries challenging existing models
# of galaxy formation.""",

#     # 14
#     """Social media platforms have fundamentally altered political communication, enabling
# direct engagement between politicians and constituents but also amplifying misinformation,
# polarisation, and foreign interference. Studies consistently find that algorithmic
# recommendation systems optimise for engagement, which tends to favour emotionally
# charged and divisive content, contributing to the formation of "echo chambers" where
# users encounter primarily views that reinforce their own. The 2016 US presidential
# election, the Brexit referendum, and numerous subsequent elections highlighted how
# social media could be weaponised through targeted advertising, coordinated inauthentic
# behaviour, and viral misinformation. Platforms have introduced fact-checking labels,
# reduced the reach of certain content, and banned high-profile accounts, triggering
# debates about censorship, free speech, and platform accountability. Regulatory
# frameworks are evolving: the EU's Digital Services Act imposes new transparency and
# risk assessment obligations on large platforms. Researchers are divided on the magnitude
# of social media's effects, with some arguing its influence on political outcomes has been
# overstated compared to traditional media and economic factors.""",

#     # 15
#     """The global food system faces an enormous challenge: feeding a projected 10 billion
# people by 2050 while reducing its environmental footprint. Agriculture currently accounts
# for about 25% of global greenhouse gas emissions, uses 70% of freshwater withdrawals,
# and is the leading driver of biodiversity loss. Food loss and waste — about one-third
# of all food produced — compounds the problem. A shift toward more plant-based diets
# is widely seen as essential, given that producing animal protein is far more
# resource-intensive than plant protein. Alternative proteins — including plant-based
# meat substitutes, cultured meat grown from animal cells, and insect-based foods — are
# attracting significant investment. Precision agriculture, using drones, sensors, and
# AI to optimise inputs, promises to reduce chemical use and improve yields. Regenerative
# agriculture practices aim to restore soil health and sequester carbon while maintaining
# productivity. Food security remains deeply unequal: over 700 million people are
# chronically undernourished while others suffer from diet-related diseases linked to
# overconsumption. Addressing this imbalance requires both technological innovation and
# systemic policy change.""",

#     # 16
#     """The human microbiome — the trillions of bacteria, viruses, fungi, and other
# microorganisms living in and on the human body — has emerged as a major focus of
# biomedical research over the past two decades. The gut microbiome in particular
# has been linked to immune function, mental health, metabolism, and susceptibility
# to chronic diseases including obesity, type 2 diabetes, and inflammatory bowel
# disease. Research suggests that early life exposure to diverse microbes, influenced
# by birth mode, breastfeeding, and antibiotic use, shapes long-term health outcomes.
# Faecal microbiota transplantation (FMT) — transferring gut bacteria from a healthy
# donor to a recipient — has proven highly effective for recurrent Clostridioides
# difficile infections and is being investigated for conditions ranging from autism
# spectrum disorder to cancer immunotherapy response. Probiotic and prebiotic
# products have boomed commercially, though the evidence base for most specific
# health claims remains limited. The field is moving toward personalised microbiome
# interventions, where dietary and therapeutic recommendations are tailored based on
# an individual's microbial profile.""",

#     # 17
#     """The global shipping industry carries approximately 80-90% of world trade by volume,
# making it the backbone of the global economy. It is also a significant source of
# greenhouse gas emissions, accounting for about 3% of global CO2 output — comparable
# to Germany's annual emissions. The International Maritime Organization has set a
# target of net zero emissions by 2050, but decarbonising shipping is technically
# challenging because vessels need energy-dense fuels for long ocean voyages. Ammonia,
# methanol, hydrogen, and liquefied natural gas are all being evaluated as cleaner
# alternatives to heavy fuel oil, but each involves trade-offs in cost, energy density,
# safety, and infrastructure requirements. Slow steaming — simply reducing vessel speeds
# — has become a widely adopted near-term measure that cuts fuel consumption and
# emissions by 10–20%. The industry's concentration in a small number of massive
# shipping alliances, and the critical role of chokepoints like the Suez Canal, Strait
# of Malacca, and Panama Canal, mean that geopolitical tensions and climate events can
# rapidly disrupt global supply chains.""",

#     # 18
#     """Gene editing technology, particularly CRISPR-Cas9, has opened new frontiers in
# medicine, agriculture, and fundamental biology. Discovered in bacteria as an immune
# mechanism, CRISPR enables scientists to make precise cuts in DNA sequences and
# insert, delete, or modify genes with unprecedented speed, accuracy, and affordability
# compared to earlier techniques. In medicine, CRISPR-based therapies have achieved
# remarkable early results: treatments for sickle cell disease and beta-thalassaemia
# received regulatory approval in 2023, representing the first approved CRISPR therapies
# in humans. Clinical trials are exploring applications in cancer, HIV, inherited blindness,
# and high cholesterol. In agriculture, CRISPR is being used to develop disease-resistant
# crops, drought-tolerant varieties, and animals with enhanced disease resistance.
# The technology raises profound ethical questions, particularly around heritable
# germline editing — modifying embryos in ways that would be passed to future generations.
# A 2018 incident in which a Chinese scientist created the world's first gene-edited babies
# sparked global condemnation and calls for a moratorium on reproductive germline editing.""",

#     # 19
#     """The rise of remote work, accelerated dramatically by the COVID-19 pandemic, has
# permanently changed assumptions about where and how knowledge work gets done.
# Before 2020, fully remote work was rare; within weeks of global lockdowns, hundreds of
# millions of office workers shifted to working from home. Survey data suggest a
# significant portion of workers prefer hybrid or fully remote arrangements and are willing
# to take pay cuts to maintain flexibility. Employers, meanwhile, are divided: some major
# technology and financial firms have mandated returns to the office, citing culture,
# collaboration, and mentorship concerns, while others have embraced remote-first models
# to expand their talent pools globally. Commercial real estate markets in many city centres
# have been severely disrupted, with high office vacancy rates. Suburbs and smaller cities
# have gained population as workers untethered from daily commutes relocate. Productivity
# research yields mixed results, varying by job type, home environment, and management
# approach. The debate over the long-term optimal balance between in-person and remote work
# remains unresolved and is likely to continue shaping corporate culture for years.""",

#     # 20
#     """The International Space Station (ISS), continuously inhabited since November 2000,
# is one of the most complex and expensive engineering projects in human history, costing
# over $150 billion and requiring contributions from 15 nations and five space agencies.
# Orbiting approximately 400 kilometres above Earth, the ISS has hosted more than 270
# astronauts from 20 countries and served as a platform for thousands of scientific
# experiments in microgravity, covering biology, physics, material science, and Earth
# observation. The station has also played a vital diplomatic role, fostering cooperation
# between the US and Russia even during periods of geopolitical tension. NASA has announced
# plans to deorbit the ISS by 2030, with a SpaceX Dragon capsule tasked with guiding
# it to a controlled re-entry over an uninhabited ocean area. Commercial successors, built
# by companies including Axiom Space and Starlab, are in development and are expected to
# maintain a US-led low-Earth orbit presence. China, meanwhile, completed its own Tiangong
# space station in 2022 and plans to expand it, setting the stage for a new era of
# competition in space.""",
# ]

# # ── Core helpers ───────────────────────────────────────────────────────────────

# def compute_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
#     p = PRICING[model_id]
#     return (input_tokens / 1_000_000) * p["input"] + (output_tokens / 1_000_000) * p["output"]


# def call_model(model_id: str, document: str) -> dict:
#     for attempt in range(3):
#         try:
#             model = genai.GenerativeModel(
#                 model_name=model_id,
#                 system_instruction=SYSTEM_PROMPT,
#             )
#             start = time.perf_counter()
#             response = model.generate_content(build_user_prompt(document))
#             latency_ms = (time.perf_counter() - start) * 1000

#             usage = response.usage_metadata
#             input_tokens  = usage.prompt_token_count
#             output_tokens = usage.candidates_token_count
#             cost = compute_cost(model_id, input_tokens, output_tokens)

#             return {
#                 "text": response.text.strip(),
#                 "latency_ms": round(latency_ms, 1),
#                 "input_tokens": input_tokens,
#                 "output_tokens": output_tokens,
#                 "cost_usd": cost,
#             }
#         except Exception as e:
#             if "429" in str(e) and attempt < 2:
#                 wait = 60 * (attempt + 1)
#                 print(f"    Rate limited, waiting {wait}s...")
#                 time.sleep(wait)
#             else:
#                 raise


# def judge_quality(document: str, summary: str) -> tuple[int, str]:
#     for attempt in range(3):
#         try:
#             model = genai.GenerativeModel(
#                 model_name=JUDGE_MODEL,
#                 system_instruction=JUDGE_SYSTEM,
#             )
#             response = model.generate_content(build_judge_prompt(document, summary))
#             raw = response.text.strip()
#             raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
#             try:
#                 data = json.loads(raw)
#                 return int(data["score"]), str(data.get("reason", ""))
#             except Exception:
#                 match = re.search(r'"score"\s*:\s*([1-5])', raw)
#                 score = int(match.group(1)) if match else 3
#                 return score, raw[:120]
#         except Exception as e:
#             if "429" in str(e) and attempt < 2:
#                 wait = 60 * (attempt + 1)
#                 print(f"    Judge rate limited, waiting {wait}s...")
#                 time.sleep(wait)
#             else:
#                 raise


# # ── Main run ───────────────────────────────────────────────────────────────────

# def run_benchmark():
#     fieldnames = [
#         "input_id", "model", "latency_ms",
#         "input_tokens", "output_tokens", "cost_usd",
#         "quality_score_1to5", "notes",
#     ]

#     results = []
#     total = len(MODELS) * len(DOCUMENTS)
#     done  = 0

#     print(f"\n{'='*60}")
#     print(f"  Document Summarisation Benchmark — {datetime.now():%Y-%m-%d %H:%M}")
#     print(f"  Models: {', '.join(MODELS.keys())}")
#     print(f"  Documents: {len(DOCUMENTS)}  |  Total calls: {total}")
#     print(f"{'='*60}\n")

#     for label, model_id in MODELS.items():
#         print(f"\n── Model: {label} ({model_id}) ──")
#         for idx, doc in enumerate(DOCUMENTS):
#             doc_id = f"doc_{idx+1:02d}"
#             try:
#                 result = call_model(model_id, doc)
#                 score, reason = judge_quality(doc, result["text"])
#                 time.sleep(4)

#                 row = {
#                     "input_id":           doc_id,
#                     "model":              label,
#                     "latency_ms":         result["latency_ms"],
#                     "input_tokens":       result["input_tokens"],
#                     "output_tokens":      result["output_tokens"],
#                     "cost_usd":           round(result["cost_usd"], 8),
#                     "quality_score_1to5": score,
#                     "notes":              reason,
#                 }
#                 results.append(row)
#                 done += 1
#                 print(
#                     f"  [{done:3d}/{total}] {doc_id} | "
#                     f"latency={result['latency_ms']:.0f}ms | "
#                     f"tokens={result['input_tokens']}+{result['output_tokens']} | "
#                     f"cost=${result['cost_usd']:.6f} | "
#                     f"quality={score}/5"
#                 )
#                 # time.sleep(4)


#             except Exception as e:
#                 print(f"  ERROR on {doc_id}: {e}")
#                 # results.append({
#                 #     "input_id":           doc_id,
#                 #     "model":              label,
#                 #     "latency_ms":         -1,
#                 #     "input_tokens":       -1,
#                 #     "output_tokens":      -1,
#                 #     "cost_usd":           -1,
#                 #     "quality_score_1to5": -1,
#                 #     "notes":              f"ERROR: {e}",
#                 # })

#             time.sleep(10)

#     # Write CSV
#     with open(OUTPUT_CSV, "w", newline="") as f:
#         writer = csv.DictWriter(f, fieldnames=fieldnames)
#         writer.writeheader()
#         writer.writerows(results)

#     print(f"\n✅  Results written to {OUTPUT_CSV}")
#     print_summary(results)


# def print_summary(results: list[dict]):
#     from collections import defaultdict
#     agg = defaultdict(lambda: {
#         "latency": [], "cost": [], "quality": [], "tokens_in": [], "tokens_out": []
#     })
#     for r in results:
#         if r["latency_ms"] < 0:
#             continue
#         m = r["model"]
#         agg[m]["latency"].append(r["latency_ms"])
#         agg[m]["cost"].append(r["cost_usd"])
#         agg[m]["quality"].append(r["quality_score_1to5"])
#         agg[m]["tokens_in"].append(r["input_tokens"])
#         agg[m]["tokens_out"].append(r["output_tokens"])

#     def avg(lst): return sum(lst) / len(lst) if lst else 0

#     print(f"\n{'='*60}")
#     print("  Per-Model Averages")
#     print(f"{'='*60}")
#     print(f"  {'Model':<25} {'Latency(ms)':>12} {'Cost($)':>12} {'Quality':>9} {'In-tok':>8} {'Out-tok':>8}")
#     print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*9} {'-'*8} {'-'*8}")
#     for model, data in agg.items():
#         print(
#             f"  {model:<25} "
#             f"{avg(data['latency']):>12.1f} "
#             f"{avg(data['cost']):>12.7f} "
#             f"{avg(data['quality']):>9.2f} "
#             f"{avg(data['tokens_in']):>8.0f} "
#             f"{avg(data['tokens_out']):>8.0f}"
#         )
#     print(f"{'='*60}\n")


# if __name__ == "__main__":
#     run_benchmark()


"""
Model Selection Benchmark: Document Summarization
Provider: Groq (groq-sdk)
Task: Summarize a 1-page document into 3 bullet points

Models used (maps to assignment tiers):
  "Pro"        → llama-3.3-70b-versatile   (largest, smartest, slowest)
  "Flash"      → meta-llama/llama-4-scout-17b-16e-instruct  (balanced)
  "Flash-Lite" → llama-3.1-8b-instant      (fastest, cheapest)

Judge: llama-3.3-70b-versatile (LLM-as-judge)
"""

import os, time, csv, json, re
from datetime import datetime
from groq import Groq

# ── Config ─────────────────────────────────────────────────────────────────────

GROQ_API_KEY='***REMOVED***'
client  = Groq(api_key=GROQ_API_KEY)

# Three tiers matching the assignment's Pro / Flash / Flash-Lite concept
MODELS = {
    "llama-3.3-70b (Pro)":        "llama-3.3-70b-versatile",
    "llama-4-scout (Flash)":      "meta-llama/llama-4-scout-17b-16e-instruct",
    "llama-3.1-8b (Flash-Lite)":  "llama-3.1-8b-instant",
}

# Groq pricing (paid/developer tier, per 1M tokens, sourced June 2026)
PRICING = {
    "llama-3.3-70b-versatile":                    {"input": 0.59, "output": 0.79},
    "meta-llama/llama-4-scout-17b-16e-instruct":  {"input": 0.11, "output": 0.34},
    "llama-3.1-8b-instant":                        {"input": 0.05, "output": 0.08},
}

JUDGE_MODEL = "llama-3.3-70b-versatile"   # best available for judging
OUTPUT_CSV  = "results.csv"

# ── Prompts ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a professional summarizer. Read the document and return EXACTLY "
    "3 concise bullet points that capture the most important information. "
    "Each bullet must start with '• ' and be one sentence. "
    "Return only the 3 bullets — no preamble, no headings, no extra text."
)

JUDGE_SYSTEM = (
    "You are an objective evaluator. Score the quality of an AI-generated "
    "3-bullet summary on a scale of 1–5.\n\n"
    "Scoring rubric:\n"
    "5 = All 3 bullets accurate, distinct, capture the most important points\n"
    "4 = Mostly good, minor omissions or slight redundancy\n"
    "3 = Acceptable but misses a key point or has vague wording\n"
    "2 = Weak — inaccurate, repetitive, or only 1 good bullet\n"
    "1 = Poor — wrong, irrelevant, or format not followed\n\n"
    "Respond with ONLY a JSON object: {\"score\": <1-5>, \"reason\": \"<one sentence>\"}"
)

def build_user_prompt(doc):
    return f"Document:\n\n{doc}\n\nSummarize into 3 bullet points."

def build_judge_prompt(doc, summary):
    return f"Original document:\n{doc}\n\nGenerated summary:\n{summary}\n\nScore the summary quality."

# ── 20 Sample Documents ────────────────────────────────────────────────────────

DOCUMENTS = [
    """The Amazon rainforest, often described as the "lungs of the Earth," covers over 5.5 million
square kilometres across nine countries, with Brazil holding the largest share at about 60%.
It produces roughly 20% of the world's oxygen through photosynthesis and absorbs vast amounts
of carbon dioxide, playing a critical role in regulating the global climate. The forest is home
to an estimated 10% of all species on Earth, including 40,000 plant species, 1,300 bird species,
and 3,000 types of fish. Despite its importance, the Amazon has lost about 17% of its original
cover over the past 50 years, primarily due to agricultural expansion, illegal logging, and
infrastructure development. Scientists warn that if deforestation reaches 20–25%, the forest
could cross a tipping point and begin to self-destruct, transitioning to savannah. International
pressure, indigenous land rights campaigns, and sustainable agriculture initiatives are among
the forces working to slow destruction.""",

    """SpaceX successfully launched its Starship rocket on its fourth integrated flight test,
achieving a major milestone in the company's ambitions to develop a fully reusable launch
system capable of carrying humans to the Moon and Mars. The test saw both the Super Heavy
booster and the Starship upper stage complete controlled splashdowns for the first time, with
the booster executing a precise flip maneuver before touching the Gulf of Mexico and the
Starship surviving re-entry heating before splashing down in the Indian Ocean. The flight
lasted approximately 65 minutes. Elon Musk called the test a tremendous success, noting that
the heat shield tiles performed better than expected. NASA, which has contracted SpaceX to use
a version of Starship as the Human Landing System for the Artemis lunar missions, praised the
progress.""",

    """Artificial intelligence is rapidly transforming the healthcare industry, offering new tools
for disease diagnosis, drug discovery, and personalised treatment. Machine learning algorithms
trained on millions of medical images can now detect cancers and other conditions with accuracy
comparable to specialist physicians. In drug discovery, AI systems like AlphaFold have solved
the long-standing problem of protein structure prediction. Hospitals are deploying AI to predict
patient deterioration, optimise scheduling, and reduce administrative burdens on clinicians.
However, the technology also raises significant concerns around data privacy, algorithmic bias,
and the risk that AI tools trained on non-representative datasets may perform poorly for certain
demographic groups. Regulatory agencies in the US, EU, and UK are developing frameworks to
evaluate and approve AI medical devices.""",

    """The global semiconductor shortage exposed deep vulnerabilities in modern supply chains and
the extreme geographic concentration of chip manufacturing. Taiwan Semiconductor Manufacturing
Company (TSMC) alone produces over 90% of the world's most advanced chips, creating a single
point of failure that has alarmed governments worldwide. The shortage forced automotive
manufacturers to idle factories, delayed consumer electronics releases, and highlighted how a
disruption in a small island nation could ripple across every sector of the global economy.
In response, the United States passed the CHIPS and Science Act, committing $52 billion to
domestic semiconductor manufacturing. The European Union launched its own Chips Act, and
countries from Japan to India have announced incentives to attract semiconductor investment.""",

    """Climate change is altering ocean ecosystems at an unprecedented rate, with rising sea
temperatures, ocean acidification, and deoxygenation combining to create what scientists call
the triple threat to marine life. Coral reefs, which support about 25% of all marine species
despite covering less than 1% of the ocean floor, have experienced mass bleaching events of
increasing frequency and severity. Fish populations are shifting poleward as they follow cooler
water, disrupting fisheries that millions of people depend on for food and income. Ocean
acidification threatens shell-forming organisms at the base of marine food webs. Researchers
are exploring interventions such as assisted evolution of heat-tolerant coral, shading reefs
with floating screens, and marine protected areas. Without significant reductions in greenhouse
gas emissions, scientists project that coral reefs could functionally disappear by end of
century.""",

    """The European Union's General Data Protection Regulation (GDPR), which came into force in
May 2018, fundamentally changed how organisations around the world handle personal data.
The regulation grants EU citizens broad rights including the right to access their data, the
right to have it deleted, and the right to know how it is being used. It imposes strict
obligations on companies, requiring them to obtain explicit consent for data collection,
appoint data protection officers, and report breaches within 72 hours. Penalties for
non-compliance can reach €20 million or 4% of global annual turnover. Since its introduction,
regulators have levied billions of euros in fines against major technology companies including
Meta, Google, and Amazon. The GDPR has also inspired similar legislation in California,
Brazil, and other jurisdictions.""",

    """Quantum computing promises to solve certain categories of problems exponentially faster
than classical computers, with potential applications in cryptography, materials science,
drug discovery, and optimisation. Unlike classical bits, which represent either 0 or 1,
quantum bits (qubits) can exist in superpositions of both states simultaneously. IBM, Google,
Microsoft, and a growing ecosystem of startups are racing to build fault-tolerant quantum
computers. Practical, fault-tolerant quantum computers remain years or decades away because
current "noisy intermediate-scale quantum" devices are too error-prone for most real-world
applications. A major concern is that sufficiently powerful quantum computers could break
current RSA and elliptic-curve encryption, motivating global efforts to develop post-quantum
cryptographic standards.""",

    """Urbanisation is one of the most significant demographic trends of the 21st century. By
2050, approximately 68% of the world's population is expected to live in cities, up from
about 55% today. This rapid growth is placing enormous pressure on infrastructure, housing,
transportation, and public services, particularly in developing nations. Smart city
technologies, including IoT sensors, AI-driven traffic management, and data analytics
platforms, are being deployed to improve urban efficiency and quality of life. However,
urbanisation also drives inequality: informal settlements and slums house over a billion
people globally. Climate change compounds the challenge, as many of the fastest-growing
cities are in coastal regions or areas vulnerable to extreme heat.""",

    """The global mental health crisis has worsened significantly since the COVID-19 pandemic,
with rates of depression, anxiety, and loneliness rising across all age groups. The World
Health Organization estimates that depression alone affects more than 280 million people
worldwide. Mental health conditions account for a significant portion of the global burden
of disease yet receive historically underfunded and understaffed care systems. Digital mental
health tools — apps, online therapy platforms, and AI chatbots — have expanded access for
some populations but raise concerns about evidence quality and data privacy. Workplace mental
health programmes have grown in prominence, with employers recognising that poor mental health
costs billions in lost productivity annually.""",

    """The history of the internet dates to the late 1960s, when ARPANET first connected computers
at universities and research institutions. Tim Berners-Lee invented the World Wide Web in 1989
while working at CERN, introducing URLs, HTML, and HTTP that made information navigable by
ordinary users. The commercialisation of the internet accelerated through the 1990s with the
rise of dial-up providers, search engines, and e-commerce platforms. The dot-com bubble of
the late 1990s saw massive speculation followed by a crash, but the underlying infrastructure
continued to grow. The 2010s brought mobile internet, social media platforms, and cloud
computing, fundamentally changing how billions of people communicate, work, and shop.
Today, more than 5 billion people are connected to the internet.""",

    """Electric vehicles are reshaping the global automotive industry at an accelerating pace.
Global EV sales surpassed 10 million units in 2022 and have continued to grow, with China
accounting for the largest share. Battery costs have fallen by over 90% since 2010, making
EVs increasingly cost-competitive with internal combustion engine vehicles. Governments
worldwide are setting targets to phase out petrol and diesel car sales, with the UK, EU,
and several US states targeting 2035. Mining lithium, cobalt, and nickel for battery
materials raises environmental and human rights concerns. Charging infrastructure, particularly
in rural areas, remains a barrier to adoption. Tesla, BYD, and legacy automakers are investing
hundreds of billions in the transition.""",

    """Antibiotic resistance is one of the greatest public health threats of the 21st century.
The World Health Organization estimates it currently causes at least 1.27 million deaths
directly each year and contributes to millions more. Without action, AMR could kill 10 million
people annually by 2050. The pipeline of new antibiotics is alarmingly thin; developing a
new antibiotic takes 10–15 years and offers limited financial returns, so pharmaceutical
companies have largely exited the field. Stewardship programmes that promote appropriate
prescribing, investment in diagnostics, and international surveillance agreements are seen
as critical near-term interventions. Longer-term, phage therapy and AI-assisted drug discovery
offer hope but remain largely unproven at scale.""",

    """The James Webb Space Telescope, launched on December 25, 2021, represents the most powerful
space observatory ever built and has already transformed our understanding of the early
universe, exoplanet atmospheres, and galaxy formation. Operating primarily in the infrared
spectrum, Webb can peer through dust clouds that obscured Hubble's view, allowing scientists
to observe the first galaxies that formed just 300 million years after the Big Bang. Its
instruments detected water vapour, carbon dioxide, and methane in the atmospheres of
exoplanets, advancing the search for potentially habitable worlds. The telescope resides at
the second Lagrange point, about 1.5 million kilometres from Earth, where its sunshield keeps
it cool enough to detect faint infrared signals. It carries enough fuel for a 20-year
mission.""",

    """Social media platforms have fundamentally altered political communication, enabling direct
engagement between politicians and constituents but also amplifying misinformation and
polarisation. Studies find that algorithmic recommendation systems optimise for engagement,
which tends to favour emotionally charged and divisive content. The 2016 US presidential
election and Brexit referendum highlighted how social media could be weaponised through
targeted advertising and viral misinformation. Platforms have introduced fact-checking labels
and banned high-profile accounts, triggering debates about censorship and free speech. The
EU's Digital Services Act imposes new transparency obligations on large platforms. Researchers
are divided on the magnitude of social media's effects compared to traditional media and
economic factors.""",

    """The global food system faces an enormous challenge: feeding a projected 10 billion people
by 2050 while reducing its environmental footprint. Agriculture currently accounts for about
25% of global greenhouse gas emissions, uses 70% of freshwater withdrawals, and is the
leading driver of biodiversity loss. A shift toward more plant-based diets is widely seen as
essential, given that producing animal protein is far more resource-intensive. Alternative
proteins — including plant-based meat substitutes, cultured meat, and insect-based foods —
are attracting significant investment. Precision agriculture, using drones, sensors, and AI
to optimise inputs, promises to reduce chemical use and improve yields. Food security remains
deeply unequal: over 700 million people are chronically undernourished.""",

    """The human microbiome — the trillions of microorganisms living in and on the human body —
has emerged as a major focus of biomedical research. The gut microbiome has been linked to
immune function, mental health, metabolism, and susceptibility to chronic diseases including
obesity and type 2 diabetes. Research suggests that early life exposure to diverse microbes,
influenced by birth mode, breastfeeding, and antibiotic use, shapes long-term health outcomes.
Faecal microbiota transplantation has proven highly effective for recurrent Clostridioides
difficile infections and is being investigated for conditions ranging from autism to cancer
immunotherapy response. The field is moving toward personalised microbiome interventions
tailored based on an individual's microbial profile.""",

    """The global shipping industry carries approximately 80–90% of world trade by volume, making
it the backbone of the global economy. It is also a significant source of greenhouse gas
emissions, accounting for about 3% of global CO2 output. The International Maritime
Organization has set a target of net zero emissions by 2050, but decarbonising shipping is
technically challenging because vessels need energy-dense fuels for long ocean voyages.
Ammonia, methanol, hydrogen, and liquefied natural gas are all being evaluated as cleaner
alternatives to heavy fuel oil. Slow steaming — simply reducing vessel speeds — has become
a widely adopted near-term measure that cuts fuel consumption and emissions by 10–20%.""",

    """Gene editing technology, particularly CRISPR-Cas9, has opened new frontiers in medicine
and agriculture. CRISPR-based therapies for sickle cell disease and beta-thalassaemia
received regulatory approval in 2023, the first approved CRISPR therapies in humans.
Clinical trials are exploring applications in cancer, HIV, inherited blindness, and high
cholesterol. In agriculture, CRISPR is being used to develop disease-resistant crops and
drought-tolerant varieties. The technology raises profound ethical questions, particularly
around heritable germline editing — modifying embryos in ways passed to future generations.
A 2018 incident where a Chinese scientist created gene-edited babies sparked global
condemnation and calls for a moratorium on reproductive germline editing.""",

    """The rise of remote work, accelerated by the COVID-19 pandemic, has permanently changed
assumptions about where knowledge work gets done. Before 2020, fully remote work was rare;
within weeks of lockdowns, hundreds of millions of office workers shifted home. Survey data
suggest workers prefer hybrid or fully remote arrangements and are willing to take pay cuts
to maintain flexibility. Some major firms have mandated returns to the office citing culture
and collaboration, while others have embraced remote-first models to expand talent pools.
Commercial real estate markets have been severely disrupted. The debate over the optimal
balance between in-person and remote work remains unresolved and will continue shaping
corporate culture for years.""",

    """The International Space Station (ISS), continuously inhabited since November 2000, is one
of the most complex engineering projects in human history, costing over $150 billion and
requiring contributions from 15 nations. Orbiting approximately 400 kilometres above Earth,
the ISS has hosted more than 270 astronauts and served as a platform for thousands of
scientific experiments in microgravity. NASA has announced plans to deorbit the ISS by 2030,
with a SpaceX Dragon capsule guiding it to a controlled re-entry over an uninhabited ocean
area. Commercial successors built by Axiom Space and Starlab are in development to maintain
a US-led low-Earth orbit presence. China completed its own Tiangong space station in 2022,
setting the stage for a new era of competition in space.""",
]

# ── Helpers ────────────────────────────────────────────────────────────────────

def compute_cost(model_id, input_tokens, output_tokens):
    p = PRICING[model_id]
    return (input_tokens / 1_000_000) * p["input"] + (output_tokens / 1_000_000) * p["output"]


def call_model(model_id, document):
    for attempt in range(3):
        try:
            start = time.perf_counter()
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": build_user_prompt(document)},
                ],
                temperature=0.2,
                max_tokens=300,
            )
            latency_ms = (time.perf_counter() - start) * 1000

            usage         = response.usage
            input_tokens  = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            cost          = compute_cost(model_id, input_tokens, output_tokens)

            return {
                "text":          response.choices[0].message.content.strip(),
                "latency_ms":    round(latency_ms, 1),
                "input_tokens":  input_tokens,
                "output_tokens": output_tokens,
                "cost_usd":      cost,
            }
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"    Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise


def judge_quality(document, summary):
    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model=JUDGE_MODEL,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM},
                    {"role": "user",   "content": build_judge_prompt(document, summary)},
                ],
                temperature=0,
                max_tokens=150,
            )
            raw = response.choices[0].message.content.strip()
            raw = re.sub(r"```(?:json)?", "", raw).strip().rstrip("`").strip()
            try:
                data = json.loads(raw)
                return int(data["score"]), str(data.get("reason", ""))
            except Exception:
                match = re.search(r'"score"\s*:\s*([1-5])', raw)
                score = int(match.group(1)) if match else 3
                return score, raw[:120]
        except Exception as e:
            if "429" in str(e) and attempt < 2:
                wait = 30 * (attempt + 1)
                print(f"    Judge rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise

# ── Main ───────────────────────────────────────────────────────────────────────

def run_benchmark():
    fieldnames = [
        "input_id", "model", "latency_ms",
        "input_tokens", "output_tokens", "cost_usd",
        "quality_score_1to5", "notes",
    ]
    results = []
    total = len(MODELS) * len(DOCUMENTS)
    done  = 0

    print(f"\n{'='*65}")
    print(f"  Groq Model Benchmark — {datetime.now():%Y-%m-%d %H:%M}")
    print(f"  Task: 1-page doc → 3-bullet summary")
    print(f"  Models: {', '.join(MODELS.keys())}")
    print(f"  Documents: {len(DOCUMENTS)}  |  Total API calls: {total * 2} (bench + judge)")
    print(f"{'='*65}\n")

    for label, model_id in MODELS.items():
        print(f"\n── {label} ──")
        for idx, doc in enumerate(DOCUMENTS):
            doc_id = f"doc_{idx+1:02d}"
            try:
                result = call_model(model_id, doc)
                score, reason = judge_quality(doc, result["text"])

                row = {
                    "input_id":           doc_id,
                    "model":              label,
                    "latency_ms":         result["latency_ms"],
                    "input_tokens":       result["input_tokens"],
                    "output_tokens":      result["output_tokens"],
                    "cost_usd":           round(result["cost_usd"], 8),
                    "quality_score_1to5": score,
                    "notes":              reason,
                }
                results.append(row)
                done += 1
                print(
                    f"  [{done:3d}/{total}] {doc_id} | "
                    f"{result['latency_ms']:.0f}ms | "
                    f"tok={result['input_tokens']}+{result['output_tokens']} | "
                    f"${result['cost_usd']:.6f} | "
                    f"quality={score}/5"
                )
            except Exception as e:
                print(f"  ERROR on {doc_id}: {e}")
                results.append({
                    "input_id": doc_id, "model": label,
                    "latency_ms": -1, "input_tokens": -1, "output_tokens": -1,
                    "cost_usd": -1, "quality_score_1to5": -1,
                    "notes": f"ERROR: {e}",
                })

            time.sleep(1)  # 1s gap — free tier is ~30 RPM

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    print(f"\n✅  Results written to {OUTPUT_CSV}")
    print_summary(results)


def print_summary(results):
    from collections import defaultdict
    agg = defaultdict(lambda: {"lat": [], "cost": [], "q": [], "ti": [], "to": []})
    for r in results:
        if r["latency_ms"] < 0:
            continue
        m = r["model"]
        agg[m]["lat"].append(r["latency_ms"])
        agg[m]["cost"].append(r["cost_usd"])
        agg[m]["q"].append(r["quality_score_1to5"])
        agg[m]["ti"].append(r["input_tokens"])
        agg[m]["to"].append(r["output_tokens"])

    def avg(l): return sum(l) / len(l) if l else 0

    print(f"\n{'='*75}")
    print("  Per-Model Averages")
    print(f"  {'Model':<35} {'Lat(ms)':>8} {'Cost($)':>10} {'Quality':>8} {'InTok':>7} {'OutTok':>7}")
    print(f"  {'-'*35} {'-'*8} {'-'*10} {'-'*8} {'-'*7} {'-'*7}")
    for m, d in agg.items():
        print(
            f"  {m:<35} {avg(d['lat']):>8.1f} "
            f"{avg(d['cost']):>10.7f} {avg(d['q']):>8.2f} "
            f"{avg(d['ti']):>7.0f} {avg(d['to']):>7.0f}"
        )
    print(f"{'='*75}\n")


if __name__ == "__main__":
    run_benchmark()