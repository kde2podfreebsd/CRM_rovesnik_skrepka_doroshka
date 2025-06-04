import {createSlice} from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import { sortEventsByFilter } from '../../shared/utils';
import { RootState } from '../../app/store';
import { initialReservationsSliceState } from '../../shared/constants';

const initialState = initialReservationsSliceState;

export const reservationSlice = createSlice({
    name: 'reservation',
    initialState,
    reducers: {
        setFocusedTable: (state, action: PayloadAction<number>) => {
            state.focusedTable = action.payload;
        }
    }
})

export const { setFocusedTable } = reservationSlice.actions;

export const selectTables = (state: RootState) => state.reservation.tables;
export const selectCurrentTableId = (state: RootState) => state.reservation.focusedTable;
export const selectTableById = (state: RootState, id: number) => selectTables(state).filter(table => table.id === id);

export default reservationSlice.reducer;
