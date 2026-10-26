# API reference

Generated from the route decorators in `backend/app/routes/` and `backend/app/explore/routes.py`.
All JSON endpoints return `{ "success": bool, ... }`. **token** = send `Authorization: Bearer <JWT>` (from `/api/login` or `/api/signup`).

73 routes.


## auth

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| POST | `/api/forgot-password` | public | 5 per minute | Send password reset email with a one-time token link. |
| POST | `/api/login` | public | 10 per minute | User login endpoint |
| POST | `/api/reset-password` | public | 10 per minute | Reset password using the token from the email link. |
| POST | `/api/signup` | public | 10 per minute | User signup endpoint |

## analysis

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| POST | `/api/analyze-resume` | token | 10 per minute | Comprehensive resume analysis with NLP and PDF generation |
| POST | `/api/analyze/manual` | token | 10 per minute | Analyze manually entered skills |
| POST | `/api/analyze/upload` | token |  | Legacy endpoint - redirects to comprehensive analysis |

## community

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/community/<int:community_id>/members` | token |  | Get all members of a community |
| GET | `/api/community/<int:community_id>/messages` | token |  | Get all messages in a community chat room |
| POST | `/api/community/create` | token |  | Create a new community |
| GET | `/api/community/feed` | token |  | Get personalized ranked feed for user |
| GET | `/api/community/feed/trending` | token |  | Get trending posts based on recent engagement |
| GET | `/api/community/groups` | token |  | Get list of community groups |
| POST | `/api/community/groups` | token |  | Legacy endpoint - redirects to /api/community/create |
| GET | `/api/community/groups/<int:community_id>` | token |  | Get a single community by ID |
| DELETE | `/api/community/groups/<int:community_id>` | token |  | Delete a community group (soft delete) |
| POST | `/api/community/groups/<int:community_id>/join` | token |  | Legacy endpoint - Join a community by ID in URL |
| POST | `/api/community/join` | token |  | Join a community |
| POST | `/api/community/message/send` | token |  | Send a message to a community chat room |
| GET | `/api/community/reach-out` | token |  | Get related user profiles based on weighted similarity scoring |
| GET | `/api/community/reachout` | token |  | Get related user profiles based on weighted similarity scoring |
| GET | `/api/community/recommended` | token |  | Get recommended communities based on user interests |

## content

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/community/blogs` | token |  | Get all blog posts |
| POST | `/api/community/blogs` | token |  | Create a new blog post with optional video upload |
| DELETE | `/api/community/blogs/<int:post_id>` | token |  | Delete a blog post (soft delete) |
| POST | `/api/community/comments/<int:comment_id>/like` | token |  | Phase 9: Toggle like on a comment |
| GET | `/api/community/feedback` | token |  | Get all feedback posts |
| POST | `/api/community/feedback` | token |  | Submit new feedback |
| DELETE | `/api/community/feedback/<int:post_id>` | token |  | Delete a feedback post (soft delete) |
| POST | `/api/community/post` | token |  | Unified endpoint to create any type of post (blog or feedback) |
| GET | `/api/community/posts` | token |  | Get posts with optional filtering |
| POST | `/api/community/posts/<int:post_id>/comments` | token |  | Phase 9: Add a comment to a post |
| POST | `/api/community/posts/<int:post_id>/like` | token |  | Phase 9: Toggle like on a post |

## explore

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| POST | `/api/explore/compare` | token |  | POST /api/explore/compare — Career Comparator (with fit scores). |
| GET | `/api/explore/evaluation` | token |  | GET /api/explore/evaluation — Run recommendation logic on test dataset and return accuracy. |
| POST | `/api/explore/future` | token |  | POST /api/explore/future — Future You Simulation (personalized). |
| POST | `/api/explore/path-suggest` | token |  | POST /api/explore/path-suggest — Confusion Solver (skill-aware). |
| GET | `/api/explore/personalized-summary` | token |  | GET /api/explore/personalized-summary — Career Snapshot for the user. |
| GET | `/api/explore/reality` | token |  | GET /api/explore/reality?career=... — Reality Check (with user readiness). |
| POST | `/api/explore/roi` | token |  | POST /api/explore/roi — Skill ROI Analyzer (highlights missing skills). |

## media

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/community/videos/<path:filename>` | public |  | Serve uploaded video files |
| GET | `/uploads/community_images/<filename>` | public |  | Serve uploaded community images |
| GET | `/uploads/profile_pictures/<filename>` | public |  | Serve uploaded profile pictures |

## messaging

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/community/conversations` | token |  | Get all conversations for the current user |
| DELETE | `/api/community/conversations/<int:conversation_id>` | token |  | Soft-delete a conversation for the current user |
| POST | `/api/community/conversations/<int:conversation_id>/read` | token |  | Mark all messages in a conversation as read |
| POST | `/api/community/message` | token |  | Phase 8: Send a message to another user |
| POST | `/api/community/messages` | token |  | Legacy: Send a message to another user |
| GET | `/api/community/messages/<int:conversation_id>` | token |  | Phase 8: Get messages from a specific conversation |
| GET | `/api/community/messages/user/<int:recipient_id>` | token |  | Legacy: Get message history with a specific user |

## notifications

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/community/notifications` | token |  | Phase 9: Get user notifications |
| DELETE | `/api/community/notifications/<int:notification_id>` | token |  | Delete a single notification for the current user |
| POST | `/api/community/notifications/<int:notification_id>/read` | token |  | Legacy: Mark notification as read |
| POST | `/api/community/notifications/read` | token |  | Phase 9: Mark notification(s) as read |
| POST | `/api/community/notifications/read-all` | token |  | Legacy: Mark all notifications as read |

## postmatrics

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/postmatrics/after10th` | token |  | Get After 10th guidance recommendations |
| POST | `/api/postmatrics/after12th` | token |  | Analyze After 12th career options |
| GET | `/api/postmatrics/exams` | token |  | Get competitive exams list |
| POST | `/api/postmatrics/interest-test` | token |  | Submit interest assessment test |
| GET | `/api/postmatrics/scholarships` | token |  | Get scholarships |
| GET | `/api/postmatrics/skills` | token |  | Get skill-based careers |

## profile

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/profile` | token |  | Get user profile (protected route) |
| PUT/PATCH | `/api/profile` | token |  | Update user profile for Reach-Out matching |
| POST | `/api/upload/profile-picture` | token |  | Upload a profile picture for the current user. |
| PUT/PATCH | `/api/user` | token |  | Update basic user fields: name, domain, email |

## progress

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| GET | `/api/routine/evolution/analytics` | token |  | Get evolution analytics with graph-ready data |
| GET | `/api/routine/progress/summary` | token |  | Get progress summary with completion statistics per skill |
| GET | `/api/routine/progress/weekly` | token |  | Get user's weekly progress for all topics |
| POST | `/api/routine/progress/weekly` | token |  | Update completion status for a specific week/topic |

## routine

| Method | Path | Auth | Rate limit | Summary |
|---|---|---|---|---|
| POST | `/api/routine/chat` | token |  | AI chat for routine guidance and support |
| GET/POST | `/api/routine/evolution` | token |  | Get evolution data with daily/monthly progress and excellence metrics |
| POST | `/api/routine/generate` | token |  | Generate personalized learning routine from uploaded analysis file |
| POST | `/api/routine/progress` | token |  | Update skill progress and recalculate metrics |
