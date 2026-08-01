import { baseApi as api } from "./baseApi";
export const addTagTypes = [
  "accounts",
  "activate",
  "analytics",
  "balances",
  "change-password",
  "authentication",
  "logout",
  "profile",
  "token",
  "transactions",
] as const;
const injectedRtkApi = api
  .enhanceEndpoints({
    addTagTypes,
  })
  .injectEndpoints({
    endpoints: (build) => ({
      accountsList: build.query<AccountsListApiResponse, AccountsListApiArg>({
        query: (queryArg) => ({
          url: `/api/accounts/`,
          params: {
            convert_to: queryArg.convertTo,
            page: queryArg.page,
            page_size: queryArg.pageSize,
          },
        }),
        providesTags: ["accounts"],
      }),
      accountsCreate: build.mutation<
        AccountsCreateApiResponse,
        AccountsCreateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/accounts/`,
          method: "POST",
          body: queryArg.writeAccount,
        }),
        invalidatesTags: ["accounts"],
      }),
      accountsRetrieve: build.query<
        AccountsRetrieveApiResponse,
        AccountsRetrieveApiArg
      >({
        query: (queryArg) => ({ url: `/api/accounts/${queryArg.id}/` }),
        providesTags: ["accounts"],
      }),
      accountsUpdate: build.mutation<
        AccountsUpdateApiResponse,
        AccountsUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/accounts/${queryArg.id}/`,
          method: "PUT",
          body: queryArg.writeAccount,
        }),
        invalidatesTags: ["accounts"],
      }),
      accountsPartialUpdate: build.mutation<
        AccountsPartialUpdateApiResponse,
        AccountsPartialUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/accounts/${queryArg.id}/`,
          method: "PATCH",
          body: queryArg.patchedWriteAccount,
        }),
        invalidatesTags: ["accounts"],
      }),
      accountsDestroy: build.mutation<
        AccountsDestroyApiResponse,
        AccountsDestroyApiArg
      >({
        query: (queryArg) => ({
          url: `/api/accounts/${queryArg.id}/`,
          method: "DELETE",
        }),
        invalidatesTags: ["accounts"],
      }),
      accountsImportTransactionCreate: build.mutation<
        AccountsImportTransactionCreateApiResponse,
        AccountsImportTransactionCreateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/accounts/${queryArg.id}/import_transaction/`,
          method: "POST",
          body: queryArg.body,
        }),
        invalidatesTags: ["accounts"],
      }),
      accountsAutocompleteList: build.query<
        AccountsAutocompleteListApiResponse,
        AccountsAutocompleteListApiArg
      >({
        query: (queryArg) => ({
          url: `/api/accounts/autocomplete/`,
          params: {
            page: queryArg.page,
            page_size: queryArg.pageSize,
          },
        }),
        providesTags: ["accounts"],
      }),
      activateRetrieve: build.query<
        ActivateRetrieveApiResponse,
        ActivateRetrieveApiArg
      >({
        query: (queryArg) => ({
          url: `/api/activate/${queryArg.uidb64}/${queryArg.token}/`,
        }),
        providesTags: ["activate"],
      }),
      analyticsNetWorthHistoryList: build.query<
        AnalyticsNetWorthHistoryListApiResponse,
        AnalyticsNetWorthHistoryListApiArg
      >({
        query: (queryArg) => ({
          url: `/api/analytics/net-worth-history/`,
          params: {
            account: queryArg.account,
            convert_to: queryArg.convertTo,
            date_after: queryArg.dateAfter,
            date_before: queryArg.dateBefore,
            id: queryArg.id,
            period: queryArg.period,
          },
        }),
        providesTags: ["analytics"],
      }),
      analyticsNetWorthRetrieve: build.query<
        AnalyticsNetWorthRetrieveApiResponse,
        AnalyticsNetWorthRetrieveApiArg
      >({
        query: (queryArg) => ({
          url: `/api/analytics/net_worth/`,
          params: {
            convert_to: queryArg.convertTo,
            date: queryArg.date,
          },
        }),
        providesTags: ["analytics"],
      }),
      balancesList: build.query<BalancesListApiResponse, BalancesListApiArg>({
        query: (queryArg) => ({
          url: `/api/balances/`,
          params: {
            date: queryArg.date,
            page: queryArg.page,
            page_size: queryArg.pageSize,
          },
        }),
        providesTags: ["balances"],
      }),
      balancesCreate: build.mutation<
        BalancesCreateApiResponse,
        BalancesCreateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/balances/`,
          method: "POST",
          body: queryArg.balanceRecord,
        }),
        invalidatesTags: ["balances"],
      }),
      balancesRetrieve: build.query<
        BalancesRetrieveApiResponse,
        BalancesRetrieveApiArg
      >({
        query: (queryArg) => ({ url: `/api/balances/${queryArg.id}/` }),
        providesTags: ["balances"],
      }),
      balancesDestroy: build.mutation<
        BalancesDestroyApiResponse,
        BalancesDestroyApiArg
      >({
        query: (queryArg) => ({
          url: `/api/balances/${queryArg.id}/`,
          method: "DELETE",
        }),
        invalidatesTags: ["balances"],
      }),
      balancesBulkCreateCreate: build.mutation<
        BalancesBulkCreateCreateApiResponse,
        BalancesBulkCreateCreateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/balances/bulk-create/`,
          method: "POST",
          body: queryArg.body,
        }),
        invalidatesTags: ["balances"],
      }),
      balancesLatestRetrieve: build.query<
        BalancesLatestRetrieveApiResponse,
        BalancesLatestRetrieveApiArg
      >({
        query: (queryArg) => ({
          url: `/api/balances/latest/`,
          params: {
            date: queryArg.date,
          },
        }),
        providesTags: ["balances"],
      }),
      changePasswordUpdate: build.mutation<
        ChangePasswordUpdateApiResponse,
        ChangePasswordUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/change-password/`,
          method: "PUT",
          body: queryArg.changePassword,
        }),
        invalidatesTags: ["change-password"],
      }),
      changePasswordPartialUpdate: build.mutation<
        ChangePasswordPartialUpdateApiResponse,
        ChangePasswordPartialUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/change-password/`,
          method: "PATCH",
          body: queryArg.patchedChangePassword,
        }),
        invalidatesTags: ["change-password"],
      }),
      loginCreate: build.mutation<LoginCreateApiResponse, LoginCreateApiArg>({
        query: (queryArg) => ({
          url: `/api/login/`,
          method: "POST",
          body: queryArg.myTokenObtainPair,
        }),
        invalidatesTags: ["authentication"],
      }),
      logoutCreate: build.mutation<LogoutCreateApiResponse, LogoutCreateApiArg>(
        {
          query: (queryArg) => ({
            url: `/api/logout/`,
            method: "POST",
            body: queryArg.logout,
          }),
          invalidatesTags: ["logout"],
        },
      ),
      profileRetrieve: build.query<
        ProfileRetrieveApiResponse,
        ProfileRetrieveApiArg
      >({
        query: () => ({ url: `/api/profile/` }),
        providesTags: ["profile"],
      }),
      profileUpdate: build.mutation<
        ProfileUpdateApiResponse,
        ProfileUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/profile/`,
          method: "PUT",
          body: queryArg.userProfile,
        }),
        invalidatesTags: ["profile"],
      }),
      profilePartialUpdate: build.mutation<
        ProfilePartialUpdateApiResponse,
        ProfilePartialUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/profile/`,
          method: "PATCH",
          body: queryArg.patchedUserProfile,
        }),
        invalidatesTags: ["profile"],
      }),
      registerCreate: build.mutation<
        RegisterCreateApiResponse,
        RegisterCreateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/register/`,
          method: "POST",
          body: queryArg.user,
        }),
        invalidatesTags: ["authentication"],
      }),
      tokenCreate: build.mutation<TokenCreateApiResponse, TokenCreateApiArg>({
        query: (queryArg) => ({
          url: `/api/token/`,
          method: "POST",
          body: queryArg.tokenObtainPair,
        }),
        invalidatesTags: ["token"],
      }),
      tokenRefreshCreate: build.mutation<
        TokenRefreshCreateApiResponse,
        TokenRefreshCreateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/token/refresh/`,
          method: "POST",
          body: queryArg.tokenRefresh,
        }),
        invalidatesTags: ["token"],
      }),
      transactionsList: build.query<
        TransactionsListApiResponse,
        TransactionsListApiArg
      >({
        query: (queryArg) => ({
          url: `/api/transactions/`,
          params: {
            account: queryArg.account,
            amount_max: queryArg.amountMax,
            amount_min: queryArg.amountMin,
            date_after: queryArg.dateAfter,
            date_before: queryArg.dateBefore,
            description: queryArg.description,
            is_system: queryArg.isSystem,
            ordering: queryArg.ordering,
            page: queryArg.page,
            page_size: queryArg.pageSize,
            raw_category: queryArg.rawCategory,
            type: queryArg["type"],
          },
        }),
        providesTags: ["transactions"],
      }),
      transactionsCreate: build.mutation<
        TransactionsCreateApiResponse,
        TransactionsCreateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/transactions/`,
          method: "POST",
          body: queryArg.writeTransaction,
        }),
        invalidatesTags: ["transactions"],
      }),
      transactionsRetrieve: build.query<
        TransactionsRetrieveApiResponse,
        TransactionsRetrieveApiArg
      >({
        query: (queryArg) => ({ url: `/api/transactions/${queryArg.id}/` }),
        providesTags: ["transactions"],
      }),
      transactionsUpdate: build.mutation<
        TransactionsUpdateApiResponse,
        TransactionsUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/transactions/${queryArg.id}/`,
          method: "PUT",
          body: queryArg.writeTransaction,
        }),
        invalidatesTags: ["transactions"],
      }),
      transactionsPartialUpdate: build.mutation<
        TransactionsPartialUpdateApiResponse,
        TransactionsPartialUpdateApiArg
      >({
        query: (queryArg) => ({
          url: `/api/transactions/${queryArg.id}/`,
          method: "PATCH",
          body: queryArg.patchedWriteTransaction,
        }),
        invalidatesTags: ["transactions"],
      }),
      transactionsDestroy: build.mutation<
        TransactionsDestroyApiResponse,
        TransactionsDestroyApiArg
      >({
        query: (queryArg) => ({
          url: `/api/transactions/${queryArg.id}/`,
          method: "DELETE",
        }),
        invalidatesTags: ["transactions"],
      }),
    }),
    overrideExisting: false,
  });
export { injectedRtkApi as backendApi };
export type AccountsListApiResponse =
  /** status 200  */ PaginatedAccountListRead;
export type AccountsListApiArg = {
  /** Convert all balances to. this currency. */
  convertTo?: "EUR" | "UAH" | "USD";
  /** A page number within the paginated result set. */
  page?: number;
  /** Number of results to return per page. */
  pageSize?: number;
};
export type AccountsCreateApiResponse = /** status 201  */ WriteAccount;
export type AccountsCreateApiArg = {
  writeAccount: WriteAccount;
};
export type AccountsRetrieveApiResponse = /** status 200  */ AccountRead;
export type AccountsRetrieveApiArg = {
  /** A unique integer value identifying this Account. */
  id: number;
};
export type AccountsUpdateApiResponse = /** status 200  */ WriteAccount;
export type AccountsUpdateApiArg = {
  /** A unique integer value identifying this Account. */
  id: number;
  writeAccount: WriteAccount;
};
export type AccountsPartialUpdateApiResponse = /** status 200  */ WriteAccount;
export type AccountsPartialUpdateApiArg = {
  /** A unique integer value identifying this Account. */
  id: number;
  patchedWriteAccount: PatchedWriteAccount;
};
export type AccountsDestroyApiResponse = unknown;
export type AccountsDestroyApiArg = {
  /** A unique integer value identifying this Account. */
  id: number;
};
export type AccountsImportTransactionCreateApiResponse = unknown;
export type AccountsImportTransactionCreateApiArg = {
  /** A unique integer value identifying this Account. */
  id: number;
  body: {
    /** Transaction file to import. Accepted formats: .csv, .xlsx */
    file?: Blob;
  };
};
export type AccountsAutocompleteListApiResponse =
  /** status 200  */ PaginatedAccountSlimListRead;
export type AccountsAutocompleteListApiArg = {
  /** A page number within the paginated result set. */
  page?: number;
  /** Number of results to return per page. */
  pageSize?: number;
};
export type ActivateRetrieveApiResponse = unknown;
export type ActivateRetrieveApiArg = {
  token: string;
  uidb64: string;
};
export type AnalyticsNetWorthHistoryListApiResponse =
  /** status 200  */ AnalyticsNetWorthHistoryItem[];
export type AnalyticsNetWorthHistoryListApiArg = {
  account?: number;
  /** Convert all balances to this currency. */
  convertTo?: "EUR" | "UAH" | "USD";
  dateAfter?: string;
  dateBefore?: string;
  id?: number;
  /** * `daily` - Daily
   * `weekly` - Weekly
   * `monthly` - Monthly */
  period?: "daily" | "monthly" | "weekly";
};
export type AnalyticsNetWorthRetrieveApiResponse =
  /** status 200  */ AnalyticsNetWorthRead;
export type AnalyticsNetWorthRetrieveApiArg = {
  /** Convert all balances to this currency. */
  convertTo?: "EUR" | "UAH" | "USD";
  /** As-of date (YYYY-MM-DD). Defaults to today. */
  date?: string;
};
export type BalancesListApiResponse =
  /** status 200  */ PaginatedBalanceRecordListRead;
export type BalancesListApiArg = {
  date?: string;
  /** A page number within the paginated result set. */
  page?: number;
  /** Number of results to return per page. */
  pageSize?: number;
};
export type BalancesCreateApiResponse = /** status 201  */ BalanceRecordRead;
export type BalancesCreateApiArg = {
  balanceRecord: BalanceRecord;
};
export type BalancesRetrieveApiResponse = /** status 200  */ BalanceRecordRead;
export type BalancesRetrieveApiArg = {
  /** A unique integer value identifying this Balance Record. */
  id: number;
};
export type BalancesDestroyApiResponse = unknown;
export type BalancesDestroyApiArg = {
  /** A unique integer value identifying this Balance Record. */
  id: number;
};
export type BalancesBulkCreateCreateApiResponse = unknown;
export type BalancesBulkCreateCreateApiArg = {
  body: BalanceRecord[];
};
export type BalancesLatestRetrieveApiResponse =
  /** status 200  */ BalanceRecordRead;
export type BalancesLatestRetrieveApiArg = {
  date?: string;
};
export type ChangePasswordUpdateApiResponse = /** status 200  */ ChangePassword;
export type ChangePasswordUpdateApiArg = {
  changePassword: ChangePassword;
};
export type ChangePasswordPartialUpdateApiResponse =
  /** status 200  */ ChangePassword;
export type ChangePasswordPartialUpdateApiArg = {
  patchedChangePassword: PatchedChangePassword;
};
export type LoginCreateApiResponse = /** status 200  */ LoginResponse;
export type LoginCreateApiArg = {
  myTokenObtainPair: MyTokenObtainPairWrite;
};
export type LogoutCreateApiResponse = unknown;
export type LogoutCreateApiArg = {
  logout: Logout;
};
export type ProfileRetrieveApiResponse = /** status 200  */ UserProfileRead;
export type ProfileRetrieveApiArg = void;
export type ProfileUpdateApiResponse = /** status 200  */ UserProfileRead;
export type ProfileUpdateApiArg = {
  userProfile: UserProfile;
};
export type ProfilePartialUpdateApiResponse =
  /** status 200  */ UserProfileRead;
export type ProfilePartialUpdateApiArg = {
  patchedUserProfile: PatchedUserProfile;
};
export type RegisterCreateApiResponse = /** status 201  */ RegisterResponseRead;
export type RegisterCreateApiArg = {
  user: UserWrite;
};
export type TokenCreateApiResponse = /** status 200  */ TokenObtainPairRead;
export type TokenCreateApiArg = {
  tokenObtainPair: TokenObtainPairWrite;
};
export type TokenRefreshCreateApiResponse = /** status 200  */ TokenRefreshRead;
export type TokenRefreshCreateApiArg = {
  tokenRefresh: TokenRefreshWrite;
};
export type TransactionsListApiResponse =
  /** status 200  */ PaginatedReadTransactionListRead;
export type TransactionsListApiArg = {
  /** Multiple values may be separated by commas. */
  account?: number[];
  amountMax?: string;
  amountMin?: string;
  dateAfter?: string;
  dateBefore?: string;
  description?: string;
  isSystem?: boolean;
  /** Ordering

    * `type` - Type
    * `-type` - Type (descending)
    * `amount` - Amount
    * `-amount` - Amount (descending)
    * `date` - Date
    * `-date` - Date (descending)
    * `description` - Description
    * `-description` - Description (descending)
    * `raw_category` - Raw category
    * `-raw_category` - Raw category (descending)
    * `is_system` - Is system
    * `-is_system` - Is system (descending) */
  ordering?: (
    | "-amount"
    | "-date"
    | "-description"
    | "-is_system"
    | "-raw_category"
    | "-type"
    | "amount"
    | "date"
    | "description"
    | "is_system"
    | "raw_category"
    | "type"
  )[];
  /** A page number within the paginated result set. */
  page?: number;
  /** Number of results to return per page. */
  pageSize?: number;
  rawCategory?: string;
  /** * `income` - Income
   * `expense` - Expense */
  type?: "expense" | "income";
};
export type TransactionsCreateApiResponse =
  /** status 201  */ WriteTransactionRead;
export type TransactionsCreateApiArg = {
  writeTransaction: WriteTransactionWrite;
};
export type TransactionsRetrieveApiResponse =
  /** status 200  */ ReadTransactionRead;
export type TransactionsRetrieveApiArg = {
  /** A unique integer value identifying this Transaction. */
  id: number;
};
export type TransactionsUpdateApiResponse =
  /** status 200  */ WriteTransactionRead;
export type TransactionsUpdateApiArg = {
  /** A unique integer value identifying this Transaction. */
  id: number;
  writeTransaction: WriteTransactionWrite;
};
export type TransactionsPartialUpdateApiResponse =
  /** status 200  */ WriteTransactionRead;
export type TransactionsPartialUpdateApiArg = {
  /** A unique integer value identifying this Transaction. */
  id: number;
  patchedWriteTransaction: PatchedWriteTransactionWrite;
};
export type TransactionsDestroyApiResponse = unknown;
export type TransactionsDestroyApiArg = {
  /** A unique integer value identifying this Transaction. */
  id: number;
};
export type AccountTypeEnum = "asset" | "liability" | "equity";
export type CategoryEnum =
  | "cash"
  | "investments"
  | "real_estate"
  | "crypto"
  | "credit_card"
  | "loan"
  | "mortgage"
  | "other";
export type CurrencyEnum = "USD" | "EUR" | "UAH";
export type Account = {
  name: string;
  type: AccountTypeEnum;
  category: CategoryEnum;
  currency: CurrencyEnum;
  is_active?: boolean;
};
export type AccountRead = {
  id: number;
  name: string;
  type: AccountTypeEnum;
  category: CategoryEnum;
  currency: CurrencyEnum;
  credit_limit: string | null;
  latest_balance: string;
  is_active?: boolean;
  created_at: string;
  updated_at: string;
};
export type PaginatedAccountList = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: Account[];
};
export type PaginatedAccountListRead = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: AccountRead[];
};
export type WriteAccount = {
  name: string;
  type: AccountTypeEnum;
  category: CategoryEnum;
  currency: CurrencyEnum;
  credit_limit?: string | null;
};
export type PatchedWriteAccount = {
  name?: string;
  type?: AccountTypeEnum;
  category?: CategoryEnum;
  currency?: CurrencyEnum;
  credit_limit?: string | null;
};
export type AccountSlim = {
  name: string;
  currency: CurrencyEnum;
};
export type AccountSlimRead = {
  id: number;
  name: string;
  currency: CurrencyEnum;
};
export type PaginatedAccountSlimList = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: AccountSlim[];
};
export type PaginatedAccountSlimListRead = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: AccountSlimRead[];
};
export type AnalyticsNetWorthHistoryItem = {
  date: string;
  net_worth: number;
  assets: number;
  liabilities: number;
};
export type AccountWithBalance = {
  name: string;
};
export type AccountWithBalanceRead = {
  id: number;
  name: string;
  latest_balance: string;
};
export type AnalyticsNetWorth = {
  net_worth: number;
  assets_total: number;
  liabilities_total: number;
  accounts: AccountWithBalance[];
};
export type AnalyticsNetWorthRead = {
  net_worth: number;
  assets_total: number;
  liabilities_total: number;
  accounts: AccountWithBalanceRead[];
};
export type BalanceRecord = {
  account: number;
  amount: string;
  date: string;
  note?: string;
};
export type BalanceRecordRead = {
  id: number;
  account: number;
  amount: string;
  date: string;
  note?: string;
  created_at: string;
};
export type PaginatedBalanceRecordList = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: BalanceRecord[];
};
export type PaginatedBalanceRecordListRead = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: BalanceRecordRead[];
};
export type ChangePassword = {
  old_password: string;
  new_password: string;
};
export type PatchedChangePassword = {
  old_password?: string;
  new_password?: string;
};
export type LoginResponse = {
  access: string;
  refresh: string;
};
export type MyTokenObtainPair = {};
export type MyTokenObtainPairWrite = {
  email: string;
  password: string;
};
export type Logout = {
  refresh: string;
};
export type UserProfile = {
  name: string;
};
export type UserProfileRead = {
  id: number;
  email: string;
  name: string;
};
export type PatchedUserProfile = {
  name?: string;
};
export type PatchedUserProfileRead = {
  id?: number;
  email?: string;
  name?: string;
};
export type User = {
  name: string;
  email: string;
};
export type UserRead = {
  id: number;
  name: string;
  email: string;
};
export type UserWrite = {
  name: string;
  password: string;
  email: string;
};
export type RegisterResponse = {
  user: User;
  access: string;
  refresh: string;
};
export type RegisterResponseRead = {
  user: UserRead;
  access: string;
  refresh: string;
};
export type RegisterResponseWrite = {
  user: UserWrite;
  access: string;
  refresh: string;
};
export type TokenObtainPair = {};
export type TokenObtainPairRead = {
  access: string;
  refresh: string;
};
export type TokenObtainPairWrite = {
  email: string;
  password: string;
};
export type TokenRefresh = {};
export type TokenRefreshRead = {
  access: string;
};
export type TokenRefreshWrite = {
  refresh: string;
};
export type TransactionTypeEnum = "income" | "expense";
export type ReadTransaction = {
  type: TransactionTypeEnum;
  amount: string;
  date: string;
  description?: string;
  raw_category?: string;
};
export type ReadTransactionRead = {
  id: number;
  type: TransactionTypeEnum;
  amount: string;
  date: string;
  description?: string;
  raw_category?: string;
  is_system: boolean;
  created_at: string;
  updated_at: string;
  account: AccountSlimRead;
};
export type PaginatedReadTransactionList = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: ReadTransaction[];
};
export type PaginatedReadTransactionListRead = {
  count: number;
  next?: string | null;
  previous?: string | null;
  results: ReadTransactionRead[];
};
export type WriteTransaction = {
  type: TransactionTypeEnum;
  amount: string;
  date: string;
  description?: string;
  raw_category?: string;
};
export type WriteTransactionRead = {
  id: number;
  type: TransactionTypeEnum;
  amount: string;
  date: string;
  description?: string;
  raw_category?: string;
  is_system: boolean;
  created_at: string;
  updated_at: string;
};
export type WriteTransactionWrite = {
  type: TransactionTypeEnum;
  amount: string;
  date: string;
  description?: string;
  raw_category?: string;
  account_id: number;
};
export type PatchedWriteTransaction = {
  type?: TransactionTypeEnum;
  amount?: string;
  date?: string;
  description?: string;
  raw_category?: string;
};
export type PatchedWriteTransactionRead = {
  id?: number;
  type?: TransactionTypeEnum;
  amount?: string;
  date?: string;
  description?: string;
  raw_category?: string;
  is_system?: boolean;
  created_at?: string;
  updated_at?: string;
};
export type PatchedWriteTransactionWrite = {
  type?: TransactionTypeEnum;
  amount?: string;
  date?: string;
  description?: string;
  raw_category?: string;
  account_id?: number;
};
export const {
  useAccountsListQuery,
  useAccountsCreateMutation,
  useAccountsRetrieveQuery,
  useAccountsUpdateMutation,
  useAccountsPartialUpdateMutation,
  useAccountsDestroyMutation,
  useAccountsImportTransactionCreateMutation,
  useAccountsAutocompleteListQuery,
  useActivateRetrieveQuery,
  useAnalyticsNetWorthHistoryListQuery,
  useAnalyticsNetWorthRetrieveQuery,
  useBalancesListQuery,
  useBalancesCreateMutation,
  useBalancesRetrieveQuery,
  useBalancesDestroyMutation,
  useBalancesBulkCreateCreateMutation,
  useBalancesLatestRetrieveQuery,
  useChangePasswordUpdateMutation,
  useChangePasswordPartialUpdateMutation,
  useLoginCreateMutation,
  useLogoutCreateMutation,
  useProfileRetrieveQuery,
  useProfileUpdateMutation,
  useProfilePartialUpdateMutation,
  useRegisterCreateMutation,
  useTokenCreateMutation,
  useTokenRefreshCreateMutation,
  useTransactionsListQuery,
  useTransactionsCreateMutation,
  useTransactionsRetrieveQuery,
  useTransactionsUpdateMutation,
  useTransactionsPartialUpdateMutation,
  useTransactionsDestroyMutation,
} = injectedRtkApi;
