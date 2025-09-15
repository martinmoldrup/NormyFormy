"""Utilities for compressing a Python module while preserving high‑level structure."""

from __future__ import annotations

import ast
from dataclasses import dataclass, field
import pathlib
from typing import Iterable, List, Sequence, Union
import grimp

_FunctionNode = Union[ast.FunctionDef, ast.AsyncFunctionDef]
_NodeWithBody = Union[ast.Module, ast.ClassDef, _FunctionNode]


def _remove_module_docstring(tree: ast.Module) -> None:
    """Remove the module docstring if present."""
    if not tree.body:
        return
    first_stmt = tree.body[0]
    if (
        isinstance(first_stmt, ast.Expr)
        and isinstance(getattr(first_stmt, "value", None), ast.Constant)
        and isinstance(first_stmt.value.value, str)
    ):
        tree.body = tree.body[1:]


def _filter_imports(tree: ast.Module) -> None:
    """Remove all import statements from the module body."""
    tree.body = [
        node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))
    ]


def _has_docstring(node: _NodeWithBody) -> bool:
    """Return True if the first statement in node.body is a docstring expression."""
    if not getattr(node, "body", None):
        return False
    first_stmt = node.body[0]
    return (
        isinstance(first_stmt, ast.Expr)
        and isinstance(getattr(first_stmt, "value", None), ast.Constant)
        and isinstance(first_stmt.value.value, str)
    )


def _append_placeholder(
    new_body: List[ast.stmt],
    original_body: Sequence[ast.stmt],
    include_line_count: bool,
) -> None:
    """Append placeholder node with optional line count info."""
    if include_line_count:
        original_lines: int = _count_total_lines(original_body)
        msg: str = f"<Content purposely removed: {original_lines} lines>"
    else:
        msg = "<Content purposely removed>"
    new_body.append(ast.Expr(value=ast.Constant(value=msg, kind=None)))


def _count_total_lines(stmts: Iterable[ast.stmt]) -> int:
    """Compute total line span of given statements."""
    total: int = 0
    for stmt in stmts:
        start: int = getattr(stmt, "lineno", 1)
        end: int = getattr(stmt, "end_lineno", start)
        total += end - start + 1
    return total


def _compress_function(
    node: _FunctionNode,
    keep_docstrings: bool,
    include_line_count: bool,
) -> None:
    """Replace function body with optional docstring and placeholder."""
    original_body: Sequence[ast.stmt] = node.body
    new_body: List[ast.stmt] = []
    if keep_docstrings and _has_docstring(node):
        new_body.append(original_body[0])
    _append_placeholder(new_body, original_body, include_line_count)
    node.body = new_body


def _compress_class(
    node: ast.ClassDef,
    keep_docstrings: bool,
    keep_class_attributes: bool,
    include_line_count: bool,
) -> None:
    """Replace class body with optional docstring, selected attributes, and placeholder."""
    original_body: Sequence[ast.stmt] = node.body
    new_body: List[ast.stmt] = []
    start_idx: int = 0
    if keep_docstrings and _has_docstring(node):
        new_body.append(original_body[0])
        start_idx = 1
    if keep_class_attributes:
        for stmt in original_body[start_idx:]:
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
                new_body.append(stmt)
    _append_placeholder(new_body, original_body, include_line_count)
    node.body = new_body


def _walk_and_compress(
    tree: ast.AST,
    keep_docstrings: bool,
    keep_class_attributes: bool,
    include_line_count: bool,
) -> None:
    """Walk the AST compressing class and function nodes."""
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            _compress_function(node, keep_docstrings, include_line_count)
        elif isinstance(node, ast.ClassDef):
            _compress_class(
                node,
                keep_docstrings=keep_docstrings,
                keep_class_attributes=keep_class_attributes,
                include_line_count=include_line_count,
            )


def compress_python_module(
    python_module: str,
    keep_docstrings: bool,
    keep_imports: bool,
    include_line_count: bool,
    keep_class_attributes: bool = True,
) -> str:
    """Compress a Python module preserving signatures, optional docstrings/imports/attributes."""
    tree: ast.Module = ast.parse(python_module)

    if not keep_imports:
        _filter_imports(tree)

    if not keep_docstrings:
        _remove_module_docstring(tree)

    _walk_and_compress(
        tree,
        keep_docstrings=keep_docstrings,
        keep_class_attributes=keep_class_attributes,
        include_line_count=include_line_count,
    )

    unparsed: str = ast.unparse(tree)
    print(unparsed)
    return unparsed


def path_to_module_str(path: pathlib.Path) -> str:
    """Convert a file path to a Python module import string, skipping __init__.py."""
    parts = path.with_suffix("").parts
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


@dataclass
class FileLoaded:
    name: str
    """The module string for the file."""

    path: pathlib.Path
    content: str

    @property
    def depth(self) -> int:
        """Return the depth of the file in the directory structure."""
        return len(self.path.parts)

    @property
    def content_length(self) -> int:
        """Return the length of the file content."""
        return len(self.content)

    @property
    def line_count(self) -> int:
        """Return the number of lines in the file content."""
        return self.content.count("\n") + 1

    importance: int
    """Number that indicates the importance, this is not normalized, and only makes sense in comparison to other files."""

    imports: set[str] = field(default_factory=set)
    """List of paths of other imported modules. Only internal modules is listed here."""

    imported_in: set[str] = field(default_factory=set)
    """List of paths of other modules that import this module."""

def determine_importance(files_loaded: list[FileLoaded]) -> list[FileLoaded]:
    """
    Determine importance for all files, based on imports, imported_in, depth and content length.

    A module is more core to understand the main control flow and what code is doing when:
    - It has a name like main.py
    - It is shallow nested
    - It imports many other modules
    """
    important_file_names: set[str] = {"main.py", "app.py", "__main__.py", "core.py"}
    def calculate_importance_feature(file: FileLoaded) -> int:
        """
        Calculate the importance feature for a single file, this is not normalized, and can be a large number.
        """
        if file.content_length == 0:
            return 0
        importance: int = 10
        if file.path.name in important_file_names:
            importance += 1000
        importance += max(0, 60 - file.depth * 10)
        importance += len(file.imports) * 10
        importance += len(file.imported_in) * 5
        # For every x lines subtract 1 point from importance
        importance -= file.line_count // 50
        return importance
    for file in files_loaded:
        file.importance = calculate_importance_feature(file)
    return files_loaded


class FileCompressor:
    def __init__(
        self,
        file_contents: dict[pathlib.Path, str],
        import_graph: grimp.ImportGraph,
        base_module: pathlib.Path,
    ) -> None:
        self._file_contents = file_contents
        self._import_graph = import_graph
        self._base_module = base_module

    def create_file_loaded_objects(self) -> list[FileLoaded]:
        """Create FileLoaded objects from the file contents."""
        files_loaded: list[FileLoaded] = []
        for file_path, content in self._file_contents.items():
            module_str: str = path_to_module_str(self._base_module / file_path)
            imports: set[str] = self._import_graph.find_modules_directly_imported_by(
                module_str
            )
            imported_in: set[str] = self._import_graph.find_modules_that_directly_import(module_str)
            file_loaded = FileLoaded(
                name=module_str,
                path=file_path,
                content=content,
                importance=-1,
                imports=imports,
                imported_in=imported_in,
            )
            files_loaded.append(file_loaded)
        determine_importance(files_loaded)
        # Sort files by importance descending
        files_loaded.sort(key=lambda file: file.importance, reverse=True)
        return files_loaded

    def report_file_contents(self) -> None:
        print(f"Got content from {len(self._file_contents)} files")
        # Sort files by content length descending
        total_chars: int = sum(len(content) for content in self._file_contents.values())
        sorted_files = sorted(
            self._file_contents.items(), key=lambda item: len(item[1]), reverse=True
        )
        for file_path, content in sorted_files:
            content_len: int = len(content)
            percent: float = (
                (content_len / total_chars * 100) if total_chars > 0 else 0.0
            )
            print(
                f"File: {file_path}, length content: {content_len} ({percent:.2f}% of total)"
            )


if __name__ == "__main__":
    from normyformy.core.file_filter import FileFilter
    from normyformy.core.file_tree import FileTreeGenerator
    from normyformy.core.file_reader import FileContentReader

    directory = pathlib.Path("src")
    depth = -1
    exclude_hidden = True
    file_filter = FileFilter(
        user_ignore_path=pathlib.Path(".copconignore"), user_target_path=None
    )

    # Generate directory tree
    tree_generator = FileTreeGenerator(directory, depth, file_filter)
    directory_tree = tree_generator.generate()

    # Read file contents
    reader = FileContentReader(directory, file_filter, exclude_hidden)
    file_contents = reader.read_all()

    # Create import graph
    module = path_to_module_str(directory)
    import_graph = grimp.build_graph(module)

    compressor = FileCompressor(file_contents, import_graph, directory)
    loaded_files = compressor.create_file_loaded_objects()
    loaded_files
