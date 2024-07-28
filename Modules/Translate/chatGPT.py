import os
import time
import openai
from typing import List, Type, Callable, Any, Optional, Literal
from typing_extensions import TypedDict
from openai import OpenAI, RateLimitError, APIConnectionError, APIError, InternalServerError, APITimeoutError

from Modules.Utils.general_utils import get_default_logger

DEFAULT_SYSTEM_ROLE_CONTENT = "You are a helpful assistant."
model_types = Literal["4k_tokens", "16k_tokens", "4k_tokens_function_calling", "16k_tokens_function_calling"]


class model_details(TypedDict):
    name: str
    max_tokens: int


model_map: dict[model_types, model_details] = {
    "4k_tokens": model_details(name="gpt-3.5-turbo", max_tokens=4096),
    "16k_tokens": model_details(name="gpt-3.5-turbo-16k", max_tokens=16384),
    "4k_tokens_function_calling": model_details(name="gpt-3.5-turbo-0613", max_tokens=4096),
    "16k_tokens_function_calling": model_details(name="gpt-3.5-turbo-16k-0613", max_tokens=16384),
}

logger = get_default_logger(__name__)


class TokenUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class QueryResponse(TypedDict):
    response: str
    usage: TokenUsage


class QueryResponseFunctionCalling(TypedDict):
    response: str
    usage: TokenUsage


class ChatGPTAPI:
    def __init__(self, model_name: model_types = "4k_tokens", system_role=DEFAULT_SYSTEM_ROLE_CONTENT, temperature=0.5, max_tokens=None):
        self.model_name = model_map[model_name]["name"]
        openai.api_key = os.environ.get("OPENAI_API_KEY", "")
        self.system_role_content = system_role
        self.temperature = temperature * 2
        self.max_tokens = max_tokens
        self.client = OpenAI()

    def query(self, prompt: str) -> QueryResponse:
        messages = [
            {"role": "system", "content": self.system_role_content},
            {"role": "user", "content": prompt},
        ]

        response = retry_on_exceptions_with_backoff(
            lambda: self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,  # type:ignore
                max_tokens=self.max_tokens,
            ),
            [
                RateLimitError,
                APITimeoutError,
                APIConnectionError,
                InternalServerError,
                APIError,
            ],
        )
        usage = TokenUsage(response["usage"])
        logger.info(f"ChatGPT Token Usage - {usage}")
        reply = response["choices"][0]["message"]["content"]
        return {"response": reply, "usage": usage}

    def query_with_function_call(self, prompt: str, function_call_dict: dict) -> QueryResponse:
        messages = [
            {"role": "system", "content": self.system_role_content},
            {"role": "user", "content": prompt},
        ]
        args_dict = {
            "model": self.model_name,
            "messages": messages,
            "functions": [function_call_dict],
            "function_call": {"name": function_call_dict["name"]},
        }
        if self.max_tokens:
            args_dict["max_tokens"] = self.max_tokens
        response = retry_on_exceptions_with_backoff(
            lambda: self.client.chat.completions.create(**args_dict),
            [RateLimitError, APITimeoutError, APIConnectionError],
        )
        json_response = response["choices"][0]["message"]["function_call"]["arguments"]
        usage = TokenUsage(response["usage"])
        # logger.info(f"ChatGPT Token Usage - {usage}")
        return {
            "response": json_response,
            "usage": usage,
        }  # the json_response may be incomplete


def retry_on_exceptions_with_backoff(
    lambda_fn: Callable,
    exception_classes: Optional[List[Type[Exception]]] = None,
    max_tries: int = 10,
    min_backoff_secs: float = 1,
    max_backoff_secs: float = 60.0,
) -> Any:
    """Execute lambda function with retries and exponential backoff.
    Args:
        lambda_fn (Callable): Function to be called and output we want.
        exception_classes (List[Type[Exception]]): List of exception classes to retry.
        max_tries (int): Maximum number of tries, including the first. Defaults to 10.
        min_backoff_secs (float): Minimum amount of backoff time between attempts.
            Defaults to 0.5.
        max_backoff_secs (float): Maximum amount of backoff time between attempts.
            Defaults to 60.
    """
    exception_class_tuples = tuple(exception_classes) if exception_classes else Exception
    backoff_secs = min_backoff_secs
    tries = 0
    while True:
        try:
            return lambda_fn()
        except exception_class_tuples as e:
            logger.error(f"exception with lambda function, tries: {tries}. error: {e}")
            tries += 1
            if tries >= max_tries:
                raise e
            time.sleep(backoff_secs)
            logger.info(f"retrying after backoff of {backoff_secs} secs")
            backoff_secs = min(backoff_secs * 2, max_backoff_secs)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    gpt = ChatGPTAPI()
    response = gpt.query("why is the sky blue?")
    print(type(response["usage"]["completion_tokens"]))
    print(response)
