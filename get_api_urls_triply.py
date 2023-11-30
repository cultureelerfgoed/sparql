import requests
import re

def get_next_urls(start_url):
    next_urls = [start_url]
    current_url = start_url

    while current_url:
        response = requests.head(current_url)
        
        link_header = response.headers.get('link')
        next_link_match = re.search(r'<([^>]+)>; rel="next"', link_header)

        if next_link_match:
            next_url = next_link_match.group(1)
            next_urls.append(next_url)
            current_url = next_url
        else:
            current_url = None

    return next_urls

# Example usage
start_url = 'https://api.linkeddata.cultureelerfgoed.nl/queries/'
result_urls = get_next_urls(start_url)

print("List of URLs:")
for url in result_urls:
    print(url)
