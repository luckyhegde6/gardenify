# Phase 4: Scale & Optimize

> Goal: Optimize for performance, add analytics, and prepare for production scale.

## Features

- [ ] Image hash caching optimization
  - [ ] Batch caching during off-peak hours
  - [ ] Cache warming for common species
  - [ ] Cache invalidation strategy
- [ ] CDN for images
  - [ ] Supabase Storage CDN configuration
  - [ ] Thumbnail generation for history list
  - [ ] Progressive image loading
- [ ] Database optimization
  - [ ] Partition identifications table by month
  - [ ] Archive old data to cold storage
  - [ ] Add read replicas for history queries
- [ ] Rate limiting dashboard
  - [ ] Admin view of PlantNet quota usage
  - [ ] Per-user usage tracking
  - [ ] Alert when quota is low
- [ ] Analytics integration
  - [ ] PostHog or Mixpanel for user analytics
  - [ ] Identification success rate tracking
  - [ ] Feature usage metrics
- [ ] Admin dashboard
  - [ ] View all identifications
  - [ ] Manage users
  - [ ] Monitor PlantNet API health
  - [ ] Export data
- [ ] Performance optimization
  - [ ] Image lazy loading in history
  - [ ] FlatList optimization for large lists
  - [ ] Backend response caching (Redis)
- [ ] Security audit
  - [ ] Penetration testing
  - [ ] RLS policy review
  - [ ] Dependency audit (npm audit, pip audit)
  - [ ] OWASP Mobile Top 10 checklist
