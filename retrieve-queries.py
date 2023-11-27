import json
import os
import requests
import html

def fetch_json_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch JSON data. Status code: {response.status_code}")

def extract_prefix_from_query(query_content):
    # Use regular expression to find the first occurrence of 'prefix' (case-insensitive)
    match = re.search(r'(?i)prefix', query_content)
    if match:
        return query_content[match.start():]
    return query_content  # Return the whole content if 'prefix' is not found

def extract_and_save_queries(api_url, github_workspace):
    data = fetch_json_data(api_url)

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
                    formatted_description = '\n'.join(f"#+ description: {line}" for line in description_lines)
                    query_file.write(f"{formatted_description}\n")
                if service_endpoint:
                    query_file.write(f"#+ service: {service_endpoint}\n\n")

                 # Write the SPARQL query content from the first mentioning of 'prefix'
                query_file.write(extract_prefix_from_query(query_content))

if __name__ == "__main__":
    api_url = "https://api.linkeddata.cultureelerfgoed.nl/queries/"
   
   # Use github.workspace as the base for the output folder
    github_workspace = os.getenv("GITHUB_WORKSPACE")
    extract_and_save_queries(api_url, github_workspace)
    