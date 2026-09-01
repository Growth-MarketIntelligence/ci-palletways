import difflib

def get_text_diff(old_text: str, new_text: str, context_lines: int = 3) -> str:
    """
    Compares two text strings and returns a unified diff.
    This provides the LLM with the changed text, a bounded amount of 
    surrounding text, and the corresponding previous text where useful.
    """
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    
    diff = difflib.unified_diff(
        old_lines, new_lines, 
        fromfile='previous_document', tofile='current_document',
        n=context_lines
    )
    return "\n".join(diff)
