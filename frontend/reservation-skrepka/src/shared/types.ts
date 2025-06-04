export type Optional<T, K extends keyof T> = Pick<Partial<T>, K> & Omit<T, K>;

export type Time = `${number}${number}:${number}${number}`;
export type Timestamp = `${number}${number}${number}${number}-${number}${number}-${number}${number}`;
export type TDateTime = `${Timestamp}T${Time}:${number}${number}.${number}${number}${number}Z`;
export type DateString = string;

export type UID = number | string;
export type EventTypeShort = 'free' | 'deposit' | 'event';
export type EventType = 'Депозит' | 'Бесплатная вечеринка' | 'Ивент';
export type TEvent = {
    event_id: number,
    bar_id: number,
    short_name: string,
    img_path: string,
    dateandtime: TDateTime,
    end_datetime?: TDateTime,
    place: string,
    price: number,
    event_type: EventTypeShort,
    description: string,
    age_restriction: number,
}
export type TTicket = {
    id: number,
    event_id: number,
    client_chat_id: number,
    qr_path: string,
    activation_status: boolean,
    friends: GuestInviteForm[] | null,
    hashcode: string,
}
export type GuestInviteForm = {
    name: string,
    username: string,
};

export type ApiResponse = TEvent[];

export type EventSliceState = {
    events: ApiResponse,
    currentBar: string,
    filter: Filter,
    barFilter: number,
    initialApiResponse: ApiResponse,
    status: 'idle' | 'loading' | 'failed',
}

export type UserSliceState = {
    tickets: TTicket[],
    uid: UID,
}

export type BarSliceState = {
    barId: BarId,
    currentBar: BarName,
}

export type Theme = 'light' | 'dark';
export type Filter = 'anyFilter' | 'dateandtime' | 'price';
export type BarId = 1 | 2 | 3;
export type BarName = 'rovesnik' | 'doroshka' | 'skrepka';
export type BarFullName = 'Ровесник' | 'Дорожка' | 'Скрепка';
export type BarFilter = BarName | 'anyBar';
export type EventId = number;
export type ReservationInfo = {
    bar: BarName,
    tableId: number,
    time: string,
    date: Timestamp,
    duration: number,
    guestCount: number,
}
export type TableData = {
    id: number,
    capacity: number,
    location: string,
    status: 'free' | 'reserved' | 'occupied',
}

export type PaymentItem = {
    Name: string,
    Price: number,
    Quantity: number,
    Amount: number,
    Tax: string,
    Ean13: string,
}

export type Receipt = {
    Items?: PaymentItem[],
    Email?: string,
    Phone?: string,
    Taxation?: string,
}

export type AcquiringTransaction = {
    TerminalKey: string,
    Amount: number,
    OrderId: number,
    PaymentId?: number,
    Description: string,
    DATA: {[k: string]: number | string},
    SuccessURL: string,
    FailURL: string,
}

export type ReservationSliceState = {
    tables: TableData[],
    focusedTable: number,
};

export interface TPurchaseFreeTicketResponse {
    status: string,
    message?: string,
    PaymentURL?: string,
}

export interface TPurchaseTicketResponse {
    status: string,
    message?: string,
    error?: {
        Details: string,
        ErrorCode: string,
        Message: string,
        Success: boolean,
    },
    PaymentURL?: string,
}

export interface TInitPaymentResponse {
    Success: boolean,
    PaymentURL: string,
}

export interface TIncreaseLoaltyApiResponse {
    Success: boolean,
}

export interface CreateTransactionApiResponse {
    status: 'Success' | 'Failed',
    message: string,
}

export type Artist = {
    artist_id: number,
    name: string,
    description: string,
    img_path: string
}

export type ArtistEventRelationship = {
    artist_id: number,
    event_id: number,
    relationship_id: number,
}

export type TGetArtistsApiResponse = Artist[];
export type TArtistEventRelationshipApiResponse = ArtistEventRelationship[];