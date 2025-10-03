"""
Utility functions for Smart Music Recommender
Separates business logic from UI code for better maintainability
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from typing import Dict, List, Optional, Tuple
import spotipy

class SpotifyDataProcessor:
    """Handles all Spotify API data processing and feature extraction"""
    
    def __init__(self, sp: spotipy.Spotify):
        self.sp = sp
        self.feature_columns = [
            'danceability', 'energy', 'valence', 'tempo',
            'acousticness', 'liveness', 'instrumentalness',
            'loudness', 'speechiness'
        ]
    
    def search_track(self, query: str, limit: int = 1) -> Optional[Dict]:
        """
        Search for a track on Spotify
        
        Args:
            query: Search query (song name or artist)
            limit: Number of results to return
            
        Returns:
            Track object or None if not found
        """
        try:
            results = self.sp.search(q=query, type='track', limit=limit)
            if results['tracks']['items']:
                return results['tracks']['items'][0]
            return None
        except Exception as e:
            print(f"Error searching track: {str(e)}")
            return None
    
    def get_audio_features(self, track_id: str) -> Optional[Dict]:
        """
        Get audio features for a track
        
        Args:
            track_id: Spotify track ID
            
        Returns:
            Audio features dictionary or None
        """
        try:
            features = self.sp.audio_features(track_id)
            return features[0] if features else None
        except Exception as e:
            print(f"Error fetching audio features: {str(e)}")
            return None
    
    def extract_track_info(self, track: Dict) -> Optional[Dict]:
        """
        Extract comprehensive track information including audio features
        
        Args:
            track: Spotify track object
            
        Returns:
            Dictionary with track details and audio features
        """
        try:
            audio_features = self.get_audio_features(track['id'])
            
            info = {
                'id': track['id'],
                'name': track['name'],
                'artist': ', '.join([artist['name'] for artist in track['artists']]),
                'album': track['album']['name'],
                'image_url': track['album']['images'][0]['url'] if track['album']['images'] else None,
                'preview_url': track['preview_url'],
                'popularity': track['popularity'],
                'release_date': track['album']['release_date'],
                'duration_ms': track['duration_ms'],
                'external_url': track['external_urls']['spotify']
            }
            
            if audio_features:
                info.update({
                    'danceability': audio_features['danceability'],
                    'energy': audio_features['energy'],
                    'valence': audio_features['valence'],
                    'tempo': audio_features['tempo'],
                    'acousticness': audio_features['acousticness'],
                    'liveness': audio_features['liveness'],
                    'instrumentalness': audio_features['instrumentalness'],
                    'loudness': audio_features['loudness'],
                    'speechiness': audio_features['speechiness'],
                    'key': audio_features['key'],
                    'mode': audio_features['mode']
                })
            
            return info
        except Exception as e:
            print(f"Error extracting track info: {str(e)}")
            return None
    
    def get_recommendations_pool(self, seed_track_id: str, limit: int = 50) -> pd.DataFrame:
        """
        Get a pool of recommended tracks from Spotify
        
        Args:
            seed_track_id: Track ID to base recommendations on
            limit: Number of recommendations to fetch
            
        Returns:
            DataFrame with track information
        """
        try:
            recommendations = self.sp.recommendations(
                seed_tracks=[seed_track_id],
                limit=limit
            )
            
            tracks_data = []
            for track in recommendations['tracks']:
                track_info = self.extract_track_info(track)
                if track_info:
                    tracks_data.append(track_info)
            
            return pd.DataFrame(tracks_data)
        except Exception as e:
            print(f"Error getting recommendations: {str(e)}")
            return pd.DataFrame()


class RecommendationEngine:
    """Content-based recommendation engine using audio features"""
    
    def __init__(self, feature_columns: List[str]):
        self.feature_columns = feature_columns
        self.scaler = StandardScaler()
    
    def calculate_similarity(
        self,
        seed_features: Dict,
        candidate_df: pd.DataFrame
    ) -> pd.DataFrame:
        """
        Calculate cosine similarity between seed track and candidates
        
        Args:
            seed_features: Dictionary of audio features for seed track
            candidate_df: DataFrame with candidate tracks
            
        Returns:
            DataFrame with similarity scores
        """
        try:
            # Prepare feature matrices
            seed_vector = np.array([[seed_features.get(col, 0) for col in self.feature_columns]])
            candidate_features = candidate_df[self.feature_columns].fillna(0).values
            
            # Normalize features
            all_features = np.vstack([seed_vector, candidate_features])
            normalized_features = self.scaler.fit_transform(all_features)
            
            seed_normalized = normalized_features[0:1]
            candidates_normalized = normalized_features[1:]
            
            # Calculate cosine similarity
            similarities = cosine_similarity(seed_normalized, candidates_normalized)[0]
            
            result_df = candidate_df.copy()
            result_df['similarity'] = similarities
            
            return result_df
        except Exception as e:
            print(f"Error calculating similarity: {str(e)}")
            return candidate_df
    
    def apply_filters(
        self,
        df: pd.DataFrame,
        popularity_range: Optional[Tuple[int, int]] = None,
        year_range: Optional[Tuple[int, int]] = None
    ) -> pd.DataFrame:
        """
        Apply filters to recommendation candidates
        
        Args:
            df: DataFrame with tracks
            popularity_range: Tuple of (min, max) popularity
            year_range: Tuple of (min, max) year
            
        Returns:
            Filtered DataFrame
        """
        filtered_df = df.copy()
        
        if popularity_range:
            filtered_df = filtered_df[
                (filtered_df['popularity'] >= popularity_range[0]) &
                (filtered_df['popularity'] <= popularity_range[1])
            ]
        
        if year_range:
            filtered_df['year'] = pd.to_datetime(filtered_df['release_date']).dt.year
            filtered_df = filtered_df[
                (filtered_df['year'] >= year_range[0]) &
                (filtered_df['year'] <= year_range[1])
            ]
        
        return filtered_df
    
    def recommend(
        self,
        seed_track: Dict,
        candidates_df: pd.DataFrame,
        n: int = 10,
        filters: Optional[Dict] = None
    ) -> pd.DataFrame:
        """
        Generate recommendations for a seed track
        
        Args:
            seed_track: Dictionary with seed track features
            candidates_df: DataFrame with candidate tracks
            n: Number of recommendations to return
            filters: Optional filters (popularity_range, year_range)
            
        Returns:
            DataFrame with top N recommendations
        """
        # Apply filters if provided
        if filters:
            candidates_df = self.apply_filters(
                candidates_df,
                filters.get('popularity_range'),
                filters.get('year_range')
            )
        
        if candidates_df.empty:
            return pd.DataFrame()
        
        # Calculate similarity
        df_with_similarity = self.calculate_similarity(seed_track, candidates_df)
        
        # Sort by similarity and return top N
        recommendations = df_with_similarity.nlargest(n, 'similarity')
        
        return recommendations


class VisualizationHelper:
    """Helper class for creating visualizations"""
    
    @staticmethod
    def prepare_pca_data(df: pd.DataFrame, feature_columns: List[str]) -> pd.DataFrame:
        """
        Prepare data for PCA visualization
        
        Args:
            df: DataFrame with tracks
            feature_columns: List of feature column names
            
        Returns:
            DataFrame with PCA coordinates
        """
        try:
            features = df[feature_columns].fillna(0).values
            
            # Normalize features
            scaler = StandardScaler()
            features_normalized = scaler.fit_transform(features)
            
            # Apply PCA
            pca = PCA(n_components=2)
            coords = pca.fit_transform(features_normalized)
            
            result_df = df.copy()
            result_df['pca_x'] = coords[:, 0]
            result_df['pca_y'] = coords[:, 1]
            result_df['explained_variance'] = pca.explained_variance_ratio_
            
            return result_df
        except Exception as e:
            print(f"Error preparing PCA data: {str(e)}")
            return df
    
    @staticmethod
    def get_audio_profile(track: Dict, features: List[str]) -> Dict[str, float]:
        """
        Extract audio profile for radar chart
        
        Args:
            track: Track dictionary with features
            features: List of feature names
            
        Returns:
            Dictionary with feature values
        """
        return {feature: track.get(feature, 0) for feature in features}


class MoodRecommender:
    """Mood-based recommendation system"""
    
    MOOD_PARAMETERS = {
        'happy': {
            'target_valence': 0.8,
            'target_energy': 0.7,
            'target_danceability': 0.7
        },
        'chill': {
            'target_valence': 0.5,
            'target_energy': 0.3,
            'target_acousticness': 0.6
        },
        'workout': {
            'target_energy': 0.85,
            'target_tempo': 140,
            'target_danceability': 0.7
        },
        'sad': {
            'target_valence': 0.2,
            'target_energy': 0.3,
            'target_acousticness': 0.5
        },
        'party': {
            'target_danceability': 0.85,
            'target_energy': 0.8,
            'target_valence': 0.7
        }
    }
    
    def __init__(self, sp: spotipy.Spotify):
        self.sp = sp
        self.data_processor = SpotifyDataProcessor(sp)
    
    def get_mood_recommendations(
        self,
        mood: str,
        limit: int = 10
    ) -> pd.DataFrame:
        """
        Get recommendations based on mood
        
        Args:
            mood: Mood string (happy, chill, workout, sad, party)
            limit: Number of recommendations
            
        Returns:
            DataFrame with recommendations
        """
        if mood not in self.MOOD_PARAMETERS:
            return pd.DataFrame()
        
        try:
            params = self.MOOD_PARAMETERS[mood]
            
            # Get recommendations from Spotify with mood parameters
            recommendations = self.sp.recommendations(
                seed_genres=[mood] if mood != 'workout' else ['rock', 'electronic'],
                limit=limit,
                **params
            )
            
            tracks_data = []
            for track in recommendations['tracks']:
                track_info = self.data_processor.extract_track_info(track)
                if track_info:
                    tracks_data.append(track_info)
            
            return pd.DataFrame(tracks_data)
        except Exception as e:
            print(f"Error getting mood recommendations: {str(e)}")
            return pd.DataFrame()


def format_duration(duration_ms: int) -> str:
    """
    Format duration from milliseconds to MM:SS
    
    Args:
        duration_ms: Duration in milliseconds
        
    Returns:
        Formatted string (MM:SS)
    """
    seconds = int(duration_ms / 1000)
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes}:{seconds:02d}"


def calculate_feature_stats(df: pd.DataFrame, feature_columns: List[str]) -> Dict:
    """
    Calculate statistics for audio features
    
    Args:
        df: DataFrame with tracks
        feature_columns: List of feature column names
        
    Returns:
        Dictionary with statistics
    """
    stats = {}
    for col in feature_columns:
        if col in df.columns:
            stats[col] = {
                'mean': df[col].mean(),
                'std': df[col].std(),
                'min': df[col].min(),
                'max': df[col].max()
            }
    return stats