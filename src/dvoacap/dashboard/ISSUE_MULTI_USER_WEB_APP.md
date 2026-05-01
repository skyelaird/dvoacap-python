# Feature Request: Multi-User Propagation Prediction Service

## Summary

Expand the current single-user Dashboard into a full multi-user web application that allows multiple amateur radio operators to configure their own stations and receive personalized propagation predictions.

## Motivation

The current Dashboard works great for VE1ATM's station, but there's potential to create a community service similar to PSKreporter or PropPy.net that serves the broader amateur radio community. This would allow any ham operator to:

- Configure their own QTH and station parameters
- Get personalized propagation predictions for their location
- Track their own DXCC progress
- Save preferences and view historical data

## Proposed Features

### 1. User Authentication & Accounts
- User registration/login system
- OAuth support (Google, GitHub, etc.)
- Callsign verification (optional, via QRZ API)

### 2. Per-User Station Configuration
Each user can configure:
- Callsign
- QTH (latitude/longitude or grid square)
- Antenna type and specifications
- Transmitter power
- Bands of interest
- Target DX regions

### 3. Database Backend
Store:
- User profiles and preferences
- Station configurations
- Historical prediction data
- QSO logs (if user chooses to sync)
- DXCC progress tracking

Suggested stack:
- PostgreSQL or SQLite for database
- SQLAlchemy ORM
- Alembic for migrations

### 4. API Endpoints

**Public API:**
- `GET /api/user/{callsign}/predictions` - Get current predictions for a user
- `GET /api/muf/{lat}/{lon}` - Get MUF for specific location
- `GET /api/solar` - Get current solar conditions

**Authenticated API:**
- `POST /api/predictions/generate` - Trigger prediction generation for logged-in user
- `GET /api/predictions/history` - Get historical prediction data
- `POST /api/station/update` - Update station configuration
- `POST /api/log/upload` - Upload ADIF log for DXCC tracking

### 5. Background Job System
- Celery or RQ for background task processing
- Scheduled prediction generation for all active users
- Configurable update frequency per user (hourly, every 2 hours, etc.)
- Redis for task queue

### 6. Enhanced Dashboard Features
- User dashboard showing their personalized predictions
- Historical graphs and trends
- Email/push notifications for DX opportunities
- Mobile-responsive design
- Export predictions as PDF/CSV
- Share prediction links with others

### 7. Community Features
- Public "Conditions Report" page showing aggregate propagation data
- Real-time propagation map (worldwide)
- Integration with DX clusters
- Community alerts for unusual propagation events

### 8. Administrative Interface
- Admin panel for managing users
- System health monitoring
- Resource usage dashboards
- Rate limiting configuration

## Technical Architecture

### Proposed Stack

**Backend:**
- FastAPI or Flask with Blueprints
- SQLAlchemy ORM
- Celery for background tasks
- Redis for caching and task queue
- PostgreSQL for primary database

**Frontend:**
- Keep existing HTML/CSS/JavaScript dashboard
- Add Vue.js or React for dynamic components
- Chart.js for historical graphs
- Leaflet.js for maps (already in use)

**Deployment:**
- Docker containers
- Docker Compose for local development
- Kubernetes for production scaling (optional)
- CI/CD with GitHub Actions

**Hosting Options:**
- AWS (EC2 + RDS + ElastiCache)
- DigitalOcean (Droplets + Managed Databases)
- Heroku (easy but more expensive)
- Self-hosted VPS

### File Structure

```
dvoacap-python/
├── src/dvoacap/          # Core prediction engine (unchanged)
├── dashboard/            # Current dashboard (becomes frontend)
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── predictions.py # Prediction endpoints
│   │   ├── stations.py   # Station management
│   │   └── users.py      # User management
│   ├── models/
│   │   ├── user.py
│   │   ├── station.py
│   │   ├── prediction.py
│   │   └── dxcc.py
│   ├── tasks/
│   │   ├── generate_predictions.py
│   │   └── solar_fetch.py
│   ├── database.py
│   ├── config.py
│   └── main.py
├── frontend/
│   ├── public/
│   ├── src/
│   └── package.json
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Implementation Phases

### Phase 1: MVP (4-6 weeks)
- [ ] User authentication (simple email/password)
- [ ] Station configuration per user
- [ ] Database schema and models
- [ ] API endpoints for predictions
- [ ] Background job for scheduled generation
- [ ] Deploy single instance for testing

### Phase 2: Community Features (4-6 weeks)
- [ ] Public propagation map
- [ ] Historical data tracking
- [ ] Email notifications for DX opportunities
- [ ] DXCC progress tracking per user
- [ ] Public API with rate limiting

### Phase 3: Scaling & Polish (4-6 weeks)
- [ ] Mobile app (React Native or Flutter)
- [ ] Advanced caching strategies
- [ ] CDN for static assets
- [ ] Admin dashboard
- [ ] Usage analytics
- [ ] Documentation and API docs

## Considerations

### Resource Requirements
- Prediction generation is CPU-intensive (DVOACAP Phases 1-5)
- Need to limit concurrent generations
- Consider:
  - Queue system with worker pool
  - Pre-compute predictions for common locations
  - Cache MUF data by region
  - Tiered service (free users get 2-hour updates, premium get hourly)

### Costs
- Cloud hosting: $50-200/month depending on users
- Database: $15-50/month
- Redis: $10-30/month
- Domain + SSL: $20/year
- Total estimate: $75-280/month for ~1000 active users

### Monetization Options (Optional)
- Keep free for basic service
- Premium tier ($5/month):
  - Hourly updates (vs 2-hour for free)
  - Historical data access
  - API access
  - No ads
  - Priority support
- One-time "supporter" tier ($25): Lifetime access to all features
- Donations via Ko-fi or Patreon

## Security Considerations
- Input validation on all user data
- Rate limiting on API endpoints
- SQL injection prevention (use ORM)
- XSS protection
- CSRF tokens
- Secure password hashing (bcrypt)
- HTTPS only
- API key authentication for programmatic access

## Success Metrics
- Number of registered users
- Daily active users
- API request volume
- Prediction generation load
- User retention rate
- Community engagement (forums, feedback)

## Alternatives Considered

### PropPy.net Integration
Instead of building everything from scratch, could integrate with PropPy.net's existing VOACAP service as a backend, focusing on:
- Better UX/UI
- DXCC tracking
- Mobile experience

**Pros:** Faster to market, lower resource usage
**Cons:** Dependency on external service, less control

### Hybrid Approach
- Offer both self-hosted (current dashboard) and hosted service
- Users can choose to:
  - Run dashboard locally (free, full control)
  - Use hosted service (convenience, mobile access)

## Related Issues
- #TBD - Dashboard cleanup and documentation
- #TBD - DVOACAP Phase 5 optimization for speed

## Questions for Discussion
1. Should this be a separate repository or stay in dvoacap-python?
2. What should the service be called? (PropStation? DXScope? HFWatch?)
3. Priority: Community service vs. research tool vs. commercial product?
4. Who would help maintain/admin such a service?

## References
- [PropPy.net](https://www.proppy.net/) - Existing VOACAP web service
- [PSKreporter](https://pskreporter.info/) - Real-time propagation monitoring
- [QRZ.com](https://www.qrz.com/) - Callsign lookup and logging

---

**Labels:** `enhancement`, `discussion`, `web-app`, `multi-user`, `dashboard`
**Priority:** Low (future consideration)
**Difficulty:** High (significant development effort)
