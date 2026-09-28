import pytest
from backend.app import create_app, db
from backend.app.models import Platform, Setting, User
from backend.app.utils.phone import normalize_phone

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_phone_normalization():
    assert normalize_phone("0202979378") == "+233202979378"
    assert normalize_phone("+233202979378") == "+233202979378"
    assert normalize_phone("233202979378") == "+233202979378"
    assert normalize_phone(" 0244 123 456 ") == "+233244123456"
    assert normalize_phone(None) is None

def test_database_seeding(app):
    runner = app.test_cli_runner()
    result = runner.invoke(args=["seed"])
    assert result.exit_code == 0
    assert "Seeding complete!" in result.output
    
    with app.app_context():
        assert Platform.query.count() == 5
        platforms = [p.name for p in Platform.query.all()]
        assert "TikTok" in platforms
        assert "Instagram" in platforms
        assert "Facebook" in platforms
        assert "X" in platforms
        assert "Telegram" in platforms
        
        # Check default settings
        payment_num = Setting.query.filter_by(key="payment_number").first()
        assert payment_num is not None
        assert payment_num.value == "0202979378"
