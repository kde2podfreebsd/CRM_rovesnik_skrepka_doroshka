import {createAsyncThunk, createSelector, createSlice} from '@reduxjs/toolkit'
import type { PayloadAction } from '@reduxjs/toolkit'
import {barFullNameMap, initialEventSliceState} from "../../shared/constants";
import { ApiResponse, BarFilter, BarId, BarName, EventId, Filter, TEvent } from '../../shared/types';
import { sortEventsByFilter } from '../../shared/utils';
import { RootState } from '../../app/store';

const initialState = initialEventSliceState;

export const eventSlice = createSlice({
    name: 'event',
    initialState,
    reducers: {
        setEvents: (state, action: PayloadAction<ApiResponse>) => {
            // @ts-ignore
            if (action.payload.message) return;

            state.events = action.payload;
            state.initialApiResponse = action.payload;
        },
        setFilter: (state, action: PayloadAction<Filter>) => {
            state.events = [...state.initialApiResponse];
            state.filter = action.payload;
            if (state.filter !== 'anyFilter')
                state.events.sort((a, b) => sortEventsByFilter(a, b, state.filter))
            console.log(action.payload);
        },
        applyFilters: (state) => {
            state.events = state.initialApiResponse;
            if (state.filter !== 'anyFilter')
                state.events.sort((a, b) => sortEventsByFilter(a, b, state.filter))
            if (state.barFilter !== 0)
                state.events = state.events.filter(event => event.bar_id === state.barFilter)
        },
        setBarFilter: (state, action: PayloadAction<number>) => {
            state.events = [...state.initialApiResponse];
            state.barFilter = action.payload;
            console.log('[STATEBARFILTER]', state.barFilter)
            console.log('[STATEEVENTS]', state.events)
            if (state.barFilter !== 0)
                state.events = state.events.filter(event => event.bar_id == state.barFilter)
        },
        filterBySearchResult: (state, action: PayloadAction<string>) => {
            state.events = [...state.initialApiResponse];
            if (action.payload.length > 0) state.events = state.events.filter(
                event => event.short_name.toLowerCase().includes(action.payload)
            )
        }
    },
})

export const { setEvents, setFilter, setBarFilter, filterBySearchResult, applyFilters } = eventSlice.actions;

export const selectEvents = (state: RootState) => state.events.events;
export const selectEventsByBarId = (state: RootState, barId: BarId) => state.events.events.filter(event => event.bar_id === barId)
export const selectFilter = (state: RootState) => state.events.filter;
export const selectBarFilter = (state: RootState) => state.events.barFilter;
export const selectEventById = createSelector(
    [selectEvents, (state, eventId) => eventId],
    (events, id) => {
        console.log(events)
        return events.filter(event => event.event_id === id)[0]
    }
)

export default eventSlice.reducer;
