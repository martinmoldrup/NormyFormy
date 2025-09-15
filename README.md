# NormyFormy
Automated code conformance to team norms and standards. Consistency, at scale.

NormyFormy helps your team enforce architectural principles, coding standards, and best practices across every project. By reviewing your code against customizable policies, NormyFormy ensures adherence to your organization’s guidelines—catching issues that slip past linters and static analysis. Achieve consistent, high-quality code and streamline onboarding by making your team’s norms easy to follow and impossible to miss.

The application leverages a Large Language Model (LLM) to automate code reviews against a customizable set of policies. By analyzing source code, it generates a structured report detailing how well the code adheres to architectural principles, design guidelines, and best practices. The tool is designed to help teams maintain high standards, improve code quality, and ensure consistency across projects.

The app is meant as a supplement to linting, type checking, and unit testing. It focuses on higher-level design and architectural concerns that are often difficult to enforce through traditional static analysis tools. The app should be easy to use and add new policies to as needed.

Important note is that it is not deterministic and the results may vary between runs. It is best used as a guide to identify potential issues and areas for improvement, rather than a definitive assessment of code quality. Because of the non-deterministic nature of LLMs, it blocking CI quality assurance pipelines is not recommended. Publishing warnings to the CI report is a better approach, for human review.

# Example Usage

```python

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
```
Result:

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓    
┃ Policy                                                                  ┃ Verdict ┃ Review Comment                                                                                                                                                                       ┃    
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩    
│ Clean_Architecture_infrastructure_code_is_separated_from_business_logic │    5    │ Infrastructure code is well-separated from business logic, as seen through the `helpers` and `infrastructure` modules providing interfaces to core components.                       │    
│ Dependency_Inversion_Principle                                          │    4    │ Most components appear to be adhering to dependency inversion, particularly through interfaces like `LLMClient`. However, more interfaces could be utilized across other components. │    
│ Separation_of_Concerns                                                  │    4    │ Overall, separation of concerns is followed but could be improved by further simplifying complex functions.                                                                          │    
│ Explicit_Boundaries_Between_Layers                                      │    5    │ Explicit boundaries between layers exist as modules organized for context creation, joining, planning, and infrastructure.                                                           │    
│ No_Direct_Data_Access_in_Business_Logic                                 │    5    │ Business logic avoids direct data accesses and uses abstractions according to functions in `activity_router.py`.                                                                     │    
│ Testability_of_Business_Logic                                           │    4    │ The use of interfaces suggests good testability; however, external dependencies still need mock provisions to facilitate testing.                                                    │    
│ Infrastructure_Code_Isolated                                            │    5    │ Infrastructure code is sufficiently isolated, using classes like `OpenAILLMClient` to manage external API communication.                                                             │    
└─────────────────────────────────────────────────────────────────────────┴─────────┴──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘ 

