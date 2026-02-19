from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

# 记录应用启动时间
app_start_time = datetime.now()

# 创建健康检测路由器
health_router = APIRouter()

# 健康检测响应模型
class HealthCheckResponse(BaseModel):
    status: str
    uptime: dict
    timestamp: str

# 健康检测端点
@health_router.get("", response_model=HealthCheckResponse)
async def health_check():
    """健康检测端点，返回项目状态和运行时间"""
    # 计算运行时间
    current_time = datetime.now()
    uptime = current_time - app_start_time
    
    # 格式化运行时间
    uptime_dict = {
        "total_seconds": uptime.total_seconds(),
        "days": uptime.days,
        "hours": uptime.seconds // 3600,
        "minutes": (uptime.seconds % 3600) // 60,
        "seconds": uptime.seconds % 60,
        "formatted": f"{uptime.days}d {uptime.seconds // 3600}h {(uptime.seconds % 3600) // 60}m {uptime.seconds % 60}s"
    }
    
    return {
        "status": "healthy",
        "uptime": uptime_dict,
        "timestamp": current_time.isoformat()
    }