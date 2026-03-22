# Testing & Validation Log: Connectly API

This document outlines the testing procedures and results for the Terminal Assessment (Milestone 2), focusing on Security (RBAC), Privacy, and Performance Optimization.

---

## 🔒 Task 8: Role-Based Access Control (RBAC) & Privacy

### 8.1 Authentication Flow
* **Test Case:** Verify Token-Based Authentication.
* **Procedure:** Authenticate via the `/auth/login/` endpoint using valid credentials to receive an access token.
* **Result:** Successfully distinguished from standard Django session-based admin login, ensuring secure API-only access.

### 8.2 RBAC Validation (Role-Based Permissions)
* **Test Case:** Restrict `DELETE` operations to Admin roles.
* **Scenario A (Admin User):** Attempting to delete a post as an Admin results in a `204 No Content` or `200 OK`.
* **Scenario B (Standard User):** Attempting to delete a post as a non-admin results in a `403 Forbidden` or `404 Not Found`.
* **Result:** Permission logic correctly identifies user roles from the `UserProfile` and blocks unauthorized destructive actions.

### 8.3 Advanced Privacy Logic
* **Test Case:** Filter private content from the News Feed.
* **Procedure:** Create a post with `is_private=True`. Request the feed as a different user.
* **Result:** The private post is successfully omitted from the feed of non-owners, while remaining visible to the creator.

---

## ⚡ Task 9: Performance & Data Management

### 9.1 Pagination & Data Scaling
* **Implementation:** `PageNumberPagination`
* **Tests Conducted:**
    * **Default Feed:** Verified the presence of `count`, `next`, and `results` keys.
    * **Custom Page Size:** Appending `?page_size=2` correctly limits the result set.
    * **Error Handling:** Requesting a non-existent page (e.g., `?page=999`) returns a `404` error.
* **Result:** Data is successfully segmented, allowing for scalable frontend rendering.

### 9.2 Server-Side Caching
* **Implementation:** Django `@cache_page` (15-minute duration).
* **Tests Conducted:**
    * **Cache Hit:** Subsequent `GET` requests to the News Feed show significant reduction in response time (e.g., from 200ms to <20ms).
    * **Cache Invalidation:** Creating a new post triggers a cache refresh to ensure users see the latest content.
* **Result:** Database overhead is minimized, meeting performance optimization requirements.

### 9.3 Sorting & Filtering
* **Test Case:** Sort posts by specific criteria.
* **Procedure:** Requesting `/api/posts/?ordering=created_at` (Oldest) and `/api/posts/?ordering=-likes` (Most Liked).
* **Result:** Response objects are correctly ordered according to the requested metadata field.
