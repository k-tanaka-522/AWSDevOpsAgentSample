# Flutter コーディング規約

## 基本方針

- **Dart 3.0+ (Null Safety)**
- **Flutter 3.0+**
- **Clean Architecture（BLoC パターン推奨）**
- **状態管理: Riverpod または BLoC**
- **ルーティング: go_router**
- **DI: get_it + injectable**
- **Effective Dart に準拠**

---

## プロジェクト構成（Clean Architecture + Feature-First）

```
my_app/
├── lib/
│   ├── main.dart                      # エントリーポイント
│   ├── app.dart                       # アプリケーションルート
│   │
│   ├── core/                          # アプリ全体で共有される機能
│   │   ├── di/                        # Dependency Injection
│   │   │   └── injection.dart
│   │   ├── router/                    # ルーティング
│   │   │   └── app_router.dart
│   │   ├── theme/                     # テーマ
│   │   │   ├── app_colors.dart
│   │   │   └── app_theme.dart
│   │   ├── constants/                 # 定数
│   │   │   └── app_constants.dart
│   │   ├── utils/                     # ユーティリティ
│   │   │   ├── validators.dart
│   │   │   └── formatters.dart
│   │   └── widgets/                   # 共通ウィジェット
│   │       ├── buttons/
│   │       │   └── primary_button.dart
│   │       └── loading_indicator.dart
│   │
│   ├── features/                      # 機能別ディレクトリ
│   │   ├── auth/                      # 認証機能
│   │   │   ├── data/                  # データ層
│   │   │   │   ├── datasources/       # データソース
│   │   │   │   │   ├── auth_local_datasource.dart
│   │   │   │   │   └── auth_remote_datasource.dart
│   │   │   │   ├── models/            # DTOモデル
│   │   │   │   │   └── user_model.dart
│   │   │   │   └── repositories/      # リポジトリ実装
│   │   │   │       └── auth_repository_impl.dart
│   │   │   ├── domain/                # ドメイン層
│   │   │   │   ├── entities/          # エンティティ
│   │   │   │   │   └── user.dart
│   │   │   │   ├── repositories/      # リポジトリインターフェース
│   │   │   │   │   └── auth_repository.dart
│   │   │   │   └── usecases/          # ユースケース
│   │   │   │       ├── login_usecase.dart
│   │   │   │       └── logout_usecase.dart
│   │   │   └── presentation/          # プレゼンテーション層
│   │   │       ├── bloc/              # BLoC（状態管理）
│   │   │       │   ├── auth_bloc.dart
│   │   │       │   ├── auth_event.dart
│   │   │       │   └── auth_state.dart
│   │   │       ├── pages/             # ページ
│   │   │       │   ├── login_page.dart
│   │   │       │   └── register_page.dart
│   │   │       └── widgets/           # ウィジェット
│   │   │           └── login_form.dart
│   │   │
│   │   └── home/                      # ホーム機能
│   │       ├── data/
│   │       ├── domain/
│   │       └── presentation/
│   │
│   └── shared/                        # 複数の機能で共有されるコード
│       ├── models/
│       ├── services/
│       └── repositories/
│
├── test/                              # ユニットテスト
│   ├── features/
│   │   └── auth/
│   │       ├── data/
│   │       ├── domain/
│   │       └── presentation/
│   └── core/
│
├── integration_test/                  # 統合テスト
│   └── app_test.dart
│
├── assets/                            # アセット
│   ├── images/
│   ├── fonts/
│   └── translations/
│
├── pubspec.yaml                       # 依存関係
└── analysis_options.yaml              # Linter設定
```

---

## コーディング規約

### 命名規則

```dart
// ✅ Good: クラス名は UpperCamelCase
class UserRepository {}
class LoginPage extends StatelessWidget {}

// ✅ Good: 変数・関数名は lowerCamelCase
String userName = 'John';
void fetchUserData() {}

// ✅ Good: 定数は lowerCamelCase（const）
const int maxRetryCount = 3;
const String apiBaseUrl = 'https://api.example.com';

// ✅ Good: プライベートは _ で始まる
class _MyWidgetState extends State<MyWidget> {}
String _privateVariable = 'private';

// ✅ Good: ファイル名は snake_case
// user_repository.dart
// login_page.dart
// primary_button.dart
```

### Null Safety

```dart
// ✅ Good: Null Safety を活用
String nonNullableString = 'Hello';
String? nullableString;

void printLength(String? text) {
  // Null チェック
  if (text != null) {
    print(text.length);
  }

  // または null-aware operator
  print(text?.length);

  // デフォルト値
  print(text?.length ?? 0);
}

// ✅ Good: late キーワード（遅延初期化）
class MyWidget extends StatefulWidget {
  @override
  State<MyWidget> createState() => _MyWidgetState();
}

class _MyWidgetState extends State<MyWidget> {
  late final TextEditingController _controller;

  @override
  void initState() {
    super.initState();
    _controller = TextEditingController();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }
}

// ❌ Bad: ! を多用（Null 安全性を破る）
String? nullableString;
print(nullableString!.length); // クラッシュの危険
```

---

## ウィジェット設計

### StatelessWidget vs StatefulWidget

```dart
// ✅ Good: 状態を持たない場合は StatelessWidget
class UserCard extends StatelessWidget {
  final String name;
  final String email;

  const UserCard({
    super.key,
    required this.name,
    required this.email,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        title: Text(name),
        subtitle: Text(email),
      ),
    );
  }
}

// ✅ Good: 状態を持つ場合は StatefulWidget
class CounterWidget extends StatefulWidget {
  const CounterWidget({super.key});

  @override
  State<CounterWidget> createState() => _CounterWidgetState();
}

class _CounterWidgetState extends State<CounterWidget> {
  int _counter = 0;

  void _incrementCounter() {
    setState(() {
      _counter++;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_counter'),
        ElevatedButton(
          onPressed: _incrementCounter,
          child: const Text('Increment'),
        ),
      ],
    );
  }
}
```

### ウィジェットの分割

```dart
// ✅ Good: 小さく再利用可能なウィジェットに分割
class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Login')),
      body: const Padding(
        padding: EdgeInsets.all(16.0),
        child: LoginForm(),
      ),
    );
  }
}

class LoginForm extends StatefulWidget {
  const LoginForm({super.key});

  @override
  State<LoginForm> createState() => _LoginFormState();
}

class _LoginFormState extends State<LoginForm> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          EmailField(controller: _emailController),
          const SizedBox(height: 16),
          PasswordField(controller: _passwordController),
          const SizedBox(height: 24),
          SubmitButton(
            onPressed: _submit,
          ),
        ],
      ),
    );
  }

  void _submit() {
    if (_formKey.currentState!.validate()) {
      // ログイン処理
    }
  }
}

// ❌ Bad: すべてを1つのウィジェットに詰め込む
class LoginPage extends StatefulWidget {
  // 500行のコード...
}
```

### const コンストラクタ

```dart
// ✅ Good: const コンストラクタを使用
class MyButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;

  const MyButton({
    super.key,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      child: Text(label),
    );
  }
}

// 使用例
const MyButton(label: 'Click', onPressed: _handleClick);

// ❌ Bad: const を使わない（不要な再ビルド）
MyButton(label: 'Click', onPressed: _handleClick);
```

---

## 状態管理（BLoC パターン）

### BLoC の基本

```dart
// Event
abstract class AuthEvent {}

class LoginRequested extends AuthEvent {
  final String email;
  final String password;

  LoginRequested(this.email, this.password);
}

class LogoutRequested extends AuthEvent {}

// State
abstract class AuthState {}

class AuthInitial extends AuthState {}

class AuthLoading extends AuthState {}

class AuthAuthenticated extends AuthState {
  final User user;

  AuthAuthenticated(this.user);
}

class AuthUnauthenticated extends AuthState {}

class AuthError extends AuthState {
  final String message;

  AuthError(this.message);
}

// BLoC
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final LoginUseCase _loginUseCase;
  final LogoutUseCase _logoutUseCase;

  AuthBloc({
    required LoginUseCase loginUseCase,
    required LogoutUseCase logoutUseCase,
  })  : _loginUseCase = loginUseCase,
        _logoutUseCase = logoutUseCase,
        super(AuthInitial()) {
    on<LoginRequested>(_onLoginRequested);
    on<LogoutRequested>(_onLogoutRequested);
  }

  Future<void> _onLoginRequested(
    LoginRequested event,
    Emitter<AuthState> emit,
  ) async {
    emit(AuthLoading());

    final result = await _loginUseCase(
      email: event.email,
      password: event.password,
    );

    result.fold(
      (failure) => emit(AuthError(failure.message)),
      (user) => emit(AuthAuthenticated(user)),
    );
  }

  Future<void> _onLogoutRequested(
    LogoutRequested event,
    Emitter<AuthState> emit,
  ) async {
    await _logoutUseCase();
    emit(AuthUnauthenticated());
  }
}
```

### BLoC の使用

```dart
// ✅ Good: BlocProvider で BLoC を提供
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => getIt<AuthBloc>(),
      child: MaterialApp(
        home: const LoginPage(),
      ),
    );
  }
}

// ✅ Good: BlocBuilder で状態を監視
class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: BlocBuilder<AuthBloc, AuthState>(
        builder: (context, state) {
          if (state is AuthLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          if (state is AuthError) {
            return Center(child: Text(state.message));
          }

          if (state is AuthAuthenticated) {
            return HomePage(user: state.user);
          }

          return const LoginForm();
        },
      ),
    );
  }
}

// ✅ Good: BlocListener でイベント処理
BlocListener<AuthBloc, AuthState>(
  listener: (context, state) {
    if (state is AuthError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(state.message)),
      );
    }

    if (state is AuthAuthenticated) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const HomePage()),
      );
    }
  },
  child: const LoginForm(),
);
```

---

## UseCase パターン

```dart
// ✅ Good: UseCase でビジネスロジックをカプセル化
class LoginUseCase {
  final AuthRepository _repository;

  LoginUseCase(this._repository);

  Future<Either<Failure, User>> call({
    required String email,
    required String password,
  }) async {
    // バリデーション
    if (email.isEmpty || password.isEmpty) {
      return Left(ValidationFailure('Email and password are required'));
    }

    // リポジトリ経由でログイン
    return await _repository.login(email: email, password: password);
  }
}

// Either型（dartz パッケージ）でエラーハンドリング
final result = await loginUseCase(email: 'test@example.com', password: 'password');

result.fold(
  (failure) => print('Error: ${failure.message}'),
  (user) => print('Success: ${user.name}'),
);
```

---

## Repository パターン

```dart
// ✅ Good: Repository インターフェース（domain層）
abstract class AuthRepository {
  Future<Either<Failure, User>> login({
    required String email,
    required String password,
  });

  Future<Either<Failure, void>> logout();
}

// ✅ Good: Repository 実装（data層）
class AuthRepositoryImpl implements AuthRepository {
  final AuthRemoteDataSource _remoteDataSource;
  final AuthLocalDataSource _localDataSource;

  AuthRepositoryImpl({
    required AuthRemoteDataSource remoteDataSource,
    required AuthLocalDataSource localDataSource,
  })  : _remoteDataSource = remoteDataSource,
        _localDataSource = localDataSource;

  @override
  Future<Either<Failure, User>> login({
    required String email,
    required String password,
  }) async {
    try {
      final userModel = await _remoteDataSource.login(
        email: email,
        password: password,
      );

      // ローカルにトークンを保存
      await _localDataSource.saveToken(userModel.token);

      // ModelをEntityに変換
      return Right(userModel.toEntity());
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } on NetworkException {
      return Left(NetworkFailure('No internet connection'));
    }
  }

  @override
  Future<Either<Failure, void>> logout() async {
    try {
      await _localDataSource.deleteToken();
      return const Right(null);
    } catch (e) {
      return Left(CacheFailure('Failed to logout'));
    }
  }
}
```

---

## Data Source

```dart
// ✅ Good: Remote Data Source（API通信）
class AuthRemoteDataSource {
  final Dio _dio;

  AuthRemoteDataSource(this._dio);

  Future<UserModel> login({
    required String email,
    required String password,
  }) async {
    try {
      final response = await _dio.post(
        '/auth/login',
        data: {
          'email': email,
          'password': password,
        },
      );

      if (response.statusCode == 200) {
        return UserModel.fromJson(response.data);
      } else {
        throw ServerException('Login failed');
      }
    } on DioException catch (e) {
      throw ServerException(e.message ?? 'Unknown error');
    }
  }
}

// ✅ Good: Local Data Source（ローカルストレージ）
class AuthLocalDataSource {
  final SharedPreferences _prefs;

  AuthLocalDataSource(this._prefs);

  Future<void> saveToken(String token) async {
    await _prefs.setString('auth_token', token);
  }

  String? getToken() {
    return _prefs.getString('auth_token');
  }

  Future<void> deleteToken() async {
    await _prefs.remove('auth_token');
  }
}
```

---

## Dependency Injection（get_it + injectable）

```dart
// ✅ Good: DI セットアップ
@InjectableInit()
Future<void> configureDependencies() async {
  final getIt = GetIt.instance;

  // External dependencies
  final sharedPreferences = await SharedPreferences.getInstance();
  getIt.registerSingleton<SharedPreferences>(sharedPreferences);

  final dio = Dio(BaseOptions(baseUrl: 'https://api.example.com'));
  getIt.registerSingleton<Dio>(dio);

  // Data sources
  getIt.registerLazySingleton<AuthRemoteDataSource>(
    () => AuthRemoteDataSource(getIt()),
  );
  getIt.registerLazySingleton<AuthLocalDataSource>(
    () => AuthLocalDataSource(getIt()),
  );

  // Repositories
  getIt.registerLazySingleton<AuthRepository>(
    () => AuthRepositoryImpl(
      remoteDataSource: getIt(),
      localDataSource: getIt(),
    ),
  );

  // Use cases
  getIt.registerLazySingleton(() => LoginUseCase(getIt()));
  getIt.registerLazySingleton(() => LogoutUseCase(getIt()));

  // BLoC
  getIt.registerFactory(
    () => AuthBloc(
      loginUseCase: getIt(),
      logoutUseCase: getIt(),
    ),
  );
}

// main.dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await configureDependencies();
  runApp(const MyApp());
}
```

---

## ルーティング（go_router）

```dart
// ✅ Good: go_router でルーティング
final goRouter = GoRouter(
  initialLocation: '/login',
  routes: [
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginPage(),
    ),
    GoRoute(
      path: '/home',
      builder: (context, state) => const HomePage(),
      routes: [
        GoRoute(
          path: 'profile',
          builder: (context, state) => const ProfilePage(),
        ),
      ],
    ),
    GoRoute(
      path: '/users/:id',
      builder: (context, state) {
        final userId = state.pathParameters['id']!;
        return UserDetailPage(userId: userId);
      },
    ),
  ],
  redirect: (context, state) {
    final isAuthenticated = getIt<AuthBloc>().state is AuthAuthenticated;
    final isLoginRoute = state.matchedLocation == '/login';

    if (!isAuthenticated && !isLoginRoute) {
      return '/login';
    }

    if (isAuthenticated && isLoginRoute) {
      return '/home';
    }

    return null;
  },
);

// 使用例
context.go('/home');
context.push('/users/123');
context.pop();
```

---

## エラーハンドリング

```dart
// ✅ Good: Failure クラスでエラーを表現
abstract class Failure {
  final String message;
  const Failure(this.message);
}

class ServerFailure extends Failure {
  const ServerFailure(super.message);
}

class NetworkFailure extends Failure {
  const NetworkFailure(super.message);
}

class ValidationFailure extends Failure {
  const ValidationFailure(super.message);
}

// ✅ Good: Exception クラス
class ServerException implements Exception {
  final String message;
  const ServerException(this.message);
}

class NetworkException implements Exception {}
```

---

## テスト

### ユニットテスト

```dart
// ✅ Good: UseCase のテスト
void main() {
  late LoginUseCase loginUseCase;
  late MockAuthRepository mockRepository;

  setUp(() {
    mockRepository = MockAuthRepository();
    loginUseCase = LoginUseCase(mockRepository);
  });

  group('LoginUseCase', () {
    test('should return User when login succeeds', () async {
      // Arrange
      final user = User(id: '1', name: 'John', email: 'john@example.com');
      when(() => mockRepository.login(
            email: any(named: 'email'),
            password: any(named: 'password'),
          )).thenAnswer((_) async => Right(user));

      // Act
      final result = await loginUseCase(
        email: 'john@example.com',
        password: 'password',
      );

      // Assert
      expect(result, Right(user));
      verify(() => mockRepository.login(
            email: 'john@example.com',
            password: 'password',
          )).called(1);
    });

    test('should return ValidationFailure when email is empty', () async {
      // Act
      final result = await loginUseCase(email: '', password: 'password');

      // Assert
      expect(result.isLeft(), true);
      result.fold(
        (failure) => expect(failure, isA<ValidationFailure>()),
        (_) => fail('Should return failure'),
      );
    });
  });
}
```

### ウィジェットテスト

```dart
// ✅ Good: ウィジェットテスト
void main() {
  testWidgets('LoginPage shows email and password fields',
      (WidgetTester tester) async {
    // Build
    await tester.pumpWidget(
      const MaterialApp(home: LoginPage()),
    );

    // Find
    expect(find.byType(TextFormField), findsNWidgets(2));
    expect(find.text('Email'), findsOneWidget);
    expect(find.text('Password'), findsOneWidget);
    expect(find.byType(ElevatedButton), findsOneWidget);
  });

  testWidgets('Login button triggers login', (WidgetTester tester) async {
    // Build
    await tester.pumpWidget(
      const MaterialApp(home: LoginPage()),
    );

    // Enter text
    await tester.enterText(
      find.byKey(const Key('email_field')),
      'test@example.com',
    );
    await tester.enterText(
      find.byKey(const Key('password_field')),
      'password',
    );

    // Tap button
    await tester.tap(find.byType(ElevatedButton));
    await tester.pump();

    // Verify
    // ... (BLoC のモックを使って検証)
  });
}
```

---

## パフォーマンス最適化

### ListView.builder

```dart
// ✅ Good: ListView.builder で大量データを効率的に表示
ListView.builder(
  itemCount: users.length,
  itemBuilder: (context, index) {
    return UserCard(user: users[index]);
  },
);

// ❌ Bad: ListView with children（すべてのウィジェットを生成）
ListView(
  children: users.map((user) => UserCard(user: user)).toList(),
);
```

### const コンストラクタ

```dart
// ✅ Good: const で不要な再ビルドを防ぐ
const Text('Hello');
const SizedBox(height: 16);
const Icon(Icons.home);

// ❌ Bad: const を使わない
Text('Hello');
SizedBox(height: 16);
```

---

## ベストプラクティス

1. **Clean Architecture**: 層を分ける（data、domain、presentation）
2. **Feature-First**: 機能ごとにディレクトリを分ける
3. **BLoC パターン**: 状態管理は BLoC または Riverpod
4. **Null Safety**: Null 安全性を活用
5. **const コンストラクタ**: 可能な限り const を使用
6. **小さなウィジェット**: 再利用可能な小さなウィジェットに分割
7. **Dependency Injection**: get_it + injectable で DI
8. **テスト**: ユニットテスト・ウィジェットテストを書く
9. **Effective Dart**: Dart の公式ガイドラインに従う
10. **Linter**: analysis_options.yaml で厳格なルールを設定

---

**参照**: `.claude/docs/10_facilitation/2.4_実装フェーズ/`
