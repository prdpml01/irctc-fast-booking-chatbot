# Build notes

## Phase 1: Core Backend (Done)
✅ FastAPI app with routing
✅ Request parser for trip details
✅ In-memory + Redis caching
✅ JWT-based authentication
✅ Rate limiting
✅ Audit logging
✅ Docker containerization

## Phase 2: Frontend (Next)
- [ ] React/Next.js UI
- [ ] Chatbot interface for natural language input
- [ ] Passenger details form
- [ ] Real-time booking status
- [ ] WebSocket for live updates

## Phase 3: Production Integration
- [ ] Connect to real IRCTC or partner API
- [ ] Secure passenger data encryption
- [ ] Payment gateway integration
- [ ] OTP/CAPTCHA forwarding (no bypass)
- [ ] Database (PostgreSQL or MongoDB)
- [ ] Monitoring and alerting

## Phase 4: Deployment
- [ ] Kubernetes manifests
- [ ] CI/CD pipeline (GitHub Actions)
- [ ] Load testing and optimization
- [ ] Security audit

## Performance Notes
- Target: < 1 second for booking-plan generation
- Parallel fetching: schedule cache + passenger profile
- Rate limiting: 10 requests per 60 seconds per user
- Audit trail: all user actions logged
