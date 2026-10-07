import re
with open("backend/app/tests/test_phase21_events.py", "r") as f:
    content = f.read()
content = content.replace("assert count_u2 == 0", "assert count_u2 == 0, f'count_u2 is {count_u2}, expected 0'")
with open("backend/app/tests/test_phase21_events.py", "w") as f:
    f.write(content)
