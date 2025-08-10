#!/usr/bin/env python3
"""
Update README.md with live CI status information.
This script is used by the GitHub Actions workflow to dynamically update the README.
"""

import datetime
import os
import re
import sys


def main():
    """Main function to update README with CI status."""
    try:
        # Read current README
        readme_path = "README.md"
        if not os.path.exists(readme_path):
            print(f"Error: {readme_path} not found")
            sys.exit(1)

        with open(readme_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Get values from environment
        status = os.environ.get("WORKFLOW_STATUS", "unknown")
        run_id = os.environ.get("WORKFLOW_RUN_ID", "")
        created_at = os.environ.get("WORKFLOW_CREATED_AT", "")
        jobs = os.environ.get("WORKFLOW_JOBS", "")
        version = os.environ.get("PACKAGE_VERSION", "unknown")

        print(f"Status: {status}, Run ID: {run_id}, Version: {version}")

        # Format timestamp
        if created_at and created_at != "null" and created_at.strip():
            try:
                dt = datetime.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                formatted_time = dt.strftime("%Y-%m-%d %H:%M UTC")
            except Exception as e:
                print(f"Warning: Could not parse timestamp '{created_at}': {e}")
                formatted_time = "unknown"
        else:
            formatted_time = "unknown"

        # Create status emoji
        status_emoji_map = {
            "success": "✅",
            "failure": "❌",
            "cancelled": "⏹️",
            "in_progress": "🔄",
            "queued": "⏳",
            "neutral": "⚪",
            "skipped": "⏭️",
        }
        status_emoji = status_emoji_map.get(status, "❓")

        # Create dynamic status section
        status_lines = [
            "",
            "## 📊 Live CI Status",
            "",
            f"**Last Build:** {status_emoji} {status.title()} | **Time:** {formatted_time} | **Version:** `{version}`",
            "",
            "| Job | Status |",
            "|-----|--------|",
        ]

        # Add job statuses
        if jobs and jobs.strip():
            job_emoji_map = {
                "success": "✅",
                "failure": "❌",
                "cancelled": "⏹️",
                "in_progress": "🔄",
                "queued": "⏳",
                "neutral": "⚪",
                "skipped": "⏭️",
            }
            print(f"Processing {len(jobs.strip().split(chr(10)))} jobs")
            for job_line in jobs.strip().split("\n"):
                if ":" in job_line:
                    job_name, job_status = job_line.split(":", 1)
                    job_emoji = job_emoji_map.get(job_status.strip(), "❓")
                    status_lines.append(
                        f"| {job_name.strip()} | {job_emoji} {job_status.strip().title()} |"
                    )

        repo_url = f"https://github.com/{os.environ.get('GITHUB_REPOSITORY', '')}"
        if run_id and run_id != "null" and run_id.strip():
            status_lines.extend(
                [
                    "",
                    f"**Build Artifacts:** [Download]({repo_url}/actions/runs/{run_id})",
                ]
            )

        status_lines.extend(["", "---", ""])
        status_section = "\n".join(status_lines)

        # Find and replace the status section or insert it
        pattern = r"## 📊 Live CI Status.*?---\n"
        if re.search(pattern, content, re.DOTALL):
            print("Found existing status section, replacing...")
            content = re.sub(pattern, status_section, content, flags=re.DOTALL)
        else:
            print("No existing status section found, inserting new one...")
            # Insert after the Discord badge line
            discord_line = "dcbadge.limes.pink/api/shield/429866199833247744"
            if discord_line in content:
                insert_point = content.find(discord_line)
                insert_point = content.find("\n", insert_point) + 1
                content = (
                    content[:insert_point] + status_section + content[insert_point:]
                )
                print("Inserted after Discord badge")
            else:
                # Insert after the last badge section (🏗️ Build Artifacts)
                build_artifacts = "## 🏗️ Build Artifacts"
                if build_artifacts in content:
                    # Find the end of the build artifacts section
                    start = content.find(build_artifacts)
                    if start != -1:
                        # Find the next double newline (end of section)
                        end = content.find("\n\n", start)
                        if end != -1:
                            # Find the next single newline after that
                            insert_point = content.find("\n", end + 2)
                            if insert_point != -1:
                                content = (
                                    content[:insert_point]
                                    + "\n"
                                    + status_section
                                    + content[insert_point:]
                                )
                                print("Inserted after Build Artifacts section")
                            else:
                                # Insert at the end of the build artifacts section
                                content = content[:end] + status_section + content[end:]
                                print("Inserted at end of Build Artifacts section")
                        else:
                            # No double newline found, insert after the build artifacts header
                            header_end = content.find("\n", start)
                            if header_end != -1:
                                content = (
                                    content[: header_end + 1]
                                    + status_section
                                    + content[header_end + 1 :]
                                )
                                print("Inserted after Build Artifacts header")
                else:
                    print("Warning: Could not find suitable insertion point")

        # Write updated README
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(content)

        print("README.md updated successfully!")

    except Exception as e:
        print(f"Error updating README: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
