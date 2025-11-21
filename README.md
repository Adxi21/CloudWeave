# Event Registration System

Full-stack event registration system with FastAPI backend and React frontend.

## 🚀 Quick EC2 Deployment

### Prerequisites
- Ubuntu EC2 instance (t2.medium or larger recommended)
- Security groups allowing ports 80, 8000, and 22

### One-Command Deployment
```bash
git clone <your-repo-url>
cd utsav-gurudev
./deploy.sh
```

### Manual Deployment Steps
```bash
# 1. Clone repository
git clone <your-repo-url>
cd utsav-gurudev

# 2. Install Docker & Docker Compose
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# 3. Build and run services
docker-compose up --build -d
```

## 🌐 Access Points
- **Frontend**: http://your-ec2-ip
- **Backend API**: http://your-ec2-ip:8000
- **API Docs**: http://your-ec2-ip:8000/docs

## 🔧 Configuration
- Database settings in `backend/database_commands.py`
- Frontend environment in `clerk-react/.env`

## 📊 Services
- **Backend**: FastAPI server on port 8000
- **Frontend**: React app served via Nginx on port 80
- **Database**: External PostgreSQL (configured in database_commands.py)

## 🛠️ Development
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend  
cd clerk-react
npm install
npm run dev
```

## 📝 Features
- Event registration with participant management
- Admin panel with analytics dashboard
- PDF generation for registration previews
- CRUD operations for user registrations
- Comprehensive reporting system