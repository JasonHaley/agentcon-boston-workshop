import json
import pathlib
import prompty

from openai.types.chat import ChatCompletionMessageParam

class PromptyService:

    PROMPTS_DIRECTORY = pathlib.Path(__file__).parent.parent / "prompts"

    def load_prompt(self, path: str):
        return prompty.load(self.PROMPTS_DIRECTORY / path)

    def load_tools(self, path: str):
        return json.loads(open(self.PROMPTS_DIRECTORY / path).read())

    def render_prompt(self, prompt, data) -> list[ChatCompletionMessageParam]:
        return prompty.prepare(prompt, data)
    
    def render_prompt_as_string(self, prompt, data) -> str:
        result = self.render_prompt(prompt, data)
        return "\n".join([msg['content'] for msg in result if 'content' in msg and msg['content']])