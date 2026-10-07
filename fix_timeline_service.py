with open('backend/app/services/timeline_service.py', 'r') as f:
    content = f.read()

# Fix: school_name -> institution
content = content.replace('ed.school_name', 'ed.institution')

# Fix: add undated education block
old_ed = '''        # Education
        educations = self.db.execute(select(Education).where(Education.person_id == person_id)).scalars().all()
        for ed in educations:
            if ed.start_date:
                events.append(TimelineEvent(
                    id=ed.id,
                    date=ed.start_date,
                    year=ed.start_date.year,
                    title=f"Started at {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))
            if ed.end_date:
                events.append(TimelineEvent(
                    id=uuid.uuid4(),
                    date=ed.end_date,
                    year=ed.end_date.year,
                    title=f"Graduated from {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))'''

new_ed = '''        # Education
        educations = self.db.execute(select(Education).where(Education.person_id == person_id)).scalars().all()
        for ed in educations:
            if ed.start_date:
                events.append(TimelineEvent(
                    id=ed.id,
                    date=ed.start_date,
                    year=ed.start_date.year,
                    title=f"Started at {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))
            if ed.end_date:
                events.append(TimelineEvent(
                    id=uuid.uuid4(),
                    date=ed.end_date,
                    year=ed.end_date.year,
                    title=f"Graduated from {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))
            if not ed.start_date and not ed.end_date:
                events.append(TimelineEvent(
                    id=ed.id,
                    date=None,
                    year=None,
                    title=f"Studied at {ed.institution}",
                    description=ed.degree,
                    icon="education"
                ))'''

content = content.replace(old_ed, new_ed)

# Fix: add undated employment block
old_emp = '''        # Employment
        employments = self.db.execute(select(Employment).where(Employment.person_id == person_id)).scalars().all()
        for emp in employments:
            if emp.start_date:
                events.append(TimelineEvent(
                    id=emp.id,
                    date=emp.start_date,
                    year=emp.start_date.year,
                    title=f"Started working at {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))
            if emp.end_date:
                events.append(TimelineEvent(
                    id=uuid.uuid4(),
                    date=emp.end_date,
                    year=emp.end_date.year,
                    title=f"Left {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))'''

new_emp = '''        # Employment
        employments = self.db.execute(select(Employment).where(Employment.person_id == person_id)).scalars().all()
        for emp in employments:
            if emp.start_date:
                events.append(TimelineEvent(
                    id=emp.id,
                    date=emp.start_date,
                    year=emp.start_date.year,
                    title=f"Started working at {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))
            if emp.end_date:
                events.append(TimelineEvent(
                    id=uuid.uuid4(),
                    date=emp.end_date,
                    year=emp.end_date.year,
                    title=f"Left {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))
            if not emp.start_date and not emp.end_date:
                events.append(TimelineEvent(
                    id=emp.id,
                    date=None,
                    year=None,
                    title=f"Worked at {emp.employer_name}",
                    description=emp.job_title,
                    icon="job"
                ))'''

content = content.replace(old_emp, new_emp)

with open('backend/app/services/timeline_service.py', 'w') as f:
    f.write(content)

print("Done")
