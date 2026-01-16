from anthropic import Anthropic
import logging
from helper import parse_json_response

class ClaudeService:
    def __init__(self, anthropic_api_key):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        self.client = self._setup_anthropic_client(anthropic_api_key)
        self.model = "claude-haiku-4-5-20251001"

    def _setup_anthropic_client(self, key):
        self.logger.info('Setting up anthropic client')

        try:
            client = Anthropic(api_key=key)
            self.logger.info("Anthropic client created")
            return client
        except Exception as e:
            self.logger.error(e)
            raise

    def query_claude(self, claude_prompt, system_prompt):
        self.logger.info('Querying claude')

        try:
            claude_response = self.client.messages.create(
                max_tokens=1024,
                messages=[
                    {
                        'role': 'user',
                        'content': claude_prompt,
                    }
                ],
                system=system_prompt,
                model=self.model
            )

            self.logger.info("Claude response created")

            return parse_json_response(claude_response.content[0].text)

        except Exception as e:
            self.logger.error(e)
            return False