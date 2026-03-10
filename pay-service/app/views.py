from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer

class ProcessPayment(APIView):
    def post(self, request):
        order_id = request.data.get("order_id")
        amount = request.data.get("amount")
        
        if not order_id or not amount:
            return Response({"error": "Thiếu thông tin order_id hoặc amount"}, status=400)
        
        # Lưu vào DB để làm bằng chứng đã thu tiền
        payment = Payment.objects.create(order_id=order_id, amount=amount, status='SUCCESS')
        
        serializer = PaymentSerializer(payment)
        return Response({
            "message": "Ting ting! Đã trừ tiền thành công!",
            "payment": serializer.data
        })

from rest_framework.views import APIView
from rest_framework.response import Response
from .models import PaymentMethod

class PaymentMethodList(APIView):
    def get(self, request):
        # 🌟 TỰ ĐẺ DATA THANH TOÁN
        if not PaymentMethod.objects.exists():
            PaymentMethod.objects.create(name="Thanh toán khi nhận hàng (COD)", code="COD")
            PaymentMethod.objects.create(name="Chuyển khoản / Thẻ tín dụng", code="CREDIT_CARD")
            
        methods = PaymentMethod.objects.all().values()
        return Response(list(methods))