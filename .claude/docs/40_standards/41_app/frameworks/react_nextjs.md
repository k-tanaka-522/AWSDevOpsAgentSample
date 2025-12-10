# React / Next.js コーディング規約

## 基本方針

- **Next.js 15+ (App Router) 推奨**
- **TypeScript 必須**
- **Server Components 優先、Client Components は必要な場合のみ**
- **関数コンポーネント + Hooks**
- **Tailwind CSS 推奨**
- **ESLint + Prettier による自動フォーマット**

---

## プロジェクト構成（Next.js App Router）

```
my-app/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # ルートグループ（認証が必要なページ）
│   │   ├── login/
│   │   │   └── page.tsx
│   │   └── register/
│   │       └── page.tsx
│   ├── (dashboard)/              # ルートグループ（ダッシュボード）
│   │   ├── layout.tsx            # ダッシュボード共通レイアウト
│   │   ├── page.tsx              # /dashboard
│   │   └── users/
│   │       ├── page.tsx          # /dashboard/users
│   │       └── [id]/
│   │           └── page.tsx      # /dashboard/users/:id
│   ├── api/                      # API Routes
│   │   └── users/
│   │       └── route.ts
│   ├── layout.tsx                # ルートレイアウト
│   ├── page.tsx                  # トップページ
│   ├── error.tsx                 # エラーページ
│   ├── loading.tsx               # ローディング UI
│   └── not-found.tsx             # 404 ページ
├── components/                   # 共通コンポーネント
│   ├── ui/                       # UI コンポーネント（shadcn/ui 等）
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   └── card.tsx
│   ├── features/                 # 機能別コンポーネント
│   │   ├── user/
│   │   │   ├── UserList.tsx
│   │   │   └── UserForm.tsx
│   │   └── auth/
│   │       └── LoginForm.tsx
│   └── layouts/                  # レイアウトコンポーネント
│       ├── Header.tsx
│       └── Footer.tsx
├── lib/                          # ユーティリティ・ヘルパー
│   ├── api.ts                    # API クライアント
│   ├── utils.ts                  # ユーティリティ関数
│   └── validations.ts            # バリデーション
├── hooks/                        # カスタムフック
│   ├── useAuth.ts
│   └── useUsers.ts
├── types/                        # TypeScript 型定義
│   ├── user.ts
│   └── api.ts
├── public/                       # 静的ファイル
│   ├── images/
│   └── fonts/
├── .env.local                    # 環境変数（ローカル）
├── next.config.js                # Next.js 設定
├── tailwind.config.ts            # Tailwind CSS 設定
├── tsconfig.json                 # TypeScript 設定
└── package.json
```

---

## Next.js App Router の基本

### Server Components（デフォルト）

```tsx
// ✅ Good: Server Component（デフォルト）
// app/users/page.tsx
import { getUsers } from '@/lib/api';

export default async function UsersPage() {
  // サーバーサイドでデータ取得
  const users = await getUsers();

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {users.map((user) => (
          <li key={user.id}>{user.name}</li>
        ))}
      </ul>
    </div>
  );
}

// ✅ Good: メタデータを生成
export async function generateMetadata() {
  return {
    title: 'Users - My App',
    description: 'User list page',
  };
}
```

### Client Components（必要な場合のみ）

```tsx
// ✅ Good: Client Component（useState、イベントハンドラ等が必要な場合）
// components/features/user/UserForm.tsx
'use client';

import { useState } from 'react';
import { createUser } from '@/lib/api';

export default function UserForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await createUser({ name, email });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name"
      />
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <button type="submit">Create User</button>
    </form>
  );
}
```

### Loading UI

```tsx
// ✅ Good: loading.tsx でローディング UI を定義
// app/users/loading.tsx
export default function Loading() {
  return (
    <div className="flex items-center justify-center h-screen">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900" />
    </div>
  );
}
```

### Error Handling

```tsx
// ✅ Good: error.tsx でエラーハンドリング
// app/users/error.tsx
'use client';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div>
      <h2>Something went wrong!</h2>
      <p>{error.message}</p>
      <button onClick={() => reset()}>Try again</button>
    </div>
  );
}
```

---

## コンポーネント設計

### 関数コンポーネント + TypeScript

```tsx
// ✅ Good: Props を型定義
interface UserCardProps {
  user: {
    id: number;
    name: string;
    email: string;
  };
  onDelete?: (id: number) => void;
}

export default function UserCard({ user, onDelete }: UserCardProps) {
  return (
    <div className="border p-4 rounded">
      <h3>{user.name}</h3>
      <p>{user.email}</p>
      {onDelete && (
        <button onClick={() => onDelete(user.id)}>Delete</button>
      )}
    </div>
  );
}

// ❌ Bad: 型定義なし
export default function UserCard({ user, onDelete }) {
  // TypeScript のメリットを享受できない
  return <div>...</div>;
}
```

### 分割代入と TypeScript

```tsx
// ✅ Good: Props を分割代入
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: 'primary' | 'secondary';
  disabled?: boolean;
}

export default function Button({
  label,
  onClick,
  variant = 'primary',
  disabled = false,
}: ButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={variant === 'primary' ? 'bg-blue-500' : 'bg-gray-500'}
    >
      {label}
    </button>
  );
}
```

### Composition Pattern

```tsx
// ✅ Good: children を活用
interface CardProps {
  children: React.ReactNode;
  title?: string;
}

export default function Card({ children, title }: CardProps) {
  return (
    <div className="border rounded p-4">
      {title && <h3>{title}</h3>}
      {children}
    </div>
  );
}

// 使用例
<Card title="User Info">
  <p>Name: John</p>
  <p>Email: john@example.com</p>
</Card>
```

---

## Hooks の使い方

### useState

```tsx
// ✅ Good: 型を明示
const [user, setUser] = useState<User | null>(null);
const [count, setCount] = useState<number>(0);
const [isLoading, setIsLoading] = useState<boolean>(false);

// ✅ Good: 関数による更新（前の状態に依存する場合）
setCount((prev) => prev + 1);

// ❌ Bad: 型推論に頼りすぎる（null や undefined が入る可能性がある場合）
const [user, setUser] = useState(null); // user の型が any になる
```

### useEffect

```tsx
// ✅ Good: 依存配列を明示
useEffect(() => {
  fetchUser(userId);
}, [userId]); // userId が変わったら再実行

// ✅ Good: クリーンアップ関数
useEffect(() => {
  const timer = setInterval(() => {
    console.log('tick');
  }, 1000);

  return () => clearInterval(timer); // クリーンアップ
}, []);

// ❌ Bad: 依存配列を忘れる（無限ループの危険）
useEffect(() => {
  fetchUser(userId);
}); // 依存配列なし → 毎回実行される
```

### カスタムフック

```tsx
// ✅ Good: カスタムフックで再利用可能なロジックを抽出
// hooks/useUsers.ts
import { useState, useEffect } from 'react';
import { getUsers } from '@/lib/api';
import type { User } from '@/types/user';

export function useUsers() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    const fetchUsers = async () => {
      try {
        setIsLoading(true);
        const data = await getUsers();
        setUsers(data);
      } catch (err) {
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, []);

  return { users, isLoading, error };
}

// 使用例
function UsersPage() {
  const { users, isLoading, error } = useUsers();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {users.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

---

## データフェッチ

### Server Components でのデータフェッチ（推奨）

```tsx
// ✅ Good: Server Component で直接データ取得
// app/users/page.tsx
import { getUsers } from '@/lib/api';

export default async function UsersPage() {
  const users = await getUsers();

  return (
    <div>
      <h1>Users</h1>
      {users.map((user) => (
        <div key={user.id}>{user.name}</div>
      ))}
    </div>
  );
}

// lib/api.ts
export async function getUsers() {
  const res = await fetch('https://api.example.com/users', {
    cache: 'no-store', // リアルタイムデータが必要な場合
    // cache: 'force-cache', // キャッシュを使用（デフォルト）
    // next: { revalidate: 60 }, // 60秒ごとに再検証
  });

  if (!res.ok) {
    throw new Error('Failed to fetch users');
  }

  return res.json();
}
```

### Client Components でのデータフェッチ（SWR 推奨）

```tsx
// ✅ Good: SWR を使用（Client Component）
'use client';

import useSWR from 'swr';
import { getUsers } from '@/lib/api';

export default function UsersPage() {
  const { data: users, error, isLoading } = useSWR('/api/users', getUsers);

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {users?.map((user) => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  );
}
```

### API Routes（Next.js）

```ts
// ✅ Good: API Route
// app/api/users/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const users = await fetchUsersFromDB();
    return NextResponse.json(users);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch users' },
      { status: 500 }
    );
  }
}

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const user = await createUserInDB(body);
    return NextResponse.json(user, { status: 201 });
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to create user' },
      { status: 500 }
    );
  }
}
```

---

## フォーム・バリデーション

### React Hook Form + Zod（推奨）

```tsx
// ✅ Good: React Hook Form + Zod
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';

const userSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type UserFormData = z.infer<typeof userSchema>;

export default function UserForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<UserFormData>({
    resolver: zodResolver(userSchema),
  });

  const onSubmit = async (data: UserFormData) => {
    await createUser(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <input {...register('name')} placeholder="Name" />
        {errors.name && <span>{errors.name.message}</span>}
      </div>

      <div>
        <input {...register('email')} type="email" placeholder="Email" />
        {errors.email && <span>{errors.email.message}</span>}
      </div>

      <div>
        <input
          {...register('password')}
          type="password"
          placeholder="Password"
        />
        {errors.password && <span>{errors.password.message}</span>}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Submitting...' : 'Submit'}
      </button>
    </form>
  );
}
```

---

## 状態管理

### Context API（軽量な状態管理）

```tsx
// ✅ Good: Context + useReducer
// contexts/AuthContext.tsx
'use client';

import { createContext, useContext, useReducer, ReactNode } from 'react';

interface User {
  id: number;
  name: string;
  email: string;
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
}

type AuthAction =
  | { type: 'LOGIN'; payload: User }
  | { type: 'LOGOUT' };

const AuthContext = createContext<{
  state: AuthState;
  dispatch: React.Dispatch<AuthAction>;
} | undefined>(undefined);

function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN':
      return { user: action.payload, isAuthenticated: true };
    case 'LOGOUT':
      return { user: null, isAuthenticated: false };
    default:
      return state;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    isAuthenticated: false,
  });

  return (
    <AuthContext.Provider value={{ state, dispatch }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
```

### Zustand（複雑な状態管理）

```ts
// ✅ Good: Zustand
// stores/useUserStore.ts
import { create } from 'zustand';

interface User {
  id: number;
  name: string;
  email: string;
}

interface UserStore {
  users: User[];
  addUser: (user: User) => void;
  removeUser: (id: number) => void;
}

export const useUserStore = create<UserStore>((set) => ({
  users: [],
  addUser: (user) => set((state) => ({ users: [...state.users, user] })),
  removeUser: (id) =>
    set((state) => ({ users: state.users.filter((u) => u.id !== id) })),
}));

// 使用例
function UsersPage() {
  const { users, addUser, removeUser } = useUserStore();

  return (
    <div>
      {users.map((user) => (
        <div key={user.id}>
          {user.name}
          <button onClick={() => removeUser(user.id)}>Delete</button>
        </div>
      ))}
    </div>
  );
}
```

---

## スタイリング（Tailwind CSS）

### 基本的な使い方

```tsx
// ✅ Good: Tailwind CSS のユーティリティクラス
export default function Button({ children }: { children: React.ReactNode }) {
  return (
    <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
      {children}
    </button>
  );
}

// ✅ Good: 条件付きクラス（clsx を使用）
import clsx from 'clsx';

interface ButtonProps {
  variant: 'primary' | 'secondary';
  children: React.ReactNode;
}

export default function Button({ variant, children }: ButtonProps) {
  return (
    <button
      className={clsx(
        'font-bold py-2 px-4 rounded',
        variant === 'primary' && 'bg-blue-500 hover:bg-blue-700 text-white',
        variant === 'secondary' && 'bg-gray-500 hover:bg-gray-700 text-white'
      )}
    >
      {children}
    </button>
  );
}
```

### カスタムコンポーネント（shadcn/ui スタイル）

```tsx
// ✅ Good: 再利用可能な UI コンポーネント
// components/ui/button.tsx
import { ButtonHTMLAttributes, forwardRef } from 'react';
import clsx from 'clsx';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'sm' | 'md' | 'lg';
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          'font-semibold rounded transition-colors',
          // Variant
          variant === 'primary' && 'bg-blue-500 hover:bg-blue-600 text-white',
          variant === 'secondary' && 'bg-gray-500 hover:bg-gray-600 text-white',
          variant === 'outline' && 'border border-gray-300 hover:bg-gray-100',
          // Size
          size === 'sm' && 'px-3 py-1 text-sm',
          size === 'md' && 'px-4 py-2',
          size === 'lg' && 'px-6 py-3 text-lg',
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export default Button;
```

---

## パフォーマンス最適化

### React.memo

```tsx
// ✅ Good: React.memo で不要な再レンダリングを防ぐ
import { memo } from 'react';

interface UserCardProps {
  user: User;
}

const UserCard = memo(function UserCard({ user }: UserCardProps) {
  return (
    <div>
      <h3>{user.name}</h3>
      <p>{user.email}</p>
    </div>
  );
});

export default UserCard;
```

### useCallback / useMemo

```tsx
// ✅ Good: useCallback で関数をメモ化
import { useCallback, useMemo } from 'react';

function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);

  // 関数のメモ化
  const handleDelete = useCallback((id: number) => {
    setUsers((prev) => prev.filter((u) => u.id !== id));
  }, []);

  // 計算結果のメモ化
  const activeUsers = useMemo(() => {
    return users.filter((u) => u.isActive);
  }, [users]);

  return (
    <div>
      {activeUsers.map((user) => (
        <UserCard key={user.id} user={user} onDelete={handleDelete} />
      ))}
    </div>
  );
}
```

### 動的インポート（Code Splitting）

```tsx
// ✅ Good: 動的インポートで初期読み込みを軽量化
import dynamic from 'next/dynamic';

const HeavyComponent = dynamic(() => import('@/components/HeavyComponent'), {
  loading: () => <div>Loading...</div>,
  ssr: false, // SSR 無効（クライアントサイドのみ）
});

export default function Page() {
  return (
    <div>
      <h1>Page</h1>
      <HeavyComponent />
    </div>
  );
}
```

---

## 環境変数

```bash
# .env.local
NEXT_PUBLIC_API_URL=https://api.example.com
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
JWT_SECRET=your-secret-key
```

```ts
// ✅ Good: 環境変数の使用
// NEXT_PUBLIC_ プレフィックス → クライアントサイドで使用可能
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// プレフィックスなし → サーバーサイドのみ
const dbUrl = process.env.DATABASE_URL;
```

---

## テスト

### Jest + React Testing Library

```tsx
// ✅ Good: コンポーネントのテスト
// __tests__/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '@/components/ui/Button';

describe('Button', () => {
  it('renders button with label', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click me</Button>);
    expect(screen.getByText('Click me')).toBeDisabled();
  });
});
```

---

## ESLint + Prettier

### .eslintrc.json

```json
{
  "extends": [
    "next/core-web-vitals",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "react/prop-types": "off",
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

### .prettierrc

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 80
}
```

---

## ベストプラクティス

1. **Server Components を優先**: 可能な限り Server Components を使用
2. **TypeScript 型を厳密に**: `any` を避ける
3. **小さなコンポーネント**: 1 コンポーネント = 1 責務
4. **カスタムフックで再利用**: 重複ロジックをカスタムフックに抽出
5. **Tailwind CSS で統一**: インラインスタイルは避ける
6. **パフォーマンスを意識**: React.memo、useCallback、useMemo を適切に使用
7. **テストを書く**: 重要なコンポーネント・ロジックはテスト必須

---

**参照**: `.claude/docs/10_facilitation/2.4_実装フェーズ/2.4.5_言語別コーディング規約適用/`
