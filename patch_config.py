import re

with open("backend/app/core/config.py", "r") as f:
    c = f.read()

c = c.replace(
    'JWT_SECRET_KEY: str = "familynest_dev_jwt_secret_key_change_in_production_32chars"',
    'JWT_SECRET_KEY: str # Required. No insecure fallback.'
)

with open("backend/app/core/config.py", "w") as f:
    f.write(c)

with open("backend/pytest.ini", "r") as f:
    p = f.read()

p = p.replace("[pytest]", "[pytest]\nenv =\n    JWT_SECRET_KEY=test_only_secret_key_for_pytest_environment_not_secure")

with open("backend/pytest.ini", "w") as f:
    f.write(p)
