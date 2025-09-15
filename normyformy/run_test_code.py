
from normyformy.main import main, PolicyToReview
import pathlib

policies: list[PolicyToReview] = [
    PolicyToReview(
        name="Clean Architecture, infrastructure code is separated from business logic",
        description="Ensure that infrastructure code (e.g., database access, API clients) is separated from business logic."
    ),
    PolicyToReview(
        name="Dependency Inversion Principle",
        description="High-level modules should not depend on low-level modules. Both should depend on abstractions."
    ),
    PolicyToReview(
        name="Separation of Concerns",
        description="Each module or class should have responsibility over a single part of the functionality provided by the software."
    ),
    PolicyToReview(
        name="Explicit Boundaries Between Layers",
        description="Clearly define boundaries between presentation, domain, and infrastructure layers."
    ),
    PolicyToReview(
        name="No Direct Data Access in Business Logic",
        description="Business logic should not directly access databases or external services; use interfaces or repositories."
    ),
    PolicyToReview(
        name="Testability of Business Logic",
        description="Business logic should be easily testable without requiring infrastructure dependencies."
    ),
    PolicyToReview(
        name="Infrastructure Code Isolated",
        description="Infrastructure code (e.g., file system, network, database) should be isolated from domain logic and accessed via abstractions."
    ),
]
PATH_CODE_TO_REVIEW = pathlib.Path("C:/code_work/GrundfosWorkCompanion/GWC.PromptFlow.Flows/src/flow_chat_product_companion_plan_and_execute_agent")

if __name__ == "__main__":
    main(PATH_CODE_TO_REVIEW, policies)