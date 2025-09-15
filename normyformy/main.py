"""Code reviewer that checks policies against the code and generates a report."""
import os
import pathlib
from typing import Any
from pydantic import BaseModel
from genson import SchemaBuilder
from langchain_openai import AzureChatOpenAI
import re
from normyformy.generate_file_report import generate_file_report
import rich.table

AZURE_ENDPOINT: str = "https://gf-oai-gwcml-s-swno.openai.azure.com/"
AZURE_OPENAI_API_KEY: str = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_API_VERSION: str = "2024-10-21"
AZURE_DEPLOYMENT_EMBEDDINGS: str = "text-embedding-ada-002"
AZURE_DEPLOYMENT_CHAT: str = "gpt-4o"
class PolicyToReview(BaseModel):
    name: str
    description: str

    def __str__(self) -> str:
        return f"Policy: {self.name}\nDescription: {self.description}"


# PATH_CODE_TO_REVIEW = pathlib.Path("C:/code_personal/toolit")


def _sanitize_property_name(prop: str) -> str:
    """Sanitize property name to be JSON schema compatible (alphanumeric, _, -)."""
    sanitized: str = prop.strip().strip(".")
    # Remove commas
    sanitized = sanitized.replace(",", "")
    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")
    # Remove ' and "
    sanitized = sanitized.replace("'", "").replace('"', "")
    # Replace any other non-alphanumeric characters
    sanitized: str = re.sub(r'[^a-zA-Z0-9_-]', '_', sanitized)
    # # Ensure it doesn't start with a digit
    # if sanitized and sanitized[0].isdigit():
    #     sanitized = f"p_{sanitized}"
    # # Optionally, truncate if too long (e.g., 64 chars)
    # sanitized = sanitized[:64]
    return sanitized

def _create_validation_model(
    sanitized_validation_policies: list[str],
) -> dict[str, Any]:
    """Create a json schema model for the code policies."""
    builder = SchemaBuilder()
    builder.add_schema({"type": "object", "properties": {},
                        "title": "CodePolicies",
                        "description": "Code policies to review code against to ensure compliance with best practices."})
    for prop in sanitized_validation_policies:
        builder.add_object({f"{prop}_review_comment": "Infrastructure code is well separated from the business logic in different folders"})
        builder.add_object({f"{prop}_policy_followed_verdict": 5})
        # builder.add_object({prop: False})
    
    schema = builder.to_schema()
    # Add minimum and maximum properties to all the '_policy_followed_verdict' properties
    for properties in schema["properties"]:
        if properties.endswith("_policy_followed_verdict"):
            schema["properties"][properties]["minimum"] = 0
            schema["properties"][properties]["maximum"] = 5
    return schema


def evaluate_policies(
    code_report: str,
    policies_to_review: list[PolicyToReview],
    llm: AzureChatOpenAI,
) -> dict[str, bool]:
    """Generate the booleans for the validation properties based on the document."""
    print("Evaluating policies...")
    property_sanitized_lookup: dict[str, str] = {
        _sanitize_property_name(prop.name): prop.name for prop in policies_to_review
    }
    json_schema = _create_validation_model(
        sanitized_validation_policies=list(property_sanitized_lookup.keys()),
    )
    prompt: str = (
        "You are an opinionated lead developer. You are an expert in domain driven design and clean architecture. You are reviewing a new codebase and checking if it aligns with clean architecture principles. Given the following codebase report, evaluate whether each policy is followed. "
        "Policies to Review:\n"
        + "\n".join([f"- {prop.name}: {prop.description}" for prop in policies_to_review]) +
        "Codebase Report:\n"
        f"{code_report}\n\n"
        # "Return if the policies are followed in the codebase following the provided schema"
        "\n\nReturn a JSON object following the provided schema. "
        "First shortly reason around if the policy is followed in the '_review_comment' field, focus upon things that can be improved if any in the comment. Only do a short single sentence with your conclusion. Then conclude by setting the corresponding '_policy_followed_verdict' property to a value between 0 and 5, where 0 means not followed at all and 5 means fully followed. If the policy is not applicable, set the '_policy_followed_verdict' to None. If you do not give it 5 then focus the review comment on why it is not a perfect 5.\n\n"
    )
    print("Running LLM...")
    response = llm.with_structured_output(json_schema).invoke(prompt)
    print("Finished running LLM.")
    return response

def print_report(evaluation: dict[str, bool]):
    """Print the evaluation report using rich in a table."""
    table = rich.table.Table(title="Policy Evaluation Report")
    table.add_column("Policy", justify="left")
    table.add_column("Verdict", justify="center")
    table.add_column("Review Comment", justify="left")

    # Group verdicts and comments by policy
    policies_dict = extract_policy_data(evaluation)

    for policy_name, data in policies_dict.items():
        verdict = data.get("verdict", None)
        comment = data.get("comment", "")
        verdict_display = str(verdict) if verdict is not None else "N/A"
        table.add_row(policy_name, verdict_display, comment)

    rich.print(table)

def extract_policy_data(evaluation: dict[str, Any]) -> dict[str, dict[str, Any]]:
    policies_dict: dict[str, dict[str, Any]] = {}

    for key, value in evaluation.items():
        if key.endswith("_policy_followed_verdict"):
            policy_name: str = key.replace("_policy_followed_verdict", "")
            policies_dict.setdefault(policy_name, {})["verdict"] = value
        elif key.endswith("_review_comment"):
            policy_name: str = key.replace("_review_comment", "")
            policies_dict.setdefault(policy_name, {})["comment"] = value
    return policies_dict

def main(path_code_to_review: pathlib.Path, policies: list[PolicyToReview]):
    open_chat_llm = AzureChatOpenAI(
        azure_endpoint=AZURE_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        azure_deployment=AZURE_DEPLOYMENT_CHAT,
        api_version=AZURE_OPENAI_API_VERSION,
    )
    file_report = generate_file_report(path_code_to_review, depth=-1, exclude_hidden=True)
    evaluation = evaluate_policies(file_report, policies, open_chat_llm)
    print_report(evaluation)
