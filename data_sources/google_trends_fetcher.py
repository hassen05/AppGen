from pytrends.request import TrendReq

def fetch_trending_searches(region="united_states", limit=5):
    pytrends = TrendReq(hl='en-US', tz=360)
    try:
        df = pytrends.trending_searches(pn=region)
    except Exception as e:
        # Try fallback region if US fails
        if region == "united_states":
            try:
                df = pytrends.trending_searches(pn="united_kingdom")
            except Exception as e2:
                return [{"title": f"[ERROR] Google Trends fetch failed: {e2}"}]
        else:
            return [{"title": f"[ERROR] Google Trends fetch failed: {e}"}]
    trends = []
    for idx, row in df.iterrows():
        if idx >= limit:
            break
        trends.append({"title": row[0]})
    return trends

if __name__ == "__main__":
    for t in fetch_trending_searches():
        print(t["title"])
