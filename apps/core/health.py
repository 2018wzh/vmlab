"""
健康检查视图
用于Docker容器健康监控
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

def health_check(request):
    """
    系统健康检查端点
    检查数据库连接、缓存等关键组件
    """
    status = {
        'status': 'healthy',
        'components': {}
    }
    
    overall_healthy = True
    
    # 检查数据库连接
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['components']['database'] = 'healthy'
    except Exception as e:
        status['components']['database'] = f'unhealthy: {str(e)}'
        overall_healthy = False
        logger.error(f"Database health check failed: {e}")
    
    # 检查Redis缓存
    try:
        cache.set('health_check', 'test', 30)
        if cache.get('health_check') == 'test':
            status['components']['cache'] = 'healthy'
        else:
            status['components']['cache'] = 'unhealthy: cache test failed'
            overall_healthy = False
    except Exception as e:
        status['components']['cache'] = f'unhealthy: {str(e)}'
        overall_healthy = False
        logger.error(f"Cache health check failed: {e}")
    
    # 检查libvirt连接（可选）
    try:
        from apps.vms.libvirt_manager import LibvirtManager
        manager = LibvirtManager()
        if manager.is_connected():
            status['components']['libvirt'] = 'healthy'
        else:
            status['components']['libvirt'] = 'unhealthy: not connected'
            # libvirt连接失败不影响整体健康状态，因为可能在开发环境中没有libvirt
    except Exception as e:
        status['components']['libvirt'] = f'unhealthy: {str(e)}'
        logger.warning(f"Libvirt health check failed: {e}")
    
    if not overall_healthy:
        status['status'] = 'unhealthy'
        return JsonResponse(status, status=503)
    
    return JsonResponse(status)
