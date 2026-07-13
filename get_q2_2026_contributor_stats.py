# Exports a .csv of the number of unique contributors in q2 of 2026 for each repo_link in https://huggingface.co/datasets/TylerHilbert/PyTorchConference2025_GithubRepos and https://huggingface.co/datasets/TylerHilbert/AI_Repos_Top100

import os
import time
import subprocess
from datasets import load_dataset
import csv

def main():
    print ("FIXME: YOU MUST DELETE ALL REPOS IN THIS DIR BEFORE RUNNING THE SCRIPT.")
    print ()

    repo_links = load_repo_links()
    clone_and_pull_repos(repo_links)
    export_q2_2026_contributors(repo_links)

# Load list of repo links
def load_repo_links():
    print ('Loading list of repo urls')
    repo_links = [] # A list of all the repo urls
    repo_links.extend(get_repo_links_from_hf(
        'TylerHilbert/PyTorchConference2025_GithubRepos', 'repo_link'
    ))
    repo_links.extend(get_repo_links_from_hf(
        'TylerHilbert/AI_Repos_Top100', 'repo_link'
    ))
    # Remove duplicate urls
    repo_links = list(dict.fromkeys(repo_links))
    print (f'List of repo links found: {repo_links}')
    print ()
    return repo_links

# Returns a list from `hf_name` of the field `field_name`
def get_repo_links_from_hf(hf_name, field_name):
    print (f'Loading {hf_name} field {field_name}')
    ds = load_dataset(hf_name)
    repo_links = []
    for row in ds['train']:
        repo_links.append(row[field_name])
    return repo_links

# Runs `git clone` and `git pull` for each of the urls in `repos_list`
def clone_and_pull_repos(repos_list):
    print ('Cloning repos')
    
    for repo in repos_list:
        # Verify repo_link is a github url
        if 'github.com' not in repo.lower():
            print (f'error: repo invalid github link')
            exit()
        
        # Clone repo
        custom_dir_name = get_repo_dir(repo)
        clone_command = f'git clone {repo} {custom_dir_name}'
        print (clone_command)
        os.system(clone_command)
        time.sleep(2)

        ####
        # FIXME bug with pulling repo
        # Pull repo
        #root_dir = os.getcwd()
        #os.chdir(custom_dir_name)
        #update_dataset_command = 'git pull'
        #print (f'${update_dataset_command}')
        #os.system(update_dataset_command)
        #os.chdir(root_dir)
        #time.sleep(2)
        #print ()
    
    print()

# Exports how many contributors there were in q2 of 2026 to a csv
# TODO may have a bug for if '|' is in name
def export_q2_2026_contributors(repos_list):
    print ('Iterating over repos list')
    q2_2026_num_contributors = {}
    root_dir = os.getcwd()
    for repo in repos_list:
        # Count the number of q2 contributors for each repo
        print (f'Processing {repo}')
        contributors_2026_q2 = set()

        os.chdir(get_repo_dir(repo))
        result = subprocess.run(
            ["git", "log", "--pretty=format:%ad|%an", "--date=format:%Y-%m-%d"], # Uses name as unique field
            #["git", "log", "--pretty=format:%ad|%ae", "--date=format:%Y-%m-%d"], # Uses email as unique field
            capture_output=True,
            encoding='utf-8',
            errors='replace'
        )
        for line in result.stdout.strip().split('\n'):
            date_str, name = line.split('|', 1) # TODO this may cause a crash if there are no commits
            name = name.lower()
            if date_str.startswith(('2026-04', '2026-05', '2026-06')): # Second quarter of 2026
                contributors_2026_q2.add(name)
        
        q2_2026_num_contributors[repo] = len(contributors_2026_q2)
        os.chdir(root_dir)
    print()

    # Export contributor counts for each repo to .csv
    q2_2026_filename = "q2_2026_contributors.csv"
    print(f"Exporting q2 2026 contributor counts to {q2_2026_filename}")
    with open(q2_2026_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["repo_link", "num_q2_2026_contributors"])
        for repo, count in q2_2026_num_contributors.items():
            writer.writerow([repo, count]) 
    print()

# Returns unique name based on the url
# TODO fix bug where repo with '__' in name could cause duplicate values
def get_repo_dir(repo_link):
    return repo_link.split('https://github.com/')[1].replace('/', '__')

main()