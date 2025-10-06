from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import never_cache
from django.db import connections
from django.core.cache import cache
import json


@csrf_exempt
@never_cache
def health_check(request):
    """
    Health check endpoint for Docker containers and load balancers.
    Returns JSON with application health status.
    """
    health_data = {
        'status': 'healthy',
        'timestamp': None,
        'checks': {
            'database': 'unknown',
            'cache': 'unknown',
            'application': 'healthy'
        }
    }
    
    try:
        from django.utils import timezone
        health_data['timestamp'] = timezone.now().isoformat()
        
        # Check database connection
        try:
            db_conn = connections['default']
            db_conn.cursor().execute('SELECT 1')
            health_data['checks']['database'] = 'healthy'
        except Exception as e:
            health_data['checks']['database'] = f'unhealthy: {str(e)}'
            health_data['status'] = 'unhealthy'
        
        # Check cache connection
        try:
            cache.set('health_check', 'ok', 30)
            if cache.get('health_check') == 'ok':
                health_data['checks']['cache'] = 'healthy'
            else:
                health_data['checks']['cache'] = 'unhealthy: cache test failed'
        except Exception as e:
            health_data['checks']['cache'] = f'unhealthy: {str(e)}'
        
    except Exception as e:
        health_data['status'] = 'unhealthy'
        health_data['error'] = str(e)
    
    status_code = 200 if health_data['status'] == 'healthy' else 503
    
    return JsonResponse(health_data, status=status_code)