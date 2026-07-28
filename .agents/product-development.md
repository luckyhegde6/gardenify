# Product Development Focus

> Build features that users love, not just features that work.

## 1. Product Thinking Framework

### Before Building Any Feature
```
□ WHO is this for? (User persona)
□ WHAT problem does it solve? (Value proposition)
□ WHY would they use it? (Motivation)
□ HOW will they discover it? (Discovery)
□ WHEN will they use it? (Context)
□ WHERE will they use it? (Environment)
```

### User Personas
| Persona | Description | Needs |
|---|---|---|
| Casual Gardener | Wants to know what plants they see | Quick ID, care tips |
| Plant Enthusiast | Deep knowledge, wants details | Full taxonomy, disease detection |
| Gardener | Needs care instructions | Watering, sunlight, soil info |
| Teacher | Uses for education | Shareable results, accuracy |

### Value Proposition
- **For casual gardeners**: "Identify any plant in seconds with your camera"
- **For plant enthusiasts**: "Get detailed species info, disease detection, and care tips"
- **For gardeners**: "Never kill a plant again with personalized care instructions"

## 2. Feature Prioritization

### MoSCoW Method
| Priority | Description | Examples |
|---|---|---|
| Must Have | Core functionality | Plant identification, results display |
| Should Have | Important but not critical | Disease detection, care tips |
| Could Have | Nice to have | Favorites, sharing, offline mode |
| Won't Have (now) | Future consideration | AR visualization, social features |

### RICE Scoring
| Factor | Weight | Description |
|---|---|---|
| Reach | 30% | How many users will this affect? |
| Impact | 30% | How much value will it add? |
| Confidence | 20% | How sure are we about estimates? |
| Effort | 20% | How much work is required? |

### Feature Examples
| Feature | Reach | Impact | Confidence | Effort | RICE |
|---|---|---|---|---|---|
| Plant ID | High | High | High | Medium | 85 |
| Disease detection | Medium | High | High | Low | 78 |
| Care tips | High | Medium | High | Low | 75 |
| Favorites | Medium | Medium | High | Low | 65 |
| Sharing | Low | Medium | Medium | Low | 45 |
| Offline mode | Low | High | Low | High | 35 |

## 3. Usability Principles

### Nielsen's Heuristics
1. **Visibility of system status**: Show loading, progress, errors
2. **Match between system and real world**: Use plant terminology
3. **User control and freedom**: Undo, back, cancel
4. **Consistency and standards**: Follow platform conventions
5. **Error prevention**: Validate inputs, confirm destructive actions
6. **Recognition rather than recall**: Show recent identifications
7. **Flexibility and efficiency**: Shortcuts for power users
8. **Aesthetic and minimalist design**: Don't overwhelm with info
9. **Help users recognize errors**: Clear error messages
10. **Help and documentation**: In-app help, tooltips

### Mobile-Specific UX
```
□ Touch targets >= 44x44 points
□ No more than 3 taps to core feature
□ Loading states for all async operations
□ Offline support for critical features
□ Clear visual feedback for all actions
□ Consistent navigation pattern
□ Safe area handling
□ Keyboard avoidance
```

### Plant ID Specific UX
```
□ Camera opens fast (< 1 second)
□ Clear instructions for best photo
□ Progress indicator during identification
□ Results load fast (< 3 seconds)
□ Clear confidence score display
□ Easy to save/share results
□ Clear care instructions
□ Error recovery (retry, new photo)
```

## 4. Feature Specification Template

```markdown
# Feature Name

## User Story
As a [persona], I want [action] so that [benefit].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## UI/UX Requirements
- Screen layout
- User flow
- Error states
- Loading states

## Technical Requirements
- API endpoints
- Database changes
- Dependencies

## Metrics
- Success metric
- How to measure
- Target value
```

## 5. Usability Testing

### Test Protocol
```
1. Give user a task (e.g., "Identify this plant")
2. Observe without helping
3. Note where they struggle
4. Ask why they did what they did
5. Suggest improvements
```

### Metrics to Track
| Metric | Target | How to Measure |
|---|---|---|
| Task completion rate | > 90% | User testing |
| Time to first identification | < 30 seconds | Analytics |
| Error rate | < 5% | Analytics |
| User satisfaction | > 4/5 | Survey |
| Retention (Day 7) | > 30% | Analytics |

## 6. Accessibility

### WCAG 2.1 Checklist
```
□ Color contrast >= 4.5:1
□ Touch targets >= 44x44
□ Screen reader support
□ Keyboard navigation
□ No flashing content
□ Alternative text for images
□ Clear focus indicators
□ Error identification
```

### Plant ID Accessibility
```
□ Camera instructions for visually impaired
□ VoiceOver/TalkBack labels
□ High contrast mode support
□ Large text support
□ Haptic feedback for actions
```

## 7. Performance Targets

| Metric | Target | Current |
|---|---|---|
| App launch time | < 2 seconds | — |
| Time to identification | < 3 seconds | — |
| Image upload time | < 2 seconds | — |
| API response time | < 500ms | — |
| Frame rate | 60 fps | — |
| Memory usage | < 200MB | — |
| Bundle size | < 50MB | — |

## 8. Analytics Events

### Core Events
```typescript
// User actions
track('app_launch');
track('camera_open');
track('image_capture');
track('image_select');
track('identify_start');
track('identify_complete', { species, confidence });
track('identify_error', { error });
track('result_view', { species });
track('result_share', { species });
track('result_save', { species });

// Navigation
track('screen_view', { screen });
track('tab_switch', { tab });

// Errors
track('api_error', { endpoint, status });
track('image_upload_error', { reason });
```

### Metrics Dashboard
```
- Daily Active Users
- Identifications per Day
- Average Confidence Score
- Error Rate
- Average Response Time
- User Retention (D1, D7, D30)
- Feature Adoption Rate
```

## 9. Release Strategy

### Feature Flags
```typescript
// Gradual rollout
const features = {
  diseaseDetection: user.plan === 'premium',
  offlineMode: config.enableOffline,
  sharing: experiment.isEnabled('sharing-v2'),
};
```

### Staged Rollout
```
1. Internal testing (team only)
2. Beta testers (100 users)
3. Limited rollout (10% of users)
4. Full rollout (100% of users)
```

### Rollback Plan
```
□ Feature flag to disable
□ Database migration rollback
□ API versioning
□ Client-side fallback
```

## 10. Success Metrics

### North Star Metric
**Weekly Active Identifications** — number of unique users who identify at least one plant per week.

### Supporting Metrics
| Category | Metric | Target |
|---|---|---|
| Acquisition | App installs | 1000/week |
| Activation | First identification | 70% of installs |
| Retention | Day 7 retention | 30% |
| Revenue | Premium conversions | 5% of active users |
| Referral | Shares per user | 2/month |
