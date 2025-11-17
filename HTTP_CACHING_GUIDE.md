# HTTP Caching Quick Reference Guide

## What You're Seeing

```
127.0.0.1 - - [17/Nov/2025 16:03:28] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [17/Nov/2025 16:03:39] "GET / HTTP/1.1" 304 -
127.0.0.1 - - [17/Nov/2025 16:04:15] "GET / HTTP/1.1" 304 -
```

**This is CORRECT behavior!** The 304 responses mean HTTP caching is working as designed.

## Quick Actions

### Disable Caching (For Development)

```bash
# Option 1: Use --no-cache flag
python3 Dashboard/server.py --no-cache

# Option 2: Use --debug flag (also disables caching)
python3 Dashboard/server.py --debug
```

### Force Browser to Fetch Fresh Content

**Hard Refresh:**
- **Windows/Linux**: `Ctrl + Shift + R` or `Ctrl + F5`
- **Mac**: `Cmd + Shift + R`

### Check Current Cache Status

```bash
# Run the test script
python3 test_caching.py

# Or check the debug endpoint
curl http://localhost:8000/api/debug/cache | python3 -m json.tool
```

## Understanding the Status Codes

| Code | Meaning | What Happens |
|------|---------|--------------|
| 200  | OK | Full content sent (first request or cache disabled) |
| 304  | Not Modified | No content sent, browser uses cached version |

## Server Startup Messages

When you start the server, you'll see:

```
================================================================================
VE1ATM HF Propagation Dashboard Server
================================================================================

✓ Server starting on http://127.0.0.1:8000
✓ Dashboard: http://127.0.0.1:8000/
✓ Debug mode: Enabled/Disabled
✓ HTTP caching: Enabled/Disabled
✓ Press Ctrl+C to stop
```

## When to Enable/Disable Caching

### Enable Caching (Production - DEFAULT)

```bash
python3 Dashboard/server.py
```

**Use when:**
- Running in production
- Want optimal performance
- Want to reduce bandwidth usage

**Result:**
- First request: 200
- Subsequent requests: 304 (fast!)

### Disable Caching (Development)

```bash
python3 Dashboard/server.py --no-cache
# or
python3 Dashboard/server.py --debug
```

**Use when:**
- Actively developing
- Testing changes
- Need fresh content every time

**Result:**
- All requests: 200 (full content)

## API Endpoints

### Debug Cache Configuration

```bash
GET /api/debug/cache
```

Returns current cache configuration and sample headers.

**Example:**
```bash
curl http://localhost:8000/api/debug/cache | python3 -m json.tool
```

**Response:**
```json
{
  "cache_enabled": true,
  "debug_mode": false,
  "disable_cache_flag": false,
  "sample_headers": {
    "Cache-Control": "public, max-age=300"
  },
  "explanation": {
    "200": "First request - Full content sent with ETag/Last-Modified headers",
    "304": "Subsequent requests - Browser sends If-None-Match/If-Modified-Since, server responds with 304 if unchanged",
    "cache_control": "public, max-age=300"
  },
  "tips": {
    "disable_cache": "Start server with --no-cache flag to disable caching",
    "debug_mode": "Start server with --debug flag to auto-disable caching",
    "browser_refresh": "Use Ctrl+Shift+R (Cmd+Shift+R on Mac) for hard refresh"
  }
}
```

## How HTTP Caching Works

### 1. First Request (200 Response)

**Browser → Server:**
```http
GET / HTTP/1.1
Host: localhost:8000
```

**Server → Browser:**
```http
HTTP/1.1 200 OK
Cache-Control: public, max-age=300
ETag: "abc123def456"
Last-Modified: Sun, 17 Nov 2025 16:00:00 GMT
Content-Length: 12345

[full HTML content]
```

Browser stores the response with ETag and Last-Modified values.

### 2. Subsequent Request (304 Response)

**Browser → Server:**
```http
GET / HTTP/1.1
Host: localhost:8000
If-None-Match: "abc123def456"
If-Modified-Since: Sun, 17 Nov 2025 16:00:00 GMT
```

**Server → Browser:**
```http
HTTP/1.1 304 Not Modified
ETag: "abc123def456"
Last-Modified: Sun, 17 Nov 2025 16:00:00 GMT

[no body - saves bandwidth!]
```

Browser uses cached version (no content transfer needed).

## Cache Headers Explained

| Header | Purpose | Example |
|--------|---------|---------|
| `Cache-Control` | Controls caching behavior | `public, max-age=300` |
| `ETag` | Content fingerprint | `"abc123def456"` |
| `Last-Modified` | File modification time | `Sun, 17 Nov 2025 16:00:00 GMT` |
| `If-None-Match` | Conditional request (ETag) | `"abc123def456"` |
| `If-Modified-Since` | Conditional request (time) | `Sun, 17 Nov 2025 16:00:00 GMT` |

### Cache-Control Values

**Production (Caching Enabled):**
```
Cache-Control: public, max-age=300
```
- `public`: Can be cached by browser and proxies
- `max-age=300`: Cache for 5 minutes

**Development (Caching Disabled):**
```
Cache-Control: no-cache, no-store, must-revalidate
Pragma: no-cache
Expires: 0
```
- `no-cache`: Must revalidate before using cache
- `no-store`: Don't store in cache at all
- `must-revalidate`: Strict cache validation

## Testing with curl

```bash
# Test first request (should be 200)
curl -I http://localhost:8000/

# Extract ETag
ETAG=$(curl -s -I http://localhost:8000/ | grep -i etag | cut -d' ' -f2 | tr -d '\r')

# Test conditional request (should be 304)
curl -I -H "If-None-Match: $ETAG" http://localhost:8000/

# Test debug endpoint
curl http://localhost:8000/api/debug/cache | python3 -m json.tool
```

## Testing with Python

```bash
python3 test_caching.py
```

This will:
1. Check debug cache configuration
2. Test first request (200)
3. Test conditional request (304 if caching enabled)
4. Show summary of caching behavior

## Troubleshooting

### Issue: Always getting 200, never 304

**Possible causes:**
- Caching is disabled (`--no-cache` or `--debug` flag)
- Using hard refresh in browser
- Browser dev tools "Disable cache" is checked
- Cache-Control header says `no-cache` or `no-store`

**Solution:**
- Start server without `--no-cache` or `--debug`
- Use normal refresh (F5) instead of hard refresh
- Uncheck "Disable cache" in browser dev tools
- Check `/api/debug/cache` endpoint

### Issue: Want 200 every time (disable caching)

**Solution:**
```bash
python3 Dashboard/server.py --no-cache
```

Or in browser: Use hard refresh (`Ctrl+Shift+R`)

## Performance Impact

### With Caching (Production - DEFAULT)

```
First request:    200 OK      12.5 KB transferred    150ms
Second request:   304 OK      0 KB transferred       20ms   ⚡️ 86% faster!
Third request:    304 OK      0 KB transferred       18ms   ⚡️ 88% faster!
```

### Without Caching (Development)

```
First request:    200 OK      12.5 KB transferred    150ms
Second request:   200 OK      12.5 KB transferred    145ms
Third request:    200 OK      12.5 KB transferred    148ms
```

## References

- Full documentation: [CACHING_DEBUG.md](CACHING_DEBUG.md)
- Test script: [test_caching.py](test_caching.py)
- MDN HTTP Caching: https://developer.mozilla.org/en-US/docs/Web/HTTP/Caching
