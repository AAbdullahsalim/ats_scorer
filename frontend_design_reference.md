# ATS Scorer v2 — Frontend Design Reference

## Design Philosophy
- Minimalist, creative, non-AI color theme
- Golden ratio proportions for layout
- Unique color palette — NOT generic tech-blue or AI-purple
- Professional business tool aesthetic
- Fast performance — HR should never wait for animations
- No emojis anywhere in the UI

## Color Direction
- Research golden ratio color harmony
- Warm neutrals + one accent color
- Dark mode primary
- Subtle gradients, not flat blocks

---

## CSS Techniques to Apply

### Transitions
- transition-property, transition-timing-function
- linear, ease-in, ease-out, ease-in-out, cubic-bezier
- Keep transitions under 300ms for snappy feel

### Transforms
- transform-origin, matrix, perspective
- x-axis, y-axis, z-axis rotations
- Use for hover effects on cards/buttons

### Filters
- drop-shadow, background-blend-mode, mix-blend-mode
- Subtle backdrop-filter for glassmorphism on modals

### Clip-path
- clip, SVG paths, url, basic-shapes
- Use for creative section dividers or card shapes

### Pseudo-elements
- ::first-letter, ::first-line, ::selection, ::placeholder, ::marker
- Custom selection colors matching theme

### 3D Effects
- transform-3d, rotateX, rotateY, rotateZ, translateZ
- Subtle card tilt on hover (max 2-3 degrees)

### Parallax Effects
- scroll-behavior, fixed, relative, viewport
- Subtle parallax on hero section if applicable

### Advanced Selectors
- :nth-child, :nth-of-type, :last-child, :only-child
- :not(), [attribute^=value], [attribute$=value], [attribute*=value]
- Use for zebra-striping tables, alternating card layouts

### Layout Techniques
- Flexbox: flex-grow, flex-shrink, flex-basis, justify-content, align-items
- Grid Layout: grid-template-columns, grid-template-rows, grid-area, grid-gap
- Multi-column layout: column-count, column-gap, column-rule

### Responsive Design
- media queries, @media, min-width, max-width
- aspect-ratio, resolution, orientation, viewport
- responsive images, srcset, sizes
- Mobile-first approach

### Animations
- @keyframes, animation-name, animation-duration
- animation-timing-function, animation-delay
- animation-iteration-count, animation-direction, animation-fill-mode
- Keep animations subtle — fade-ins, slide-ups, scale transitions
- No bouncing, no spinning, no flashy effects

### Advanced Effects
- box-shadow (layered shadows for depth)
- text-shadow (minimal, only for headings if needed)
- border-radius (consistent rounding)
- gradient: linear-gradient, radial-gradient, conic-gradient
- filter, blend modes

### CSS Variables
- --var-name, var(), custom properties
- Global design tokens: colors, spacing, typography, shadows
- Local component variables

### Pseudo-Classes
- :hover, :focus, :active, :checked
- :disabled, :valid, :invalid, :required, :optional
- Focus-visible for keyboard navigation

### Performance Optimization
- Critical CSS, CSS minification
- Avoid render-blocking resources
- Use will-change sparingly
- Prefer transform/opacity for animations (GPU-accelerated)

### CSS Architecture
- BEM naming if using vanilla CSS
- Component-scoped styles with CSS Modules or styled-components
- Atomic design principles

---

## HTML Elements & Attributes

### Semantic Elements
- <main>, <section>, <article>, <aside>, <header>, <footer>, <nav>
- <figure>, <figcaption>, <details>, <summary>
- <blockquote>, <cite>, <abbr>, <code>, <pre>, <mark>, <time>

### Interactive Elements
- <button>, <dialog> for modals
- tabindex, accesskey, hidden

### Forms and Inputs
- type="email", type="number", type="date", type="range", type="color"
- placeholder, autofocus, autocomplete, pattern

### Accessibility
- role, aria-label, aria-labelledby, aria-hidden, aria-live
- tabindex, screen reader support
- Accessibility tree compliance

### Meta Tags
- <meta name="description">, <meta name="keywords">
- <link rel="icon">, <link rel="canonical">

---

## Performance Checklist
- Lighthouse score target: 90+
- Lazy loading for images and heavy components
- Image optimization
- HTTP/2 ready
- Service worker for offline capability (if needed)
- Caching strategies for static assets
