# 🎵 Smart Music Recommender

An AI-powered music recommendation system built with Streamlit and Spotify Web API that provides personalized song recommendations using machine learning algorithms.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32-red)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

### 🎯 Core Functionality
- **🔍 Smart Search**: Find any song from Spotify's database
- **🤖 AI-Powered Recommendations**: Uses cosine similarity on audio features for content-based filtering
- **📊 Audio Feature Analysis**: Analyzes danceability, energy, valence, tempo, and more
- **📈 Interactive Visualizations**: 2D PCA plots showing song similarity clusters
- **🎧 Real-time Previews**: Listen to 30-second song previews

### 🌟 Advanced Features
- **🎭 Mood-Based Discovery**: Get recommendations by mood (😊 happy, 😌 chill, 💪 workout, 😢 sad, 🎉 party)
- **⚙️ Smart Filters**: 
  - ⭐ Popularity range (0-100)
  - 📅 Release year (1960-present)
  - 🔢 Adjustable recommendation count (5-20)
- **🎲 Surprise Me Mode**: Random mood-based recommendations
- **📊 Audio Analytics Dashboard**: Radar charts and detailed metrics

### 🎨 User Experience
- 🌈 Modern gradient UI with smooth animations
- 📱 Responsive card-based design
- 🖼️ Album artwork integration
- 🔗 Direct Spotify links
- ▶️ Inline audio players

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **API**: Spotipy (Spotify Web API)
- **ML/Data**: Scikit-learn, Pandas, NumPy
- **Visualization**: Plotly
- **Algorithms**: 
  - Cosine Similarity
  - PCA (Principal Component Analysis)
  - StandardScaler normalization

## 📋 Prerequisites

- Python 3.8+
- Spotify Developer Account (free)

## 🚀 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Shaikirfan007/smart-music-recommender.git
cd smart-music-recommender
```

### 2️⃣ Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Spotify API Credentials

**🔑 Get your credentials:**
1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click **"Create App"**
4. Fill in:
   - App name: "My Music Recommender" (or any name)
   - App description: "Personal music recommendation app"
   - Redirect URI: `http://localhost:8501` (optional)
5. Copy your **Client ID** and **Client Secret**

**⚙️ Configure the app:**
1. Navigate to the `.streamlit` folder
2. Copy `secrets.toml.example` to `secrets.toml`:
   ```bash
   # Windows
   copy .streamlit\secrets.toml.example .streamlit\secrets.toml
   
   # macOS/Linux
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```
3. Edit `.streamlit/secrets.toml` and replace with your actual credentials:
   ```toml
   SPOTIFY_CLIENT_ID = "your_actual_client_id_here"
   SPOTIFY_CLIENT_SECRET = "your_actual_client_secret_here"
   ```

**⚠️ IMPORTANT:** Never commit `secrets.toml` to GitHub. It's already in `.gitignore`.

### 5️⃣ Run the App
```bash
streamlit run app.py
```

🎉 The app will open at `http://localhost:8501`

## 📖 Usage Guide

### 🔍 Search & Recommend
1. Enter a song name or artist
2. Click "🔍 Search"
3. View song details and audio features
4. Explore personalized recommendations based on similarity
5. Click recommendations to view details and play previews

### 🎲 Surprise Me
1. Navigate to "🎲 Surprise Me" tab
2. Select a mood (😊😌💪😢🎉)
3. Get instant recommendations matching that vibe

### 📊 Analytics
1. Search for any song
2. Go to "📊 Analytics" tab
3. View radar chart of audio features
4. Analyze detailed metrics

### ⚙️ Filters (Sidebar)
- 🔢 Adjust number of recommendations (5-20)
- ⭐ Set popularity range
- 📅 Filter by release year
- 🎭 Select mood preference

## 🧠 How It Works

### Content-Based Filtering Algorithm

The app uses a multi-step recommendation process:

1. **📥 Feature Extraction**: Retrieves 9 audio features from Spotify API
   - 💃 Danceability, ⚡ Energy, 😊 Valence, 🎵 Tempo, 🎸 Acousticness
   - 🎤 Liveness, 🎹 Instrumentalness, 🔊 Loudness, 🗣️ Speechiness

2. **🔎 Data Collection**: Gathers candidate songs from:
   - Artist's top tracks
   - Related artists' tracks
   - Similar song searches

3. **📐 Normalization**: Uses StandardScaler to normalize features

4. **🎯 Similarity Calculation**: Computes cosine similarity:
   ```
   similarity = (A · B) / (||A|| × ||B||)
   ```

5. **🏆 Ranking**: Returns top N most similar songs

6. **📊 Visualization**: Applies PCA to reduce 9D space to 2D plot

## 📁 Project Structure

```
smart-music-recommender/
├── 📄 app.py                       # Main Streamlit application
├── 🔧 utils.py                     # Helper functions and classes
├── 📦 requirements.txt             # Python dependencies
├── 📖 README.md                    # This file
├── 🚀 quickstart.md                # Quick setup guide
├── 🚫 .gitignore                   # Git ignore rules
└── 📁 .streamlit/
    ├── 📝 secrets.toml.example     # Template for credentials
    └── 🔐 secrets.toml             # Your credentials (not in git)
```

## 🔒 Security

- ✅ API credentials stored in `.streamlit/secrets.toml` (excluded from git)
- ✅ Never commit sensitive data to version control
- ✅ Use environment variables for production deployment
- ✅ App suppresses API error logging to avoid exposing credentials

## 🐛 Troubleshooting

### ❌ "Spotify API initialization failed"
**💡 Solution:** 
- Check `.streamlit/secrets.toml` exists and has correct credentials
- Verify no extra spaces or quotes in the credentials
- Ensure app is active in Spotify Developer Dashboard

### ⚠️ "No recommendations found"
**💡 Solution:**
- Try a more popular song
- Relax filters (increase popularity/year ranges)
- Some songs may have limited data

### 🔴 403 Errors in Terminal
**ℹ️ Note:** These warnings are normal for new Spotify apps in Development Mode. The app works despite these messages.

To eliminate them, request "Extended Quota Mode" in your Spotify Developer Dashboard (free for personal projects).

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

1. Push code to GitHub (secrets.toml is automatically excluded)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo
4. In App Settings → Secrets, paste your credentials:
   ```toml
   SPOTIFY_CLIENT_ID = "your_id"
   SPOTIFY_CLIENT_SECRET = "your_secret"
   ```
5. 🚀 Deploy!

### Alternative: Use Environment Variables

For local deployment without secrets.toml:
```bash
# Windows PowerShell
$env:SPOTIFY_CLIENT_ID="your_client_id"
$env:SPOTIFY_CLIENT_SECRET="your_client_secret"
streamlit run app.py

# macOS/Linux
export SPOTIFY_CLIENT_ID="your_client_id"
export SPOTIFY_CLIENT_SECRET="your_client_secret"
streamlit run app.py
```

## 📸 Screenshots

### 🔍 Search & Recommendations
![Search Interface](screenshots/search.png)
*Search for any song and get AI-powered recommendations*

### 📊 Song Similarity Visualization
![PCA Visualization](screenshots/visualization.png)
*2D PCA plot showing song clusters by audio similarity*

### 📈 Audio Analytics Dashboard
![Analytics](screenshots/analytics.png)
*Radar chart displaying audio feature profiles*

### 🎲 Mood-Based Discovery
![Surprise Me](screenshots/surprise.png)
*Get random recommendations based on your mood*

## 🤝 Contributing

Contributions are welcome! Please:

1. 🍴 Fork the repository
2. 🌿 Create a feature branch (`git checkout -b feature/NewFeature`)
3. ✍️ Commit changes (`git commit -m 'Add NewFeature'`)
4. 📤 Push to branch (`git push origin feature/NewFeature`)
5. 🔄 Open a Pull Request

## 🎯 Future Enhancements

- [ ] 👤 User authentication and listening history
- [ ] 📋 Playlist generation and Spotify export
- [ ] 🤝 Collaborative filtering
- [ ] 🎸 Genre-based recommendations
- [ ] 📝 Lyrics integration
- [ ] 🎵 Multi-song seed selection
- [ ] 📱 Social sharing features

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- 🎵 Spotify Web API for comprehensive music data
- ⚡ Streamlit for the amazing web framework
- 🧠 Scikit-learn for ML algorithms
- 📊 Plotly for interactive visualizations

## 📧 Contact

**Shaik Irfan**
- 💼 [GitHub](https://github.com/Shaikirfan007)
- 🔗 [LinkedIn](https://linkedin.com/in/yourprofile) *(optional)*
- 📧 Email: your.email@example.com *(optional)*

**Project Link:** [https://github.com/Shaikirfan007/smart-music-recommender](https://github.com/Shaikirfan007/smart-music-recommender)

---

⚠️ **Note:** This project requires your own Spotify API credentials. Follow the installation guide to set them up.

Made with ❤️ using Python and Spotify API

⭐ **If you find this project useful, please give it a star!**
