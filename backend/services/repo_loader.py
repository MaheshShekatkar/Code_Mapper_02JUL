import os
import glob
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor

SUPPORTED_EXTENSIONS = (".py", ".java", ".yaml", ".yml", ".json",".cs",".go","proto")

CACHE_ROOT = "./repos/cache"

def is_git_url(path):
    return path.startswith("http://") or path.startswith("https://") or path.startswith("git@")

def clone_repo(name, url):
    if shutil.which("git") is None:
        raise RuntimeError("Git is not installed or not found in PATH")
    repo_path = os.path.join(CACHE_ROOT, name)
    if os.path.exists(repo_path):
        print(f"[INFO] Repo already exists: {repo_path} (skipping clone)")
        return repo_path

    print(f"[INFO] Cloning {url} → {repo_path}")
    os.makedirs(CACHE_ROOT, exist_ok=True)
    try:
        subprocess.run(["git", "clone", "--depth", "1", url, repo_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Failed to clone {url}: {e}")
        return None
    return repo_path

def read_code_files(repo_path: str) -> dict:
    """
    Recursively reads all .py, .java, .ts, etc. files from the repo and returns a dict:
    { filename: file_content }
    """
    file_map = {}
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_map[rel_path] = content
                except Exception as e:
                    print(f"[WARN] Could not read {file_path}: {e}")
    return file_map


def load_repositories(repo_config):
    result = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(read_code_files, repo) for repo in repo_config]
        for future in futures:
            name, files = future.result()
           # print(f"name:{name},files:{files}")
            result[name] = files
           # print("files",len(files))
    return result
