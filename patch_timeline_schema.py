with open('backend/app/schemas/timeline.py', 'r') as f:
    content = f.read()

content = content.replace('from datetime import date', 'from datetime import date as dt_date')
content = content.replace('date: Optional[date] = None', 'date: Optional[dt_date] = None')

with open('backend/app/schemas/timeline.py', 'w') as f:
    f.write(content)
