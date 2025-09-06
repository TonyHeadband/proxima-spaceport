from fastapi import APIRouter, HTTPException, Depends, status
from dependencies import get_db

from sqlalchemy.orm import Session

from models.indexer import IndexerResponseModel, ReposResponse
from models.indexer import CreateNewRepoModel, RepoCredentialsModel, NewRepoCredentialsModel

from services.indexer import create_new_repo, list_repositories
from services.indexer import create_new_credentials, get_all_credentials
from services.indexer import get_index_values


router = APIRouter()


@router.post(
    "/repos",
    name="indexer:add-repo",
)
async def add_repo(new_repo: CreateNewRepoModel, db: Session = Depends(get_db)):
    """
    Add a new repository to be indexed.
    """
    if not new_repo.url.startswith("http"):
        raise HTTPException(status_code=400, detail="Invalid repository URL")

    create_new_repo(new_repo.url, new_repo.name, new_repo.credentials_name, db)

    return IndexerResponseModel(status=status.HTTP_200_OK, message="RepositoryModel added successfully")


@router.get(
    "/repos",
    name="indexer:list-repos",
)
async def list_repos(db: Session = Depends(get_db)):
    """
    List all indexed repositories.
    """
    repos = list_repositories(db)

    return ReposResponse(repos=repos)


@router.post(
    "/credentials",
    name="indexer:add-credentials",
)
async def add_credentials(credentials: NewRepoCredentialsModel, db: Session = Depends(get_db)):
    """
    Add new credentials for accessing private repositories.
    """

    if not credentials.name:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Name is required")
    if not credentials.username:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="username is required")
    if not (credentials.password or credentials.token):
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail="Password or token is required")

    create_new_credentials(
        credentials.name, credentials.username, credentials.password, credentials.token, db)

    return IndexerResponseModel(status=status.HTTP_200_OK, message="Credentials added successfully")


@router.get(
    "/credentials",
    name="indexer:get-credentials",
)
async def get_credentials(db: Session = Depends(get_db)) -> list[RepoCredentialsModel]:
    """
    List all stored credentials.
    """
    return get_all_credentials(db)


@router.get(
    "/index",
    name="indexer:get-index",
)
async def get_index(name: str, db: Session = Depends(get_db)) -> list[str]:
    """
    Get indexing information for a specific repository.
    """
    try:
        values = get_index_values(db)
    except HTTPException:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="get_credentials_by_name failed unexpectedly")

    return values
