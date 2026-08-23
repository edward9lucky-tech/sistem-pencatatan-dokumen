from User import load_users, save_user


def test_admin_role_and_pending_user():
    df = load_users()
    admin = df[df['username'].astype(str).str.strip().str.lower() == 'edward']
    assert not admin.empty
    assert admin.iloc[0]['role'] == 'superadmin'

    save_user('testuser01', 'pass123', '628123456789', status='pending', role='user')
    df2 = load_users()
    pending = df2[df2['username'].astype(str).str.strip().str.lower() == 'testuser01']
    assert not pending.empty
    assert pending.iloc[0]['status'] == 'pending'
    assert pending.iloc[0]['role'] == 'user'


if __name__ == '__main__':
    test_admin_role_and_pending_user()
    print('admin flow test passed')
