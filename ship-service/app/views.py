from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Shipment, ShippingMethod
from .serializers import ShipmentSerializer

class ShipOrder(APIView):
    def post(self, request):
        order_id = request.data.get("order_id")
        
        if not order_id:
            return Response({"error": "Thiếu mã đơn hàng (order_id)"}, status=400)
        
        # Tạo vận đơn mới cho Đơn hàng
        shipment = Shipment.objects.create(order_id=order_id, status='PREPARING')
        
        serializer = ShipmentSerializer(shipment)
        return Response({
            "message": "Đã tạo mã vận đơn! Hàng đang được đóng gói xuất kho.",
            "shipment": serializer.data
        })

class ShippingMethodList(APIView):
    def get(self, request):
        # 🌟 BÍ KÍP TỰ ĐẺ DATA: Nếu bảng trống, tự động tạo 2 loại Ship!
        if not ShippingMethod.objects.exists():
            ShippingMethod.objects.create(name="Giao hàng tiêu chuẩn", fee=2.0, description="Nhận hàng trong 3-5 ngày")
            ShippingMethod.objects.create(name="Giao hàng Hỏa tốc", fee=5.0, description="Nhận hàng trong 24h")
            
        methods = ShippingMethod.objects.all().values()
        return Response(list(methods))