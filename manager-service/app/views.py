from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RevenueReport
from .serializers import ReportSerializer
import requests

ORDER_SERVICE_URL = "http://order-service:8000"

class GenerateReport(APIView):
    def post(self, request):
        # 1. Gọi điện sang Order Service xin danh sách hóa đơn
        try:
            res = requests.get(f"{ORDER_SERVICE_URL}/orders/")
            if res.status_code != 200:
                return Response({"error": "Không kết nối được kho dữ liệu Order!"}, status=500)
            
            orders = res.json()
        except Exception:
            return Response({"error": "Order Service đang sập!"}, status=500)

        # 2. Ngồi tính nhẩm: Lọc ra các đơn đã thanh toán thành công
        successful_orders = [o for o in orders if o['status'] == 'PAID_AND_SHIPPING']
        
        total_orders = len(successful_orders)
        # Cộng dồn tiền (chuyển đổi string sang float để cộng cho an toàn)
        total_revenue = sum(float(o['total_price']) for o in successful_orders)

        # 3. Tạo bản báo cáo cất vào Database của Manager
        report = RevenueReport.objects.create(
            report_name="Báo cáo Doanh thu Tự động",
            total_orders=total_orders,
            total_revenue=total_revenue
        )

        serializer = ReportSerializer(report)
        return Response({
            "message": "Sếp ơi, báo cáo đã sẵn sàng!",
            "data": serializer.data
        })