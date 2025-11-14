# Wiki Migration Recommendation

## Current Documentation Structure

### Root-Level Documentation
- `README.md` (370 lines) - Main project overview, installation, usage
- `CONTRIBUTING.md` - Contribution guidelines
- `VALIDATION.md` - Validation status and strategy
- `VALIDATION_SUMMARY.md` - Validation results summary
- `VALIDATION_STRATEGY.md` - Detailed validation methodology
- `FORTRAN_ANALYSIS_AND_RECOMMENDATIONS.md` - FORTRAN source analysis
- `DEBUG_QUICKSTART.md` - Debug guide
- `ABSORPTION_BUG_ANALYSIS.md` - D-layer absorption bug analysis

### docs/ Directory (Mixed MD and PDF)
- `USAGE.md` (17 KB) - API usage guide
- `INTEGRATION.md` (33 KB) - Integration examples
- `PHASE3_COMPLETE.md` (12 KB) - Phase 3 implementation summary
- `PHASE4_SUMMARY.md` (7.8 KB) - Phase 4 implementation summary
- `REORGANIZATION_GUIDE.md` (7.5 KB) - Code reorganization guide
- `CHECKLIST.md` (2 KB) - Development checklist
- `PATHGEOMETRY_PORT_SUMMARY.pdf` (429 KB) - Phase 1 summary
- `PHASE2_COMPLETE.pdf` (971 KB) - Phase 2 summary
- `PROJECT_STATUS.pdf` (696 KB) - Overall project status
- `QUICK_START v0.1.pdf` (548 KB) - Quick start guide
- `README.pdf` (813 KB) - README in PDF format

### Dashboard Documentation
- `Dashboard/README.md` - Dashboard setup and usage
- `Dashboard/ISSUE_MULTI_USER_WEB_APP.md` - Multi-user roadmap

## Recommendation: **Keep docs/ in repository, use Wiki for user-facing guides**

### Rationale

1. **PDFs are version-controlled assets** - The large PDF files (PATHGEOMETRY_PORT_SUMMARY.pdf, PHASE2_COMPLETE.pdf, etc.) should remain in the repository as they are:
   - Historical development documentation
   - Detailed technical specifications
   - Best suited for git LFS or direct repository storage

2. **Technical docs should stay in /docs** - The Markdown files in docs/ are:
   - Tightly coupled to code versions
   - Reference material for developers
   - Better suited for version control than wiki
   - Can be linked from README and wiki

3. **Wiki should host user-facing content** - The GitHub Wiki is ideal for:
   - Getting started guides (convert QUICK_START v0.1.pdf to MD)
   - Tutorials and examples
   - FAQ and troubleshooting
   - Community contributions
   - Living documentation that changes frequently

## Proposed Wiki Structure

### Home
- Project overview (condensed from README.md)
- Quick navigation to other wiki pages
- Links to repository docs/ for technical details

### Getting Started
- Installation guide (from README.md)
- Quick start tutorial (convert docs/QUICK_START v0.1.pdf to Markdown)
- First prediction example
- Common issues and solutions

### User Guide
- API Usage (from docs/USAGE.md or link to it)
- Ionospheric Profiles Guide
- Antenna Configuration
- Noise Modeling
- Path Geometry Calculations

### Integration Guide
- Web Applications (from docs/INTEGRATION.md)
- Dashboard Setup (from Dashboard/README.md)
- Database Integration
- API Endpoints
- Example Projects

### Validation & Accuracy
- Validation Strategy (from VALIDATION_STRATEGY.md)
- Test Results (from VALIDATION_SUMMARY.md)
- Known Issues (from ABSORPTION_BUG_ANALYSIS.md)
- Comparison with VOACAP

### Development Guide
- Contributing (link to CONTRIBUTING.md)
- Phase Implementation Status (summarize from PROJECT_STATUS.pdf)
- Debug Guide (from DEBUG_QUICKSTART.md)
- FORTRAN Source Analysis (link to FORTRAN_ANALYSIS_AND_RECOMMENDATIONS.md)

### FAQ
- Installation issues
- Common errors
- Performance optimization
- Accuracy vs VOACAP

## Migration Plan

### Phase 1: Create Wiki Structure (Quick Win)
1. Create Home page with project overview
2. Create Getting Started page (extract from README.md)
3. Create FAQ page for common issues
4. Add links from README.md to wiki

### Phase 2: Convert Key Documentation
1. Convert docs/QUICK_START v0.1.pdf to Markdown wiki page
2. Link or summarize docs/USAGE.md in wiki
3. Link or summarize docs/INTEGRATION.md in wiki
4. Create Validation & Accuracy page from VALIDATION_*.md files

### Phase 3: Community Pages
1. Create Troubleshooting page
2. Create Examples Gallery
3. Create Performance Tips page
4. Encourage community contributions to wiki

## What Should NOT Move to Wiki

1. **Keep in repository:**
   - README.md (should remain as repo entry point)
   - CONTRIBUTING.md (GitHub expects this in root)
   - LICENSE
   - All PDF technical documentation (large binary files)
   - Code-specific docs (REORGANIZATION_GUIDE.md, etc.)
   - Bug analysis docs (ABSORPTION_BUG_ANALYSIS.md)

2. **Keep in docs/ directory:**
   - Phase summaries (PHASE*.md, PHASE*.pdf)
   - Technical specifications
   - API reference documentation
   - Developer-focused guides

## Benefits of This Approach

1. **Single source of truth** - Technical docs stay version-controlled in repo
2. **Better discoverability** - Users find guides on wiki, developers find specs in docs/
3. **Community editing** - Wiki allows community contributions without PRs
4. **Reduced clutter** - Repo focuses on code, wiki focuses on usage
5. **Flexible updates** - Wiki can be updated independently of releases

## Recommendation

**Start with Phase 1 (wiki structure) without moving existing docs**

The current docs/ structure is well-organized and version-controlled. Rather than migrating everything, create a complementary wiki that:
- Provides user-friendly guides (converted from PDFs)
- Offers tutorials and examples
- Allows community FAQ and troubleshooting
- Links back to authoritative docs/ for technical details

This gives the best of both worlds: version-controlled technical documentation in the repo, and community-editable user guides on the wiki.
