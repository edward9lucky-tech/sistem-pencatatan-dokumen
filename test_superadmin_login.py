import pandas as pd

from User import load_users


def test_admin_credential():
    df = load_users()
    selected = df[df['username'].astype(str).str.strip().str.lower() == 'edward']
    assert not selected.empty
    assert selected.iloc[0]['password'] == '090990'


if __name__ == '__main__':
    test_admin_credential()
    print('admin credential test passed')
