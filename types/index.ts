export type AuthStackParamList = {
  Login: undefined;
  SignUp: undefined;
  ForgotPassword: undefined;
};

export type AppStackParamList = {
  Home: undefined;
  Profile: undefined;
  Settings: undefined;
};

export type User = {
  id: string;
  email: string;
  username?: string;
  avatar_url?: string;
  created_at: string;
};

export type Session = {
  user: User | null;
  isLoggedIn: boolean;
  isLoading: boolean;
};
