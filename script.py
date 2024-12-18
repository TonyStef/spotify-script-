import spotipy
from spotipy.oauth2 import SpotifyOAuth

CLIENT_ID = "your client id"  
CLIENT_SECRET = "your client secret" 
REDIRECT_URI = "http://localhost:8888/callback" 


SCOPE = "user-library-read playlist-modify-public playlist-modify-private"
def update_playlist_with_new_tracks(artist_names, playlist_name):

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                                   client_secret=CLIENT_SECRET,
                                                   redirect_uri=REDIRECT_URI,
                                                   scope=SCOPE))
    user_profile = sp.current_user()
    user_id = user_profile["id"]
    print(f"Successfully authenticated as: {user_profile['display_name']} ({user_id})")

    print("Fetching your liked songs...")
    liked_tracks = []
    results = sp.current_user_saved_tracks(limit=50)
    while results:
        for item in results["items"]:
            track = item["track"]
            liked_tracks.append({
                "name": track["name"],
                "artist": track["artists"][0]["name"],
                "uri": track["uri"]
            })
        results = sp.next(results)  
    
    print(f"Total liked songs fetched: {len(liked_tracks)}")

    filtered_tracks = [track for track in liked_tracks if track["artist"].lower() in [a.lower() for a in artist_names]]
    if not filtered_tracks:
        print("No tracks found for the specified artists in your liked songs.")
        return

    print(f"Searching for an existing playlist named '{playlist_name}'...")
    playlists = sp.current_user_playlists()
    playlist_id = None
    for playlist in playlists["items"]:
        if playlist["name"].lower() == playlist_name.lower():
            playlist_id = playlist["id"]
            break

    if not playlist_id:
        print(f"No playlist found with the name '{playlist_name}'. Creating a new one.")
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
        playlist_id = playlist["id"]

    print(f"Fetching existing tracks in the playlist '{playlist_name}'...")
    existing_tracks = []
    results = sp.playlist_tracks(playlist_id)
    while results:
        for item in results["items"]:
            track = item["track"]
            existing_tracks.append(track["uri"])
        results = sp.next(results)

    new_tracks = [track["uri"] for track in filtered_tracks if track["uri"] not in existing_tracks]
    print(f"Found {len(new_tracks)} new tracks to add.")

    for i in range(0, len(new_tracks), 100):
        sp.playlist_add_items(playlist_id, new_tracks[i:i + 100])
        print(f"Added tracks {i + 1} to {min(i + 100, len(new_tracks))} to the playlist.")

    print(f"Playlist '{playlist_name}' has been updated with {len(new_tracks)} new tracks.")

if __name__ == "__main__":
    print("Enter artist names separated by commas (e.g., Drake, Taylor Swift):")
    artist_names_input = input("Artists: ")
    artist_names = [name.strip() for name in artist_names_input.split(",")]

    playlist_name = input("Enter the name of the playlist to update (or create): ")
    
    update_playlist_with_new_tracks(artist_names, playlist_name)
