# Frontend Build Process - NPM Migration

## Overview
The Kshethra-mithram Frontend has been migrated from CDN/local library files to NPM package management. All JavaScript and CSS dependencies are now managed through `package.json` and bundled using Webpack.

## Dependencies
The project now uses:
- **Bootstrap 5** - UI Framework
- **Bootstrap Icons** - Icon library
- **jQuery 3.6** - DOM manipulation
- **Tom Select** - Enhanced select boxes
- **Webpack** - Module bundler

## Local Development Setup

### Installation
```bash
npm install
```

This installs all dependencies defined in `package.json` into the `node_modules/` directory.

### Development Build (Watch Mode)
```bash
npm run dev
```

This runs Webpack in watch mode, automatically rebuilding when files change. Useful for active development.

### Production Build
```bash
npm run build
```

This creates optimized, minified bundles in `app/static/dist/`:
- `app.css` - All CSS concatenated and minified
- `app.js` - All JavaScript bundled and minified
- `fonts/` - Bootstrap Icon font files

### Clean Build
```bash
npm run clean
```

Removes the `app/static/dist/` directory to start fresh.

## Build Output

After running `npm run build`, the following files are generated:
- `app/static/dist/app.css` - ~343 KB (combined CSS from Bootstrap, Bootstrap Icons, Tom Select)
- `app/static/dist/app.js` - ~217 KB (combined JS from Bootstrap, jQuery, Tom Select)
- `app/static/dist/fonts/` - Bootstrap Icon fonts

These bundled files are referenced in `app/templates/base.html`.

## Docker Build

The `Dockerfile` uses a **multi-stage build process**:

### Stage 1: Frontend Build (Node.js)
- Installs Node.js dependencies
- Builds frontend assets with Webpack
- Output: `app/static/dist/` directory

### Stage 2: Python Runtime
- Inherits from Python 3.11-slim
- Installs Python dependencies
- Copies pre-built frontend assets from Stage 1

To build the Docker image:
```bash
docker build -t kshethra-mithram:latest .
```

To run the container:
```bash
docker run -p 5000:5000 kshethra-mithram:latest
```

## File Structure

```
kshethra-mithram/
├── package.json              # NPM dependencies & build scripts
├── webpack.config.js         # Webpack bundler configuration
├── .npmrc                    # NPM configuration
├── assets/
│   └── index.js             # Entry point for webpack
├── app/
│   ├── static/
│   │   ├── dist/            # Generated bundled files (gitignored)
│   │   ├── css/             # Old library files (deprecated)
│   │   ├── js/              # Old library files (deprecated)
│   │   └── uploads/         # User uploads
│   └── templates/
│       └── base.html        # Updated to use dist/ assets
├── Dockerfile               # Multi-stage Docker build
└── .gitignore              # Includes node_modules/ and /app/static/dist/
```

## Migration Notes

### What Changed
1. **Asset Loading**: Templates now load `{{ url_for('static', filename='dist/app.css') }}` and `{{ url_for('static', filename='dist/app.js') }}`
2. **Old Files**: Files in `app/static/css/` and `app/static/js/` are deprecated (kept for reference but not used)
3. **Version Management**: All versions are now in `package.json`, making updates easier

### Benefits
- ✅ Centralized dependency management
- ✅ Easy version updates: `npm update`
- ✅ Can use npm ecosystem and additional packages
- ✅ Smaller git repo (no minified libraries committed)
- ✅ Better Docker layer caching (separate build stages)

## Troubleshooting

### Build errors
If `npm run build` fails:
1. Delete `node_modules/` and `package-lock.json`
2. Run `npm install` again
3. Run `npm run build`

### Static assets not loading
1. Verify `app/static/dist/` directory exists
2. Verify `Dockerfile` ran the build stage successfully
3. Check browser DevTools Network tab for 404 errors

### Tom Select not working
The Tom Select script automatically initializes on all `<select class="form-select">` elements. Ensure selects have the `form-select` class.

## Future Improvements

Potential optimizations:
- Code splitting to separate CSS by page
- Bundle analysis and optimization
- Service Worker for offline support
- TypeScript support
