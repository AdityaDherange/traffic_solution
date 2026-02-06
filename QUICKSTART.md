# Quick Start Guide

## 🚀 Quick Start (3 Steps)

### Windows Users

1. **Double-click** `start.bat`
2. Wait for the application to open in your browser
3. Login with demo credentials:
   - Username: `demo`
   - Password: `demo123`

### Linux/Mac Users

1. **Make the script executable:**
   ```bash
   chmod +x start.sh
   ```

2. **Run the script:**
   ```bash
   ./start.sh
   ```

3. Login with demo credentials:
   - Username: `demo`
   - Password: `demo123`

## 📝 Manual Setup

If the automatic script doesn't work:

### 1. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
streamlit run app_new.py
```

### 4. Open Browser
Navigate to: `http://localhost:8501`

## 🎯 First Steps in the App

1. **Login** with demo credentials
2. **Auto-detect location** or set manually
3. **Try features:**
   - 📸 Upload traffic image for analysis
   - 🗺️ Plan a route between two locations
   - 🔥 View traffic heatmap

## 🆘 Troubleshooting

### Port Already in Use
```bash
streamlit run app_new.py --server.port 8502
```

### Module Not Found
```bash
pip install -r requirements.txt
```

### Permission Denied (Linux/Mac)
```bash
chmod +x start.sh
```

## 📖 Full Documentation

See [README.md](README.md) for complete documentation.
