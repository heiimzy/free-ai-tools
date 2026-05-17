import json

with open(r'C:\Users\123\free-ai-tools\blog\posts.json', 'r', encoding='utf-8') as f:
    raw = f.read()

result = []
in_string = False
escape = False

for line in raw.split('\n'):
    new_chars = []
    i = 0
    while i < len(line):
        c = line[i]

        if escape:
            new_chars.append(c)
            escape = False
            i += 1
            continue

        if c == '\\':
            new_chars.append(c)
            escape = True
            i += 1
            continue

        if in_string:
            if c == '"':
                # ASCII double quote inside a JSON string - this was meant to be Chinese quotes
                new_chars.append('“' if self_closing else '”')
            else:
                if c in '“”':
                    pass  # already proper Chinese quotes
                new_chars.append(c)
        else:
            if c == '"':
                in_string = True
                self_closing = False
            new_chars.append(c)

        i += 1

    result.append(''.join(new_chars))

rebuilt = '\n'.join(result)

# Alternative approach: just escape internal double quotes properly
# Actually, the state-machine approach won't work well because we can't distinguish
# Let me try a simpler approach: parse the file more carefully

# Simpler: read the entire file as text, find all "key": "value" patterns
# and fix the values

# Actually, all Chinese quotes "" appear as " in the content
# We need to replace them with “ and ”
# Let's just replace them contextually

# Reset and try differently
with open(r'C:\Users\123\free-ai-tools\blog\posts.json', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace Chinese-context double quotes with Unicode Chinese quotes
# These appear in titles and summaries
import re

# Find all string values that contain Chinese characters and have embedded ASCII quotes
# Strategy: for text between a Chinese character and a " that isn't a JSON delimiter

# Actually, the simplest fix: just replace " after Chinese chars with “ and " before Chinese chars with ”
# Pattern: (Chinese) " (text) " (Chinese/punctuation)
chinese_range = r'[一-鿿㐀-䶿＀-￯　-〿]'

# Replace "that are surrounded by Chinese context with Unicode quotes
# Opening: after Chinese char or Chinese punctuation, before non-quote text
# Closing: after non-quote text, before Chinese char or punctuation

fixed = ''
i = 0
in_json_string = False
prev_was_chinese = False

while i < len(content):
    c = content[i]
    nc = content[i+1] if i+1 < len(content) else ''

    if c == '\\':
        fixed += c
        if i+1 < len(content):
            i += 1
            fixed += content[i]
        i += 1
        continue

    if c == '"':
        # Check if this is a JSON structural quote or a content quote
        # Look at context
        prev_char = fixed[-1] if fixed else ''
        next_char = content[i+1] if i+1 < len(content) else ''

        # If preceded by : or , or [ or { or whitespace after these, it's a JSON structural opening quote
        # If followed by , or ] or } or : or whitespace before these, it's a JSON structural closing quote

        prev_is_structure = prev_char in ':,[]{} \t\n\r'
        next_is_structure = next_char in ':,[]{} \t\n\r'

        if in_json_string:
            # We're closing a JSON string value
            # Check if the next char suggests structure (JSON closing) or content (Chinese quote)
            if next_char in ',]}\n\r\t ':
                # This is a JSON structural close
                in_json_string = False
                fixed += c
            else:
                # This is a Chinese closing quote inside content
                fixed += '”'
        else:
            # Determine if this opens a JSON string or is a Chinese opening quote
            if prev_is_structure:
                # JSON structural open
                in_json_string = True
                fixed += c
            else:
                # Chinese opening quote inside content
                fixed += '“'
    else:
        fixed += c

    i += 1

# Validate
try:
    data = json.loads(fixed)
    print(f'SUCCESS: Valid JSON with {len(data)} posts')

    with open(r'C:\Users\123\free-ai-tools\blog\posts.json', 'w', encoding='utf-8') as f:
        f.write(fixed)
    print('Saved!')

    # Check problematic titles
    for p in data:
        t = p['zh']['title']
        if '“' in t or '”' in t:
            print(f'  #{p["id"]}: {t}')

except json.JSONDecodeError as e:
    print(f'FAILED: {e}')
    lines = fixed.split('\n')
    if e.lineno:
        start = max(0, e.lineno-2)
        for n in range(start, min(len(lines), e.lineno+3)):
            marker = '>>>' if n == e.lineno-1 else '   '
            print(f'{marker} {n+1}: {repr(lines[n][:150])}')
