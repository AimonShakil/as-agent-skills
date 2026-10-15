---
paths:
  - "website/**"
  - "marketingpage/**" 
---
# Website rules

## Where these rules apply

These rules apply to every file inside the `website/` folder and its subfolders, including:

- `website/index.html`: home page
- `website/marketing.html`: marketing page
- `website/css/`, `website/js/`, `website/assets/`: shared styles, scripts and media
- `website/README.md`

They do not apply to anything outside `website/`, such as `bookcontent/` (which has its own rule in `content.md`).

## Rules

- Keep the site static: plain HTML, CSS and JavaScript, no build step or framework unless asked.
- Follow the layout in `website/README.md`: pages at the root, styles in `css/`, scripts in `js/`, images and fonts in `assets/`.
- Use semantic HTML (`header`, `nav`, `main`, `section`, `footer`) and give every image meaningful `alt` text.
- Make every page responsive and usable at phone width (~400px).
- Use 2-space indentation and lowercase, hyphenated file names (e.g. `about-us.html`).
- No inline styles or inline scripts; link external `.css` and `.js` files.
- When adding or moving files, update `website/README.md` if the project structure changes.
