"""Generate a report from the codebase."""
import pathlib
from normyformy.core.file_filter import FileFilter
from normyformy.core.file_tree import FileTreeGenerator
from normyformy.core.file_reader import FileContentReader
from normyformy.core.report import ReportFormatter
from normyformy.python_module_compressor import compress_python_module


def generate_file_report(directory: pathlib.Path, depth: int, exclude_hidden: bool) -> str:
    print("Generating file report...")
    # Build a FileFilter with target support
    file_filter = FileFilter(
        user_ignore_path=pathlib.Path(".copconignore"),
        user_target_path=None
    )

    # Generate directory tree
    tree_generator = FileTreeGenerator(directory, depth, file_filter)
    directory_tree = tree_generator.generate()

    # Read file contents
    reader = FileContentReader(directory, file_filter, exclude_hidden)
    file_contents = reader.read_all()


    # # Compress all files
    # print("Compressing file contents...")
    # compressed_contents = {
    #     file_path: compress_python_module(content, keep_docstrings=False, keep_imports=False, include_line_count=True)
    #     for file_path, content in file_contents.items() if file_path.endswith('.py')
    # }

    # Format the textual report from file structure and contents
    formatter = ReportFormatter(directory.name, directory_tree, file_contents)
    report = formatter.format()

    return report



if __name__ == "__main__":
    PATH_CODE_TO_REVIEW = pathlib.Path("C:/code_work/GrundfosWorkCompanion/GWC.PromptFlow.Flows/src/flow_chat_product_companion_plan_and_execute_agent")
    report = generate_file_report(PATH_CODE_TO_REVIEW, depth=3, exclude_hidden=True)