# FoodFlow Restaurant – Next.js Demo

A restaurant website showcasing Nepali & Indian cuisine with an admin panel for managing menu items and viewing user messages.

## Features

### Public Site
- Responsive layout with a warm, human‑chosen colour palette.
- Home, Menu, About, Contact pages.
- Menu data fetched from an internal `/api/menu` route.
- Contact form sends messages to `/api/contact` (stored as JSON).

### Admin Panel
- Login page (`/admin/login`) – demo credentials: `admin` / `admin123`.
- Dashboard (`/admin/dashboard`) with two tabs:
  - **Messages**: view and delete messages submitted via the contact form.
  - **Menu Management**: add, edit, and delete menu items.
- All admin APIs (`/api/menu` POST/PUT/DELETE, `/api/contact` GET/DELETE) are protected by a simple cookie‑based auth.
- No payment integration (as requested).

## Getting Started

1. **Clone or copy the project** into a folder.
2. **Install dependencies**:

   ```bash
   npm install
   ```

3. **(Optional) Add placeholder images**  
   The UI references `/images/food.jpeg` and dish images listed in `src/data/menu.json` (e.g., `momo.jpg`, `chatamari.jpg`, etc.).  
   You can download free stock photos or create simple coloured placeholders and place them in `public/images/`.

4. **Run the development server**:

   ```bash
   npm run dev
   ```

5. Open <http://localhost:3000> to view the public site.  
   Visit <http://localhost:3000/admin/login> to access the admin panel (use demo credentials).

## Project Structure

```
foodflow-restaurant/
├─ .gitignore
├─ package.json
├─ next.config.js
├─ tsconfig.json
├─ README.md
├─ public/
│   └─ images/
│      ├─ food.jpeg          # used in home, menu, contact, hero
│      ├─ logo.png           # optional
│      ├─ momo.jpg
│      ├─ chatamari.jpg
│      ├─ biryani.jpg
│      ├─ paneer.jpg
│      ├─ gulabjamun.jpg
│      └─ chai.jpg
├─ src/
│   ├─ components/
│   │   ├─ Layout.tsx
│   │   ├─ Navbar.tsx
│   │   ├─ Footer.tsx
│   │   ├─ Hero.tsx
│   │   ├─ MenuCard.tsx
│   │   ├─ LoadingSpinner.tsx
│   │   └─ ErrorMessage.tsx
│   ├─ styles/
│   │   └─ globals.css
│   ├─ lib/
│   │   ├─ api.ts
│   │   ├─ file.ts
│   │   └─ auth.ts
│   └─ data/
│       └─ menu.json          # initial menu (can be extended via admin)
├─ pages/
│   ├─ _app.tsx
│   ├─ index.tsx
│   ├─ menu.tsx
│   ├─ about.tsx
│   ├─ contact.tsx
│   ├─ admin/
│   │   ├─ login.tsx
│   │   └─ dashboard.tsx
│   └─ api/
│       ├─ menu.ts
│       ├─ contact.ts
│       └─ admin/
│           ├─ login.ts
│           └─ logout.ts
```

## Colour Palette (chosen by humans)

| Variable          | Hex      | Usage                              |
|-------------------|----------|------------------------------------|
| `--color-primary` | `#C41E3A`| Deep red – primary buttons, headings |
| `--color-secondary`| `#E07A5F`| Warm orange – hover states        |
| `--color-accent`  | `#F2CC8F`| Soft gold – accents, underlines   |
| `--color-dark`    | `#3E2723`| Dark brown – body text, backgrounds|
| `--color-cream`   | `#FFF8E1`| Cream – page background           |
| `--color-teal`    | `#009688`| Teal – links, secondary buttons   |

Feel free to tweak these values in `src/styles/globals.css`.

## Admin Credentials (demo)

- **Username**: `admin`
- **Password**: `admin123`

> **Note**: This is a simple demo authentication using a hard‑coded cookie. For production, replace with a proper authentication system (e.g., NextAuth, JWT, etc.).

## License

MIT – feel free to adapt and extend.