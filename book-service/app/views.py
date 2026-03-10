from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

class BookListCreate(APIView):
    def get(self, request):
        # Lắng nghe xem người ta có muốn lọc theo category không
        cat_id = request.query_params.get('category_id')
        
        if cat_id:
            # Nếu có, chỉ lấy sách thuộc thể loại đó
            books = Book.objects.filter(category_id=cat_id)
        else:
            # Nếu không, lấy hết
            books = Book.objects.all()
            
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetail(APIView):
    """GET / PUT / DELETE cho 1 cuốn sách theo ID"""

    def get_object(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return None

    def get(self, request, pk):
        book = self.get_object(pk)
        if not book:
            return Response({"error": "Sách không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)
        return Response(BookSerializer(book).data)

    def put(self, request, pk):
        book = self.get_object(pk)
        if not book:
            return Response({"error": "Sách không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BookSerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        book = self.get_object(pk)
        if not book:
            return Response({"error": "Sách không tồn tại!"}, status=status.HTTP_404_NOT_FOUND)
        book.delete()
        return Response({"message": f"Đã xóa sách #{pk} khỏi kho!"}, status=status.HTTP_200_OK)