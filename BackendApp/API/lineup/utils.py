from BackendApp.API.lineup.scheme import *

def parse_artist_into_format(artist):
    return ArtistResponse(
        artist_id=artist.id,
        name=artist.name,
        description=artist.description,
        img_path=artist.img_path
    )
    
def parse_artists_into_format(artists):
    return [parse_artist_into_format(artist) for artist in artists]