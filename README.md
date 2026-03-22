Check out our Detailed Testing & Validation Log for a full breakdown of our RBAC and Performance tests!
Connectly API

Features:
- User authentication
- Google OAuth login
- Create posts
- Like posts
- Comment on posts
- News feed

Endpoints:

POST /auth/google/login
POST /posts
POST /posts/{id}/like
POST /posts/{id}/comment
GET /posts/{id}/comments
GET /feed
# Testing & Validation Log: Connectly API

## 🔒 Task 8: Role-Based Access Control (RBAC) & Privacy
* **Authentication:** Verified Token-Based Auth via `/auth/login/`.
* **RBAC:** Confirmed that only Admin roles can perform `DELETE` operations (403/404 handling).
* **Privacy:** Verified that private posts are filtered out for non-owners.

## ⚡ Task 9: Performance & Data Management
* **Pagination:** Confirmed `count`, `next`, and `previous` keys are functional.
* **Caching:** Verified significant response time reduction on subsequent GET requests.
* **Sorting:** Confirmed ordering by `created_at` and `likes` works as intended.
