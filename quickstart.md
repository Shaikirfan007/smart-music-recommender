# 🚀 Quick Start Guide - Smart Music Recommender

Get up and running in **5 minutes**!

## 📋 Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] pip package manager
- [ ] Spotify account (free or premium)
- [ ] Internet connection

## ⚡ Fast Setup (5 Steps)

### Step 1: Download the Project

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-music-recommender.git
cd smart-music-recommender

# OR download and extract the ZIP file
```

### Step 2: Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed streamlit-1.32.0 spotipy-2.23.0 pandas-2.2.0 ...
```

### Step 3: Get Spotify API Credentials

1. Visit: https://developer.spotify.com/dashboard
2. Log in with Spotify
3. Click **"Create an App"**
4. Enter any name (e.g., "My Music Recommender")
5. Copy your **Client ID** and **Client Secret**

### Step 4: Configure Credentials

**Option A: Use the setup script (Easiest)**
```bash
python setup.py
```
Follow the prompts and paste your credentials.

**Option B: Manual setup**
```bash
# Create folder
mkdir .streamlit

# Create and edit secrets file
# Windows:
notepad .streamlit\secrets.toml
# macOS/Linux:
nano .streamlit/secrets.toml
```

Paste this content:
```toml
SPOTIFY_CLIENT_ID = "paste_your_client_id_here"
SPOTIFY_CLIENT_SECRET = "paste_your_client_secret_here"
```

Save and close.

### Step 5: Run the App

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

**🎉 That's it! You're ready to discover music!**

---

## 🎵 How to Use

### 1. Search for a Song

1. Type a song name or artist in the search box
2. Click "Search"
3. View song details and audio features

### 2. Get Recommendations

1. After searching, scroll down to see recommendations
2. Adjust filters in the sidebar:
   - Number of songs (5-20)
   - Popularity range
   - Release year range
3. Click on any recommendation to explore

### 3. Explore Moods

1. Click the **"Surprise Me"** tab
2. Select a mood (happy, chill, workout, etc.)
3. Click "Get Surprise Recommendations"
4. Discover new music!

### 4. Analyze Songs

1. Click the **"Analytics"** tab
2. View audio feature radar charts
3. Explore detailed metrics

---

## 🔧 Troubleshooting

### Problem: "Spotify API initialization failed"

**Solution:**
1. Check `.streamlit/secrets.toml` exists
2. Verify credentials are correct (no extra spaces)
3. Ensure app is active in Spotify Dashboard

### Problem: "Module not found" error

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Problem: App won't start

**Solution:**
```bash
# Check Streamlit installation
streamlit --version

# If not installed:
pip install streamlit
```

### Problem: "No recommendations found"

**Solution:**
1. Try a more popular song
2. Relax filters (increase year range, popularity range)
3. Uncheck "Mood Filter"

---

## 💡 Pro Tips

### Get Better Recommendations
- **Use popular songs** as seeds for more variety
- **Adjust similarity threshold** by changing the number of recommendations
- **Combine filters** for highly specific results

### Performance Tips
- **First search takes longer** (API initialization)
- **Subsequent searches are faster** (cached data)
- **Clear browser cache** if experiencing issues

### Best Practices
- **Start with familiar songs** to test the system
- **Experiment with mood filters** for discovery
- **Use the visualization** to understand song relationships

---

## 📊 Understanding Audio Features

| Feature | What it means | Range |
|---------|---------------|-------|
| **Danceability** | How suitable for dancing | 0-1 |
| **Energy** | Intensity and activity | 0-1 |
| **Valence** | Musical positiveness/happiness | 0-1 |
| **Tempo** | Speed (BPM) | 50-200+ |
| **Acousticness** | Confidence the track is acoustic | 0-1 |
| **Liveness** | Presence of audience | 0-1 |
| **Instrumentalness** | Predicts no vocals | 0-1 |
| **Loudness** | Overall loudness in dB | -60-0 |
| **Speechiness