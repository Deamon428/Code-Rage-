"""
GitHub Repository & File Ingestion Utility.
Uses requests and the GitHub REST API to fetch direct raw files or explore repository contents
with strict HTTP 404 and 403 rate-limit error handling, automatic raw URL conversion,
custom User-Agent headers, explicit timeouts, and 100k character limit protection.
"""

import base64
import re
from typing import Any, Dict, List, Optional
import requests

DEFAULT_USER_AGENT = "CodeRage-App"
DEFAULT_TIMEOUT = 10
MAX_FILE_SIZE_CHARS = 100000
FILE_TOO_LARGE_ERROR = "Error: Repository file exceeds the 100,000 character limit for AI analysis. Please ingest a smaller file."


def convert_blob_to_raw_url(url: str) -> str:
    """
    If the provided URL contains github.com and /blob/, automatically convert it
    to a raw.githubusercontent.com URL so only raw text content is downloaded.
    Example:
      https://github.com/owner/repo/blob/branch/path/to/file.py
      -> https://raw.githubusercontent.com/owner/repo/branch/path/to/file.py
    """
    url = url.strip()
    if "github.com" in url and "/blob/" in url:
        raw_url = re.sub(
            r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/blob/(.+)$",
            r"https://raw.githubusercontent.com/\1/\2/\3",
            url,
        )
        return raw_url
    return url


def parse_github_url(url: str) -> Dict[str, Any]:
    """
    Parses a GitHub URL into components: owner, repo, branch, path, and url_type.
    Automatically converts /blob/ links to raw.githubusercontent.com URLs.
    """
    url = url.strip()

    # If it contains github.com and /blob/, convert directly to raw
    if "github.com" in url and "/blob/" in url:
        raw_url = convert_blob_to_raw_url(url)
        raw_match = re.match(
            r"^https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)$",
            raw_url,
        )
        if raw_match:
            owner, repo, branch, path = raw_match.groups()
            return {
                "type": "file",
                "owner": owner,
                "repo": repo,
                "branch": branch,
                "path": path,
                "raw_url": raw_url,
            }

    # Raw URL pattern
    raw_match = re.match(
        r"^https?://raw\.githubusercontent\.com/([^/]+)/([^/]+)/([^/]+)/(.+)$",
        url,
    )
    if raw_match:
        owner, repo, branch, path = raw_match.groups()
        return {
            "type": "raw_file",
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "path": path,
            "raw_url": url,
        }

    # GitHub Tree (subdirectory) pattern
    tree_match = re.match(
        r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/tree/([^/]+)/(.+)$",
        url,
    )
    if tree_match:
        owner, repo, branch, path = tree_match.groups()
        return {
            "type": "tree",
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "path": path,
        }

    # GitHub Repository root pattern
    repo_match = re.match(
        r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/?$",
        url,
    )
    if repo_match:
        owner, repo = repo_match.groups()
        if repo.endswith(".git"):
            repo = repo[:-4]
        return {
            "type": "repo_root",
            "owner": owner,
            "repo": repo,
            "branch": "main",
            "path": "",
        }

    return {"type": "unknown", "raw_url": url}


def detect_language_from_filename(filename: str) -> str:
    """Infers programming language (Python, C++, Java) from file extension."""
    lower = filename.lower()
    if lower.endswith(".py"):
        return "Python"
    if lower.endswith((".cpp", ".cc", ".cxx", ".hpp", ".h", ".c")):
        return "C++"
    if lower.endswith(".java"):
        return "Java"
    return "Python"


def fetch_github_resource(
    url: str,
    github_token: Optional[str] = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Fetches raw file data or repository directory listing from GitHub.
    - Sets User-Agent header: {'User-Agent': 'CodeRage-App'}
    - Automatically converts github.com blob URLs to raw.githubusercontent.com URLs
    - Enforces 100,000 character limit protection against huge files
    - Handles HTTP 404 (Repo/file not found) and HTTP 403 (Rate limit exceeded) strictly
    - Uses an explicit timeout=10 for all requests.

    Returns a dict with:
      - success: bool
      - type: "file" | "repo_contents"
      - content: str (if file)
      - files: list (if repo_contents)
      - language: str
      - error: Optional[str]
    """
    headers = {"User-Agent": DEFAULT_USER_AGENT}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    # Auto-convert github.com/.../blob/... to raw URL before parsing
    converted_url = convert_blob_to_raw_url(url)
    parsed = parse_github_url(converted_url)

    try:
        # Case 1: Direct Raw File or Converted Blob Link
        if parsed["type"] in ("raw_file", "file"):
            raw_url = parsed.get("raw_url", converted_url)
            response = requests.get(raw_url, headers=headers, timeout=10)
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"File not found on GitHub (HTTP 404). Please verify the file path or ensure the repository is public.\nURL: {raw_url}",
                }
            if response.status_code == 403:
                return {
                    "success": False,
                    "error": "GitHub API rate limit exceeded (HTTP 403). Please try again in a few minutes or use a direct raw URL.",
                }
            response.raise_for_status()

            file_content = response.text
            # Context window firewall (100k character limit)
            if len(file_content) > 100000:
                raise ValueError("Repository file exceeds the 100,000 character limit. Context window protected.")

            filename = parsed.get("path", "").split("/")[-1] or "downloaded_file"
            lang = detect_language_from_filename(filename)

            return {
                "success": True,
                "type": "file",
                "filename": filename,
                "content": file_content,
                "language": lang,
                "source_url": url,
            }

        # Case 2: Repository Root or Subdirectory (Fetch Contents API)
        if parsed["type"] in ("repo_root", "tree"):
            owner = parsed["owner"]
            repo = parsed["repo"]
            path = parsed.get("path", "")
            
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code == 404:
                return {
                    "success": False,
                    "error": f"Repository '{owner}/{repo}' or path '{path}' not found (HTTP 404). Check if the repo exists and is public.",
                }
            if response.status_code == 403:
                return {
                    "success": False,
                    "error": "GitHub REST API rate limit exceeded (HTTP 403). Authenticate or try again later.",
                }
            response.raise_for_status()

            data = response.json()

            # If the contents API resolved to a single file
            if isinstance(data, dict) and data.get("type") == "file":
                content = ""
                if data.get("content"):
                    content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
                elif data.get("download_url"):
                    r_raw = requests.get(data["download_url"], headers=headers, timeout=10)
                    r_raw.raise_for_status()
                    content = r_raw.text

                # Context window firewall (100k character limit)
                if len(content) > 100000:
                    raise ValueError("Repository file exceeds the 100,000 character limit. Context window protected.")

                lang = detect_language_from_filename(data.get("name", ""))
                return {
                    "success": True,
                    "type": "file",
                    "filename": data.get("name", "file"),
                    "content": content,
                    "language": lang,
                    "source_url": data.get("html_url", url),
                }

            # If it's a directory listing of files
            if isinstance(data, list):
                file_items = []
                for item in data:
                    item_type = item.get("type", "file")
                    item_name = item.get("name", "")
                    is_code = item_name.lower().endswith(
                        (".py", ".cpp", ".cc", ".cxx", ".hpp", ".h", ".c", ".java")
                    )
                    file_items.append({
                        "name": item_name,
                        "path": item.get("path", item_name),
                        "type": item_type,
                        "download_url": item.get("download_url"),
                        "html_url": item.get("html_url"),
                        "is_code": is_code,
                    })

                return {
                    "success": True,
                    "type": "repo_contents",
                    "owner": owner,
                    "repo": repo,
                    "path": path,
                    "files": file_items,
                    "source_url": url,
                }

        # Case 3: Fallback attempt to fetch URL directly with User-Agent & timeout=10
        response = requests.get(converted_url, headers=headers, timeout=10)
        if response.status_code == 404:
            return {"success": False, "error": f"Resource not found (HTTP 404) at: {url}"}
        if response.status_code == 403:
            return {"success": False, "error": "GitHub API rate limit exceeded (HTTP 403)."}
        response.raise_for_status()

        fallback_content = response.text
        if len(fallback_content) > 100000:
            raise ValueError("Repository file exceeds the 100,000 character limit. Context window protected.")

        return {
            "success": True,
            "type": "file",
            "filename": "code_snippet",
            "content": fallback_content,
            "language": "Python",
            "source_url": url,
        }

    except ValueError as ve:
        return {"success": False, "error": f"Error: {str(ve)}"}
    except requests.exceptions.HTTPError as he:
        status_code = getattr(he.response, "status_code", None)
        if status_code == 404:
            return {"success": False, "error": f"Repository or file not found (HTTP 404).\nURL: {url}"}
        elif status_code == 403:
            return {"success": False, "error": "GitHub API rate limit exceeded (HTTP 403)."}
        return {"success": False, "error": f"HTTP Error fetching from GitHub: {str(he)}"}
    except requests.exceptions.ConnectionError:
        return {"success": False, "error": "Network connection error: Unable to reach GitHub servers."}
    except requests.exceptions.Timeout:
        return {"success": False, "error": "Request timed out (10s) while trying to fetch from GitHub."}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error during GitHub ingestion: {str(e)}"}
