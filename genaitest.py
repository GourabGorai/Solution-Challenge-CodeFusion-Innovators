from newsapi import NewsApiClient

def get_stock_news(company_name):
  """Fetches the latest news related to the given company from News API."""
  newsapi = NewsApiClient(api_key='93888de4c8d749d3ac4fc66b360b3c38')
  all_articles = newsapi.get_everything(q=company_name)
  return all_articles['articles']

# Example usage:
companies = ['Apple', 'Google', 'Microsoft']

for company in companies:
  stock_news = get_stock_news(company)
  print(f"Stock News for {company}:\n")
  for article in stock_news:
    print(f" - {article['title']}")
    print(f"   Source: {article['source']['name']}")
    print(f"   URL: {article['url']}")
    print("-"*20)