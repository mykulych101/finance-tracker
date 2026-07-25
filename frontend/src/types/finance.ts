export interface Account {
  id: string;
  name: string;
  type: 'asset' | 'liability' | 'equity';
  category: string;
  createdAt: Date;
}

export interface Balance {
  id: string;
  accountId: string;
  amount: number;
  date: Date;
}

export interface AccountWithBalance extends Account {
  currentBalance: number;
}

export interface AccountWithHistory extends Account {
  balanceHistory: { date: Date; amount: number }[];
}
