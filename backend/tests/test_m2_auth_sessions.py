import pytest
from backend.app import create_app, db
from backend.app.models import User, UserRole, UserStatus, Order, Payment, LedgerTransaction

@pytest.fixture
def app():
    import os
    db_path = os.path.join(os.path.dirname(__file__), "test_m2.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
        "SECRET_KEY": "test-secret-key"
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

@pytest.fixture
def client(app):
    return app.test_client()

def test_guest_session(client):
    res = client.post("/api/session")
    assert res.status_code == 200
    data = res.get_json()
    assert "csrf_token" in data
    assert data["is_guest"] is True
    assert "boostx_guest" in res.headers.get("Set-Cookie", "")

def test_customer_registration_and_login(client):
    # Register customer
    res = client.post("/api/auth/register", json={
        "full_name": "Joseph Asare",
        "identifier": "0244123456",
        "password": "Password123!"
    })
    assert res.status_code == 211 or res.status_code == 201
    data = res.get_json()
    assert data["redirect_path"] == "/account/orders"
    assert "csrf_token" in data

    # Check /api/auth/me
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 200
    me_data = res_me.get_json()
    assert me_data["authenticated"] is True
    assert me_data["role"] == "customer"
    assert me_data["phone"] == "+233244123456"

def test_generic_login_error(client, app):
    # Create user
    with app.app_context():
        runner = app.test_cli_runner()
        runner.invoke(args=["seed"])

    # Wrong password
    res1 = client.post("/api/auth/login", json={
        "identifier": "admin@boostx.com",
        "password": "WrongPassword!"
    })
    assert res1.status_code == 401
    assert res1.get_json()["error"] == "Incorrect email/phone or password."

    # Non-existent user
    res2 = client.post("/api/auth/login", json={
        "identifier": "nonexistent@boostx.com",
        "password": "WrongPassword!"
    })
    assert res2.status_code == 401
    assert res2.get_json()["error"] == "Incorrect email/phone or password."

def test_admin_login_redirect(client, app):
    with app.app_context():
        runner = app.test_cli_runner()
        runner.invoke(args=["seed"])

    res = client.post("/api/auth/login", json={
        "identifier": "admin@boostx.com",
        "password": "AdminPass123!"
    })
    assert res.status_code == 200
    assert res.get_json()["redirect_path"] == "/admin"

def test_guest_session_claiming(client, app):
    # Establish guest session
    res_sess = client.post("/api/session")
    csrf_token = res_sess.get_json()["csrf_token"]
    headers = {"X-CSRF-Token": csrf_token}

    from backend.app.auth.session import hash_token
    guest_cookie = res_sess.headers["Set-Cookie"].split(";")[0].split("=")[1]
    guest_hash = hash_token(guest_cookie)

    # Insert a guest order and payment
    with app.app_context():
        order = Order(
            public_order_id="BX-ORD-GUEST1",
            session_id=guest_hash,
            platform="Instagram",
            service_id=1,
            service_name="Instagram Followers",
            target="https://instagram.com/test",
            quantity=1000,
            charge_ghs=20.00,
            status="Pending"
        )
        db.session.add(order)
        db.session.commit()

    # Register as customer with same guest session cookie
    res_reg = client.post("/api/auth/register", json={
        "full_name": "Joseph Asare",
        "identifier": "joseph@example.com",
        "password": "Password123!"
    }, headers=headers)
    assert res_reg.status_code == 201
    assert res_reg.get_json()["orders_claimed"] == 1

    # Verify order user_id is updated
    with app.app_context():
        claimed_order = Order.query.filter_by(public_order_id="BX-ORD-GUEST1").first()
        assert claimed_order.user_id is not None
