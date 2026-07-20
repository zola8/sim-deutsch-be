## The Wiring Flow in the app:

```
HTTP Request
    ↓
Router (uses UserSvcDep / AuthSvcDep)
    ↓
FastAPI resolves dependency:
    - get_user_service() 
        - get_user_repo()
            - get_db()  → yields Session
        - returns SQLAlchemyUserRepository(session)
    - returns UserService(repo)
    ↓
Service method executes
    ↓
Repository translates Pydantic ↔ ORM
    ↓
Database operation
    ↓
Response returned, session closed automatically
```
