# calculator.py

def calculate_target_price(
    sourcing_price_krw: float,
    weight_kg: float,
    markup_multiplier: float = 2.0,
    shipping_fee_per_kg_krw: float = 10000.0,
    platform_fee_percent: float = 10.0,  # e.g. 10%
    exchange_rate: float = 1350.0        # e.g. 1350 KRW per 1 USD
) -> dict:
    """
    Calculates the final listing price in target currency and estimates profits.
    
    Formula:
    1. Base Price (KRW) = Sourcing Price * Markup Multiplier
    2. Estimated Shipping (KRW) = Weight (kg) * Shipping Fee per KG
    3. Price before Platform Fees (KRW) = Base Price + Estimated Shipping
    4. Price with Platform Fees (KRW) = Price before Platform Fees / (1 - platform_fee_percent / 100)
    5. Final Price in Target Currency = Price with Platform Fees / Exchange Rate
    """
    base_price_krw = sourcing_price_krw * markup_multiplier
    shipping_fee_krw = weight_kg * shipping_fee_per_kg_krw
    
    price_before_fees_krw = base_price_krw + shipping_fee_krw
    
    fee_factor = 1.0 - (platform_fee_percent / 100.0)
    if fee_factor <= 0:
        fee_factor = 0.9  # Safe fallback
        
    final_price_krw = price_before_fees_krw / fee_factor
    
    # Calculate target currency price
    final_price_target = final_price_krw / exchange_rate
    
    # Estimate Profit in KRW
    # Profit = (Final Price in KRW * (1 - Platform Fee)) - Sourcing Cost - Shipping Cost
    revenue_after_fees_krw = final_price_krw * fee_factor
    profit_krw = revenue_after_fees_krw - sourcing_price_krw - shipping_fee_krw
    
    return {
        "sourcing_price_krw": sourcing_price_krw,
        "base_price_krw": round(base_price_krw),
        "shipping_fee_krw": round(shipping_fee_krw),
        "final_price_krw": round(final_price_krw),
        "final_price_target": round(final_price_target, 2),
        "platform_fee_krw": round(final_price_krw - price_before_fees_krw),
        "profit_krw": round(profit_krw),
        "margin_percent": round((profit_krw / final_price_krw) * 100, 1) if final_price_krw > 0 else 0
    }

if __name__ == "__main__":
    # Test calculator
    res = calculate_target_price(
        sourcing_price_krw=10000,
        weight_kg=0.2,
        markup_multiplier=2.0,
        shipping_fee_per_kg_krw=10000,
        platform_fee_percent=10,
        exchange_rate=1350
    )
    print("Pricing Calculation Test:")
    for k, v in res.items():
        print(f"  {k}: {v}")
