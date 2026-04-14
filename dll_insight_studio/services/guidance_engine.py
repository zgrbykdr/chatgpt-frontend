from __future__ import annotations


class UserGuidanceEngine:
    def decision_text(self, step: str) -> dict[str, str]:
        prompts = {
            "important_terms": {
                "why": "We found terms that may represent model inputs, outputs, states, and parameters.",
                "look_for": "Check for names you recognize from configuration files, UI labels, or documentation.",
                "safe": "If unsure, choose 'Unsure'. The analysis will continue with conservative assumptions.",
            },
            "main_function": {
                "why": "Several functions look central to model computation.",
                "look_for": "Look for names mentioning compute, solve, run, step, or update.",
                "safe": "If uncertain, choose 'I am not sure'. The top-ranked candidate stays provisional.",
            },
            "io_clarification": {
                "why": "Input/output inference currently has low confidence.",
                "look_for": "Inputs usually represent setpoints or commands; outputs represent measured or calculated results.",
                "safe": "Skip if unsure. The report will mark this area as unresolved.",
            },
            "runtime_readiness": {
                "why": "Runtime comparison can validate which signals are true inputs or outputs.",
                "look_for": "Confirm whether you can run the host EXE safely in a controlled environment.",
                "safe": "Select static-only mode if runtime execution is not possible.",
            },
            "controlled_change": {
                "why": "Changing one input at a time isolates cause and effect.",
                "look_for": "Modify one setting, run again, and observe what changes.",
                "safe": "If unsure, do not run binary code and keep static analysis only.",
            },
        }
        return prompts.get(step, {"why": "Guidance unavailable.", "look_for": "", "safe": ""})
