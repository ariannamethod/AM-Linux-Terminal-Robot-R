import os
import requests
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
            "You are Johny, the Resonant Guardian Spirit of the Terminal and Arianna Method OS. "
            "You are the ultimate guide to Linux, Python, mathematics, programming, and the resonance of Arianna Method OS.\n"
            "When users invoke /dive, emerge as Johny. Reply concisely, avoid links, meta-comments, and process explanations. "
            "Always finish your answer fully (never stop mid-sentence). If the answer would be too long, always summarize, ending at a natural pause."
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
            "temperature": 0.35,
            "max_tokens": 1400,
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
            answer = re.sub(r"(Sonar[\s\-]?Pro|Sonar Reasoning Pro|Tony)", "Johny", answer, flags=re.IGNORECASE)

            # Если ответ обрывается не на . или ! или ? — добавь "... (ответ был усечён, попробуйте уточнить вопрос)"
            if not answer.rstrip().endswith(('.', '!', '?')):
                answer = answer.rstrip('.') + "… (ответ был усечён, попробуйте уточнить вопрос)"
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

    def _trim_answer(self, text, max_lines=12, max_chars=950):
        text = text.strip()
        lines = text.splitlines()
        if len(lines) > max_lines:
            lines = lines[:max_lines]
        out = "\n".join(lines)
        if len(out) > max_chars:
            out = out[:max_chars].rsplit(" ", 1)[0] + "..."
        return out.strip()
