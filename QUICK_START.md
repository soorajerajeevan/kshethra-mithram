# Quick Start: NPM Frontend Build

## First Time Setup

```bash
# 1. Install dependencies
npm install

# 2. Build frontend assets
npm run build

# 3. Start Flask app (from project root)
python run.py
```

Open http://localhost:5000 in your browser.

## Development Workflow

### Continuous Build (Watch Mode)
If you're modifying assets, run this in a separate terminal:
```bash
npm run dev
```

The build will automatically rebuild when you change files in the `assets/` directory.

### Production Build
```bash
npm run build
```

This creates optimized, minified bundles in `app/static/dist/`.

## Docker Deployment

### Build Image
```bash
docker build -t kshethra-mithram:latest .
```

The Dockerfile automatically:
1. Installs Node.js dependencies
2. Builds frontend assets with Webpack
3. Installs Python dependencies
4. Bundles everything for production

### Run Container
```bash
docker run -p 5000:5000 kshethra-mithram:latest
```

Open http://localhost:5000

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `npm: command not found` | Install Node.js from https://nodejs.org/ |
| Build fails | Run `npm install` again to reinstall dependencies |
| Assets not loading | Verify `app/static/dist/` exists and has files |
| Docker build fails | Check if Node.js is available in the build container |

## What Changed?

**Before (CDN/Local)**
- Assets stored as individual files in `app/static/css/` and `app/static/js/`
- Hard to update library versions
- Large git repository

**After (NPM)**
- Single `package.json` defines all dependencies
- Webpack bundles everything into `app/static/dist/app.css` and `app.js`
- Easy to update: `npm update`
- Smaller git repository

## File References

| File | Purpose |
|------|---------|
| `package.json` | NPM dependencies & build scripts |
| `webpack.config.js` | Bundler configuration |
| `assets/index.js` | Entry point for bundler |
| `app/static/dist/` | Generated bundled files |
| `FRONTEND_BUILD.md` | Detailed build documentation |
| `MIGRATION_SUMMARY.md` | Full migration details |

## Next Steps

1. ✅ Run `npm install` and `npm run build` to verify setup
2. ✅ Test Flask app locally and verify assets load
3. ✅ Test Docker build: `docker build -t test .`
4. ✅ Run container and test in browser
5. Deploy with confidence!

## Need Help?

- See `FRONTEND_BUILD.md` for detailed documentation
- See `MIGRATION_SUMMARY.md` for what changed and why
- Check browser DevTools Console for JavaScript errors
- Check browser DevTools Network tab to verify assets load

---

**Happy building!** 🚀
