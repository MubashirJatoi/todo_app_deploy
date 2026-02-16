# Frontend Guidelines

## Stack
- Next.js 16+ (App Router)
- TypeScript
- Tailwind CSS

## Patterns
- Use server components by default
- Client components only for interactivity
- API calls through `/lib/api.ts`

## Structure
- `/components` - Reusable UI components
- `/app` - Pages and layouts
- `/lib` - Utilities and API client

## API Client Pattern
```typescript
import { api } from '@/lib/api'
const tasks = await api.getTasks()
```

## Styling
- Use Tailwind CSS only
- No inline styles
- Follow existing patterns