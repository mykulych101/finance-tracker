import { createSlice, type PayloadAction } from '@reduxjs/toolkit'
import type { CurrencyEnum } from './api'

interface CurrencyState {
  convertTo: CurrencyEnum | null
}

const stored = typeof window !== 'undefined' ? localStorage.getItem('convertTo') : null

const initialState: CurrencyState = {
  convertTo: (stored as CurrencyEnum | null) ?? null,
}

export const currencySlice = createSlice({
  name: 'currency',
  initialState,
  reducers: {
    setConvertTo(state, action: PayloadAction<CurrencyEnum | null>) {
      state.convertTo = action.payload
      if (action.payload) {
        localStorage.setItem('convertTo', action.payload)
      } else {
        localStorage.removeItem('convertTo')
      }
    },
  },
})

export const { setConvertTo } = currencySlice.actions
