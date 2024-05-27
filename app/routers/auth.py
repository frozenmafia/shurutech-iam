from fastapi import APIRouter, Depends, status, HTTPException
from .. import schemas, database, models, utils, oauth2
from sqlalchemy.orm import Session

router = APIRouter(
    tags=["Authentication"]
)


@router.post("/login", response_model=schemas.LoginResponse)
async def login(user_credentials: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    # Fetch user by username (OAuth2PasswordRequestForm uses "username" field, which should be an email)
    user: models.User = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token_data = {"id": user.id}
    access_token = oauth2.create_access_token(token_data)
    refresh_token = oauth2.create_refresh_token(token_data)

    return schemas.LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        token=access_token,
        token_type="bearer",
        refresh_token=refresh_token
    )


@router.post("/refresh_token", response_model=schemas.LoginResponse)
async def refresh_token(refresh_token: str = Depends(utils.get_token), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_data = oauth2.verify_access_token(refresh_token, credentials_exception)
    print(token_data)
    user = db.query(models.User).filter(models.User.id == token_data.user_id).first()

    if not user:
        raise credentials_exception

    new_access_token = oauth2.create_access_token({"id": user.id})

    return schemas.LoginResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        token=new_access_token,
        token_type="bearer",
        refresh_token=refresh_token
    )


@router.post("/register", response_model=schemas.UserCreated, status_code=status.HTTP_201_CREATED)
async def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing_user: models.User = db.query(models.User).filter(models.User.email == user.email).first()
    print('---------------------------------------------------------')
    print(existing_user)
    print('---------------------------------------------------------')
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email {user.email} already exists"
        )

    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/get_current_user", response_model=schemas.UserCreated)
async def get_current_user(token: str = Depends(utils.get_token), db: Session = Depends(database.get_db)):
    http_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials',
                                   headers={'WWW-Authenticate': 'Bearer'})

    token_data = oauth2.verify_access_token(token, http_exception)
    exists = db.query(models.User).filter(models.User.id == token_data.user_id).first()
    if exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User does not exists')
    return exists
