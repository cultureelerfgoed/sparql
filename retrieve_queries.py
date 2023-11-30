import os
import requests
import re


def get_next_urls(start_url):
    next_urls = [start_url]
    current_url = start_url

    while current_url:
        response = requests.head(current_url)
        
        link_header = response.headers.get('Link')
        next_link_match = re.search(r'<([^>]+)>; rel="next"', link_header)

        if next_link_match:
            next_url = next_link_match.group(1)
            next_urls.append(next_url)
            current_url = next_url
        else:
            current_url = None

    return next_urls

def fetch_json_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch JSON data. Status code: {response.status_code}")

def extract_and_save_queries(url, github_workspace):
    data = fetch_json_data(url)

    for payload in data:
        query_content = payload.get('requestConfig', {}).get('payload', {}).get('query', '')
        name = payload.get('name', '')
        description = payload.get('description', '')
        service_endpoint = payload.get('service', '')

        if query_content and name and service_endpoint:
             # Use github_workspace as the base for the output folder
            output_folder = os.path.join(github_workspace, "LDV")
            filename = os.path.join(output_folder, f"{name}.rq")
            with open(filename, 'w') as query_file:
                # Write the name, description, and service endpoint at the top of the file
                if name:
                    query_file.write(f"#+ name: {name}\n")
                if description:
                    # Replace newlines in the description with newline and #+
                    description_lines = description.split('\n')
                    formatted_description = '\n'.join([f"#+ description: {line}" if index == 0 else f"#- {line}" for index, line in enumerate(description_lines)])
                    query_file.write(f"{formatted_description}\n")
                if service_endpoint:
                    query_file.write(f"#+ endpoint: {service_endpoint}\n\n")

                # Write the SPARQL query content
                query_file.write(query_content)

if __name__ == "__main__":
    start_url = 'https://api.linkeddata.cultureelerfgoed.nl/queries/'
        
    # Step 1: Get all "next" URLs
    all_urls = get_next_urls(start_url)

    # Step 2: Iterate over each URL and extract/save queries
    for url in all_urls:
        github_workspace = os.getenv("GITHUB_WORKSPACE")
        extract_and_save_queries(url, github_workspace)
