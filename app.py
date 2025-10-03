import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import logging

# Suppress Spotify API warnings
logging.getLogger('spotipy').setLevel(logging.ERROR)
logging.getLogger('urllib3').setLevel(logging.ERROR)

# Page configuration
st.set_page_config(
    page_title="🎵 Smart Music Recommender",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    h1, h2, h3 {
        color: white;
    }
    .stButton>button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: bold;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def init_spotify():
    """Initialize Spotify API client"""
    try:
        client_id = None
        client_secret = None
        
        # Try Streamlit secrets
        if hasattr(st, 'secrets'):
            try:
                if "SPOTIFY_CLIENT_ID" in st.secrets:
                    client_id = st.secrets["SPOTIFY_CLIENT_ID"]
                    client_secret = st.secrets["SPOTIFY_CLIENT_SECRET"]
            except Exception:
                pass
        
        # Fallback to environment variables
        if not client_id:
            client_id = os.environ.get("SPOTIFY_CLIENT_ID") or os.getenv("SPOTIFY_CLIENT_ID")
            client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET") or os.getenv("SPOTIFY_CLIENT_SECRET")
        
        if not client_id or not client_secret:
            return None, "missing_credentials"
        
        client_id = str(client_id).strip()
        client_secret = str(client_secret).strip()
        
        auth_manager = SpotifyClientCredentials(
            client_id=client_id,
            client_secret=client_secret
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        
        # Test connection
        sp.search(q="test", type='track', limit=1)
        
        return sp, "success"
        
    except Exception as e:
        return None, f"error: {str(e)}"


def fetch_song(sp, query):
    """Search for a song on Spotify"""
    try:
        if not query or not query.strip():
            return None, "Empty search query"
        
        results = sp.search(q=query.strip(), type='track', limit=1)
        
        if results['tracks']['items']:
            return results['tracks']['items'][0], None
        return None, "No results found"
        
    except Exception as e:
        return None, f"Search error: {str(e)}"


def get_audio_features(sp, track_id):
    """Get audio features for a track"""
    try:
        features = sp.audio_features([track_id])
        if features and len(features) > 0 and features[0]:
            return features[0], None
        return {}, "No audio features"
    except Exception as e:
        return {}, f"Error: {str(e)}"


def get_track_details(sp, track):
    """Extract detailed track information"""
    try:
        audio_features, _ = get_audio_features(sp, track['id'])
        
        details = {
            'id': track['id'],
            'name': track['name'],
            'artist': ', '.join([artist['name'] for artist in track['artists']]),
            'album': track['album']['name'],
            'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
            'preview_url': track['preview_url'],
            'popularity': track['popularity'],
            'release_date': track['album']['release_date'],
            'duration_ms': track['duration_ms'],
            'external_url': track['external_urls']['spotify'],
            'artist_ids': [artist['id'] for artist in track['artists']]
        }
        
        # Add audio features with defaults
        details.update({
            'danceability': audio_features.get('danceability', 0.5),
            'energy': audio_features.get('energy', 0.5),
            'valence': audio_features.get('valence', 0.5),
            'tempo': audio_features.get('tempo', 120),
            'acousticness': audio_features.get('acousticness', 0.5),
            'liveness': audio_features.get('liveness', 0.5),
            'instrumentalness': audio_features.get('instrumentalness', 0.5),
            'loudness': audio_features.get('loudness', -10),
            'speechiness': audio_features.get('speechiness', 0.5),
            'key': audio_features.get('key', 0),
            'mode': audio_features.get('mode', 1)
        })
        
        return details, None
    except Exception as e:
        return None, f"Error: {str(e)}"


def get_artist_top_tracks(sp, artist_id, limit=10):
    """Get top tracks from an artist"""
    try:
        results = sp.artist_top_tracks(artist_id, country='US')
        tracks_data = []
        
        for track in results['tracks'][:limit]:
            track_details, error = get_track_details(sp, track)
            if track_details and not error:
                tracks_data.append(track_details)
        
        return pd.DataFrame(tracks_data), None
    except Exception as e:
        return pd.DataFrame(), f"Error: {str(e)}"


def get_related_artists_tracks(sp, artist_id, limit=20):
    """Get tracks from related artists"""
    try:
        related = sp.artist_related_artists(artist_id)
        tracks_data = []
        
        for artist in related['artists'][:5]:
            top_tracks = sp.artist_top_tracks(artist['id'], country='US')
            for track in top_tracks['tracks'][:4]:
                track_details, error = get_track_details(sp, track)
                if track_details and not error:
                    tracks_data.append(track_details)
                    if len(tracks_data) >= limit:
                        break
            if len(tracks_data) >= limit:
                break
        
        return pd.DataFrame(tracks_data), None
    except Exception as e:
        return pd.DataFrame(), f"Error: {str(e)}"


def recommend_songs(sp, seed_track_details, num_recommendations=10, filters=None):
    """Get recommendations using multiple strategies"""
    try:
        all_tracks = []
        
        # Strategy 1: Get artist's other tracks
        if seed_track_details.get('artist_ids'):
            artist_id = seed_track_details['artist_ids'][0]
            artist_tracks, _ = get_artist_top_tracks(sp, artist_id, limit=15)
            if not artist_tracks.empty:
                all_tracks.append(artist_tracks)
        
        # Strategy 2: Get tracks from related artists
        if seed_track_details.get('artist_ids'):
            artist_id = seed_track_details['artist_ids'][0]
            related_tracks, _ = get_related_artists_tracks(sp, artist_id, limit=25)
            if not related_tracks.empty:
                all_tracks.append(related_tracks)
        
        # Strategy 3: Search similar tracks
        try:
            search_query = f"{seed_track_details['name']} {seed_track_details['artist']}"
            search_results = sp.search(q=search_query, type='track', limit=20)
            search_tracks = []
            for track in search_results['tracks']['items']:
                track_details, error = get_track_details(sp, track)
                if track_details and not error:
                    search_tracks.append(track_details)
            if search_tracks:
                all_tracks.append(pd.DataFrame(search_tracks))
        except:
            pass
        
        if not all_tracks:
            return pd.DataFrame(), "Could not find recommendations"
        
        # Combine all tracks
        df = pd.concat(all_tracks, ignore_index=True)
        
        # Remove seed track
        df = df[df['id'] != seed_track_details['id']]
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['id'])
        
        if df.empty:
            return pd.DataFrame(), "No recommendations found"
        
        # Apply filters
        if filters:
            if 'popularity_range' in filters:
                df = df[(df['popularity'] >= filters['popularity_range'][0]) & 
                       (df['popularity'] <= filters['popularity_range'][1])]
            
            if 'year_range' in filters:
                df['year'] = pd.to_datetime(df['release_date'], errors='coerce').dt.year
                df = df.dropna(subset=['year'])
                df = df[(df['year'] >= filters['year_range'][0]) & 
                       (df['year'] <= filters['year_range'][1])]
        
        if df.empty:
            return pd.DataFrame(), "No songs match the filters"
        
        # Calculate similarity
        feature_cols = ['danceability', 'energy', 'valence', 'tempo', 
                       'acousticness', 'liveness', 'instrumentalness', 
                       'loudness', 'speechiness']
        
        df_features = df[feature_cols].fillna(0.5)
        seed_features = np.array([[seed_track_details.get(col, 0.5) for col in feature_cols]])
        
        scaler = StandardScaler()
        df_features_scaled = scaler.fit_transform(df_features)
        seed_features_scaled = scaler.transform(seed_features)
        
        similarities = cosine_similarity(seed_features_scaled, df_features_scaled)[0]
        df['similarity'] = similarities
        
        recommendations = df.nlargest(min(num_recommendations, len(df)), 'similarity')
        
        return recommendations, None
    except Exception as e:
        return pd.DataFrame(), f"Error: {str(e)}"


def get_mood_based_recommendations(sp, mood, num_recommendations=10):
    """Get mood-based recommendations using search"""
    mood_queries = {
        'happy': 'happy upbeat pop dance',
        'chill': 'chill relax ambient calm',
        'workout': 'workout energy gym motivation',
        'sad': 'sad emotional melancholy',
        'party': 'party dance club edm'
    }
    
    try:
        if mood not in mood_queries:
            return pd.DataFrame(), "Invalid mood"
        
        query = mood_queries[mood]
        results = sp.search(q=query, type='track', limit=num_recommendations * 2)
        
        tracks_data = []
        for track in results['tracks']['items']:
            track_details, error = get_track_details(sp, track)
            if track_details and not error:
                tracks_data.append(track_details)
                if len(tracks_data) >= num_recommendations:
                    break
        
        return pd.DataFrame(tracks_data), None
    except Exception as e:
        return pd.DataFrame(), f"Error: {str(e)}"


def visualize_recommendations(seed_track, recommendations_df):
    """Visualize recommendations using PCA"""
    if recommendations_df.empty:
        return None
    
    try:
        feature_cols = ['danceability', 'energy', 'valence', 'tempo', 
                       'acousticness', 'liveness', 'instrumentalness', 
                       'loudness', 'speechiness']
        
        all_tracks = recommendations_df.copy()
        features = all_tracks[feature_cols].fillna(0.5)
        
        pca = PCA(n_components=2)
        coords = pca.fit_transform(StandardScaler().fit_transform(features))
        
        all_tracks['x'] = coords[:, 0]
        all_tracks['y'] = coords[:, 1]
        
        fig = px.scatter(
            all_tracks,
            x='x',
            y='y',
            hover_data=['name', 'artist', 'popularity'],
            size='popularity',
            color='similarity',
            color_continuous_scale='Viridis',
            title='🎯 Song Similarity Map (PCA Visualization)'
        )
        
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=500
        )
        
        return fig
    except Exception as e:
        return None


def display_song_card(track, show_similarity=False):
    """Display a song card with details"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if track.get('image_url'):
            st.image(track['image_url'], width=150)
    
    with col2:
        st.markdown(f"### 🎵 {track['name']}")
        st.markdown(f"**🎤 Artist:** {track['artist']}")
        st.markdown(f"**💿 Album:** {track['album']}")
        
        cols = st.columns(4)
        with cols[0]:
            st.metric("⭐ Popularity", f"{track['popularity']}/100")
        with cols[1]:
            st.metric("💃 Danceability", f"{track.get('danceability', 0):.2f}")
        with cols[2]:
            st.metric("⚡ Energy", f"{track.get('energy', 0):.2f}")
        with cols[3]:
            st.metric("😊 Valence", f"{track.get('valence', 0):.2f}")
        
        if show_similarity and 'similarity' in track:
            st.progress(float(track['similarity']))
            st.caption(f"🎯 Similarity Score: {track['similarity']:.2%}")
        
        col_a, col_b = st.columns(2)
        with col_a:
            if track.get('preview_url'):
                st.audio(track['preview_url'])
            else:
                st.info("🔇 No preview available")
        with col_b:
            st.link_button("🎧 Open in Spotify", track['external_url'])


def main():
    st.title("🎵 Smart Music Recommender")
    st.markdown("### Discover your next favorite song powered by AI and Spotify")
    
    # Initialize Spotify
    sp, status = init_spotify()
    
    if status != "success":
        st.error("⚠️ Spotify API Connection Failed")
        st.info("""
        **Setup:** Create `.streamlit/secrets.toml` with your credentials or use environment variables.
        """)
        st.stop()
    
    st.success("✅ Connected to Spotify API")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Filters & Settings")
        num_recommendations = st.slider("📊 Number of recommendations", 5, 20, 10)
        
        st.subheader("🎭 Mood Filter")
        mood_filter = st.selectbox(
            "Select mood",
            ["None", "😊 happy", "😌 chill", "💪 workout", "😢 sad", "🎉 party"]
        )
        
        st.subheader("📈 Popularity Range")
        popularity_range = st.slider("Popularity", 0, 100, (0, 100))
        
        st.subheader("📅 Release Year Range")
        current_year = datetime.now().year
        year_range = st.slider("Year", 1960, current_year, (1990, current_year))
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Search & Recommend", "🎲 Surprise Me", "📊 Analytics"])
    
    with tab1:
        search_query = st.text_input(
            "🎼 Search for a song",
            placeholder="Enter song name or artist..."
        )
        
        search_button = st.button("🔍 Search", use_container_width=True)
        
        if search_button and search_query:
            with st.spinner("🔎 Searching..."):
                track, error = fetch_song(sp, search_query)
                
                if error:
                    st.error(f"❌ {error}")
                elif track:
                    st.success("✅ Song found!")
                    track_details, error = get_track_details(sp, track)
                    
                    if error:
                        st.error(f"❌ Error: {error}")
                    elif track_details:
                        st.markdown("---")
                        st.subheader("🎯 Selected Song")
                        display_song_card(track_details)
                        
                        st.markdown("---")
                        st.subheader("🎁 Recommendations for You")
                        
                        with st.spinner("🎵 Generating recommendations..."):
                            filters = {
                                'popularity_range': popularity_range,
                                'year_range': year_range
                            }
                            
                            recommendations, error = recommend_songs(
                                sp, 
                                track_details, 
                                num_recommendations,
                                filters
                            )
                            
                            if error:
                                st.error(f"❌ {error}")
                            elif not recommendations.empty:
                                fig = visualize_recommendations(track_details, recommendations)
                                if fig:
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                st.markdown("### 🎵 Recommended Songs")
                                
                                for idx, (_, rec_track) in enumerate(recommendations.iterrows(), 1):
                                    with st.expander(f"{idx}. {rec_track['name']} - {rec_track['artist']}", expanded=(idx <= 3)):
                                        display_song_card(rec_track.to_dict(), show_similarity=True)
                            else:
                                st.warning("⚠️ No recommendations found. Try adjusting filters.")
    
    with tab2:
        st.header("🎲 Surprise Me!")
        st.markdown("Get random recommendations based on mood")
        
        mood_choice = st.selectbox(
            "Pick a mood for surprise recommendations",
            ["😊 happy", "😌 chill", "💪 workout", "😢 sad", "🎉 party"],
            key="surprise_mood"
        )
        
        if st.button("🎲 Get Surprise Recommendations", use_container_width=True):
            mood_key = mood_choice.split()[1]  # Extract mood name without emoji
            with st.spinner("🔍 Finding amazing songs..."):
                surprise_recs, error = get_mood_based_recommendations(sp, mood_key, num_recommendations)
                
                if error:
                    st.error(f"❌ {error}")
                elif not surprise_recs.empty:
                    st.success(f"✨ Found {len(surprise_recs)} {mood_key} songs!")
                    
                    for idx, (_, track) in enumerate(surprise_recs.iterrows(), 1):
                        with st.expander(f"{idx}. {track['name']} - {track['artist']}", expanded=(idx <= 3)):
                            display_song_card(track.to_dict())
                else:
                    st.warning("⚠️ No songs found. Try another mood!")
    
    with tab3:
        st.header("📊 Music Analytics")
        st.markdown("Analyze audio features and trends")
        
        if search_query and search_button:
            track, _ = fetch_song(sp, search_query)
            if track:
                track_details, _ = get_track_details(sp, track)
                
                if track_details:
                    features = ['danceability', 'energy', 'valence', 'acousticness', 'liveness']
                    values = [track_details.get(f, 0) for f in features]
                    
                    fig = go.Figure(data=go.Scatterpolar(
                        r=values,
                        theta=features,
                        fill='toself',
                        name='Audio Features'
                    ))
                    
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                        showlegend=False,
                        template='plotly_dark'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.subheader("📈 Feature Breakdown")
                    feature_cols = st.columns(len(features))
                    for i, feature in enumerate(features):
                        with feature_cols[i]:
                            st.metric(feature.capitalize(), f"{values[i]:.2f}")
        else:
            st.info("💡 Search for a song in the 'Search & Recommend' tab to see analytics")


if __name__ == "__main__":
    main()