import requests
import os
import glob

def create_or_update_gist(token, files, gist_id=None, description="Lichess Bots Rankings"):
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {
        "description": description,
        "public": False,  # Set to True for public Gist, False for secret
        "files": {}
    }
    
    # Add all CSV files and output.log
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        file_name = os.path.basename(file_path)
        payload["files"][file_name] = {"content": content}
    
    if gist_id:
        # Update existing Gist
        url = f"https://api.github.com/gists/{gist_id}"
        response = requests.patch(url, headers=headers, json=payload)
    else:
        # Create new Gist
        url = "https://api.github.com/gists"
        response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code in [200, 201]:
        gist_data = response.json()
        print(f"Gist URL: {gist_data['html_url']}")
        # Save gist_id for future updates
        with open("gist_id.txt", "w") as f:
            f.write(gist_data["id"])
    else:
        print(f"Failed to create/update Gist: {response.status_code} {response.text}")
        exit(1)

if __name__ == "__main__":
    token = os.getenv("GIST_TOKEN")
    if not token:
        print("Error: GIST_TOKEN environment variable not set")
        exit(1)
    
    # Collect all CSV files and output.log
    files = glob.glob("lichess_bots_ranking_*.csv") + ["output.log"]
    
    # Check if gist_id.txt exists to update an existing Gist
    gist_id = None
    if os.path.exists("gist_id.txt"):
        with open("gist_id.txt", "r") as f:
            gist_id = f.read().strip()
    
    create_or_update_gist(token, files, gist_id)
