<div class="center-align">
  <h1>darninator 🦆</h1>
  <p><i>(Because darwinator was taken). Institutional-grade quantitative value screening, open-sourced.</i></p>
  <p>Over thousands of years of human history, we have attempted to predict the future through everything from celestial alignments to bad gut feelings (and occasionally reading spreadsheets). Inspired by Pulak Prasad’s framework in <i>What I Learned from Darwin on Investing</i>, <strong>Darninator</strong> treats businesses as organisms—evaluating which corporate entities are structurally "fit" to survive and discarding the junk through a ruthless, unemotional pipeline.</p>
</div>

<hr>

<h2>📖 Contents</h2>
<ul>
  <li><a href="#the-overview">The Overview</a></li>
  <li><a href="#core-architecture">Core Architecture: The Layers of Defense</a></li>
  <li><a href="#quick-start">Quick Start: For Those Who Hate Manual Labor</a></li>
  <li><a href="#quantitative-methodology">The Quantitative Methodology: Expert Mode</a></li>
  <li><a href="#known-limitations">Known Limitations</a></li>
  <li><a href="#project-structure">Project Structure</a></li>
  <li><a href="#legal-disclaimer">Legal Disclaimer</a></li>
</ul>

<hr>

<h2 id="the-overview"><span class="emoji">🔍</span>The Overview</h2>
<p>Darninator is a two-stage pipeline designed to turn messy, raw market data into a curated watchlist of high-conviction value opportunities. It automates the "heavy lifting" of fundamental analysis (the parts that usually make me want to take a nap).</p>
<ul>
  <li><strong>Ingestion Phase (<code>initialize.py</code>):</strong> A defensive scraper that queries Yahoo Finance, extracts accounting sheets, and populates a local JSON cache. It includes built-in rate limiting to prevent us from getting blocked by their security protocols (which are much smarter than I am).</li>
  <li><strong>Screening Phase (<code>darninator.py</code>):</strong> A vectorized processing engine that consumes the cache, applies multi-pillar scoring, filters via hard institutional constraints, and outputs a chronologically versioned CSV report grouped by conviction tiers.</li>
</ul>

<h2 id="core-architecture"><span class="emoji">🏗</span>Core Architecture: The Layers of Defense</h2>
<p>To prevent the system from collapsing under its own weight (much like my ambitions), it is built on four distinct layers:</p>
<ul>
  <li><strong>Persistence Layer:</strong> Uses a disk-based JSON cache (<code>cache.py</code>) with TTL expiration to ensure data freshness without redundant network requests.</li>
  <li><strong>Resiliency Layer:</strong> Implements a <code>CheckpointManager</code> so that if the process crashes (and it might), you can resume without starting from a fresh misery.</li>
  <li><strong>Execution Layer:</strong> Utilizes vectorized transformation via <code>pandas</code> and <code>numpy</code>. Unlike standard loops, this allows for $O(1)$ complexity on metric calculations across the entire universe simultaneously.</li>
  <li><strong>Network Layer:</strong> Features a <code>RateLimiter</code> to respect API etiquette and maintain high uptime during large-scale ingestions.</li>
</ul>

<h2 id="quick-start"><span class="emoji">🚀</span>Quick Start: For Those Who Hate Manual Labor</h2>

<h3>1. Prerequisites</h3>
<p>Ensure you have Python 3.8+ installed (and a functioning internet connection).</p>

<h3>2. Installation</h3>
<p>Clone the repository and install the necessary dependencies:</p>
<pre><code>git clone https://github.com/your-username/darninator.git
cd darninator
pip install -r requirements.txt</code></pre>

<h3>3. Prepare Your Universe</h3>
<p>Edit <code>all_tickers.txt</code> to include the stock tickers you wish to track—one per line.</p>

<h3>4. Step 1: Populate the Cache</h3>
<p>Run the ingestion engine to download fundamental data:</p>
<pre><code>python initialize.py</code></pre>
<p>You will see <code>[ticker] ✅ successfully written</code> for every successful fetch.</p>

<h3>5. Step 2: Run the Screen</h3>
<p>Execute the pipeline to generate your report:</p>
<pre><code>python darninator.py</code></pre>
<p>The results appear in the <code>/output</code> directory as a timestamped CSV (e.g., <code>20260620_darninator.csv</code>) split into <strong>Tier 1 (Alpha/Further Research)</strong> and <strong>Tier 2 (Secondary Core)</strong> targets.</p>

<h2 id="quantitative-methodology"><span class="emoji">🧠</span>The Quantitative Methodology: Expert Mode</h2>
<p>Darninator does not just "filter" stocks; it calculates a weighted geometric mean of three distinct fundamental pillars.</p>

<h3>The Three Pillars</h3>
<p>The engine calculates normalized percentile ranks (0–100) for metrics within each pillar:</p>

<table border="1" cellpadding="5" cellspacing="0">
  <thead>
    <tr>
      <th align="left">Pillar</th>
      <th align="left">Metrics Included</th>
      <th align="left">Weight ($w$)</th>
      <th align="left">Objective</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Quality</strong></td>
      <td>ROCE, ROIC-WACC spread, EBIT margin</td>
      <td>40%</td>
      <td>Find efficient capital compounders</td>
    </tr>
    <tr>
      <td><strong>Valuation</strong></td>
      <td>EV/EBITDA, FCF yield, PE ratio</td>
      <td>35%</td>
      <td>Ensure we buy them cheap when no one loves them</td>
    </tr>
    <tr>
      <td><strong>Health</strong></td>
      <td>Net Debt/EBITDA, Interest Coverage, Current Ratio</td>
      <td>25%</td>
      <td>Survival defense against bankruptcy and macro shocks</td>
    </tr>
  </tbody>
</table>

<h3>The Composite Score Formula</h3>
<p>$$Score = (Rank_{qual})^{0.40} \times (Rank_{val})^{0.35} \times (Rank_{health})^{0.25}$$</p>

<blockquote>
  <p><strong>Why the Geometric Mean?</strong><br>
  Most amateur investment screeners use a simple arithmetic average. If a company scores 100/100 on Quality but 0/100 on Valuation, a simple average marks it as a mediocre 50. The Darninator does not tolerate mediocrity. The geometric mean is <strong>intentionally punitive</strong>. If <em>any</em> single pillar drops toward zero, the entire final score collapses, ensuring the pipeline only surfaces companies that excel across all three dimensions simultaneously.</p>
</blockquote>

<h3>The Institutional Sieve (Hard Constraints)</h3>
<p>After ranking, we apply a "sieve" to remove companies that do not meet our entry requirements:</p>
<ul>
  <li><strong>Market cap floor:</strong> $\ge \$1\text{B}$</li>
  <li><strong>Valuation cap:</strong> $\text{PE} \le 15.0$</li>
  <li><strong>Profitability gate:</strong> $\text{EBIT margin} > 0\%$</li>
  <li><strong>Solvency gate:</strong> $\text{Net Debt/EBITDA} \le 3.5$</li>
</ul>
<p>Only stocks passing <em>all</em> sieves advance to the final ranked output.</p>

<h2 id="known-limitations"><span class="emoji">⚠️</span>Known Limitations</h2>
<ul>
  <li><strong>Value Traps &amp; Data Integrity:</strong> The tool assumes incoming data from third-party APIs is accurate. While it treats missing data harshly, it cannot autonomously spot fat-finger data entry errors from upstream sources (e.g., millions mixed up with billions or raw currency conversion glitches).</li>
  <li><strong>Regional / ADR Risk:</strong> A significant number of stocks passing the US market screen are international ADRs trading on US exchanges. You must factor in localized geopolitical or currency risks independently.</li>
  <li><strong>Point-in-Time Static Output:</strong> This tool produces a static financial snapshot. If you are someone who acts purely on real-time news alerts, macro events, or sentiment shifts, this point-in-time calculation engine is not for you.</li>
</ul>

<h2 id="project-structure"><span class="emoji">📂</span>Project Structure</h2>
<pre><code>darninator/
├── cache/                  # persistent json storage for fundamentals
├── output/                 # final timestamped csv reports
├── all_tickers.txt         # your target universe (input)
├── cache.py                # cache management & ttl logic
├── darninator.py           # the core quantitative engine
├── initialize.py           # data ingestion & yfinance scraper
├── requirements.txt        # dependency manifest
└── readme.md               # this document</code></pre>

<h2 id="legal-disclaimer"><span class="emoji">⚖️</span>Legal Disclaimer</h2>
<p>All information provided by this screening utility is intended exclusively for educational research and informational purposes. This tool does not provide personalized investment advice, financial planning, or tax counsel. Quantitative screening results are based on historical financial metrics sourced from third-party APIs; validity, accuracy, and completeness cannot be guaranteed. The user assumes all operational and financial risk associated with data deployment, strategy implementation, or calculation error. Developers and authors shall not be held liable for any direct, indirect, incidental, or consequential trading losses or damages.</p>
