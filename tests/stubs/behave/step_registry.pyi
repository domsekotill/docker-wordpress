from typing import Callable
from typing import TypeVar

C = TypeVar("C")
StepDecorator = Callable[[str], Callable[[C], C]]
StepFunction = Callable[..., None]


Given: StepDecorator[StepFunction]
given: StepDecorator[StepFunction]

When: StepDecorator[StepFunction]
when: StepDecorator[StepFunction]

Then: StepDecorator[StepFunction]
then: StepDecorator[StepFunction]

Step: StepDecorator[StepFunction]
step: StepDecorator[StepFunction]


class AmbiguousStep(ValueError): ...


class StepRegistry:

	steps: dict[str, list[StepFunction]]
