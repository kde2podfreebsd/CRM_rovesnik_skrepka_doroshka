export default interface IEvent {
    event_id: number;
    short_name: string;
    description: string;
    img_path: string;
    datetime: string;
    bar_id: number;
    place: string;
    age_restriction: number;
    event_type: string;
    price: number;
}