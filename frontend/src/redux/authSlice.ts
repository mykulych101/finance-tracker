import { createSlice } from '@reduxjs/toolkit'
import { backendApi, type UserProfileRead } from './api'

// Define a type for the slice state
interface AuthState {
  access: string | null
  refresh: string | null
  isAuthenticated: boolean
  user: UserProfileRead | null
  userId: number | null
}

const isBrowser = typeof window !== 'undefined'

const initialState: AuthState = {
  access: isBrowser ? localStorage.getItem('access') : null,
  isAuthenticated: isBrowser ? !!localStorage.getItem('access') : false,
  refresh: isBrowser ? localStorage.getItem('refresh') : null,
  user: null,
  userId: isBrowser && localStorage.getItem('userId') ? Number(localStorage.getItem('userId')) : null,
}
export const authSlice = createSlice({
  extraReducers: (builder) => {
    builder.addMatcher(backendApi.endpoints.registerCreate.matchFulfilled, (state, { payload }) => {
      state.access = payload.access
      state.refresh = payload.refresh
      state.isAuthenticated = true
      localStorage.setItem('access', payload.access)
      localStorage.setItem('refresh', payload.refresh)
    })
    builder.addMatcher(backendApi.endpoints.loginCreate.matchFulfilled, (state, { payload }) => {
      state.access = payload.access
      state.refresh = payload.refresh
      state.isAuthenticated = true
      localStorage.setItem('access', payload.access)
      localStorage.setItem('refresh', payload.refresh)
    })
    builder.addMatcher(backendApi.endpoints.logoutCreate.matchFulfilled, (state) => {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('userId')
      state.access = null
      state.refresh = null
      state.isAuthenticated = false
      state.user = null
      state.userId = null
    })
    builder.addMatcher(
      backendApi.endpoints.profileRetrieve.matchFulfilled,
      (state, { payload }) => {
        state.user = payload
        state.userId = payload.id
        localStorage.setItem('userId', String(payload.id))
      }
    )
  },
  initialState,
  name: 'auth',
  reducers: {
    logout: (state) => {
      localStorage.removeItem('access')
      localStorage.removeItem('refresh')
      localStorage.removeItem('userId')
      state.access = null
      state.refresh = null
      state.isAuthenticated = false
      state.user = null
      state.userId = null
    },
    override_token(_, action) {
      localStorage.setItem('access', action.payload.access)
    },
    refreshToken: (state, action) => {
      state.access = action.payload.access
      localStorage.setItem('access', action.payload.access)
    },
  },
})

export const { logout, override_token, refreshToken } = authSlice.actions

export default authSlice.reducer
