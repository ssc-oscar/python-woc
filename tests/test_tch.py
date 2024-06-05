import pytest

# Import the TCHashDB class
from woc.tch import TCHashDB

@pytest.fixture
def db(tmp_path):
    """Fixture to create and return a TCHashDB instance"""
    path = tmp_path / "test_db.tch"
    db = TCHashDB(path=bytes(str(path), 'utf-8'))
    yield db

def test_put_and_get(db):
    key = b'key1'
    value = b'value1'
    db.put(key, value)
    assert db.get(key) == value

def test_get_nonexistent_key(db):
    with pytest.raises(KeyError):
        db.get(b'nonexistent_key')

def test_delete(db):
    key = b'key2'
    value = b'value2'
    db.put(key, value)
    db.delete(key)
    with pytest.raises(KeyError):
        db.get(key)

def test_drop(db):
    db.put(b'key3', b'value3')
    db.put(b'key4', b'value4')
    db.drop()
    assert len(db) == 0

def test_len(db):
    db.put(b'key5', b'value5')
    db.put(b'key6', b'value6')
    assert len(db) == 2

def test_iter(db):
    keys = [b'key7', b'key8', b'key9']
    for key in keys:
        db.put(key, b'value')
    assert set(db) == set(keys)

def test_getitem(db):
    key = b'key10'
    value = b'value10'
    db[key] = value
    assert db[key] == value

def test_setitem(db):
    key = b'key11'
    value = b'value11'
    db[key] = value
    assert db.get(key) == value

def test_delitem(db):
    key = b'key12'
    value = b'value12'
    db[key] = value
    del db[key]
    with pytest.raises(KeyError):
        db.get(key)