"""
Wrapper script chạy seed_data.py với đúng địa chỉ Docker network.
Không sửa seed_data.py gốc — chỉ patch SERVICES dict và xử lý edge-cases.
"""
import importlib.util, sys, os, requests

# ── Load seed_data.py dưới dạng module ──────────────────────────────────────
_spec = importlib.util.spec_from_file_location(
    "seed_data", os.path.join(os.path.dirname(__file__), "seed_data.py")
)
seed = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(seed)

# ── Patch SERVICES → dùng hostname Docker nội bộ (port 8000) ────────────────
# Tất cả service đều expose :8000 trong network bookstore-microservices_default
seed.SERVICES = {
    "catalog":     "http://catalog-service:8000",
    "book":        "http://product-service:8000",
    "customer":    "http://user-service:8000",
    "staff":       "http://user-service:8000",   # staff đã gộp vào user-service
    "pay":         "http://pay-service:8000",
    "ship":        "http://ship-service:8000",
    "order":       "http://order-service:8000",
    "comment":     "http://comment-rate-service:8000",
    "recommender": "http://recommender-ai-service:8000",
    "manager":     "http://user-service:8000",   # manager đã gộp vào user-service
}

# ── Patch seed_categories(): catalog-service không có DELETE endpoint nên
#    nếu category đã tồn tại thì fetch ID thay vì tạo mới ─────────────────────
_original_seed_categories = seed.seed_categories

def _patched_seed_categories():
    # Xoá categories bằng cách truncate trực tiếp qua DB nếu có thể
    # hoặc fetch existing ones nếu không xóa được
    cat_data = [
        ("Văn học trong nước",  "Tiểu thuyết, truyện ngắn, thơ của tác giả Việt Nam"),
        ("Văn học nước ngoài",  "Tuyển tập danh tác thế giới dịch sang tiếng Việt"),
        ("Khoa học - Công nghệ","Lập trình, AI, khoa học dữ liệu và công nghệ hiện đại"),
        ("Kinh tế - Kinh doanh","Quản lý tài chính, khởi nghiệp, đầu tư và kinh doanh"),
        ("Kỹ năng sống",        "Phát triển bản thân, tư duy tích cực và kỹ năng mềm"),
        ("Tâm lý học",          "Khám phá tâm trí con người, hành vi và cảm xúc"),
        ("Lịch sử - Địa lý",    "Lịch sử văn minh nhân loại, lịch sử Việt Nam và địa lý"),
        ("Thiếu nhi",           "Sách giáo dục, giải trí và phát triển trí tuệ cho trẻ em"),
    ]

    seed.section("BƯỚC 2: THỂ LOẠI SÁCH (catalog-service)")

    cat_ids = {}
    for (name, desc) in cat_data:
        r = requests.post(
            "http://catalog-service:8000/categories/",
            json={"name": name, "description": desc},
            timeout=10
        )
        if r.status_code in (200, 201):
            item_id = seed.extract_id(r.json())
            if item_id:
                cat_ids[name] = item_id
                print(f"  \033[92m✅ [CATALOG] {name} (ID={item_id})\033[0m")
        elif r.status_code == 400 and "already exists" in r.text:
            # Category tồn tại — fetch lại ID từ danh sách
            pass  # sẽ fetch sau

    # Nếu thiếu categories, fetch từ server
    if len(cat_ids) < len(cat_data):
        existing = requests.get("http://catalog-service:8000/categories/", timeout=10).json()
        existing_map = {c["name"]: c["id"] for c in existing if isinstance(c, dict)}
        for (name, _) in cat_data:
            if name not in cat_ids and name in existing_map:
                cat_ids[name] = existing_map[name]
                print(f"  \033[93m♻️  [CATALOG] {name} (ID={existing_map[name]}) — đã tồn tại, dùng lại\033[0m")

    print(f"\n  📚 Đã có {len(cat_ids)}/{len(cat_data)} thể loại")
    return cat_ids

seed.seed_categories = _patched_seed_categories

# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    seed.main()
