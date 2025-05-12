# React Native Expo with Supabase Auth

A modern React Native application using Expo and Supabase for authentication and backend services.

## Features

- 🔐 Authentication (Login, Sign Up, Forgot Password)
- 📱 Clean UI with React Native Paper
- 🔄 TypeScript for type safety
- 🌐 Supabase integration for backend services
- 🔒 Environment variable configuration
- 📱 Responsive design

## Prerequisites

- Node.js (v14 or newer)
- npm or yarn
- Expo CLI
- Supabase account and project

## Getting Started

### 1. Clone the repository

```bash
git clone <repository-url>
cd supabase-expo-auth
```

### 2. Install dependencies

```bash
npm install
# or
yarn install
```

### 3. Set up environment variables

Create a `.env` file in the root directory with the following variables:

```
EXPO_PUBLIC_SUPABASE_URL=your_supabase_url
EXPO_PUBLIC_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Replace `your_supabase_url` and `your_supabase_anon_key` with your actual Supabase project credentials.

### 4. Set up Supabase

1. Create a new project in Supabase
2. Enable Email Auth in Authentication settings
3. Create a `profiles` table with the following SQL:

```sql
CREATE TABLE profiles (
  id UUID REFERENCES auth.users ON DELETE CASCADE,
  username TEXT,
  updated_at TIMESTAMP WITH TIME ZONE,
  PRIMARY KEY (id)
);

-- Create a secure RLS policy
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own profile" 
  ON profiles FOR SELECT 
  USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" 
  ON profiles FOR UPDATE 
  USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" 
  ON profiles FOR INSERT 
  WITH CHECK (auth.uid() = id);
```

### 5. Run the application

```bash
npx expo start
```

## Project Structure

```
supabase-expo-auth/
├── App.tsx                # Main application component
├── babel.config.js        # Babel configuration
├── context/               # React context providers
│   └── AuthContext.tsx    # Authentication context
├── lib/                   # Utility libraries
│   └── supabase.ts        # Supabase client configuration
├── navigation/            # Navigation configuration
│   └── index.tsx          # Navigation structure
├── screens/               # Application screens
│   ├── app/               # Authenticated screens
│   │   ├── HomeScreen.tsx
│   │   ├── ProfileScreen.tsx
│   │   └── SettingsScreen.tsx
│   └── auth/              # Authentication screens
│       ├── LoginScreen.tsx
│       ├── SignUpScreen.tsx
│       └── ForgotPasswordScreen.tsx
└── types/                 # TypeScript type definitions
    └── index.ts
```

## Environment Variables

The application uses the following environment variables:

- `EXPO_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `EXPO_PUBLIC_SUPABASE_ANON_KEY`: Your Supabase anonymous key

## Authentication Flow

1. Users can sign up with email and password
2. Users can log in with email and password
3. Users can request a password reset
4. Authentication state is persisted using AsyncStorage

## Customization

### Theme

You can customize the theme by modifying the theme object in `App.tsx`:

```typescript
const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#6200ee', // Change to your primary color
    accent: '#03dac4',  // Change to your accent color
  },
};
```

### Supabase Configuration

You can modify the Supabase client configuration in `lib/supabase.ts`.

## License

MIT
