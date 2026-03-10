from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Order, OrderItem
from .serializers import OrderSerializer
import requests

CART_SERVICE_URL = "http://cart-service:8000"
BOOK_SERVICE_URL = "http://book-service:8000"
PAY_SERVICE_URL = "http://pay-service:8000"
SHIP_SERVICE_URL = "http://ship-service:8000"

# Lưu ý: Nhớ đổi tên class thành CreateOrder nếu urls.py của ông đang dùng tên này (hoặc OrderCreate tùy ông nhé)
class CreateOrder(APIView):
    # API xem danh sách đơn hàng cho Sếp
    def get(self, request):
        orders = Order.objects.all()
        return Response(OrderSerializer(orders, many=True).data)

    def post(self, request):
        data = request.data
        customer_id = data.get("customer_id")
        address = data.get("address")
        ship_id = data.get("shipping_method_id")
        pay_id = data.get("payment_method_id")

        # Rào chắn bảo vệ: Thiếu data là đuổi về luôn
        if not all([customer_id, address, ship_id, pay_id]):
            return Response({"error": "Thiếu thông tin nhận hàng hoặc phương thức thanh toán!"}, status=400)

        # 1. Gọi sang Cart Service để check giỏ hàng
        try:
            cart_res = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
            if cart_res.status_code != 200:
                return Response({"error": "Không lấy được giỏ hàng!"}, status=400)
            cart_items = cart_res.json()
            if not cart_items:
                return Response({"error": "Giỏ hàng rỗng!"}, status=400)
        except Exception:
            return Response({"error": "Cart Service sập nguồn!"}, status=500)

        # 2. Tạo Đơn hàng Nháp (Lưu kèm ĐỊA CHỈ và CÁCH SHIP/PAY)
        order = Order.objects.create(
            customer_id=customer_id, 
            status='PENDING', 
            total_price=0,
            address=address,
            shipping_method_id=ship_id,
            payment_method_id=pay_id
        )
        total_price = 0

        # ==========================================
        # 🔴 VÁ LỖI Ở ĐÂY: PHẢI SANG BOOK SERVICE ĐỂ XEM GIÁ SÁCH
        # ==========================================
        try:
            books_res = requests.get(f"{BOOK_SERVICE_URL}/books/")
            books = {str(b['id']): b for b in books_res.json()}
        except:
            books = {}

        # 3. Tính tiền sách, Lưu chi tiết đơn và Xóa giỏ hàng
        for item in cart_items:
            book_id = str(item['book_id'])
            qty = int(item.get('quantity', 1))
            
            book_info = books.get(book_id, {})
            price = float(book_info.get('price', 0)) 
            
            total_price += price * qty
            
            OrderItem.objects.create(
                order=order, 
                book_id=item['book_id'], 
                quantity=qty, 
                price=price
            )
            
            item_id = item.get('item_id') or item.get('id')
            try:
                requests.delete(f"{CART_SERVICE_URL}/cart-items/{item_id}/")
            except:
                pass

        # ==========================================
        # 🔴 VÁ LỖI THIẾU TIỀN SHIP: Sang nhà Ship hỏi giá
        # ==========================================
        ship_fee = 0
        try:
            ship_methods_res = requests.get(f"{SHIP_SERVICE_URL}/shipping-methods/")
            if ship_methods_res.status_code == 200:
                # Lục tìm đúng cái gói Ship mà khách chọn để lấy giá tiền
                for method in ship_methods_res.json():
                    if str(method['id']) == str(ship_id):
                        ship_fee = float(method['fee'])
                        break
        except Exception as e:
            print("Lỗi lấy giá Ship:", e)

        # Cập nhật lại tổng tiền CHUẨN (Tiền sách + Tiền ship)
        order.total_price = total_price + ship_fee
        order.save()

        # =========================================================
        # 4. KÍCH HOẠT THANH TOÁN & VẬN CHUYỂN
        # =========================================================
        # (Phần gọi PAY và SHIP bên dưới giữ nguyên)
        # =========================================================
        # 4. KÍCH HOẠT THANH TOÁN & VẬN CHUYỂN
        # =========================================================
        
        # Gọi Payment Service
        try:
            pay_res = requests.post(f"{PAY_SERVICE_URL}/payments/", json={
                "order_id": order.id,
                "payment_method_id": pay_id,
                "amount": float(total_price)
            })
            pay_data = pay_res.json() if pay_res.status_code in [200, 201] else {"error": "Lỗi thanh toán"}
        except:
            pay_data = {"error": "Pay Service không phản hồi"}

        # Gọi Shipping Service
        try:
            ship_res = requests.post(f"{SHIP_SERVICE_URL}/shippings/", json={
                "order_id": order.id,
                "shipping_method_id": ship_id,
                "address": address
            })
            ship_data = ship_res.json() if ship_res.status_code in [200, 201] else {"error": "Lỗi giao hàng"}
        except:
            ship_data = {"error": "Ship Service không phản hồi"}

        # 5. Cập nhật trạng thái chốt hạ
        if "error" not in pay_data and "error" not in ship_data:
            order.status = 'PAID_AND_SHIPPING'
            order.save()
            msg = "🎉 Chốt đơn thành công! Đã lên đơn giao hàng."
        else:
            msg = "⚠️ Đơn hàng đã ghi nhận nhưng có lỗi khi gọi Pay/Ship!"

        return Response({
            "message": msg,
            "order_id": order.id,
            "payment_details": pay_data,
            "shipping_details": ship_data
        }, status=201)


class UpdateOrderStatus(APIView):
    """PATCH /orders/<id>/status/ — Nhân viên duyệt hoặc hủy đơn hàng"""

    ALLOWED_STATUSES = ['APPROVED', 'CANCELLED', 'DELIVERED', 'PENDING', 'PAID_AND_SHIPPING']

    def patch(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({"error": f"Đơn hàng #{pk} không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        if not new_status:
            return Response({"error": "Thiếu trường 'status'!"}, status=status.HTTP_400_BAD_REQUEST)

        if new_status not in self.ALLOWED_STATUSES:
            return Response(
                {"error": f"Trạng thái '{new_status}' không hợp lệ. Chỉ chấp nhận: {self.ALLOWED_STATUSES}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = order.status
        order.status = new_status
        order.save()

        return Response({
            "message": f"Đơn #{pk} đã được cập nhật: {old_status} → {new_status}",
            "order": OrderSerializer(order).data
        })