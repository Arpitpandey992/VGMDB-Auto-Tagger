
class TemplateValidationException(ValueError):
    def __init__(self, message):
        super().__init__(message)


class TemplateResolver:
    # Public Functions:
    def __init__(self, mapping: dict) -> None:
        self.mapping = {
            key.lower(): value for key, value in mapping.items()
        }

    def evaluate(self, expression: str) -> str:
        return self._evaluate(expression)[0]

    @staticmethod
    def validateTemplate(expression: str):
        """
        Check if template is valid or not.
        :param expression: The expression string to validate
        :raises TemplateValidationException: if provided expression is invalid
        """
        open = 0
        for character in expression:
            if character != '{' and character != '}':
                continue
            if character == '{':
                open += 1
            elif open == 0:
                raise TemplateValidationException(f"invalid template expression: {expression}")
            else:
                open -= 1
        if open != 0:
            raise TemplateValidationException(f"invalid template expression: {expression}")

# Private functions:
    def _evaluate(self, expression: str) -> tuple[str, bool]:
        """
        Recursively evaluate a given expression, not extremely optimized, but it's not needed here
        """
        if expression.lower().strip() in self.mapping:
            expressionValue = self.mapping[expression.lower().strip()]
            # checking for both None, and ""
            if expressionValue:
                return (expressionValue, True)
            return ("", False)
        expressionLength = len(expression)
        closingIndices = self._getClosingIndices(expression)
        left = 0
        finalExpression = ""
        finalResolved = True
        while left < expressionLength:
            if closingIndices[left] != -1:
                right = closingIndices[left]
                solvedExpression, resolved = self._evaluate(expression[left + 1:right])
                if not resolved:
                    finalResolved = False
                else:
                    finalExpression += solvedExpression
                left = right + 1
            else:
                finalExpression += expression[left]
                left += 1
        return (finalExpression, finalResolved)

    def _getClosingIndices(self, expression: str) -> list[int]:
        expressionLength = len(expression)
        closingIndices: list[int] = [-1] * expressionLength
        stack: list[int] = []
        for i, character in enumerate(expression):
            if character != '{' and character != '}':
                continue
            if character == '{':
                stack.append(i)
            else:
                lastOpeningIndex = stack.pop()
                closingIndices[lastOpeningIndex] = i
        return closingIndices


if __name__ == '__main__':
    mapping = {
        "catalog": "KSLA-0020",
        # "catalog": None,
        "date": "2020-01-05",
        # "date": None,
        "barcode": "033325551233",
        "name": "damnson"
    }
    template = TemplateResolver(mapping)
    testName = "{[{catalog}] }{name}{ [{date}]}"
    finalExpression = template.evaluate(testName)
    print(finalExpression)
