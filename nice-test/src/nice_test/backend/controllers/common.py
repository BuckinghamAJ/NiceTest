import re

# Regex expression for word document requirements, example: [E-SYS-1101]
bracket_pattern = re.compile(pattern=r"\[([A-Z]+-\w+-\d+)\]")
