import { apiEndpoint } from "../../shared/constants"
import { TArtistEventRelationshipApiResponse, TGetArtistsApiResponse } from "../../shared/types"

type TGetArtistsByEventId = (eventId: string | number) => Promise<TGetArtistsApiResponse>
export const getArtistsByEventId: TGetArtistsByEventId = async (eventId) => {
    const artistIds: TArtistEventRelationshipApiResponse = await fetch(`${apiEndpoint}/event/get_related_artists?event_id=${eventId}`, {
        method: 'GET',
    }).then(res => res.json());

    return Promise.all(artistIds.map(({artist_id}) =>
        fetch(`${apiEndpoint}/artist/${artist_id}`).then(res => res.json()
    )));
}