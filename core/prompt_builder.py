from core.input_handler import CodePayload


def build_prompt(payload: CodePayload) -> str:
    return f"""You are a code analysis assistant.

Analyze the following {payload.language.value} code and provide a short summary of what it does.

Code:
{payload.code}

Summary:"""
