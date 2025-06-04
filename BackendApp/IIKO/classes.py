from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from uuid import UUID

# class paymentTypeKind(str, Enum):
#     Cash = "Cash"
#     Card = "Card"
#     LoyaltyCard = "LoyaltyCard"
#     External = "External"


# @dataclass
# class Product:
#     id: UUID
#     name: str


# class Size:
#     id: str
#     name: str


@dataclass
class TransactionData:
    sum: int
    balance: int
    orderId: Optional[UUID]
    orderNumber: Optional[str]
    isDelivery: Optional[bool]
    terminalGroupId: Optional[str]
    walletId: UUID
    id: UUID
    organizationId: UUID
    uocId: UUID
    notificationType: int
    customerId: UUID
    phone: str
    transactionType: str
    subscriptionPassword: Optional[str]
    changedOn: str


@dataclass
class rawGuestCategorie:
    id: UUID
    name: str
    isActive: bool
    isDefaultForNewGuests: bool


@dataclass
class guestCategorie:
    id: UUID
    name: str
    isActive: bool
    isDefaultForNewGuests: bool
    cashback: float
    category: Literal["level", "additional"]
    spend_money_amount: Optional[float] = None
    level: Optional[int] = None


@dataclass
class Organization:
    responseType: Literal["Simple", "Extended"]
    id: UUID
    name: str
    code: Optional[str] = None
    externalData: Optional[List[dict]] = None


@dataclass
class OrganizationData:
    correlationId: str
    organizations: List[Organization]


@dataclass
class Combo:
    id: UUID
    name: str
    amount: Union[float, int]
    price: float
    sourceId: UUID
    programId: UUID
    sizeId: Optional[UUID] = None


@dataclass
class Modifier:
    productId: UUID
    amount: float
    productGroupId: Optional[UUID] = None
    price: Optional[float] = None
    positionId: Optional[UUID] = None


@dataclass
class ComboInformation:
    comboId: UUID
    comboSourceId: UUID
    comboGroupId: UUID


@dataclass
class OrderItem:
    productId: UUID
    type: Literal["Product", "Compound"]
    amount: float
    modifiers: Optional[List[Modifier]] = None
    price: Optional[float] = None
    positionId: Optional[UUID] = None
    productSizeId: Optional[UUID] = None
    comboInformation: Optional[ComboInformation] = None
    comment: Optional[str] = None


# class Gender(str, Enum):
#     NotSpecified = "NotSpecified"
#     Male = "Male"
#     Female = "Female"


# class CustomerType(str, Enum):
#     regular = "regular"
#     one_time = "one-time"


# class Type(str, Enum):
#     Product = "Product"
#     Combo = "Combo"


# class Status(str, Enum):
#     Added = "Added"
#     PrintedNotCooking = "PrintedNotCooking"
#     CookingStarted = "CookingStarted"
#     CookingCompleted = "CookingCompleted"
#     Served = "Served"


# class removalType:
#     id: UUID
#     name: str


# class deletionMethod:
#     id: str
#     comment: Optional[str]
#     removalType: removalType


# class Deleted:
#     deletionMethod: deletionMethod


@dataclass
class PaymentAdditionalData:
    credential: str
    searchScope: Literal[
        "Reserved", "Phone", "CardNumber", "CardTrack", "PaymentToken", "FindFaceId"
    ]
    type: Literal["LoyaltyCard"]


# class Kind(str, Enum):
#     Unknown = "Unknown"
#     Cash = "Cash"
#     Card = "Card"
#     Credit = "Credit"
#     Writeoff = "Writeoff"
#     Voucher = "Voucher"
#     External = "External"
#     SmartSale = "SmartSale"
#     Sberbank = "Sberbank"
#     Trpos = "Trpos"


@dataclass
class Tip:
    paymentTypeKind: Literal["Cash", "Card", "LoyaltyCard", "External"]
    tipsTypeId: UUID
    sum: float
    paymentTypeId: UUID
    isProcessedExternally: bool
    isFiscalizedExternally: bool
    isPrepay: bool
    paymentAdditionalData: Optional[PaymentAdditionalData] = None


# class paymentType:
#     id: UUID
#     name: str
#     kind: Kind
#     sum: float
#     isPreliminary: bool
#     isExternal: bool
#     isProcessedExternally: bool
#     isFiscalizedExternally: Optional[bool]
#     isPrepay: bool


@dataclass
class LoyaltyInfo:
    coupon: Optional[str] = None
    applicableManualConditions: Optional[List[UUID]] = None


class ChequeAdditionalInfo:
    needReceipt: bool
    email: Optional[str] = None
    settlementPlace: Optional[str] = None
    phone: Optional[str] = None


class ExternalData:
    key: str
    value: str
    isPublic: Optional[bool] = None


class WalletType(Enum):
    DepositOrCorporateNutrition = 0
    BonusProgram = 1
    ProductsProgram = 2
    DiscountProgram = 3
    CertificateProgram = 4


class Sex(Enum):
    NotSpecified = 0
    Male = 1
    Female = 2


class ConsentStatus(Enum):
    Unknown = 0
    Given = 1
    Revoked = 2


@dataclass
class Payments:
    paymentTypeKind: Literal[
        "Cash",
        "Card",
        "LoyaltyCard",
        "External",
    ]
    sum: float
    paymentTypeId: UUID
    isProcessedExternally: bool
    isFiscalizedExternally: bool
    isPrepay: bool
    paymentAdditionalData: Optional[PaymentAdditionalData] = None


@dataclass
class Card:
    id: UUID
    track: str
    number: str
    validToDate: str


@dataclass
class ReservationOrderDiscountCard:
    track: str


@dataclass
class Discount:
    discountTypeId: UUID
    sum: float
    selectivePositions: Optional[List[UUID]]
    type: Literal["RMS", "iikoCard"]


@dataclass
class DiscountsInfo:
    card: Optional[Union[Card, ReservationOrderDiscountCard]] = None
    discounts: Optional[List[Discount]] = None


@dataclass
class Discount:
    discountTypeId: UUID
    sum: float
    selectivePositions: Optional[List[UUID]]
    type: Literal["RMS", "iikoCard"]


@dataclass
class DiscountsInfo:
    card: Card
    discounts: Optional[List[Discount]]


@dataclass
class Category:
    id: UUID
    name: str
    isActive: bool
    isDefaultForNewGuests: bool


@dataclass
class WalletBalance:
    id: UUID
    name: float
    type: WalletType
    balance: float


@dataclass
class Guests:
    count: int


@dataclass
class CustomerInfo:
    id: Optional[UUID] = None
    referrerId: Optional[UUID] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    middleName: Optional[str] = None
    comment: Optional[str] = None
    phone: Optional[str] = None
    cultureName: Optional[str] = None
    birthday: Optional[str] = None
    email: Optional[str] = None
    sex: Optional[Sex] = None
    consentStatus: Optional[ConsentStatus] = None
    anonymized: Optional[bool] = None
    cards: Optional[List[Card]] = None
    categories: Optional[List[Category]] = None
    walletBalances: Optional[List[WalletBalance]] = None
    userData: Optional[str] = None
    shouldReceivePromoActionsInfo: Optional[bool] = None
    shouldReceiveLoyaltyInfo: Optional[bool] = None
    shouldReceiveOrderStatusInfo: Optional[bool] = None
    personalDataConsentFrom: Optional[str] = None
    personalDataConsentTo: Optional[str] = None
    personalDataProcessingFrom: Optional[str] = None
    personalDataProcessingTo: Optional[str] = None
    isDeleted: Optional[bool] = None


@dataclass
class Order:
    id: Optional[UUID] = None
    items: List[OrderItem] = None
    externalNumber: Optional[str] = None
    tableIds: Optional[List[UUID]] = None
    customer: Optional[CustomerInfo] = None
    phone: Optional[str] = None
    guests: Optional[Guests] = None
    tabName: Optional[str] = None
    menuId: Optional[str] = None
    combos: Optional[List[Combo]] = None
    payments: Optional[List[Payments]] = None
    tips: Optional[List[Tip]] = None
    sourceKey: Optional[str] = None
    discountsInfo: Optional[DiscountsInfo] = None
    loyaltyInfo: Optional[LoyaltyInfo] = None
    orderTypeId: Optional[UUID] = None
    chequeAdditionalInfo: Optional[ChequeAdditionalInfo] = None
    externalData: Optional[List[ExternalData]] = None


@dataclass
class createOrderSettings:
    servicePrint: Optional[bool]
    transportToFrontTimeout: Optional[int]
    checkStopList: bool


@dataclass
class ErrorInfo:
    code: str
    message: str
    additionalData: Any


@dataclass
class orderInfo:
    id: UUID
    posId: UUID
    externalNumber: Optional[str]
    organizationId: UUID
    timestamp: int
    creationStatus: Literal["Success", "InProgress", "Error"]
    errorInfo: Optional[ErrorInfo]
    order: Optional[Order]


@dataclass
class OrderResponse:
    correlationId: UUID
    orders: List[orderInfo]


class OrderCreateResponse:
    correlationId: UUID
    orderInfo: orderInfo


@dataclass
class addOrderItemsSettings:
    servicePrint: Optional[bool] = None


"""
                   РЕЗЕРВАЦИИ
"""


@dataclass
class OrganizationExternalData:
    key: str
    value: str


@dataclass
class Organization:
    id: UUID
    responseType: str
    name: Optional[str] = None
    code: Optional[str] = None
    externalData: Optional[OrganizationExternalData] = None
    # если responseType = extended, тогда будут следующие поля:

    country: Optional[str] = None
    restaurantAddress: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    useUaeAddressingSystem: Optional[bool] = None
    version: Optional[str] = None
    currencyIsoName: Optional[str] = None
    currencyMinimumDenomination: Optional[float] = None
    countryPhoneCode: Optional[str] = None
    marketingSourceRequiredInDelivery: Optional[bool] = None
    defaultDeliveryCityId: Optional[UUID] = None
    deliveryCityIds: Optional[List[UUID]] = None
    deliveryServiceType: Optional[str] = None
    defaultCallCenterPaymentTypeId: Optional[UUID] = None
    orderItemCommentEnabled: Optional[bool] = None
    inn: Optional[str] = None
    addressFormatType: Optional[str] = None
    isConfirmationEnabled: Optional[bool] = None
    confirmAllowedIntervalInMinutes: Optional[int] = None
    isCloud: Optional[bool] = None
    isAnonymousGuestsAllowed: Optional[bool] = None
    addressLookup: Optional[List[str]] = None


@dataclass
class Table:
    id: UUID
    number: int
    name: str
    seatingCapacity: int
    revision: int
    isDeleted: bool
    posId: UUID


@dataclass
class RestaurantSection:
    id: UUID
    terminalGroupId: UUID
    name: str
    tables: List[Table]
    schema: Optional[dict] = None  # Эту вещь я пока не обрабатываю, т.к. она не нужна.


@dataclass
class Reservation:
    id: UUID
    tableIds: List[UUID]
    estimatedStartTime: str
    durationInMinutes: int
    guestsCount: int


@dataclass
class ErrorInfo:
    code: str
    message: Optional[str] = None
    description: Optional[str] = None
    additionalData: Optional[Any] = None


@dataclass
class ReservationCustomer:
    name: str
    type: Literal["regular", "one-time"]
    gender: Optional[Literal["NotSpecified", "Male", "Female"]] = None
    id: Optional[UUID] = None
    birthdate: Optional[str] = None
    inBlacklist: Optional[bool] = None
    blacklistReason: Optional[str] = None
    comment: Optional[str] = None
    surname: Optional[str] = None


@dataclass
class ReservationConcept:
    id: UUID
    name: str
    code: str


@dataclass
class ReservationGuestsInfo:
    count: int
    splitBetweenPersons: bool


@dataclass
class ReservationProduct:
    id: UUID
    name: str


@dataclass
class ReservationProductGroup:
    id: UUID
    name: str


@dataclass
class ReservationDeletionMethodRemovalType:
    id: UUID
    name: str


@dataclass
class ReservationDeletionMethod:
    id: UUID
    removalType: ReservationDeletionMethodRemovalType
    comment: Optional[str] = None


@dataclass
class ReservationDeletionDetails:
    deletionMethod: ReservationDeletionMethod


@dataclass
class ReservationOrderModifiers:
    product: ReservationProduct
    amount: float
    amountIndependentOfParentAmount: bool
    price: float
    pricePredefined: bool
    resultSum: float
    deleted: Optional[ReservationDeletionDetails] = None
    productGroup: Optional[ReservationProductGroup] = None
    positionId: Optional[UUID] = None
    defaultAmount: Optional[int] = None
    hideIfDefaultAmount: Optional[bool] = None
    taxPercent: Optional[float] = None
    freeOfChargeAmount: Optional[int] = None


@dataclass
class ReservationOrderItemSize:
    id: UUID
    name: str


@dataclass
class ReservationComboInformation:
    comboId: UUID
    comboSourceId: UUID
    groupId: UUID


@dataclass
class ReservationOrderPrimaryComponent:
    product: ReservationProduct
    price: float
    cost: float
    pricePredefined: bool
    resultSum: float
    modifiers: Optional[ReservationOrderModifiers] = None
    positionId: Optional[UUID] = None
    taxPercent: Optional[float] = None


@dataclass
class ReservationOrderItemTemplate:
    id: UUID
    name: str


@dataclass
class ReservationOrderItemService:
    id: UUID
    name: str


@dataclass
class ReservationOrderItem:
    type: Literal["Product", "Compound", "Service"]
    status: Literal["Added", "PrintedNotCooking", "CookingStarted", "CookingCompleted", "Served"]
    amount: float
    product: Optional[ReservationProduct] = None
    price: Optional[float] = None
    cost: Optional[float] = None

    pricePredefined: Optional[bool] = None
    resultSum: Optional[float] = None
    modifiers: Optional[List[ReservationOrderModifiers]] = None
    positionId: Optional[UUID] = None
    taxPercent: Optional[float] = None
    deleted: Optional[ReservationDeletionDetails] = None
    comment: Optional[str] = None
    whenPrinted: Optional[str] = None
    size: Optional[ReservationOrderItemSize] = None
    comboInformation: Optional[ReservationComboInformation] = None

    # если type = Compound:
    primaryComponent: Optional[ReservationOrderPrimaryComponent] = None
    secondaryComponent: Optional[ReservationOrderPrimaryComponent] = None
    commonModifiers: Optional[ReservationOrderModifiers] = None
    template: Optional[ReservationOrderItemTemplate] = None

    # если type = service
    service: Optional[ReservationOrderItemService] = None


@dataclass
class ReservationOrderCombo:
    id: UUID
    name: str
    amount: int
    price: float
    sourceId: UUID
    size: ReservationOrderItemSize


@dataclass
class ReservationOrderPaymentType:
    id: UUID
    name: str
    kind: Literal[
        "Unknown",
        "Cash",
        "Card",
        "Credit",
        "Writeoff",
        "Voucher",
        "External",
        "SmartSale",
        "Sberbank",
        "Trpos",
    ]


@dataclass
class ReservationOrderPayment:
    paymentType: ReservationOrderPaymentType
    sum: float
    isPreliminary: bool
    isExternal: bool
    isProcessedExternally: bool
    isFiscalizedExternally: bool
    isPrepay: bool


@dataclass
class ReservationOrderTipType:
    id: UUID
    name: str


@dataclass
class ReservationOrderTip:
    tipsType: ReservationOrderTipType
    paymentType: ReservationOrderPaymentType
    sum: float
    isPreliminary: bool
    isExternal: bool
    isProcessedExternally: bool
    isFiscalizedExternally: bool
    isPrepay: bool


@dataclass
class ReservationOrderDiscountType:
    id: UUID
    name: str


@dataclass
class ReservationOrderItemsPositionsWithPositionDiscountSum:
    positionId: UUID
    sum: float


@dataclass
class ReservationOrderDiscount:
    discountType: ReservationOrderDiscountType
    sum: float
    selectivePositions: Optional[List[UUID]] = None
    selectivePositionsWithSum: Optional[
        List[ReservationOrderItemsPositionsWithPositionDiscountSum]
    ] = None


@dataclass
class ReservationOrderType:
    id: UUID
    name: str
    orderServiceType: Literal["Common", "DeliveryByCourier", "DeliveryByClient"]


@dataclass
class ReservationOrderLoyaltyInfo:
    coupon: Optional[str] = None
    appliedManualConditions: Optional[List[UUID]] = None


@dataclass
class ReservationOrderExternalData:
    key: str
    value: str


@dataclass
class ReservationOrder:
    sum: float
    number: int
    items: List[ReservationOrderItem]
    terminalGroupId: UUID
    menuId: Optional[str] = None
    sourceKey: Optional[str] = None
    whenBillPrinted: Optional[str] = None
    whenClosed: Optional[str] = None
    conception: Optional[ReservationConcept] = None
    guestsInfo: Optional[ReservationGuestsInfo] = None
    combos: Optional[List[ReservationOrderCombo]] = None
    payments: Optional[List[ReservationOrderPayment]] = None
    tips: Optional[List[ReservationOrderTip]] = None
    discounts: Optional[List[ReservationOrderDiscount]] = None
    orderType: Optional[ReservationOrderType] = None
    processedPaymentsSum: Optional[float] = None
    loyaltyInfo: Optional[ReservationOrderLoyaltyInfo] = None
    externalData: Optional[List[ReservationOrderExternalData]] = None


@dataclass
class ReservationInsideReserveInfo:
    customer: ReservationCustomer
    guestsCount: int
    durationInMinutes: int
    shouldRemind: bool
    status: Literal["New", "Started", "Closed"]
    tableIds: List[UUID]
    estimatedStartTime: str
    guestsComingTime: Optional[str]
    comment: Optional[str] = None
    cancelReason: Optional[Literal["ClientNotAppeared", "ClientRefused", "Other"]] = None
    phone: Optional[str] = None
    eventType: Optional[str] = None
    order: Optional[ReservationOrder] = None


@dataclass
class ReserveInfo:
    id: UUID
    organizationId: UUID
    timestamp: int
    creationStatus: Literal["Success", "InProgress", "Error"]
    isDeleted: bool
    errorInfo: Optional[ErrorInfo] = None
    externalNumber: Optional[str] = None
    reserve: Optional[ReservationInsideReserveInfo] = None


@dataclass
class CreatingReservationItemModifier:
    productId: UUID
    amount: float
    productGroupId: Optional[UUID] = None
    price: Optional[float] = None
    positionId: Optional[UUID] = None


@dataclass
class CreatingReservationItem:
    productId: UUID
    amount: float
    type: Literal["Product", "Compound"]
    price: Optional[float] = (
        None  # По идее это не должно быть обязательным, но в апишке - обязательное
    )
    modifiers: Optional[List[CreatingReservationItemModifier]] = None
    positionId: Optional[UUID] = None
    productSizeId: Optional[UUID] = None
    comboInformation: Optional[ComboInformation] = None
    comment: Optional[str] = None


@dataclass
class CreatingReservationOrder:
    """
    Заказ который передаём при создании резервации (банкета в данном случае)
    """

    items: List[CreatingReservationItem]
    menuId: Optional[str] = None
    combos: Optional[List[Combo]] = None
    payments: Optional[List[Payments]] = None
    tips: Optional[List[Tip]] = None
    sourceKey: Optional[str] = None
    discountsInfo: Optional[DiscountsInfo] = None
    loyaltyInfo: Optional[LoyaltyInfo] = None
    orderTypeId: Optional[UUID] = None
    chequeAdditionalInfo: Optional[ChequeAdditionalInfo] = None
    externalData: Optional[List[ExternalData]] = None


@dataclass
class CreatingReservationCustomer:
    gender: Literal["NotSpecified", "Male", "Female"]
    type: Literal["regular", "one-time"]
    id: Optional[UUID] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    comment: Optional[str] = None
    birthdate: Optional[str] = None
    email: Optional[str] = None
    shouldReceivePromoActionsInfo: Optional[bool] = None
    shouldReceiveOrderStatusNotifications: Optional[bool] = None


@dataclass
class CreatingReservationGuest:
    count: int


@dataclass
class CreateReserveSettings:
    checkStopList: bool
    transportToFrontTimeout: Optional[int] = None


@dataclass
class InformationForCreatingReservation:
    organizationId: UUID
    terminalGroupId: UUID
    phone: str
    shouldRemind: bool
    tableIds: List[UUID]
    estimatedStartTime: str
    durationInMinutes: int = 120

    id: Optional[UUID] = None
    externalNumber: Optional[str] = None
    order: Optional[CreatingReservationOrder] = None
    customer: Optional[CreatingReservationCustomer] = None
    guestsCount: Optional[int] = 1
    comment: Optional[str] = None
    transportToFrontTimeout: Optional[int] = None
    eventType: Optional[str] = None
    guests: Optional[CreatingReservationGuest] = None
    createReserveSettings: Optional[CreateReserveSettings] = None


@dataclass
class AdditionalItemsToReservation:
    reserveId: UUID
    organizationId: UUID
    items: List[OrderItem]
    combos: Optional[List[Combo]] = None


@dataclass
class FrontendTableInfo:
    organization_id: UUID

    section_name: str

    table_id: UUID
    table_name: str
    capacity: int
    is_deleted: bool
    table_status: Literal["free", "is_vacant_2h", "busy_now"]


@dataclass
class NotActivatedCoupon:
    id: str
    number: str
    seriesName: str
    seriesId: str
