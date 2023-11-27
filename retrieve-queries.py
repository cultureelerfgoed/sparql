import json
import os
import requests

def fetch_json_data(api_url):
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch JSON data. Status code: {response.status_code}")

def extract_and_save_queries(api_url, output_folder):
    data = fetch_json_data(api_url)

    for payload in data:
        query_content = payload.get('requestConfig', {}).get('payload', {}).get('query', '')
        name = payload.get('name', '')
        description = payload.get('description', '')
        service_endpoint = payload.get('service', '')

        if query_content and name and service_endpoint:
            filename = os.path.join(output_folder, f"{name}.rq")
            with open(filename, 'w') as query_file:
                # Write the name, description, and service endpoint at the top of the file
                if name:
                    query_file.write(f"#+ name: {name}\n")
                if description:
                    # Replace newlines in the description with newline and #+
                    description_lines = description.split('\n')
                    formatted_description = '\n'.join(f"#+ {line}" for line in description_lines)
                    query_file.write(f"{formatted_description}\n")
                if service_endpoint:
                    query_file.write(f"#+ service: {service_endpoint}\n\n")

                # Write the SPARQL query content
                query_file.write(query_content)

if __name__ == "__main__":
    api_url = "https://api.linkeddata.cultureelerfgoed.nl/queries/"
    output_folder_path = "C:\\Users\\Ruben\\Desktop\\rce_queries2"
    extract_and_save_queries(api_url, output_folder_path)
