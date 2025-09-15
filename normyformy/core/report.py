"""Report Formatting.

This module provides functionality to format the directory structure and file contents
into a comprehensive report.

NOTE: This module is a modified version of Copcon module: copcon/core/report.py
"""
from typing import Dict
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ReportFormatter:
    """Formats the directory structure and file contents into a structured report."""

    def __init__(self, project_name: str, directory_tree: str, file_contents: Dict[Path, str]):
        """
        Initialize the ReportFormatter.

        Args:
            project_name (str): The name of the project.
            directory_tree (str): The directory tree representation.
            file_contents (Dict[str, str]): A mapping of file paths to their contents.
        """

        self.project_name = project_name
        self.directory_tree = directory_tree
        self.file_contents = file_contents

    def format(self) -> str:
        """Format the report as a string.

        Returns:
            str: The formatted report.
        """

        report = [
            "Directory Structure:",
            self.project_name,
            self.directory_tree,
            "\nFile Contents:"
        ]
        for relative_path, content in self.file_contents.items():
            report.extend([
                f"\nFile: {relative_path}",
                "-" * 40,
                content,
                "-" * 40
            ])
        return "\n".join(report)

    def write_to_file(self, report: str, output_file: Path):
        """Write the formatted report to a file.

        Args:
            report (str): The formatted report to write.
            output_file (Path): The path to the output file.

        Raises:
            Exception: If there is an error writing to the file.
        """

        try:
            with output_file.open('w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Output written to {output_file}")
        except Exception as e:
            logger.error(f"Error writing to file {output_file}: {e}")
            raise
