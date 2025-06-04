from BackendApp.API.event.scheme import *
from BackendApp.Database.Models.event_model import Event
from BackendApp.Database.Models.atrist_event_relationship_model import ArtistEventRelationship


def parse_event_into_format(event: Event):
    return EventForReturn(
        event_id=event.id,
        short_name=event.short_name,
        description=event.description,
        img_path=event.img_path,
        dateandtime=event.datetime,
        end_datetime=event.end_datetime,
        bar_id=event.bar_id,
        place=event.place,
        age_restriction=event.age_restriction,
        event_type=event.event_type,
        price=event.price,
        notification_time=event.notification_time,
        motto=event.motto
    )
    
def parse_events_into_format(events):
    return [parse_event_into_format(event) for event in events]

def parse_relationship_into_format(relationship: ArtistEventRelationship):
    return EventArtistRelationshipResponse(
        relationship_id=relationship.id,
        event_id=relationship.event_id,
        artist_id=relationship.artist_id
    )
    
def parse_relationships_into_format(relationships):
    return [parse_relationship_into_format(relationship) for relationship in relationships]

