import pytest
from app.udp.manager import UDPManager

@pytest.fixture
def udp_manager():
    return UDPManager()

@pytest.mark.asyncio
async def test_start_and_stop_udp_server(udp_manager):
    response = await udp_manager.start_udp_server(1, '127.0.0.1', 10000, lambda x: x)
    assert response["status"] == "已启动服务器 1 在 127.0.0.1:10000"
    
    stop_response = await udp_manager.stop_udp_server(1, 10000)
    assert stop_response["status"] == "已停止服务器 1 在端口 10000"