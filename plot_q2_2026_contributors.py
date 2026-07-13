import os
import time
import subprocess
from datasets import load_dataset
import csv
import matplotlib.pyplot as plt

def main():
    print ("FIXME: YOU MUST DELETE ALL REPOS IN THIS DIR BEFORE RUNNING THE SCRIPT.")
    print ()

    repo_links = load_repo_links()
    clone_and_pull_repos(repo_links)
    q2_2026_num_contributors = get_q2_2026_contributors(repo_links)
    plot_top_contributors(q2_2026_num_contributors)

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

# TODO may have a bug for if '|' is in name
def get_q2_2026_contributors(repos_list):
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
    return q2_2026_num_contributors

# Returns unique name based on the url
# TODO fix bug where repo with '__' in name could cause duplicate values
def get_repo_dir(repo_link):
    return repo_link.split('https://github.com/')[1].replace('/', '__')

# Generates a plot of the repos with the most contributors
def plot_top_contributors(data_dict, top_n=5):
    print(f"Generating LinkedIn-optimized chart for the top {top_n} repositories...")
    
    # Sort the dictionary by contributor count in descending order, grab top 5
    sorted_data = sorted(data_dict.items(), key=lambda item: item[1], reverse=True)[:top_n]
    
    if not sorted_data:
        print("Error: No data to plot!")
        return

    # Extract just the repo name (e.g., "hermes-agent") from the full URL
    # We reverse ([::-1]) the lists so the #1 repo appears at the TOP of the horizontal chart
    repos = [item[0].rstrip('/').split('/')[-1] for item in sorted_data][::-1]
    counts = [item[1] for item in sorted_data][::-1]

    # Set up the figure size for a 5:4 aspect ratio (10 wide, 8 high)
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create the horizontal bar chart
    bars = ax.barh(repos, counts, color='steelblue', edgecolor='black')
    
    # Add labels and title
    ax.set_xlabel('# of GitHub Contributors', fontsize=14, fontweight='bold')
    ax.set_ylabel('') # Explicitly leaving Y-axis label blank
    ax.set_title('# of Contributors During Q2 2026 (Open-Source AI Repos)', fontsize=18, fontweight='bold', pad=20)
    
    # Print the exact number of contributors on the end of each bar
    ax.bar_label(bars, padding=8, fontsize=14, fontweight='bold', color='black')
    
    # Clean up the axes a bit for a modern look
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.tick_params(axis='y', labelsize=14)
    ax.tick_params(axis='x', labelsize=12)
    
    # Automatically adjust padding
    plt.tight_layout() 
    
    # Save the figure with a high DPI so it looks crisp on LinkedIn mobile
    filename = 'linkedin_q2_2026_contributors.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    print(f"Success! Graph saved as '{filename}'")
    
    # Display the graph in a popup window (optional)
    plt.show()

main()