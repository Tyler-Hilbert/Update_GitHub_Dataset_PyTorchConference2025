# Updates the below fields for the dataset https://huggingface.co/datasets/TylerHilbert/PyTorchConference2025_GithubRepos
#   contributors_all
#   contributors_2025
#   contributors_2024
#   contributors_2023
# This script performs and clone and then overwrites the file PyTorchConference2025_GithubRepos.json
# The script does not push the update to HuggingFace.
# The values are updated by cloning each `repo_link` and using a git log command.
# The script does not change the order the repos are listed in the dataset.

import os
import json
import time
import subprocess

def main():
    clone_dataset()
    update_dataset()
    repos = clone_and_pull_repos()
    repos_updated = update_contributors(repos)
    save_updated_dataset(repos_updated)

# Clones the original dataset
# TODO verify git is installed on machine before running
def clone_dataset():
    print ('Cloning original dataset')
    clone_dataset_command = 'git clone https://huggingface.co/datasets/TylerHilbert/PyTorchConference2025_GithubRepos'
    print (f'${clone_dataset_command}')
    os.system(clone_dataset_command)
    print()

# Updates the original dataset
def update_dataset():
    print ('Updating original dataset')

    root_dir = os.getcwd()
    os.chdir('PyTorchConference2025_GithubRepos')
    update_dataset_command = 'git pull'
    print (f'${update_dataset_command}')
    os.system(update_dataset_command)
    os.chdir(root_dir)

    print()

# Does a git clone and git pull for each `repo_link` in dataset .json file
def clone_and_pull_repos():
    print ('Cloning repos')
    dataset_path = 'PyTorchConference2025_GithubRepos/PyTorchConference2025_GithubRepos.json'
    with open(dataset_path, 'r', encoding='utf-8') as file:
        repos = json.load(file)
    
    for repo in repos:
        # Verify repo_link is a github url
        if 'github.com' not in repo['repo_link'].lower():
            print (f'error: repo["repo_link"] invalid github link')
            exit()
        
        # Clone repo
        custom_dir_name = get_repo_dir(repo)
        clone_command = f'git clone {repo["repo_link"]} {custom_dir_name}'
        print (clone_command)
        os.system(clone_command)
        time.sleep(2)

        # Pull repo
        root_dir = os.getcwd()
        os.chdir(custom_dir_name)
        update_dataset_command = 'git pull'
        print (f'${update_dataset_command}')
        os.system(update_dataset_command)
        os.chdir(root_dir)
        time.sleep(2)
        print ()
    
    print()
    return repos

# Returns unique name based on the repo_url
# TODO fix bug where repo with '__' in name could cause duplicate values
def get_repo_dir(repo):
    return repo['repo_link'].split('https://github.com/')[1].replace('/', '__')

# Updates the following fields for `repos`:
#   contributors_all
#   contributors_2025
#   contributors_2024
#   contributors_2023
# TODO may have a bug for if '|' is in name
def update_contributors(repos):
    print ('Updating contributors')
    root_dir = os.getcwd()
    for repo in repos:
        print (f'Updating {repo['repo_name']}')
        contributors_all = set()
        contributors_2025 = set()
        contributors_2024 = set()
        contributors_2023 = set()

        os.chdir(get_repo_dir(repo))
        result = subprocess.run(
            ["git", "log", "--pretty=format:%ad|%an", "--date=format:%Y"], # Uses name as unique field
            #["git", "log", "--pretty=format:%ad|%ae", "--date=format:%Y"], # Uses email as unique field
            capture_output=True,
            encoding='utf-8',
            errors='replace'
        )
        for line in result.stdout.strip().split('\n'):
            year, name = line.split('|', 1)
            name = name.lower()
            contributors_all.add(name)
            if '2025' in year:
                contributors_2025.add(name)
            elif '2024' in year:
                contributors_2024.add(name)
            elif '2023' in year:
                contributors_2023.add(name)
        
        repo['contributors_all'] = len(contributors_all)
        repo['contributors_2025'] = len(contributors_2025)
        repo['contributors_2024'] = len(contributors_2024)
        repo['contributors_2023'] = len(contributors_2023)
        os.chdir(root_dir)

    print()
    return repos

# Saves the dataset with contributors updated back to the .json file
def save_updated_dataset(repos):
    dataset_path = 'PyTorchConference2025_GithubRepos/PyTorchConference2025_GithubRepos.json'
    print(f'Saving updated dataset to {dataset_path}')
    
    with open(dataset_path, 'w', encoding='utf-8') as file:
        json.dump(repos, file, indent=2, ensure_ascii=False)
    
    print(f'Successfully saved {len(repos)} entries to {dataset_path}')
    print()

main()