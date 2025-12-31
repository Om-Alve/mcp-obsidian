import json
import logging
import os
from dotenv import load_dotenv
from fastmcp import FastMCP

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-obsidian")

mcp = FastMCP("mcp-obsidian")

api_key = os.getenv("OBSIDIAN_API_KEY")
obsidian_host = os.getenv("OBSIDIAN_HOST", "127.0.0.1")

if not api_key:
    raise ValueError(
        f"OBSIDIAN_API_KEY environment variable required. Working directory: {os.getcwd()}"
    )

from . import obsidian


@mcp.tool()
def obsidian_list_files_in_vault() -> str:
    """Lists all files and directories in the root directory of your Obsidian vault."""
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    files = api.list_files_in_vault()
    return json.dumps(files, indent=2)


@mcp.tool()
def obsidian_list_files_in_dir(dirpath: str) -> str:
    """Lists all files and directories that exist in a specific Obsidian directory.

    Args:
        dirpath: Path to list files from (relative to your vault root). Note that empty directories will not be returned.
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    files = api.list_files_in_dir(dirpath)
    return json.dumps(files, indent=2)


@mcp.tool()
def obsidian_get_file_contents(filepath: str) -> str:
    """Return the content of a single file in your vault.

    Args:
        filepath: Path to the relevant file (relative to your vault root).
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    content = api.get_file_contents(filepath)
    return json.dumps(content, indent=2)


@mcp.tool()
def obsidian_simple_search(query: str, context_length: int = 100) -> str:
    """Simple search for documents matching a specified text query across all files in the vault.

    Args:
        query: Text to search for in the vault.
        context_length: How much context to return around the matching string (default: 100)
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.search(query, context_length)

    formatted_results = []
    for result in results:
        formatted_matches = []
        for match in result.get("matches", []):
            context = match.get("context", "")
            match_pos = match.get("match", {})
            start = match_pos.get("start", 0)
            end = match_pos.get("end", 0)

            formatted_matches.append(
                {"context": context, "match_position": {"start": start, "end": end}}
            )

        formatted_results.append(
            {
                "filename": result.get("filename", ""),
                "score": result.get("score", 0),
                "matches": formatted_matches,
            }
        )

    return json.dumps(formatted_results, indent=2)


@mcp.tool()
def obsidian_append_content(filepath: str, content: str) -> str:
    """Append content to a new or existing file in the vault.

    Args:
        filepath: Path to the file (relative to vault root)
        content: Content to append to the file
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    api.append_content(filepath, content)
    return f"Successfully appended content to {filepath}"


@mcp.tool()
def obsidian_patch_content(
    filepath: str, operation: str, target_type: str, target: str, content: str
) -> str:
    """Insert content into an existing note relative to a heading, block reference, or frontmatter field.

    Args:
        filepath: Path to the file (relative to vault root)
        operation: Operation to perform (append, prepend, or replace)
        target_type: Type of target to patch (heading, block, or frontmatter)
        target: Target identifier (heading path, block reference, or frontmatter field)
        content: Content to insert
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    api.patch_content(filepath, operation, target_type, target, content)
    return f"Successfully patched content in {filepath}"


@mcp.tool()
def obsidian_put_content(filepath: str, content: str) -> str:
    """Create a new file in your vault or update the content of an existing one.

    Args:
        filepath: Path to the relevant file (relative to your vault root)
        content: Content of the file you would like to upload
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    api.put_content(filepath, content)
    return f"Successfully uploaded content to {filepath}"


@mcp.tool()
def obsidian_delete_file(filepath: str, confirm: bool = False) -> str:
    """Delete a file or directory from the vault.

    Args:
        filepath: Path to the file or directory to delete (relative to vault root)
        confirm: Confirmation to delete the file (must be true)
    """
    if not confirm:
        raise RuntimeError("confirm must be set to true to delete a file")

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    api.delete_file(filepath)
    return f"Successfully deleted {filepath}"


@mcp.tool()
def obsidian_complex_search(query: dict) -> str:
    """Complex search for documents using a JsonLogic query.

    Supports standard JsonLogic operators plus 'glob' and 'regexp' for pattern matching.
    Results must be non-falsy. Use this tool when you want to do a complex search,
    e.g. for all documents with certain tags etc. ALWAYS follow query syntax in examples.

    Examples:
    1. Match all markdown files:
       {"glob": ["*.md", {"var": "path"}]}

    2. Match all markdown files with 1221 substring inside them:
       {"and": [{"glob": ["*.md", {"var": "path"}]}, {"regexp": [".*1221.*", {"var": "content"}]}]}

    3. Match all markdown files in Work folder containing name Keaton:
       {"and": [{"glob": ["*.md", {"var": "path"}]}, {"regexp": [".*Work.*", {"var": "path"}]}, {"regexp": ["Keaton", {"var": "content"}]}]}

    Args:
        query: JsonLogic query object following the syntax in examples
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.search_json(query)
    return json.dumps(results, indent=2)


@mcp.tool()
def obsidian_batch_get_file_contents(filepaths: list[str]) -> str:
    """Return the contents of multiple files in your vault, concatenated with headers.

    Args:
        filepaths: List of file paths to read (relative to your vault root)
    """
    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    content = api.get_batch_file_contents(filepaths)
    return content


@mcp.tool()
def obsidian_get_periodic_note(period: str, type: str = "content") -> str:
    """Get current periodic note for the specified period.

    Args:
        period: The period type (daily, weekly, monthly, quarterly, yearly)
        type: The type of data to get ('content' or 'metadata'). 'content' returns just the content
              in Markdown format. 'metadata' includes note metadata (including paths, tags, etc.) and the content.
    """
    valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
    if period not in valid_periods:
        raise RuntimeError(
            f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}"
        )

    valid_types = ["content", "metadata"]
    if type not in valid_types:
        raise RuntimeError(
            f"Invalid type: {type}. Must be one of: {', '.join(valid_types)}"
        )

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    content = api.get_periodic_note(period, type)
    return content


@mcp.tool()
def obsidian_get_recent_periodic_notes(
    period: str, limit: int = 5, include_content: bool = False
) -> str:
    """Get most recent periodic notes for the specified period type.

    Args:
        period: The period type (daily, weekly, monthly, quarterly, yearly)
        limit: Maximum number of notes to return (default: 5, max: 50)
        include_content: Whether to include note content (default: false)
    """
    valid_periods = ["daily", "weekly", "monthly", "quarterly", "yearly"]
    if period not in valid_periods:
        raise RuntimeError(
            f"Invalid period: {period}. Must be one of: {', '.join(valid_periods)}"
        )

    if not isinstance(limit, int) or limit < 1:
        raise RuntimeError(f"Invalid limit: {limit}. Must be a positive integer")

    if not isinstance(include_content, bool):
        raise RuntimeError(
            f"Invalid include_content: {include_content}. Must be a boolean"
        )

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.get_recent_periodic_notes(period, limit, include_content)
    return json.dumps(results, indent=2)


@mcp.tool()
def obsidian_get_recent_changes(limit: int = 10, days: int = 90) -> str:
    """Get recently modified files in the vault.

    Args:
        limit: Maximum number of files to return (default: 10, max: 100)
        days: Only include files modified within this many days (default: 90)
    """
    if not isinstance(limit, int) or limit < 1:
        raise RuntimeError(f"Invalid limit: {limit}. Must be a positive integer")

    if not isinstance(days, int) or days < 1:
        raise RuntimeError(f"Invalid days: {days}. Must be a positive integer")

    api = obsidian.Obsidian(api_key=api_key, host=obsidian_host)
    results = api.get_recent_changes(limit, days)
    return json.dumps(results, indent=2)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9000)
