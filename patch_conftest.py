with open("backend/app/tests/conftest.py", "r") as f:
    content = f.read()

content = content.replace('(scope="function")', '@pytest.fixture(scope="function")')
content = content.replace('def test_user(db_session):', '@pytest.fixture(scope="function")\ndef test_user(db_session):')
content = content.replace('def normal_user_token_headers(test_user):', '@pytest.fixture(scope="function")\ndef normal_user_token_headers(test_user):')

with open("backend/app/tests/conftest.py", "w") as f:
    f.write(content)
