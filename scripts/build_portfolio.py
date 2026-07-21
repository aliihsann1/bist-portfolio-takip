"""
Bu script transactions.json'daki işlemleri okur, borsapy ile güncel fiyatları
çeker, pozisyonları (ağırlıklı ortalama maliyet ile) hesaplar ve sonucu
portfolio.json'a yazar. GitHub Actions bunu düzenli aralıklarla çalıştırır.

Elle çalıştırmak için:
    pip install borsapy pandas
    python scripts/build_portfolio.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import borsapy as bp

ROOT = Path(__file__).resolve().parent.parent
TRANSACTIONS_FILE = ROOT / "transactions.json"
PORTFOLIO_FILE = ROOT / "portfolio.json"

MAX_HISTORY_POINTS = 3000  # dosya büyümesin diye eski noktaları seyreltiyoruz


def load_transactions():
    if not TRANSACTIONS_FILE.exists():
        return []
    with open(TRANSACTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def load_previous_portfolio():
    if not PORTFOLIO_FILE.exists():
        return {"history": []}
    try:
        with open(PORTFOLIO_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"history": []}


def get_current_price(symbol, asset_type):
    """Varlık tipine göre borsapy'den güncel fiyatı çeker."""
    try:
        if asset_type == "stock":
            return float(bp.Ticker(symbol).fast_info["last_price"])
        elif asset_type == "fund":
            hist = bp.Fund(symbol).history(period="5d")
            return float(hist["Close"].iloc[-1])
        elif asset_type == "fx":
            return float(bp.FX(symbol).current)
        elif asset_type == "crypto":
            return float(bp.Crypto(symbol).current)
        else:
            print(f"Bilinmeyen asset_type: {asset_type} ({symbol})", file=sys.stderr)
            return None
    except Exception as e:
        print(f"Fiyat çekilemedi: {symbol} ({asset_type}) -> {e}", file=sys.stderr)
        return None


def compute_holdings(transactions):
    """Ağırlıklı ortalama maliyet yöntemiyle pozisyonları hesaplar."""
    tx_sorted = sorted(transactions, key=lambda t: t["date"])
    positions = {}  # symbol -> {asset_type, shares, cost}

    for tx in tx_sorted:
        symbol = tx["symbol"]
        asset_type = tx["asset_type"]
        shares = float(tx["shares"])
        price = float(tx["price"])

        if symbol not in positions:
            positions[symbol] = {"asset_type": asset_type, "shares": 0.0, "cost": 0.0}
        pos = positions[symbol]

        if tx["action"] == "Alış":
            pos["shares"] += shares
            pos["cost"] += shares * price
        else:  # Satış
            avg_cost = pos["cost"] / pos["shares"] if pos["shares"] > 0 else 0
            pos["shares"] -= shares
            pos["cost"] -= shares * avg_cost
            if pos["shares"] < 1e-9:
                pos["shares"] = 0.0
                pos["cost"] = 0.0

    return {sym: p for sym, p in positions.items() if p["shares"] > 1e-9}


def main():
    transactions = load_transactions()
    previous = load_previous_portfolio()
    positions = compute_holdings(transactions)

    holdings = []
    total_value = 0.0
    total_cost = 0.0

    # önceki çalıştırmadaki fiyatları fallback olarak tutalım (API hatasında)
    prev_prices = {h["symbol"]: h["current_price"] for h in previous.get("holdings", [])}

    for symbol, pos in positions.items():
        avg_cost = pos["cost"] / pos["shares"]
        price = get_current_price(symbol, pos["asset_type"])
        if price is None:
            price = prev_prices.get(symbol, avg_cost)

        value = pos["shares"] * price
        cost_basis = pos["cost"]
        pnl_tl = value - cost_basis
        pnl_pct = (pnl_tl / cost_basis * 100) if cost_basis > 0 else 0.0

        holdings.append({
            "symbol": symbol,
            "asset_type": pos["asset_type"],
            "shares": pos["shares"],
            "avg_cost": avg_cost,
            "current_price": price,
            "value": value,
            "cost_basis": cost_basis,
            "pnl_tl": pnl_tl,
            "pnl_pct": pnl_pct,
        })

        total_value += value
        total_cost += cost_basis

    holdings.sort(key=lambda h: h["value"], reverse=True)

    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0

    now = datetime.now(timezone.utc).isoformat()

    history = previous.get("history", [])
    history.append({"t": now, "v": total_value, "pnl_pct": total_pnl_pct})
    if len(history) > MAX_HISTORY_POINTS:
        # eski noktaları 2'de 1 seyrelt, dosya şişmesin
        history = history[::2]

    output = {
        "generated_at": now,
        "holdings": holdings,
        "totals": {
            "value": total_value,
            "cost": total_cost,
            "pnl_tl": total_pnl,
            "pnl_pct": total_pnl_pct,
        },
        "history": history,
        "transactions": sorted(transactions, key=lambda t: t["date"], reverse=True),
    }

    with open(PORTFOLIO_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"portfolio.json güncellendi. Toplam değer: {total_value:.2f} TL")


if __name__ == "__main__":
    main()
