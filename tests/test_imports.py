import app.dashboard.main as dashboard
import app.generator.main as generator
import app.receiver.main as receiver


def test_import_generator():
    assert generator is not None


def test_import_receiver():
    assert receiver is not None


def test_import_dashboard():
    assert dashboard is not None
