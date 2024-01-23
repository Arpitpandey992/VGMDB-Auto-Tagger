class TemplateValidationException(ValueError):
    def __init__(self, message: str):
        super().__init__(message)


class TemplateResolver:
    # Public Functions:
    def __init__(self, mapping: dict[str, str | None]):
        self.mapping = {key.lower(): value for key, value in mapping.items()}

    def evaluate(self, expression: str) -> str:
        return self._evaluate(expression)

    @staticmethod
    def validateTemplate(expression: str):
        """
        Check if template is valid or not.
        :param expression: The expression string to validate
        :raises TemplateValidationException: if provided expression is invalid
        """
        open = 0
        for character in expression:
            if character != "{" and character != "}":
                continue
            if character == "{":
                open += 1
            elif open == 0:
                raise TemplateValidationException(f"invalid template expression: {expression}")
            else:
                open -= 1
        if open != 0:
            raise TemplateValidationException(f"invalid template expression: {expression}")

    # Private functions:
    def _evaluate(self, expression: str) -> str:
        """
        Recursively evaluate a given expression, not extremely optimized, but it's not needed here
        """
        """
        what to do? : 
            break the expression in all top level |
            evaluate each part and return the first proper part
            evaluate all top level names under {}
            Now, the expression is without any {} with things which failed under {} returning None
            evaluate all expression by splitting around | and returning the first one we get
        """
        # Checking if this expression needs everything in it to be evaluated
        closingIndices = self._getClosingIndices(expression)
        returnNoneIfAnyFailure = False
        if expression[0] == "{" and closingIndices[0] == len(expression) - 1:
            returnNoneIfAnyFailure = True
            expression = expression[1:-1]
            closingIndices = self._getClosingIndices(expression)

        # Breaking the expression on top level OR operator and evaluating each part (this will supercede the above check)
        parts = self._splitExpressionOnTopLevel(expression, "|")
        if len(parts) > 1:
            for part in parts:
                finalExpression = self._evaluate(part)
                if finalExpression:
                    return finalExpression
            return ""

        # Evaluating all top level {...}
        finalExpression, left = "", 0
        while left < len(expression):
            if closingIndices[left] != -1:
                right = closingIndices[left]
                solvedExpression = self._evaluate(expression[left : right + 1])
                if returnNoneIfAnyFailure and not solvedExpression:
                    return ""
                finalExpression += solvedExpression
                left = right + 1
            else:
                finalExpression += expression[left]
                left += 1

        # checking the final block
        if finalExpression.strip().lower() not in self.mapping:
            return finalExpression
        expressionValue = self.mapping[finalExpression.strip().lower()]
        if expressionValue:  # checking for both None, and ""
            return expressionValue
        return ""

    def _splitExpressionOnTopLevel(self, expression: str, divider: str) -> list[str]:
        curDelta = 0
        cur = ""
        ans: list[str] = []
        for character in expression:
            if curDelta == 0 and character == divider:
                ans.append(cur)
                cur = ""
            else:
                cur += character
                if character == "{":
                    curDelta += 1
                elif character == "}":
                    curDelta -= 1
        if cur:
            ans.append(cur)
        return ans

    def _getClosingIndices(self, expression: str) -> list[int]:
        expressionLength = len(expression)
        closingIndices: list[int] = [-1] * expressionLength
        stack: list[int] = []
        for i, character in enumerate(expression):
            if character != "{" and character != "}":
                continue
            if character == "{":
                stack.append(i)
            else:
                lastOpeningIndex = stack.pop()
                closingIndices[lastOpeningIndex] = i
        return closingIndices
