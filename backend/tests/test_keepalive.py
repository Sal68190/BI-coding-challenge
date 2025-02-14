import pytest
from unittest.mock import Mock, patch
from ..utils.keepalive import KeepAliveSystem

def test_keepalive_initialization():
    keepalive = KeepAliveSystem("http://test.com")
    assert not keepalive.running
    assert keepalive.interval == 840

@patch('requests.get')
def test_keepalive_ping(mock_get):
    mock_get.return_value = Mock(status_code=200)
    keepalive = KeepAliveSystem("http://test.com")
    keepalive._ping()
    mock_get.assert_called_once_with("http://test.com/api/health")
