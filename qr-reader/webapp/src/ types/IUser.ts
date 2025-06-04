interface LoyaltyLevel {
    id: string;
    name: string;
    isActive: boolean;
    isDefaultForNewGuests: boolean;
    cashback: number;
    category: string;
    spend_money_amount: number;
    level: number;
}

export default interface IUser {
    chat_id: number;
    iiko_id: string;
    iiko_card: string;
    username: string;
    first_name: string;
    last_name: string | null;
    spent_amount: number;
    qr_code_path: string | null;
    referral_link: string;
    balance: number;
    loyalty_info: LoyaltyLevel[];
}
