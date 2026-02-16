import pytest
from fastapi.testclient import TestClient
from main import app
from models import User
from db import get_session
import json
from sqlmodel import Session, select

@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

def test_user_registration_flow_integration(client):
    """Integration test for the complete user registration flow"""

    # Clean up any existing test user
    with get_session() as session:
        existing_user = session.exec(select(User).where(User.email == "integration_test@example.com")).first()
        if existing_user:
            session.delete(existing_user)
            session.commit()

    # Step 1: Register a new user
    registration_response = client.post("/auth/register", json={
        "email": "integration_test@example.com",
        "password": "SecurePassword123!"
    })

    # Verify registration was successful
    assert registration_response.status_code == 200
    reg_data = registration_response.json()
    assert "access_token" in reg_data
    assert reg_data["token_type"] == "bearer"

    # Step 2: Verify user was created in the database
    with get_session() as session:
        created_user = session.exec(
            select(User).where(User.email == "integration_test@example.com")
        ).first()
        assert created_user is not None
        assert created_user.email == "integration_test@example.com"
        # Verify password is hashed (not stored in plain text)
        assert created_user.hashed_password != "SecurePassword123!"

    # Step 3: Use the token to access protected endpoint
    headers = {"Authorization": f"Bearer {reg_data['access_token']}"}
    protected_response = client.get("/auth/me", headers=headers)
    assert protected_response.status_code == 200

    user_data = protected_response.json()
    assert user_data["email"] == "integration_test@example.com"

def test_user_login_flow_integration(client):
    """Integration test for the complete user login flow"""

    # First, ensure user exists (register if not)
    test_email = "login_test@example.com"
    test_password = "AnotherSecurePassword123!"

    # Clean up any existing test user
    with get_session() as session:
        existing_user = session.exec(select(User).where(User.email == test_email)).first()
        if existing_user:
            session.delete(existing_user)
            session.commit()

    # Register the user
    register_response = client.post("/auth/register", json={
        "email": test_email,
        "password": test_password
    })
    assert register_response.status_code == 200

    # Now try to login with the registered user
    login_response = client.post("/auth/login", json={
        "email": test_email,
        "password": test_password
    })

    # Verify login was successful
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    # Verify the token works for protected endpoints
    headers = {"Authorization": f"Bearer {login_data['access_token']}"}
    protected_response = client.get("/auth/me", headers=headers)
    assert protected_response.status_code == 200

    user_data = protected_response.json()
    assert user_data["email"] == test_email

def test_invalid_credentials_login_fails(client):
    """Test that login with invalid credentials fails appropriately"""

    # Try to login with non-existent user
    invalid_login_response = client.post("/auth/login", json={
        "email": "nonexistent@example.com",
        "password": "wrongpassword"
    })

    assert invalid_login_response.status_code == 401

    # Try to login with wrong password for existing user
    # First create a user
    test_email = "wrongpass_test@example.com"
    test_password = "CorrectPassword123!"

    # Clean up any existing test user
    with get_session() as session:
        existing_user = session.exec(select(User).where(User.email == test_email)).first()
        if existing_user:
            session.delete(existing_user)
            session.commit()

    register_response = client.post("/auth/register", json={
        "email": test_email,
        "password": test_password
    })
    assert register_response.status_code == 200

    # Now try to login with wrong password
    wrong_pass_response = client.post("/auth/login", json={
        "email": test_email,
        "password": "wrongpassword"
    })

    assert wrong_pass_response.status_code == 401