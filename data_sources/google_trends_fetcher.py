from pytrends.request import TrendReq

def fetch_trending_searches(region="united_states", limit=5):
    pytrends = TrendReq(hl='en-US', tz=360)
    df = pytrends.trending_searches(pn=region)
    trends = []
    for idx, row in df.iterrows():
        if idx >= limit:
            break
        trends.append({
            "title": row[0]
        })
    return trends

if __name__ == "__main__":
    for t in fetch_trending_searches():
        print(t["title"])
