# Agent Guidelines for SigmaVerde

## Commands
- **Dev server**: `npm run dev` (Vite development server)
- **Build**: `npm run build` (production build)
- **Lint**: `npm run lint` (ESLint with auto-fix)
- **Preview**: `npm run preview` (preview production build)

## Architecture
- **Framework**: Vue 3 + Vite + PrimeVue UI library + Tailwind CSS
- **State Management**: Pinia stores (`src/stores/`)
- **Routing**: Vue Router with monitoring and index routes (`src/router/`)
- **Authentication**: RBAC system with role-based permissions (admin, l1_analyst, l2_analyst)
- **Main directories**: `components/`, `views/`, `stores/`, `services/`, `layout/`, `utils/`
- **Aliases**: Use `@/` for `src/` imports

## Code Style
- **Composition API**: Use `<script setup>` syntax for Vue components
- **Imports**: ES6 imports, use `@/` alias for src paths
- **Naming**: camelCase for variables/functions, PascalCase for components
- **Store pattern**: Pinia with `defineStore`, organized by domain (auth, cases, layout)
- **Styling**: Tailwind CSS with custom AML color palette, PrimeVue components
- **State**: Reactive state with computed getters for permissions/roles
- **Error handling**: Try-catch with error state in stores, console logging for debugging
