# Website

A simple static website project.

## Overview

This folder contains the source files for the website: HTML pages, stylesheets, scripts, and assets such as images and fonts.

## Project Structure

```
website/
├── index.html        # Home page
├── marketing.html    # Marketing page
├── css/
│   └── styles.css    # Global styles
├── js/
│   └── main.js       # Client-side scripts
├── assets/
│   ├── images/       # Images and icons
│   └── fonts/        # Web fonts
└── README.md         # This file
```

## Getting Started

### Prerequisites

- A modern web browser (Chrome, Firefox, Edge, Safari)
- Optional: a local web server for testing (e.g. Python or Node.js)

### Running Locally

Open `index.html` directly in a browser, or serve the folder with a local web server:

```bash
# Using Python
python3 -m http.server 8000

# Using Node.js
npx serve .
```

Then visit <http://localhost:8000> in your browser.

## Development

- Keep page markup in `.html` files, styles in `css/`, and scripts in `js/`.
- Use semantic HTML and keep pages accessible (alt text, labels, sufficient color contrast).
- Make layouts responsive so they work on both mobile and desktop.
- Optimize images before adding them to `assets/images/`.

## Deployment

Since this is a static site, it can be hosted on any static hosting service, such as:

- GitHub Pages
- Netlify
- Vercel
- Cloudflare Pages

Upload or connect the `website/` folder as the site root.

## Contributing

1. Create a new branch for your change.
2. Make and test your changes locally.
3. Open a pull request with a short description of what changed.

## License

Add license information here.
