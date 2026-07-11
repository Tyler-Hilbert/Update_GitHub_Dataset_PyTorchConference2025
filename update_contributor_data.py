# This script updates the below values for the PyTorch GitHub Repos Dataset (https://huggingface.co/datasets/TylerHilbert/PyTorchConference2025_GithubRepos)
#   contributors_all
#   contributors_2026_q1
#   contributors_2025
#   contributors_2024
#   contributors_2023
# This script clones and overwrites PyTorchConference2025_GithubRepos.json
# Sorting by most contributors is toggled with `save_updated_dataset`.
# This script does not push the update to HuggingFace.
# The values are updated by cloning each `repo_link` and using a git log command.

import os
import json
import time
import subprocess

def main():
    repos_list = get_repos_list()
    clone_and_pull_repos(repos_list)
    print_repo_stats(repos_list)

# Returns list of repo urls
def get_repos_list():
    clone_repos_list('https://huggingface.co/datasets/TylerHilbert/PyTorchConference2025_GithubRepos')
    pull_repos_list('PyTorchConference2025_GithubRepos')
    repos_list = extract_repos_list()
    return repos_list

# Clones the dataset of GitHub repos (not each repo)
# TODO verify git is installed on machine before running
def clone_repos_list(huggingface_url):
    print ('Cloning Repos list')
    clone_dataset_command = f'git clone {huggingface_url}'
    print (f'${clone_dataset_command}')
    os.system(clone_dataset_command)
    print()

# Executes Git Pull on dataset is updated
def pull_repos_list(local_repo_list_name):
    print ("Pulling repos list (making sure it's updated)")

    root_dir = os.getcwd()
    os.chdir(f'{local_repo_list_name}')
    update_dataset_command = 'git pull'
    print (f'${update_dataset_command}')
    os.system(update_dataset_command)
    os.chdir(root_dir)

    print()

# Returns the list of repo urls
# TODO don't have this hardcoded
def extract_repos_list():
    dataset_path = 'PyTorchConference2025_GithubRepos/PyTorchConference2025_GithubRepos.json'
    with open(dataset_path, 'r', encoding='utf-8') as file:
        repos = json.load(file)
    repos_list = []
    for repo in repos:
        repos_list.append(repo['repo_link'])
    return repos_list

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

# TODO may have a bug for if '|' is in name
def print_repo_stats(repos_list):
    print ('Iterating over repos list')
    root_dir = os.getcwd()
    for repo in repos_list:
        print (f'Processing {repo}')
        contributors_all = set()
        contributors_2026_q1 = set()
        contributors_2025 = set()
        contributors_2024 = set()
        contributors_2023 = set()

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
            contributors_all.add(name)
            if date_str.startswith(('2026-01', '2026-02', '2026-03')): # First quarter of 2026
                contributors_2026_q1.add(name)
            elif '2025' in date_str:
                contributors_2025.add(name)
            elif '2024' in date_str:
                contributors_2024.add(name)
            elif '2023' in date_str:
                contributors_2023.add(name)
        
        print ('contributors_all', len(contributors_all))
        print ('contributors_2026_q1', len(contributors_2026_q1))
        print ('contributors_2025', len(contributors_2025))
        print ('contributors_2024', len(contributors_2024))
        print ('contributors_2023', len(contributors_2023))
        os.chdir(root_dir)

    print()

# Returns unique name based on the url
# TODO fix bug where repo with '__' in name could cause duplicate values
def get_repo_dir(repo_link):
    return repo_link.split('https://github.com/')[1].replace('/', '__')

'''
# Updates the following fields for `repos`:
#   contributors_all
#   contributors_2026_q1
#   contributors_2025
#   contributors_2024
#   contributors_2023
# TODO may have a bug for if '|' is in name
def update_contributors(repos):
    print ('Updating contributors')
    root_dir = os.getcwd()
    for repo in repos:
        print (f'Updating {repo["repo_name"]}')
        contributors_all = set()
        contributors_2026_q1 = set()
        contributors_2025 = set()
        contributors_2024 = set()
        contributors_2023 = set()

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
            contributors_all.add(name)
            if date_str.startswith(('2026-01', '2026-02', '2026-03')): # First quarter of 2026
                contributors_2026_q1.add(name)
            elif '2025' in date_str:
                contributors_2025.add(name)
            elif '2024' in date_str:
                contributors_2024.add(name)
            elif '2023' in date_str:
                contributors_2023.add(name)
        
        repo['contributors_all'] = len(contributors_all)
        repo['contributors_2026_q1'] = len(contributors_2026_q1)
        repo['contributors_2025'] = len(contributors_2025)
        repo['contributors_2024'] = len(contributors_2024)
        repo['contributors_2023'] = len(contributors_2023)
        os.chdir(root_dir)

    print()
    return repos

# Saves the dataset with contributors updated back to the .json file
def save_updated_dataset(repos, sort_by_contributors):
    dataset_path = 'PyTorchConference2025_GithubRepos/PyTorchConference2025_GithubRepos.json'
    print(f'Saving updated dataset to {dataset_path}')

    if sort_by_contributors:
        repos.sort(key=lambda r: r['contributors_all'], reverse=True)

    with open(dataset_path, 'w', encoding='utf-8') as file:
        json.dump(repos, file, indent=2, ensure_ascii=False)
    
    print(f'Successfully saved {len(repos)} entries to {dataset_path}')
    print()
'''
main()