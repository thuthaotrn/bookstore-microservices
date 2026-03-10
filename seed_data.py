"""
================================================================
  BOOKSTORE MICROSERVICE - SCRIPT SEED DỮ LIỆU TỔNG HỢP v2.0
================================================================

Cách chạy:
  pip install requests
  python seed_data.py

Yêu cầu:
  - Hệ thống phải đang chạy: docker-compose up -d
  - Chờ ~10s cho các service khởi động trước khi chạy script

Dữ liệu sẽ được seed:
  ✅ 8 Thể loại sách (catalog-service)
  ✅ 27 Sách với ảnh bìa thật (book-service)
  ✅ 8 Khách hàng (customer-service)
  ✅ 4 Nhân viên (staff-service) 
  ✅ 30+ Đánh giá sách ← THỨC ĂN CHO AI! (comment-rate-service)
  ℹ️  Payment/Shipping Methods: Các service tự seed khi có GET request
  ℹ️  Orders: Phải tạo qua flow Cart → Order thật (xem ghi chú cuối)
"""

import requests
import sys
import time
import json

# ==========================================================
# CONFIG
# ==========================================================
BASE = "http://localhost"
SERVICES = {
    "catalog":     f"{BASE}:8006",
    "book":        f"{BASE}:8002",
    "customer":    f"{BASE}:8001",
    "staff":       f"{BASE}:8004",
    "pay":         f"{BASE}:8009",
    "ship":        f"{BASE}:8008",
    "order":       f"{BASE}:8007",
    "comment":     f"{BASE}:8010",
    "recommender": f"{BASE}:8011",
    "manager":     f"{BASE}:8005",
}

# ==========================================================
# HELPERS
# ==========================================================
BOLD   = "\033[1m"
GREEN  = "\033[92m"
RED    = "\033[91m"
CYAN   = "\033[96m"
YELLOW = "\033[93m"
GRAY   = "\033[90m"
RESET  = "\033[0m"

created_ids = {}  # Track all created IDs

def section(title):
    print(f"\n{BOLD}{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{CYAN}{'='*60}{RESET}")

def extract_id(result):
    """
    Tự động tìm 'id' trong response dù service trả về format nào:
    - Trực tiếp:    {"id": 1, "name": ...}                → 1
    - Bọc envelope: {"message": "...", "category": {"id": 1}} → 1
    - Bọc envelope: {"message": "...", "review": {"id": 1}}   → 1
    """
    if not isinstance(result, dict):
        return None
    # Thử lấy trực tiếp
    if 'id' in result:
        return result['id']
    # Tìm ở một level sâu hơn (envelope)
    for val in result.values():
        if isinstance(val, dict) and 'id' in val:
            return val['id']
    return None

def extract_data(result):
    """
    Lấy object thật (có id) từ response dù là envelope hay direct.
    """
    if not isinstance(result, dict):
        return result
    if 'id' in result:
        return result
    for val in result.values():
        if isinstance(val, dict) and 'id' in val:
            return val
    return result

def post(service_name, path, data, label=""):
    url = f"{SERVICES[service_name]}{path}"
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code in (200, 201):
            result = r.json()
            item_id = extract_id(result) or '?'
            display = label or str(data.get('name') or data.get('title') or data.get('email') or item_id)
            print(f"  {GREEN}✅ [{service_name.upper()}] {display} (ID={item_id}){RESET}")
            return result
        else:
            display = label or path
            print(f"  {RED}❌ [{service_name.upper()}] {display} → HTTP {r.status_code}: {r.text[:100]}{RESET}")
            return None
    except requests.exceptions.ConnectionError:
        print(f"  {RED}💀 [{service_name.upper()}] OFFLINE! Kiểm tra docker-compose up{RESET}")
        return None
    except Exception as e:
        print(f"  {RED}⚠️  [{service_name.upper()}] Lỗi: {str(e)[:80]}{RESET}")
        return None

def get_list(service_name, path):
    url = f"{SERVICES[service_name]}{path}"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def delete_item(service_name, path, item_id):
    url = f"{SERVICES[service_name]}{path}{item_id}/"
    try:
        r = requests.delete(url, timeout=5)
        return r.status_code in (200, 204)
    except:
        return False

def clear_service(service_name, list_path, delete_path=None):
    """Xoá tất cả items trong một service"""
    items = get_list(service_name, list_path)
    if not isinstance(items, list) or not items:
        return 0
    
    delete_path = delete_path or list_path
    count = 0
    for item in items:
        item_id = item.get('id')
        if item_id and delete_item(service_name, delete_path, item_id):
            count += 1
    
    if count:
        print(f"  {YELLOW}🗑️  [{service_name.upper()}] Đã xoá {count} bản ghi cũ{RESET}")
    return count

# ==========================================================
# BƯỚC 1: XOÁ DỮ LIỆU CŨ
# ==========================================================
def clear_old_data():
    section("BƯỚC 1: DỌN DẸP DATABASE CŨ")
    print(f"  {YELLOW}Đang dọn dẹp...{RESET}")
    
    # Xoá theo thứ tự: phụ trước, chính sau
    clear_service("comment",  "/reviews/")
    clear_service("book",     "/books/")
    clear_service("catalog",  "/categories/")
    clear_service("customer", "/customers/")
    clear_service("staff",    "/staffs/")
    
    print(f"  {GREEN}✅ Đã dọn dẹp xong!{RESET}")

# ==========================================================
# BƯỚC 2: SEED CATEGORIES
# ==========================================================
def seed_categories():
    section("BƯỚC 2: THỂ LOẠI SÁCH (catalog-service :8006)")
    
    cat_data = [
        # (tên, mô tả)
        ("Văn học trong nước",  "Tiểu thuyết, truyện ngắn, thơ của tác giả Việt Nam"),
        ("Văn học nước ngoài",  "Tuyển tập danh tác thế giới dịch sang tiếng Việt"),
        ("Khoa học - Công nghệ","Lập trình, AI, khoa học dữ liệu và công nghệ hiện đại"),
        ("Kinh tế - Kinh doanh","Quản lý tài chính, khởi nghiệp, đầu tư và kinh doanh"),
        ("Kỹ năng sống",        "Phát triển bản thân, tư duy tích cực và kỹ năng mềm"),
        ("Tâm lý học",          "Khám phá tâm trí con người, hành vi và cảm xúc"),
        ("Lịch sử - Địa lý",    "Lịch sử văn minh nhân loại, lịch sử Việt Nam và địa lý"),
        ("Thiếu nhi",           "Sách giáo dục, giải trí và phát triển trí tuệ cho trẻ em"),
    ]
    
    cat_ids = {}
    for (name, desc) in cat_data:
        result = post("catalog", "/categories/", {"name": name, "description": desc})
        if result:
            item_id = extract_id(result)
            if item_id:
                cat_ids[name] = item_id
            else:
                print(f"  {YELLOW}⚠️  Không lấy được ID từ response: {str(result)[:100]}{RESET}")
    
    print(f"\n  📚 Đã tạo {len(cat_ids)}/{len(cat_data)} thể loại")
    return cat_ids

# ==========================================================
# BƯỚC 3: SEED BOOKS với ảnh bìa thật
# ==========================================================
def seed_books(cat_ids):
    section("BƯỚC 3: SÁCH VỚI ẢNH BÌA THẬT (book-service :8002)")
    print(f"  {GRAY}💡 Ảnh từ Open Library Covers API (openlibrary.org){RESET}")
    
    def cat(name):
        return cat_ids.get(name)
    
    # Ảnh bìa sách thật từ Open Library: https://covers.openlibrary.org/b/isbn/{ISBN}-L.jpg
    # Backup: Google Books API thumbnails
    books = [
        # =================== VĂN HỌC TRONG NƯỚC ===================
        {
            "title": "Số Đỏ",
            "author": "Vũ Trọng Phụng",
            "price": 55000, "stock": 80,
            "category_id": cat("Văn học trong nước"),
            "image_url": "https://salt.tikicdn.com/ts/product/ef/53/aa/680db45e7d4a2e5f09a3d4c9df62d8b3.jpg"
        },
        {
            "title": "Tắt Đèn",
            "author": "Ngô Tất Tố",
            "price": 48000, "stock": 65,
            "category_id": cat("Văn học trong nước"),
            "image_url": "https://salt.tikicdn.com/ts/product/f4/b5/65/97e1e8de2e0bec1ce31ace05f4bc48ec.jpg"
        },
        {
            "title": "Dế Mèn Phiêu Lưu Ký",
            "author": "Tô Hoài",
            "price": 45000, "stock": 120,
            "category_id": cat("Văn học trong nước"),
            "image_url": "https://salt.tikicdn.com/ts/product/59/e8/0b/e9c3b52a8a0f4a4827ae99e17f3b49c0.jpg"
        },
        {
            "title": "Chí Phèo",
            "author": "Nam Cao",
            "price": 52000, "stock": 90,
            "category_id": cat("Văn học trong nước"),
            "image_url": "https://salt.tikicdn.com/ts/product/a3/e7/84/09bcc9234a0d8e2fc3d52f7e81a87b64.jpg"
        },

        # =================== VĂN HỌC NƯỚC NGOÀI ===================
        {
            "title": "Nhà Giả Kim (The Alchemist)",
            "author": "Paulo Coelho",
            "price": 79000, "stock": 95,
            "category_id": cat("Văn học nước ngoài"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780062315007-L.jpg"
        },
        {
            "title": "Harry Potter và Hòn Đá Phù Thủy",
            "author": "J.K. Rowling",
            "price": 115000, "stock": 200,
            "category_id": cat("Văn học nước ngoài"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780439708180-L.jpg"
        },
        {
            "title": "Kiêu Hãnh và Định Kiến (Pride and Prejudice)",
            "author": "Jane Austen",
            "price": 92000, "stock": 45,
            "category_id": cat("Văn học nước ngoài"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg"
        },
        {
            "title": "Bố Già (The Godfather)",
            "author": "Mario Puzo",
            "price": 98000, "stock": 60,
            "category_id": cat("Văn học nước ngoài"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780451167712-L.jpg"
        },
        {
            "title": "Những Người Khốn Khổ (Les Misérables)",
            "author": "Victor Hugo",
            "price": 145000, "stock": 35,
            "category_id": cat("Văn học nước ngoài"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780140444308-L.jpg"
        },
        {
            "title": "1984",
            "author": "George Orwell",
            "price": 88000, "stock": 110,
            "category_id": cat("Văn học nước ngoài"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780451524935-L.jpg"
        },

        # =================== KHOA HỌC - CÔNG NGHỆ ===================
        {
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "price": 185000, "stock": 40,
            "category_id": cat("Khoa học - Công nghệ"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780132350884-L.jpg"
        },
        {
            "title": "Design Patterns - Gang of Four",
            "author": "Erich Gamma et al.",
            "price": 195000, "stock": 25,
            "category_id": cat("Khoa học - Công nghệ"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780201633610-L.jpg"
        },
        {
            "title": "Python Crash Course",
            "author": "Eric Matthes",
            "price": 195000, "stock": 70,
            "category_id": cat("Khoa học - Công nghệ"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9781593279288-L.jpg"
        },
        {
            "title": "AI Superpowers - Kỷ Nguyên AI",
            "author": "Kai-Fu Lee",
            "price": 128000, "stock": 55,
            "category_id": cat("Khoa học - Công nghệ"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9781328915542-L.jpg"
        },
        {
            "title": "The Pragmatic Programmer",
            "author": "David Thomas & Andrew Hunt",
            "price": 175000, "stock": 35,
            "category_id": cat("Khoa học - Công nghệ"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780135957059-L.jpg"
        },

        # =================== KINH TẾ - KINH DOANH ===================
        {
            "title": "Tư Duy Nhanh và Chậm (Thinking, Fast and Slow)",
            "author": "Daniel Kahneman",
            "price": 135000, "stock": 75,
            "category_id": cat("Kinh tế - Kinh doanh"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780374533557-L.jpg"
        },
        {
            "title": "Zero to One - Từ Không Đến Một",
            "author": "Peter Thiel",
            "price": 110000, "stock": 88,
            "category_id": cat("Kinh tế - Kinh doanh"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780804139021-L.jpg"
        },
        {
            "title": "Cha Giàu Cha Nghèo (Rich Dad Poor Dad)",
            "author": "Robert Kiyosaki",
            "price": 95000, "stock": 130,
            "category_id": cat("Kinh tế - Kinh doanh"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9781612680194-L.jpg"
        },

        # =================== KỸ NĂNG SỐNG ===================
        {
            "title": "Đắc Nhân Tâm (How to Win Friends and Influence People)",
            "author": "Dale Carnegie",
            "price": 88000, "stock": 150,
            "category_id": cat("Kỹ năng sống"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780671027032-L.jpg"
        },
        {
            "title": "7 Thói Quen Của Người Thành Đạt",
            "author": "Stephen R. Covey",
            "price": 118000, "stock": 160,
            "category_id": cat("Kỹ năng sống"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9781982137274-L.jpg"
        },
        {
            "title": "Nghĩ Giàu Làm Giàu (Think and Grow Rich)",
            "author": "Napoleon Hill",
            "price": 88000, "stock": 200,
            "category_id": cat("Kỹ năng sống"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9781585424337-L.jpg"
        },

        # =================== TÂM LÝ HỌC ===================
        {
            "title": "Atomic Habits - Thói Quen Nguyên Tử",
            "author": "James Clear",
            "price": 125000, "stock": 175,
            "category_id": cat("Tâm lý học"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780735211292-L.jpg"
        },
        {
            "title": "Đi Tìm Lẽ Sống (Man's Search for Meaning)",
            "author": "Viktor Frankl",
            "price": 79000, "stock": 85,
            "category_id": cat("Tâm lý học"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780807014295-L.jpg"
        },
        {
            "title": "Dám Bị Ghét (The Courage to be Disliked)",
            "author": "Ichiro Kishimi & Fumitake Koga",
            "price": 98000, "stock": 140,
            "category_id": cat("Tâm lý học"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9781501197277-L.jpg"
        },

        # =================== LỊCH SỬ - ĐỊA LÝ ===================
        {
            "title": "Sapiens: Lược Sử Loài Người",
            "author": "Yuval Noah Harari",
            "price": 165000, "stock": 120,
            "category_id": cat("Lịch sử - Địa lý"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780062316097-L.jpg"
        },
        {
            "title": "Homo Deus: Lược Sử Tương Lai",
            "author": "Yuval Noah Harari",
            "price": 155000, "stock": 95,
            "category_id": cat("Lịch sử - Địa lý"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780062464316-L.jpg"
        },

        # =================== THIẾU NHI ===================
        {
            "title": "Hoàng Tử Bé (The Little Prince)",
            "author": "Antoine de Saint-Exupéry",
            "price": 65000, "stock": 250,
            "category_id": cat("Thiếu nhi"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9780156013987-L.jpg"
        },
        {
            "title": "Truyện Cổ Grimm (Fairy Tales by Brothers Grimm)",
            "author": "Anh Em Nhà Grimm",
            "price": 75000, "stock": 180,
            "category_id": cat("Thiếu nhi"),
            "image_url": "https://covers.openlibrary.org/b/isbn/9781853261800-L.jpg"
        },
    ]
    
    book_ids = []
    for b in books:
        result = post("book", "/books/", b, label=b["title"])
        if result:
            item_id = extract_id(result)
            if item_id:
                book_ids.append(item_id)
    
    print(f"\n  📖 Đã tạo {len(book_ids)}/{len(books)} cuốn sách")
    return book_ids

# ==========================================================
# BƯỚC 4: SEED CUSTOMERS
# ==========================================================
def seed_customers():
    section("BƯỚC 4: KHÁCH HÀNG (customer-service :8001)")
    
    customers = [
        {"name": "Nguyễn Văn An",   "email": "an.nguyen@gmail.com"},        # Fan KHCN
        {"name": "Trần Thị Bình",   "email": "binh.tran@gmail.com"},        # Fan kỹ năng sống
        {"name": "Lê Minh Châu",    "email": "chau.le@gmail.com"},          # Fan VH nước ngoài
        {"name": "Phạm Thị Dung",   "email": "dung.pham@gmail.com"},        # Đọc nhiều thể loại
        {"name": "Hoàng Văn Em",    "email": "em.hoang@gmail.com"},          # Mới bắt đầu đọc
        {"name": "Vũ Thị Phương",   "email": "phuong.vu@gmail.com"},        # Fan lịch sử
        {"name": "Đặng Minh Quân",  "email": "quan.dang@gmail.com"},        # Fan kinh doanh
        {"name": "Bùi Thị Hoa",     "email": "hoa.bui@gmail.com"},          # Fan VH trong nước
    ]
    
    customer_ids = []
    for c in customers:
        result = post("customer", "/customers/", c)
        if result:
            item_id = extract_id(result)
            if item_id:
                customer_ids.append(item_id)
    
    print(f"\n  👥 Đã tạo {len(customer_ids)}/{len(customers)} khách hàng")
    return customer_ids

# ==========================================================
# BƯỚC 5: SEED STAFF
# ==========================================================
def seed_staff():
    section("BƯỚC 5: NHÂN VIÊN (staff-service :8004)")
    
    staffs = [
        {"name": "Ngô Thị Lan",     "email": "lan.ngo@bookstore.vn",    "department": "Catalog"},
        {"name": "Trịnh Văn Hùng",  "email": "hung.trinh@bookstore.vn", "department": "Warehouse"},
        {"name": "Phan Thị Mai",    "email": "mai.phan@bookstore.vn",   "department": "Customer Support"},
        {"name": "Đinh Quang Khải", "email": "khai.dinh@bookstore.vn",  "department": "Delivery"},
    ]
    
    staff_ids = []
    for s in staffs:
        result = post("staff", "/staffs/", s)
        if result:
            item_id = extract_id(result)
            if item_id:
                staff_ids.append(item_id)
    
    print(f"\n  👔 Đã tạo {len(staff_ids)}/{len(staffs)} nhân viên")
    return staff_ids

# ==========================================================
# BƯỚC 6: KÍCH HOẠT AUTO-SEED PaymentMethods & ShippingMethods
# Các service này tự tạo dữ liệu khi nhận GET request đầu tiên
# ==========================================================
def trigger_auto_seed():
    section("BƯỚC 6: KÍCH HOẠT PHƯƠNG THỨC THANH TOÁN & VẬN CHUYỂN")
    print(f"  {GRAY}💡 Pay & Ship service tự seed data khi nhận GET request{RESET}")
    
    methods = get_list("pay", "/payment-methods/")
    if methods:
        print(f"  {GREEN}✅ [PAY] Đã có {len(methods)} phương thức thanh toán:{RESET}")
        for m in methods:
            print(f"     • {m.get('name')} (ID={m.get('id')})")
    else:
        print(f"  {RED}❌ [PAY] Không lấy được payment methods{RESET}")
    
    methods = get_list("ship", "/shipping-methods/")
    if methods:
        print(f"  {GREEN}✅ [SHIP] Đã có {len(methods)} phương thức vận chuyển:{RESET}")
        for m in methods:
            print(f"     • {m.get('name')} - {m.get('fee')}đ (ID={m.get('id')})")
    else:
        print(f"  {RED}❌ [SHIP] Không lấy được shipping methods{RESET}")

# ==========================================================
# BƯỚC 7: SEED REVIEWS ⭐⭐⭐ QUAN TRỌNG NHẤT - THỨC ĂN CHO AI
# ==========================================================
def seed_reviews(customer_ids, book_ids):
    """
    Chiến lược seed để AI hoạt động hiệu quả:
    
    customer[0] Nguyễn Văn An   → Fan KHCN → AI sẽ gợi ý sách KHCN
    customer[1] Trần Thị Bình  → Fan kỹ năng sống → AI gợi ý kỹ năng/tâm lý
    customer[2] Lê Minh Châu   → Fan VH nước ngoài → AI gợi ý VH ngoài
    customer[3] Phạm Thị Dung  → Fan Lịch sử → AI gợi ý lịch sử
    customer[4] Hoàng Văn Em   → Ít đánh giá → AI dùng trending fallback
    customer[5] Vũ Thị Phương  → Fan lịch sử
    customer[6] Đặng Minh Quân → Fan Kinh doanh
    customer[7] Bùi Thị Hoa   → Fan VH trong nước
    """
    section("BƯỚC 7: ĐÁNH GIÁ SÁCH ⭐ (comment-rate-service :8010)")
    print(f"  {CYAN}🤖 Đây là 'thức ăn' cho AI. Thuật toán sẽ phân tích:")
    print(f"     1. Rating cao (≥4★) → xác định gu sở thích")
    print(f"     2. Category_id → tìm nhóm sách yêu thích")
    print(f"     3. Gợi ý sách cùng thể loại, chưa đọc, điểm cao nhất{RESET}\n")
    
    def cid(i): return customer_ids[i] if i < len(customer_ids) else customer_ids[0]
    def bid(i): return book_ids[i] if i < len(book_ids) else book_ids[0]
    
    # -------------------------------------------------------
    # Index map (theo thứ tự seed books):
    # 0=Nỗi Buồn CT, 1=Số Đỏ, 2=Tắt Đèn, 3=Dế Mèn, 4=Chí Phèo (VH VN)
    # 5=Nhà Giả Kim, 6=Harry Potter, 7=Kiêu Hãnh, 8=Bố Già, 9=Người Khốn Khổ, 10=1984 (VH NN)
    # 11=Clean Code, 12=Design Patterns, 13=Python CC, 14=AI Superpowers, 15=Pragmatic (KH/CN)
    # 16=Tư Duy Nhanh, 17=Zero to One, 18=Cha Giàu (Kinh doanh)
    # 19=Đắc Nhân Tâm, 20=7 Thói Quen, 21=Nghĩ Giàu (Kỹ năng)
    # 22=Atomic Habits, 23=Đi Tìm Lẽ Sống, 24=Dám Bị Ghét (Tâm lý)
    # 25=Sapiens, 26=Homo Deus (Lịch sử)
    # 27=Hoàng Tử Bé, 28=Truyện Cổ Grimm (Thiếu nhi)
    # -------------------------------------------------------
    
    reviews = [
        # === CUSTOMER 0 (An) → Fan KHCN → AI gợi ý sách KHCN còn lại ===
        {"customer_id": cid(0), "book_id": bid(11), "rating": 5, "comment": "Clean Code là kinh thánh! Mọi dev phải đọc!"},
        {"customer_id": cid(0), "book_id": bid(12), "rating": 5, "comment": "Design Patterns cực kỳ hữu ích cho dự án thực tế"},
        {"customer_id": cid(0), "book_id": bid(13), "rating": 4, "comment": "Python Crash Course - học Python từ đây rất mượt"},
        {"customer_id": cid(0), "book_id": bid(5),  "rating": 3, "comment": "Nhà Giả Kim hay nhưng không phải sở thích mình"},
        
        # === CUSTOMER 1 (Bình) → Fan Kỹ năng sống ===
        {"customer_id": cid(1), "book_id": bid(19), "rating": 5, "comment": "Đắc Nhân Tâm thay đổi cách mình giao tiếp hoàn toàn!"},
        {"customer_id": cid(1), "book_id": bid(20), "rating": 5, "comment": "7 Thói Quen - best seller xứng đáng, mình đọc 3 lần rồi"},
        {"customer_id": cid(1), "book_id": bid(21), "rating": 4, "comment": "Nghĩ Giàu Làm Giàu truyền cảm hứng tuyệt vời"},
        {"customer_id": cid(1), "book_id": bid(22), "rating": 5, "comment": "Atomic Habits 5 sao! Đã thay đổi thói quen của mình"},
        {"customer_id": cid(1), "book_id": bid(6),  "rating": 3, "comment": "Harry Potter hay nhưng không phải sở thích mình"},
        
        # === CUSTOMER 2 (Châu) → Fan VH nước ngoài ===
        {"customer_id": cid(2), "book_id": bid(6),  "rating": 5, "comment": "Harry Potter - di sản văn học thế kỷ 20!"},
        {"customer_id": cid(2), "book_id": bid(7),  "rating": 5, "comment": "Kiêu Hãnh và Định Kiến - đọc đi đọc lại vẫn hay"},
        {"customer_id": cid(2), "book_id": bid(8),  "rating": 5, "comment": "Bố Già kinh điển - không bàn cãi"},
        {"customer_id": cid(2), "book_id": bid(5),  "rating": 4, "comment": "Nhà Giả Kim - triết lý sâu sắc"},
        {"customer_id": cid(2), "book_id": bid(10), "rating": 4, "comment": "1984 - dystopia kinh điển, rùng rợn mà hay"},
        
        # === CUSTOMER 3 (Dung) → Fan Lịch sử ===
        {"customer_id": cid(3), "book_id": bid(25), "rating": 5, "comment": "Sapiens thay đổi cách nhìn nhân loại của mình!"},
        {"customer_id": cid(3), "book_id": bid(26), "rating": 5, "comment": "Homo Deus - tầm nhìn tương lai kinh khủng"},
        {"customer_id": cid(3), "book_id": bid(9),  "rating": 4, "comment": "Những Người Khốn Khổ bất hủ!"},
        {"customer_id": cid(3), "book_id": bid(16), "rating": 3, "comment": "Tư Duy hay nhưng hơi khô"},
        
        # === CUSTOMER 4 (Em) → Ít review → AI dùng trending (stock cao nhất) ===
        {"customer_id": cid(4), "book_id": bid(27), "rating": 4, "comment": "Hoàng Tử Bé - nhỏ mà triết lý lớn"},
        
        # === CUSTOMER 5 (Phương) → Fan Lịch sử & VH nước ngoài ===
        {"customer_id": cid(5), "book_id": bid(25), "rating": 5, "comment": "Sapiens quá đỉnh! Không thể đặt xuống được"},
        {"customer_id": cid(5), "book_id": bid(26), "rating": 4, "comment": "Homo Deus tiếp nối Sapiens rất xứng đáng"},
        {"customer_id": cid(5), "book_id": bid(9),  "rating": 5, "comment": "Victor Hugo - bậc thầy văn chương!"},
        {"customer_id": cid(5), "book_id": bid(7),  "rating": 4, "comment": "Kiêu Hãnh và Định Kiến - romance kinh điển"},
        
        # === CUSTOMER 6 (Quân) → Fan Kinh doanh ===
        {"customer_id": cid(6), "book_id": bid(18), "rating": 5, "comment": "Cha Giàu Cha Nghèo - đọc bao nhiêu lần cũng hay!"},
        {"customer_id": cid(6), "book_id": bid(16), "rating": 5, "comment": "Tư Duy Nhanh Chậm - sâu sắc nhất về kinh tế hành vi"},
        {"customer_id": cid(6), "book_id": bid(17), "rating": 5, "comment": "Zero to One ngắn gọn mà cực kỳ súc tích!"},
        {"customer_id": cid(6), "book_id": bid(22), "rating": 4, "comment": "Atomic Habits rất hay cho người muốn thành công"},
        
        # === CUSTOMER 7 (Hoa) → Fan VH trong nước ===
        {"customer_id": cid(7), "book_id": bid(0),  "rating": 5, "comment": "Nỗi Buồn Chiến Tranh - văn chương Việt đỉnh nhất!"},
        {"customer_id": cid(7), "book_id": bid(1),  "rating": 5, "comment": "Số Đỏ - hài hước châm biếm cực tinh tế"},
        {"customer_id": cid(7), "book_id": bid(2),  "rating": 4, "comment": "Tắt Đèn xúc động, phản ánh xã hội rất thật"},
        {"customer_id": cid(7), "book_id": bid(3),  "rating": 5, "comment": "Dế Mèn - tuổi thơ ký ức không quên!"},
        {"customer_id": cid(7), "book_id": bid(4),  "rating": 4, "comment": "Chí Phèo - Nam Cao viết sâu sắc lắm"},
    ]

    count = 0
    fail = 0
    for rv in reviews:
        result = post("comment", "/reviews/", rv, 
                      label=f"Customer{rv['customer_id']} → Book{rv['book_id']} ({'⭐'*rv['rating']})")
        if result:
            count += 1
        else:
            fail += 1
    
    print(f"\n  🤖 Đã tạo {count}/{len(reviews)} reviews | {fail} thất bại")
    print(f"  {CYAN}→ AI sẽ phân tích {count} reviews này để gợi ý sách cho từng khách!{RESET}")
    return count

# ==========================================================
# BƯỚC 8: KIỂM TRA AI RECOMMENDER
# ==========================================================
def test_ai_recommender(customer_ids, book_ids):
    section("BƯỚC 8: KIỂM THỬ AI RECOMMENDER (recommender-ai-service :8011)")
    
    if not customer_ids:
        print(f"  {YELLOW}⚠️ Không có customer IDs để test{RESET}")
        return
    
    print(f"  {GRAY}Đang test AI recommend cho Customer ID = {customer_ids[0]}...{RESET}")
    
    url = f"{SERVICES['recommender']}/ai-suggest/"
    try:
        r = requests.post(url, json={"customer_id": customer_ids[0]}, timeout=15)
        if r.status_code == 200:
            data = r.json()
            book = data.get("book", {})
            reason = data.get("reason", "")
            print(f"  {GREEN}✅ AI HOẠT ĐỘNG TỐT!{RESET}")
            print(f"  📖 Gợi ý: {book.get('title', '?')} (by {book.get('author', '?')})")
            print(f"  💭 Lý do: {reason}")
        else:
            print(f"  {RED}❌ AI trả lỗi: {r.status_code} - {r.text[:200]}{RESET}")
    except requests.exceptions.ConnectionError:
        print(f"  {RED}💀 recommender-ai-service offline!{RESET}")
    except Exception as e:
        print(f"  {YELLOW}⚠️ Test AI gặp lỗi: {e}{RESET}")

# ==========================================================
# MAIN
# ==========================================================
def main():
    print(f"\n{BOLD}{'#'*62}{RESET}")
    print(f"{BOLD}  🚀 BOOKSTORE DATA SEEDER v2.0{RESET}")
    print(f"{BOLD}  Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}")
    print(f"{BOLD}{'#'*62}{RESET}")
    
    # Bước 1: Dọn DB cũ
    clear_old_data()
    
    # Bước 2-3: Seed catalog & books
    cat_ids  = seed_categories()
    book_ids = seed_books(cat_ids)
    
    # Bước 4-5: Seed customers & staff
    customer_ids = seed_customers()
    seed_staff()
    
    # Bước 6: Trigger auto-seed cho Pay/Ship methods
    trigger_auto_seed()
    
    # Bước 7: Seed reviews (QUAN TRỌNG NHẤT cho AI!)
    review_count = seed_reviews(customer_ids, book_ids)
    
    # Bước 8: Test AI
    test_ai_recommender(customer_ids, book_ids)
    
    # === TỔNG KẾT ===
    section("✅ TỔNG KẾT - DỮ LIỆU ĐÃ SEED XONG")
    print(f"""
  {BOLD}Service             | Loại dữ liệu              | Số lượng{RESET}
  {GRAY}{'─'*55}{RESET}
  catalog-service     | Thể loại sách             | {len(cat_ids)}
  book-service        | Sách (có ảnh bìa thật)    | {len(book_ids)}
  customer-service    | Khách hàng                | 8
  staff-service       | Nhân viên                 | 4
  pay-service         | Phương thức thanh toán    | auto (COD + CREDIT_CARD)
  ship-service        | Phương thức vận chuyển    | auto (Tiêu chuẩn + Hỏa tốc)
  comment-rate-service| Đánh giá sách (AI data)   | {review_count}+
  recommender-service | AI hoạt động dựa trên     | reviews + categories

  {BOLD}{CYAN}🤖 Test AI Recommend thủ công:{RESET}
  POST http://localhost:8011/ai-suggest/
  Body: {{"customer_id": {customer_ids[0] if customer_ids else 1}}}

  {BOLD}{CYAN}📝 Lưu ý về Orders:{RESET}
  Để tạo Orders thật, cần dùng UI thêm sách vào giỏ hàng trước.
  Order API yêu cầu có dữ liệu Cart → không thể seed trực tiếp.

  {BOLD}{GREEN}✅ Hệ thống đã có dữ liệu! Mở http://localhost:8000 để xem.{RESET}
""")

if __name__ == "__main__":
    main()
