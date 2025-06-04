import { reservationsApiMockResponse, tableDataApiMockResponse } from "../../shared/constants";
import { ReservationInfo, TableData, UID } from "../../shared/types"
import { sleep } from "../../shared/utils"

type TGetReservationsByUID = (uid: UID) => Promise<ReservationInfo[]>
export const getReservationsByUID: TGetReservationsByUID = async (uid) => {
    await sleep(500);

    return Promise.resolve(reservationsApiMockResponse);
}

type TGetTableDataByTableId = (tableId: number) => Promise<TableData>
export const getTableDataByTableId: TGetTableDataByTableId = async (tableId) => {
    await sleep(1000);

    return Promise.resolve(tableDataApiMockResponse);
}