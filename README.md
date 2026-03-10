# Bookstore Microservices Project

Welcome to the Bookstore Microservices application! This project demonstrates a scalable e-commerce platform built using a microservices architecture. It contains multiple independent services communicating with each other.

## 🏗 System Architecture

This project is built using a Monorepo structured microservices architecture. The system contains the following services:

| Service Name | Description |
|---|---|
| `api-gateway` | The main entry point for clients, routing requests to the appropriate microservices |
| `book-service` | Manages book records and inventory |
| `cart-service` | Handles user shopping carts and active sessions |
| `catalog-service` | Stores and retrieves book catalog and category details |
| `comment-rate-service` | Handles user ratings and comments on books |
| `customer-service` | Manages customer profiles |
| `manager-service` | Admin dashboard and management operations |
| `order-service` | Handles order creation and lifecycle |
| `pay-service` | Manages payment processing |
| `recommender-ai-service` | AI-based book recommendation engine |
| `ship-service` | Manages shipping and delivery updates |
| `staff-service` | Platform for bookstore staff to manage tasks |

## 🚀 How to Run the Project (Using Docker)

The easiest way to run the entire cluster of microservices is by using `docker-compose`.

### Prerequisites:
- Git
- Docker and Docker Compose installed on your machine.

### Steps to Run:
1. **Clone the repository:**
   ```bash
   git clone <your-github-repo-url>
   cd bookstore-microservice
   ```

2. **Start the services:**
   Run the following command in the root directory:
   ```bash
   docker-compose up --build -d
   ```
   *The `-d` flag runs the containers in the background.*

3. **Access the Application:**
   - The Main Website (Frontend via API Gateway): `http://localhost:<YOUR_GATEWAY_PORT>`
   - To stop the system, run:
     ```bash
     docker-compose down
     ```

## 🛠 Running Services Manually (Local Environment)

If you'd rather run the services individually without Docker, you will need Python installed. Do the following for **each service directory** in separate terminal windows:

1. Navigate to the service folder (e.g., `cd book-service`).
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the dependencies for that specific service:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the development server (make sure you use a unique port per service):
   ```bash
   python manage.py runserver 8000
   ```

## 📦 Deliverables
- [x] GitHub Repository setup
- [ ] Architecture diagram for each service
- [ ] API documentation
- [ ] 10-minute demo video
- [ ] 8-12 page technical report

---
*Developed for Software Engineering Project / Microservice Architecture.*
