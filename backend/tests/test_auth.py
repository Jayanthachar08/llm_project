def test_register_and_login(client):
    # 1. Register student
    reg_response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Student",
            "email": "jane@campus.edu",
            "password": "securepassword123"
        }
    )
    assert reg_response.status_code == 201
    reg_data = reg_response.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["email"] == "jane@campus.edu"

    token = reg_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get profile
    me_response = client.get("/api/auth/me", headers=headers)
    assert me_response.status_code == 200
    assert me_response.json()["name"] == "Jane Student"

    # 3. Duplicate email registration fails
    dup_response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Duplicate",
            "email": "jane@campus.edu",
            "password": "anotherpassword"
        }
    )
    assert dup_response.status_code == 400

    # 4. Login with correct credentials
    login_response = client.post(
        "/api/auth/login",
        json={
            "email": "jane@campus.edu",
            "password": "securepassword123"
        }
    )
    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    # 5. Login with invalid password fails
    wrong_login = client.post(
        "/api/auth/login",
        json={
            "email": "jane@campus.edu",
            "password": "wrongpassword"
        }
    )
    assert wrong_login.status_code == 401
