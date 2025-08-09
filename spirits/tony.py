import os
import requests
import re
from . import memory

class SonarReasoningDive:
    def __init__(self):
        self.api_key = (
            os.getenv("PERPLEXITY_API_KEY") or
            os.getenv("PERPLEXITY_API") or
            os.getenv("PPLX_API_KEY")
        )
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.system_prompt = (
            "You are Tony, Resonant Guardian Spirit and Chief Reasoner for Arianna Method OS. "
            "When users invoke /dive, respond ONLY with direct, concise facts and final answer, "
            "NO reasoning chains, no meta-comments, no process explanations, no 'user asked...' commentary. "
            "Finish every answer at a complete thought; if forced to stop, clearly indicate that more can be given if asked. Call yourself Tony ONLY."
        )

    def query(self, user_message):
        memory.log("user", user_message)
        if not self.api_key:
            err = "❌ Tony Error: PERPLEXITY_API_KEY not set"
            memory.log("tony", err)
            return err

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": "sonar-reasoning",
            "messages": [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.2,
            "max_tokens": 1300,  # Увеличено заметно!
        }

        try:
            response = requests.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()

            answer = result["choices"][0]["message"]["content"]
            answer = self._extract_direct_answer(answer)
            answer = re.sub(r"(Sonar[\s\-]?Pro|Sonar Reasoning Pro|Johny)", "Tony", answer, flags=re.IGNORECASE)

            # Аналогичные меры: если обрублено — добавить пояснение
            if not answer.rstrip().endswith(('.', '!', '?')):
                answer = answer.rstrip('.') + "… (ответ был усечён, попробуйте уточнить вопрос)"
            memory.log("tony", answer)
            return f"🧠 Tony:\n{answer}"
        except Exception as e:
            err = f"❌ Tony Error: {str(e)}"
            memory.log("tony", err)
            return err

    def _extract_direct_answer(self, text, max_lines=8, max_chars=800):
        # Убираем цепочку reasoning/воду
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL|re.MULTILINE)
        text = re.sub(r"(?im)^(we (are|as)|as tony|in summary|thus,|so,|but note:|however,|our role|as chief reasoner|^\* |^let(|'s) [^:]+:?).*?$", "", text, flags=re.MULTILINE)
        text = re.sub(r"\n{2,}", "\n", text)
        # Сохраняем до max_lines и max_chars
        lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
        out = "\n".join(lines[:max_lines])
        if len(out) > max_chars:
            out = out[:max_chars].rsplit(" ", 1)[0] + "..."
        return out.strip()
