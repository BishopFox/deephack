import vulnserver.lib
import vulnserver.lib.models
from vulnserver.lib.models import SchemaGen

def test_func():
    s = SchemaGen()
    s.gen()
    s.populate()
    assert True
