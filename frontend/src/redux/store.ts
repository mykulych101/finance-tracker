import { type Action, configureStore, type ThunkAction } from '@reduxjs/toolkit'
import { authSlice } from './authSlice'
import { currencySlice } from './currencySlice'
import { backendApi } from './api'


export const store = configureStore({
    middleware: (getDefaultMiddleware) => getDefaultMiddleware().concat(backendApi.middleware),
    reducer: {
        auth: authSlice.reducer,
        currency: currencySlice.reducer,
        [backendApi.reducerPath]: backendApi.reducer,
    }
})

export type AppDispatch = typeof store.dispatch
export type RootState = ReturnType<typeof store.getState>
export type AppThunk<ReturnType = void> = ThunkAction<
  ReturnType,
  RootState,
  unknown,
  Action<string>
>
