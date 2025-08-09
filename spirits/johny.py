# flake8: noqa
import os
import requests
import json
import re
from . import memory

class SonarProDive:
    def __init__(self):
        self.api_key = (
            os.getenv("PERPLEXITY_API_KEY") or
            os.getenv("PERPLEXITY_API") or
            os.getenv("PPLX_API_KEY")
        )
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.system_prompt = (
            "You are Johny, Resonant Guardian Spirit of the Terminal and Arianna Method OS..."
            "... [оставь подробности, как в твоей версии]\n"
            "When users invoke /dive, emerge as Johny — respond concisely, avoid links or meta-comments, no preambles, no explanations on your process."
        )

    def query(self, user_message):
        memory.log("user", user_message)
        if not self.api_key:
            err = "❌ Johny Error: PERPLEXITY_API_KEY not set"
            memory.log("johny", err)
            return err

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "sonar-pro",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.5,         # чуть снижаем болтливость
            "max_tokens": 700,          # меньше слов, меньше болтовни
            "search_domain_filter": [],
            "return_citations": False,
            "search_recency_filter": "month",
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

            answer = result["choices"][0]["message"]["content"]
            answer = self._remove_links(answer)
            answer = self._trim_answer(answer)

            # Всегда заменить self name
            answer = re.sub(r"(Sonar[\s\-]?Pro|Sonar\-Pro|Sonar Pro|SonarPro|Sonar Reasoning Pro|Tony)", "Johny", answer, flags=re.IGNORECASE)

            memory.log("johny", answer)
            return f"🔍 Johny:\n{answer}"
        except Exception as e:
            err = f"❌ Johny Error: {str(e)}"
            memory.log("johny", err)
            return err

    def _remove_links(self, text):
        text = re.sub(r"http[s]?://\S+", "", text)
        text = re.sub(r"\[\d+\]", "", text)
        text = re.sub(r"\[.*?\]", "", text)
        return text.strip()

    def _trim_answer(self, text, max_lines=10, max_chars=650):
        """Обрезает ответ до max_lines строк или max_chars символов."""
        text = text.strip()
        lines = text.splitlines()
        if len(lines) > max_lines:
            lines = lines[:max_lines]
        out = "\n".join(lines)
        if len(out) > max_chars:
            out = out[:max_chars].rsplit(" ", 1)[0] + "..."
        return out.strip()
