# DVOACAP-Python Wiki Content

This directory contains the complete Wiki documentation for DVOACAP-Python. The Wiki provides comprehensive guides, tutorials, and reference materials for users and developers.

## Wiki Pages

### Core Documentation

1. **[Home.md](Home.md)** - Wiki home page with navigation
   - Project overview
   - Quick links to all wiki pages
   - Current status

2. **[Getting-Started.md](Getting-Started.md)** - Installation and first steps
   - Installation options
   - Basic usage examples
   - Common installation issues

3. **[Architecture.md](Architecture.md)** - System design and structure
   - 5-phase architecture overview
   - Module dependencies
   - Data flow

4. **[API-Reference.md](API-Reference.md)** - Complete API documentation
   - All public classes and methods
   - Code examples
   - Type signatures

### User Guides

5. **[Validation-Status.md](Validation-Status.md)** - Testing and accuracy
   - Validation methodology
   - Current test coverage
   - Accuracy metrics by phase
   - Known issues

6. **[Troubleshooting.md](Troubleshooting.md)** - Common issues and solutions
   - Installation problems
   - Prediction issues
   - Dashboard problems
   - Performance tips

7. **[Comparison-Guide.md](Comparison-Guide.md)** - DVOACAP vs alternatives
   - vs Original VOACAP
   - vs DVOACAP (Pascal)
   - vs ITU P.533
   - vs WSPR/PSKReporter
   - When to use each

### Developer Guides

8. **[Contributing.md](Contributing.md)** - How to contribute
   - Development setup
   - Coding guidelines
   - Testing requirements
   - Pull request process

## Copying to GitHub Wiki

Once the GitHub Wiki is enabled for the repository, follow these steps to populate it:

### Method 1: Clone Wiki and Copy Files

```bash
# Enable Wiki on GitHub first (Repository Settings → Features → Wikis)

# Clone the wiki repository
git clone https://github.com/skyelaird/dvoacap-python.wiki.git

# Copy all markdown files
cd dvoacap-python.wiki
cp ../dvoacap-python/wiki/*.md .

# Commit and push
git add *.md
git commit -m "Initial wiki population"
git push origin master
```

### Method 2: Manual Copy (If Git Clone Doesn't Work)

1. Enable Wiki in repository settings
2. Visit https://github.com/skyelaird/dvoacap-python/wiki
3. Click "Create the first page"
4. For each .md file in this directory:
   - Click "New Page"
   - Use filename without .md as page title (e.g., "Getting Started" for Getting-Started.md)
   - Copy and paste markdown content
   - Save page

### Wiki Page Naming

GitHub Wiki converts filenames to page titles:
- `Home.md` → "Home" page
- `Getting-Started.md` → "Getting Started" page
- `API-Reference.md` → "API Reference" page

**Important:** The sidebar links in Home.md use GitHub Wiki syntax:
- `[Getting Started](Getting-Started)` links to the "Getting-Started" page
- Hyphens in filenames are preserved in URLs

## Wiki Structure

```
wiki/
├── README.md                    # This file
├── Home.md                      # Wiki homepage
├── Getting-Started.md           # Installation & basics
├── Architecture.md              # System design
├── API-Reference.md             # Complete API docs
├── Validation-Status.md         # Testing & accuracy
├── Troubleshooting.md           # Common issues
├── Contributing.md              # Development guide
└── Comparison-Guide.md          # vs other tools
```

## Updating the Wiki

### Automated Sync ✨

**Good news!** Wiki syncing is now automated via GitHub Actions.

When you push changes to the `main` branch that modify files in `wiki/`, the wiki is automatically synced to GitHub Wiki within a few minutes.

**Workflow:** `.github/workflows/wiki-sync.yml`

Just edit the markdown files and push to main - the rest happens automatically!

### Local Development

Edit markdown files in this directory:
```bash
cd wiki/
vim Getting-Started.md  # Make your changes
git add wiki/Getting-Started.md
git commit -m "Update getting started guide"
git push origin main  # ← Triggers automatic wiki sync!
```

### Manual Sync (If Needed)

If you need to sync the wiki manually (for testing or troubleshooting):

**Option 1: Use the sync script**
```bash
./scripts/sync-wiki.sh
```

**Option 2: Manual git commands**
```bash
# Clone wiki repo
git clone https://github.com/skyelaird/dvoacap-python.wiki.git wiki-repo

# Copy updated files
cp wiki/*.md wiki-repo/

# Push changes
cd wiki-repo
git add -A
git commit -m "Update wiki documentation"
git push
```

**Option 3: Trigger GitHub Action manually**
1. Go to Actions tab on GitHub
2. Select "Sync Wiki" workflow
3. Click "Run workflow"

### Best Practices

1. **Edit locally first** - Keep wiki/ directory as source of truth
2. **Test links** - Verify all internal links work
3. **Preview markdown** - Use a markdown previewer
4. **Automatic sync** - Push to main and let GitHub Actions handle the sync
5. **Commit to main repo** - Wiki markdown is version controlled

## Wiki Conventions

### Linking

**Internal wiki links:**
```markdown
[Getting Started](Getting-Started)
[API Reference](API-Reference)
```

**Repository links:**
```markdown
[NEXT_STEPS.md](https://github.com/skyelaird/dvoacap-python/blob/main/NEXT_STEPS.md)
```

**External links:**
```markdown
[VOACAP Online](https://www.voacap.com/)
```

### Code Blocks

Always specify language for syntax highlighting:
````markdown
```python
from dvoacap import FourierMaps
maps = FourierMaps()
```

```bash
pip install -e .
```
````

### Tables

Use GitHub-flavored markdown tables:
```markdown
| Feature | Status |
|---------|--------|
| Phase 1 | ✅ Complete |
| Phase 2 | ✅ Complete |
```

### Images (Future)

If adding images:
1. Create `wiki/images/` directory
2. Upload images to GitHub Wiki
3. Reference using relative paths:
```markdown
![Architecture Diagram](images/architecture.png)
```

## Contributing to Wiki

### Adding New Pages

1. Create new .md file in wiki/ directory
2. Follow naming convention: `Page-Title.md`
3. Add link to Home.md navigation
4. Update this README.md
5. Commit to repository
6. Sync to GitHub Wiki

### Updating Existing Pages

1. Edit .md file in wiki/ directory
2. Test locally (markdown preview)
3. Commit changes
4. Sync to GitHub Wiki

## Wiki Maintenance

### Regular Updates Needed

- **Validation Status** - Update as tests improve
- **API Reference** - Update when API changes
- **Troubleshooting** - Add new issues/solutions
- **Getting Started** - Update for new versions

### Version Tracking

Wiki content should match the latest development state. When making breaking changes:
1. Note version in page footer
2. Document migration steps
3. Keep old examples for reference

## Wiki Analytics (Future)

Once deployed, consider adding:
- GitHub Wiki page view tracking
- User feedback forms
- Most visited pages analysis
- Search term tracking

## Additional Resources

### External Documentation

The wiki complements but doesn't replace:
- **README.md** - Project overview
- **CONTRIBUTING.md** - Detailed contribution guide
- **NEXT_STEPS.md** - Development roadmap
- **docs/** directory - Technical specifications

### Links

- **Repository:** https://github.com/skyelaird/dvoacap-python
- **Issues:** https://github.com/skyelaird/dvoacap-python/issues
- **Wiki:** https://github.com/skyelaird/dvoacap-python/wiki (once enabled)

## Questions?

If you have questions about the wiki:
1. Check this README
2. Look at existing wiki pages for examples
3. Open an issue on GitHub
4. Ask in discussions

---

**Wiki Status:** ✅ Complete and ready to deploy (with automatic sync!)

**Version:** v1.0.0 (Production Ready)

**Last Updated:** 2025-11-18

**Total Pages:** 18 (including this README)

**Automation:** Automatic sync via GitHub Actions (`.github/workflows/wiki-sync.yml`)
