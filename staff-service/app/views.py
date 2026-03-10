from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Staff
from .serializers import StaffSerializer
import requests

BOOK_SERVICE_URL = "http://book-service:8000"

# API 1: Đăng ký nhân viên mới
class StaffRegister(APIView):
    def post(self, request):
        serializer = StaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

# API 2: Nhân viên nhập sách vào kho
class ManageBookViaStaff(APIView):
    def post(self, request):
        staff_id = request.data.get("staff_id")
        book_data = request.data.get("book_data") # Cục dữ liệu sách (title, author...)

        # 1. Kiểm tra xem có đúng là nhân viên không?
        try:
            staff = Staff.objects.get(id=staff_id)
        except Staff.DoesNotExist:
            return Response({"error": "Cảnh báo xâm nhập: Bạn không phải nhân viên!"}, status=403)

        # 2. Nếu đúng nhân viên, gọi sang Book Service để nhập sách
        res = requests.post(f"{BOOK_SERVICE_URL}/books/", json=book_data)
        
        if res.status_code == 200 or res.status_code == 201:
            return Response({
                "message": f"Sếp {staff.name} đã thêm sách thành công!",
                "book": res.json()
            })
        return Response({"error": "Lỗi khi thêm sách vào kho"}, status=res.status_code)