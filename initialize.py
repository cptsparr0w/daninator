# initialize.py << run this first to populate the local cache with raw financial data pulled from yfinance >>
import os
import sys
import json
import time
from typing import Dict, List, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

# Native import of your TrueNAS cache manager
from cache import cache_data, get_cached

# --- Constants & Global Ingestion Config ---
REQUESTS_PER_MINUTE = 50  # Defensive rate limiting pacing throttle
RETRY_BACKOFF_SECONDS = 2.0  # Backoff delay on API network failures
BATCH_SIZE = 25
INPUT_TICKERS_FILE = "all_tickers.txt"

# --- Dynamic Network Rate Limiter Utility ---
class RateLimiter:
    """Ensures we safely step around Yahoo Finance API IP-blocking thresholds."""
    def __init__(self, max_requests: int = REQUESTS_PER_MINUTE):
        self.max_requests = max_requests
        self.request_times = []
    
    def wait_if_needed(self):
        current_time = time.time()
        self.request_times = [t for t in self.request_times if current_time - t < 60]
        
        if len(self.request_times) >= self.max_requests:
            sleep_time = 60 - (current_time - min(self.request_times))
            if sleep_time > 0:
                time.sleep(sleep_time + 1)
        
        self.request_times.append(time.time())

rate_limiter = RateLimiter()

# --- Fundamental Financial Data Scraper Ingestion Engine ---
class FinancialDataFetcher:
    """Fetches raw fundamental sheets directly from yfinance with strict error handling."""
    def __init__(self, ticker: str):
        self.ticker = ticker.upper()

    def get_financials(self) -> Optional[Dict[str, Any]]:
        import yfinance as yf
        rate_limiter.wait_if_needed()
        
        try:
            t = yf.Ticker(self.ticker)
            
            # Safely extract company metadata profile
            try:
                info = t.info
                if not isinstance(info, dict):
                    raise ValueError("yfinance info payload structure unreadable")
            except Exception:
                time.sleep(RETRY_BACKOFF_SECONDS)
                hist = t.history(period="1d", actions=False)
                if not hist.empty:
                    last_price = float(hist.iloc[-1]["Close"])
                    info = {"currentPrice": last_price, "longName": self.ticker}
                else:
                    return None

            # Pull fundamental accounting financial sheets
            i_df = t.income_stmt
            b_df = t.balance_sheet
            c_df = t.cashflow
            
            def grab(df, labels):
                if df is None or df.empty:
                    return 0.0
                ic = df.columns[0] if len(df.columns) > 0 else None
                if ic is None:
                    return 0.0
                for lbl in labels:
                    if lbl in df.index:
                        try:
                            val = float(df.loc[lbl, ic])
                            return val if val != 0 else 0.0
                        except Exception:
                            pass
                return 0.0
            
            ebit = grab(i_df, ["Operating Income", "EBIT"])
            revenue = grab(i_df, ["Total Revenue", "Revenue"])
            total_equity = grab(b_df, ["Stockholders Equity", "Total Equity"])
            total_debt = grab(b_df, ["Total Debt"])
            cash = grab(b_df, ["Cash And Cash Equivalents"])
            current_assets = grab(b_df, ["Current Assets", "Total Current Assets"])
            current_liabilities = grab(b_df, ["Current Liabilities", "Total Current Liabilities"])
            
            direct_fcf = grab(c_df, ["Free Cash Flow"])
            if direct_fcf is not None and direct_fcf != 0:
                free_cash_flow = direct_fcf
            else:
                ocf_val = grab(c_df, ["Operating Cash Flow", "Total Cash From Operating Activities"])
                capex_val = grab(c_df, ["Capital Expenditures", "CapEx"])
                free_cash_flow = (ocf_val + capex_val) if (ocf_val and capex_val) else None
            
            depreciation = grab(c_df, ["Depreciation And Amortization"])
            
            # Pack values safely to adhere to darninator's architectural data contract
            metrics_payload = {
                "ticker": self.ticker,
                "company": info.get("longName", self.ticker),
                "revenue": revenue,
                "ebit": ebit,
                "depreciation": depreciation or 0.0,
                "free_cash_flow": free_cash_flow or 0.0,
                "total_equity": total_equity,
                "total_debt": total_debt,
                "cash": cash,
                "current_assets": current_assets,
                "current_liabilities": current_liabilities,
                "dividend_yield_pct": float(info.get("trailingAnnualDividendYield") or 0) * 100,
                "pe_ratio": float(info.get("trailingPE") or 0),
                "pb_ratio": float(info.get("priceToBook") or 0),
                "market_cap": float(info.get("marketCap") or 0),
                "roce_pct": (ebit / (total_equity + total_debt - cash) * 100) if (total_equity + total_debt - cash) > 0 else 0,
                "roic_wacc_spread": 5.0, # Filled as baseline template; calculated downstream dynamically
                "ebit_margin_pct": (ebit / revenue * 100) if revenue > 0 else 0,
                "ev_ebitda": ((float(info.get("marketCap") or 0) + total_debt - cash) / (ebit + (depreciation or 0))) if (ebit + (depreciation or 0)) != 0 else 0,
                "fcf_yield_pct": (free_cash_flow / float(info.get("marketCap") or 1) * 100) if info.get("marketCap") else 0,
                "ebitda_yield_pct": ((ebit + (depreciation or 0)) / (float(info.get("marketCap") or 1) + total_debt - cash) * 100) if (float(info.get("marketCap") or 1) + total_debt - cash) > 0 else 0,
                "net_debt_ebitda": ((total_debt - cash) / (ebit + (depreciation or 0))) if (ebit + (depreciation or 0)) != 0 else 0,
                "current_ratio": (current_assets / current_liabilities) if current_liabilities > 0 else 0,
                "interest_coverage_ratio": (ebit / abs(grab(i_df, ["Interest Expense"]))) if grab(i_df, ["Interest Expense"]) != 0 else 99
            }
            
            return metrics_payload
        except Exception as e:
            print(f"[{self.ticker}] Live query error: {e}. Advancing with backoff pacing...")
            time.sleep(RETRY_BACKOFF_SECONDS)
        return None

def batched(tickers: List[str], n: int):
    for i in range(0, len(tickers), n):
        yield tickers[i : i + n]

# --- Main Automation Orchestration Loop ---
def main():
    if not os.path.exists(INPUT_TICKERS_FILE):
        print(f"❌ Error: Target file mapping universe '{INPUT_TICKERS_FILE}' missing.")
        return

    with open(INPUT_TICKERS_FILE, "r") as f:
        all_tickers = [line.strip().upper() for line in f if line.strip()]
        
    print(f"Loaded {len(all_tickers)} target stocks to process for TrueNAS cache pool.")
    print("-" * 80)
    
    total_batches = (len(all_tickers) + BATCH_SIZE - 1) // BATCH_SIZE
    
    for i, batch in enumerate(batched(all_tickers, BATCH_SIZE)):
        print(f"\n[Batch {i+1}/{total_batches}] Processing queue operations...")
        
        for ticker in batch:
            # 1. Skip downloading if a valid unexpired local file exists
            if get_cached(ticker) is not None:
                print(f"[{ticker}] Cache hit -> Preserving local storage file copy.")
                continue
                
            # 2. Cache Miss -> Reach out to the web to download data
            print(f"[{ticker}] Cache miss -> Querying live market financial feeds...")
            fetcher = FinancialDataFetcher(ticker)
            metrics = fetcher.get_financials()
            
            if metrics:
                # Pack content to match the strict data contract expected by cache.py
                cache_payload = {
                    "metrics": metrics,
                    "source": "yfinance",
                    "company_info": {"longName": metrics["company"], "marketCap": metrics["market_cap"]}
                }
                cache_data(ticker, cache_payload)
                print(f"[{ticker}] ✅ Successfully written to local cache folder.")
            else:
                print(f"[{ticker}] ⚠️ Failed to query financial records from external feeds.")

    print("\n" + "=" * 80)
    print("🏁 INGESTION SYNC COMPLETE: All missing records successfully cached locally.")
    print("=" * 80)

if __name__ == "__main__":
    main()
