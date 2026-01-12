import re


def extract_action_items(text: str) -> list[str]:
    """
    Extract action items from text using sophisticated pattern recognition and analysis.
    
    Patterns recognized:
    1. Action keywords: TODO, ACTION, FIXME, BUG, HACK, NOTE, REMINDER, WARNING, IMPORTANT, URGENT
    2. Action verbs: must, should, need to, remember to, ensure, make sure, consider, review
    3. Imperative sentences: sentences starting with common action verbs
    4. Exclamatory sentences: sentences ending with !
    5. Context-aware filtering: excludes questions and non-actionable statements
    
    Args:
        text: Input text to extract action items from
        
    Returns:
        List of extracted action item strings (deduplicated)
    """
    if not text or not text.strip():
        return []
    
    # Action keywords (case-insensitive, with optional colon)
    action_keywords = [
        r"^(todo|action|fixme|bug|hack|note|reminder|warning|important|urgent|critical)\s*:",
    ]
    
    # Action verb phrases that indicate action items
    action_verb_patterns = [
        r"^\s*(?:must|should|need to|remember to|ensure|make sure|consider|review)\b",
        r"^\s*(?:implement|add|remove|update|fix|refactor|test|verify|check|confirm)\b",
        r"^\s*(?:complete|finish|start|create|delete|modify|improve|optimize)\b",
        r"^\s*(?:document|clarify|resolve|address|handle|process|validate)\b",
        r"^\s*(?:deploy|rollback|merge|split|prioritize|schedule|assign)\b",
        r"^\s*(?:notify|inform|contact|follow up|investigate|analyze)\b",
        r"^\s*(?:evaluate|assess|monitor|track|log|debug|trace)\b",
    ]
    
    # Common imperative verbs (for capital-letter sentence start detection)
    imperative_verbs = {
        "add", "update", "fix", "remove", "create", "delete", "modify",
        "implement", "test", "verify", "check", "review", "complete",
        "finish", "start", "ensure", "improve", "refactor",
        "document", "clarify", "resolve", "handle", "process", "validate",
        "deploy", "merge", "split", "prioritize", "schedule", "assign",
        "notify", "investigate", "analyze", "monitor", "track",
    }
    
    lines = text.splitlines()
    results: list[str] = []
    seen_items = set()  # Avoid duplicates
    
    for line in lines:
        if not line.strip():
            continue
            
        # Clean up common prefixes (bullets, dashes, numbers)
        cleaned = re.sub(r"^\s*[-*•]\s+", "", line.strip())
        cleaned = re.sub(r"^\s*\d+[\.\)]\s+", "", cleaned)
        
        # Skip empty lines after cleaning
        if not cleaned or len(cleaned) < 3:
            continue
            
        # Normalize for comparison (lowercase, trimmed)
        normalized = cleaned.lower().strip()
        
        # Skip questions (ending with ?)
        if cleaned.rstrip().endswith("?"):
            continue
        
        # Skip if it's just a statement without action indicators
        if not re.search(r"[a-zA-Z]", cleaned):
            continue
            
        # Pattern 1: Action keywords (TODO, ACTION, FIXME, etc.)
        matched = False
        for pattern in action_keywords:
            if re.search(pattern, cleaned, re.IGNORECASE):
                if normalized not in seen_items:
                    results.append(cleaned)
                    seen_items.add(normalized)
                    matched = True
                    break
        if matched:
            continue
            
        # Pattern 2: Action verb phrases at the start
        for pattern in action_verb_patterns:
            if re.search(pattern, cleaned, re.IGNORECASE):
                if normalized not in seen_items:
                    results.append(cleaned)
                    seen_items.add(normalized)
                    matched = True
                    break
        if matched:
            continue
            
        # Pattern 3: Exclamatory sentences (ending with !)
        if cleaned.rstrip().endswith("!"):
            # Must contain letters (not just punctuation)
            if re.search(r"[a-zA-Z]", cleaned):
                if normalized not in seen_items:
                    results.append(cleaned)
                    seen_items.add(normalized)
                    continue
        
        # Pattern 4: Imperative sentences starting with action verbs (capitalized)
        words = cleaned.split()
        if words:
            first_word = words[0].lower()
            # Check if first word is an imperative verb and sentence starts with capital
            if first_word in imperative_verbs and cleaned[0].isupper():
                # Additional check: should be a complete thought (at least 3 words or contains verb-object structure)
                if len(words) >= 2:  # At least verb + object
                    if normalized not in seen_items:
                        results.append(cleaned)
                        seen_items.add(normalized)
                        continue
    
    return results


