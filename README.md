darninator
<p align="center"> <i> (because darwinator was taken) over thousands of years of human history, we have attempted to predict the future through everything from celestial alignments to bad gut feelings (and occasionally reading spreadsheets). but since i am entirely unqualified to comment on actual economic theory, here is darninator.</i> </p> <p align="center"> <img src="https://img.shields.io/badge/license-mit-blue?style=flat-square" alt="license"> <img src="single-point-institutional-configuration-map" src="https://img.shields.io/badge/status-experimental-orange?style=flat-square" alt="status"> </p>
📖 contents
the overview
core architecture (the layers of defense)
quick start: for those who hate manual labor
the quantitative methodology (expert mode)
project structure
legal disclaimer
🔍 the overview
darninator is a two-stage pipeline designed to turn messy, raw market data into a curated watchlist of high-conviction value opportunities. it automates the "heavy lifting" of fundamental analysis (the parts that usually make me want to take a nap).

ingestion phase (initialize.py): a defensive scraper that queries yahoo finance, extracts accounting sheets, and populating a local json cache. it includes built-in rate limiting to prevent us from getting blocked by their security protocols (which are much smarter than i am).
screening phase (darninator.py): a vectorized processing engine that consumes the cache, applies multi-pillar scoring, and outputs a chronologically versioned csv report.
🏗 core architecture: the layers of defense
to prevent the system from collapsing under its own weight (much like my ambitions), it is built on four distinct layers:

persistence layer: uses a disk-based json cache (cache.py) with ttl expiration to ensure data freshness without redundant network requests.
resiliency layer: implements a checkpointmanager so that if the process crashes (and it might), you can resume without starting from zero.
execution layer: utilizes vectorized transformation via pandas and numpy. unlike standard loops, this allows for 
O
(
1
)
O(1) complexity on metric calculations across the entire universe simultaneously.
network layer: a built-in ratelimiter to respect api etiquette and maintain high uptime during large-scale ingestions.
🚀 quick start: for those who hate manual labor
prerequisites
ensure you have python 3.8+ installed (and a functioning internet connection).

installation
bash
git clone https://github.com/cptsparr0w/darninator.git
cd darninator
pip install -r requirements.txt
step 1: prepare your universe
edit all_tickers.txt to include the stock tickers you wish to track—one per line.

step 2: populate the cache
run the ingestion engine to download fundamental data.

bash
python initialize.py
you will see [ticker] ✅ successfully written for every successful fetch.

step 3: run the screen
execute the pipeline to generate your report.

bash
python darninator.py
the results appear in the /output directory as a timestamped csv (e.g., 20231027_darninator.csv).

🧠 the quantitative methodology: expert mode
darninator does not just "filter" stocks; it calculates a weighted geometric mean of three distinct fundamental pillars.

the three pillars
the engine calculates normalized percentile ranks (0–100) for metrics within each pillar:

pillar	metrics included	weight (
w
w)
quality	roce, roic-wacc spread, ebit margin	
40
%
40%
valuation	ev/ebitda, fcf yield, pe ratio	
35
%
35%
health	net debt/ebitda, interest coverage, current ratio	
25
%
25%
the composite score formula
score
=
(
rank
qual
)
0.40
×
(
rank
val
)
0.35
×
(
rank
health
)
0.25
score=(rank 
qual
​
 ) 
0.40
 ×(rank 
val
​
 ) 
0.35
 ×(rank 
health
​
 ) 
0.25
 

the institutional sieve (hard constraints)
after ranking, we apply a "sieve" to remove companies that do not meet our entry requirements:

market cap floor: 
≥
$
1
b
≥$1b
valuation cap: 
pe
≤
15.0
pe≤15.0
profitability gate: 
ebit margin
>
0
%
ebit margin>0%
solvency gate: 
net debt/ebitda
≤
3.5
net debt/ebitda≤3.5
📂 project structure
darninator/
├── cache/               # persistent json storage for fundamentals
├── output/              # final timestamped csv reports
├── all_tickers.txt      # your target universe (input)
├── cache.py             # cache management & ttl logic
├── darninator.py        # the core quantitative engine
├── initialize.py        # data ingestion & yfinance scraper
├── requirements.txt     # dependency manifest
└── readme.md            # this document
⚖️ legal disclaimer
all information provided by this screening utility is intended exclusively for educational research and informational purposes. this tool does not provide personalized investment advice, financial planning, or tax counsel. quantitative screening results are based on historical financial metrics sourced from third-party apis; validity, accuracy, and completeness cannot be guaranteed. the user assumes all operational and financial risk associated with data deployment, strategy implementation, or calculation error. developers and authors shall not be held liable for any direct, indirect, incidental, or consequential trading losses or damages.

<p align="center"> <b>credits:</b> built by <a href="https://opensourceholdings.com">opensourceholdings.com</a>. inspired by the work found at <a href="https://firstmillion.substack.com">firstmillion.substack.com</a>. source code lives with <a href="https://github.com/cptsparr0w">cptsparr0w</a> on github.<br> <b>contact:</b> <a href="mailto:contact@opensourceholdings.com">contact@opensourceholdings.com</a> | <a href="https://opensourceholdings.com">opensourceholdings.com</a> </p> <p align="center"> <i>thank you for nourishing my narcissism. what is your favorite way to misinterpret financial data?</i> </p>
