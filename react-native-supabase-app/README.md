# React Native Expo Supabase App

A React Native mobile application built with Expo and Supabase for backend services.

## Features

- Authentication (Sign In, Sign Up, Password Reset)
- TypeScript for type safety
- Environment variables setup
- Clean UI with React Native Paper
- Tab-based navigation

## Prerequisites

Before you begin, ensure you have the following installed:
- [Node.js](https://nodejs.org/)
- [npm](https://www.npmjs.com/) or [Yarn](https://yarnpkg.com/)
- [Expo CLI](https://docs.expo.dev/get-started/installation/)

## Setup

1. Clone this repository:
```
git clone <repository-url>
cd react-native-supabase-app
```

2. Install dependencies:
```
npm install
```
or
```
yarn install
```

3. Create a `.env` file in the root directory with your Supabase credentials:
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
```

## Running the App

Start the development server:
```
npx expo start
```

This will open up Expo DevTools in your browser. You can then:
- Run on an Android emulator or device
- Run on an iOS simulator or device (if on a Mac)
- Scan the QR code with the Expo Go app on your physical device

## Project Structure

```
src/
  ├── components/     # Reusable components
  ├── navigation/     # Navigation configurations
  ├── screens/        # Application screens
  │    ├── app/       # Main app screens
  │    └── auth/      # Authentication screens
  ├── types/          # TypeScript type definitions
  └── utils/          # Utility functions
      └── supabase.ts # Supabase client configuration
```

## Supabase Setup

1. Create a Supabase project at [supabase.io](https://supabase.io)
2. Enable authentication in your Supabase dashboard
3. Get your API URL and public API key from the Settings > API section
4. Add them to your `.env` file

## Customization

- Modify the screens in the `src/screens` directory
- Add new components in the `src/components` directory
- Update the navigation in the `src/navigation` directory

## License

This project is licensed under the MIT License - see the LICENSE file for details. 